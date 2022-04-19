import logging

import xarray as xr
import datetime as dt
import pandas as pd
import numpy as np

# import lidarSuit as lst
from .filters import filtering
from .filters import secondTripEchoFilter

from .lidar_code import getLidarData

module_logger = logging.getLogger('lidarSuit.dataOperator')
module_logger.debug('loading dataOperator')


class dataOperations:

    def __init__(self, dataPaths, verbose=False):

        self.logger = logging.getLogger('lidarSuit.dataOperator.dataOperations')
        self.logger.info('creating an instance of dataOperations')

        self.verbose = verbose
        self.dataPaths = dataPaths
        self.tmp90 = xr.Dataset()
        self.tmpNon90 = xr.Dataset()

        self.elevationFilter()
        self.renameVar90()
        self.getMergeData()

        return None


    def elevationFilter(self):

        self.logger.info('coverting azimuth: from 360 to 0 degrees')

        for filePath in self.dataPaths:

            try:
                tmpFile = getLidarData(filePath).openLidarFile()
                elevation = tmpFile.elevation.round(1)
                tmpFile['elevation'] = elevation
                tmpFile['azimuth'] = tmpFile.azimuth.round(1)
                tmpFile['azimuth'][tmpFile.azimuth==360]=0
            except:
                self.logger.info('Unknown file format: {0}'.format(filePath))

            try: 
                self.tmp90 = xr.merge([self.tmp90, tmpFile.where(elevation==90, drop=True)])
            except:
                self.logger.info('This file does not have 90 elv: {0}'.format(filePath))

            try:
                self.tmpNon90 = xr.merge([self.tmpNon90, tmpFile.where(elevation!=90, drop=True)])
            except:
                self.logger.info('This file only has 90 elv: {0}'.format(filePath))

        return self


    def renameVar90(self):

        self.logger.info('renaming range coordinate from vertical measurements')

        for var in self.tmp90.variables:

            if 'range' in self.tmp90[var].dims:

                self.tmp90 = self.tmp90.rename({var:'{0}90'.format(var)})

        return self


    def getMergeData(self):

        self.logger.info('merging vertical and non-vertical measurements')

        self.mergedData = xr.merge([self.tmp90, self.tmpNon90])

        return self


class readProcessedData:

    def __init__(self, fileList):

        self.fileList = fileList

        return None

    def mergeData(self):
        # open_msfdataset is massing up the dimensions
        # from radial observations. It will be deactivated
        # for while

        try:
            tmpMerged = self.mergeDataM1()

        except:
            print('switching from xr.open_mfdataset to xr.open_dataset' )
            tmpMerged = self.mergeDataM2()

#         tmpMerged = self.mergeDataM2()

        return tmpMerged

    def mergeDataM1(self):

        tmpMerged = xr.open_mfdataset(self.fileList, parallel=True)

        return tmpMerged

    def mergeDataM2(self):

        tmpMerged = xr.Dataset()

        for fileName in sorted(self.fileList):

            try:
                print('opening {0}'.format(fileName))
                tmpMerged = xr.merge([tmpMerged, xr.open_dataset(fileName)])

            except:
                print('problems with: {0}'.format(fileName))
                pass

        return tmpMerged


class getRestructuredData:

    def __init__(self, data, snr=False, status=True, nProf=500,
                       center=True, min_periods=30, nStd=2):

        self.data = data
        self.snr = snr
        self.status = status
        self.nProf = nProf
        self.center = center
        self.min_periods = min_periods
        self.nStd = nStd

        self.getCoordNon90()
        self.dataTransform()
        self.dataTransform90()

        return None


    def getCoordNon90(self):

        self.elvNon90 = np.unique(self.data.elevation.where(self.data.elevation!=90, drop=True))
        self.azmNon90 = np.unique(self.data.azimuth.where(self.data.elevation!=90, drop=True))
        self.azmNon90 = np.sort(self.azmNon90)

        self.timeNon90 = self.data.time.where(self.data.elevation != 90, drop=True)
        self.rangeNon90 = self.data.range

        return self


    def dataTransform(self):

        dopWindArr = np.empty((self.timeNon90.shape[0], self.rangeNon90.shape[0],
                               len(self.azmNon90), len(self.elvNon90)))

        for j, elv in enumerate(self.elvNon90):

            for i, azm in enumerate(self.azmNon90):

                tmpRadWind = filtering(self.data).getRadialObsComp('radial_wind_speed', azm,
                                                                   snr=self.snr, status=self.status)

                dopWindArr[:,:,i,j] = tmpRadWind.sel(time=self.timeNon90, method='Nearest').values

        newRange = self.data.range90.values[:len(self.data.range)]
        respDopVel = xr.DataArray(data=dopWindArr, dims=('time', 'range', 'azm', 'elv'),
                                  coords={'time':self.timeNon90, 'range':newRange,
                                          'azm':self.azmNon90, 'elv':self.elvNon90})

        respDopVel.attrs = {'standard_name': 'radial_wind_speed',
                            'units': 'm s-1',
                            'comments': 'radial wind speed vector.'}


        self.dataTransf = respDopVel
        # (maybe all STE filter should be in the same class)
        # self.dataTransf = secondTripEchoFilter(respDopVel, nProf=self.nProf, center=self.center,
        #                                        min_periods=self.min_periods, nStd=self.nStd).data

        return self


    def dataTransform90(self):

        tmpData = filtering(self.data).getVerticalObsComp('radial_wind_speed90',
                                                          snr=self.snr, status=self.status)
        tmpData = tmpData.isel(range90=slice(0,len(self.rangeNon90)))
        self.dataTransf90 = tmpData


        tmpData = filtering(self.data).getVerticalObsComp('relative_beta90',
                                                          snr=self.snr, status=self.status)
        tmpData = tmpData.isel(range90=slice(0,len(self.rangeNon90)))
        self.relative_beta90 = tmpData


        return self



class getResampledData:

    def __init__(self, xrDataArray, vertCoord = 'range',
                 timeFreq = '15s', tolerance=10, timeCoord = 'time'):


        self.varName = xrDataArray.name
        self.attrs = xrDataArray.attrs
        data = xrDataArray
        date = pd.to_datetime(data[timeCoord].values[0])

        self.timeRef = self.getTimeRef(date, timeFreq)
        self.vertCoord = data[vertCoord]


        timeRefSec = np.array(self.timeRef, float)*10**(-9)
        timeOrigSec = np.array(data[timeCoord].values, float)*10**(-9)

        deltaGrid = self.calcDeltaGrid(timeRefSec, timeOrigSec)
        timeIndexArray = self.getNearestIndexM2(deltaGrid, tolerance)

        self.values = self.timeResample(data, timeIndexArray, self.vertCoord)
        self.resampled = self.toDataArray()

        return None


    def getTimeRef(self, date, timeFreq='1s'):
        """
        Genetates the time reference grid used for
        resampling the data
        Parameters
        ----------
        date: date for resampling (pandas Timestamp)
        dateFreq: resolution of the reference grid (str, default=1s)
        Returns
        -------
        timeRef: time reference grid (DatetimeIndex)
        """

        start = dt.datetime(date.year,
                            date.month,
                            date.day,
                            0, 0, 0)

        end = dt.datetime(date.year,
                          date.month,
                          date.day,
                          23, 59, 59)

        timeRef = pd.date_range(start, end, freq=timeFreq)

        return timeRef


    def calcDeltaGrid(self, refGrid, origGrid):
        """
        Calculates the distance between the reference grid
        and the radar grid (time or range)
        Parameters
        ----------
        refGrid: reference grid (array[n])
        radarGrid: radar grid (array[m])
        Returns
        -------
        deltaGrid: distance between each element from
            the reference grid to each element from the
            radar grid
        """

        tmpGrid2d = np.ones((len(refGrid),
                             len(origGrid)))*origGrid

        deltaGrid = tmpGrid2d - np.reshape(refGrid,(len(refGrid),1))

        return deltaGrid


    def getNearestIndexM2(self, deltaGrid, tolerance):
        """
        Identify the index of the deltaGrid that fulfil
        the resampling tolerance
        Parameters
        ----------
        deltaGrid: output from calcRadarDeltaGrid
        tolerance: tolerance distance for detecting
            the closest neighbour (time or range)
        Returns
        -------
        gridIndex: array of indexes that fulfil the resampling
            tolerance
        """

        gridIndex = np.argmin(abs(deltaGrid), axis=1)
        deltaGridMin = np.min(abs(deltaGrid), axis=1)
        gridIndex = np.array(gridIndex, float)
        gridIndex[deltaGridMin>tolerance] = np.nan

        return gridIndex


    def timeResample(self, data, timeIndexArray, vertCoord):
        """
        It resamples a given radar variable using the
        time and range index calculated by getNearestIndexM2
        Parameters
        ----------
        var: radar variable name to be resampled
        xrDataset: xarray dataset containing the variables to
            be resampled
        timeIdexArray: time resampling index (output from getNearestIndexM2)
        rangeIndexArray: range resampling index (output from getNearestIndexM2)
        Returns
        -------
        resampledArr: time/range resampled numpy array
        """

        resampledTimeArr = np.ones((timeIndexArray.shape[0], self.vertCoord.shape[0]))*np.nan

        for t, timeIndex in enumerate(timeIndexArray):

            try:
                resampledTimeArr[t]= data.values[int(timeIndex)]

            except:
                pass

        return resampledTimeArr


    def toDataArray(self):
        """
        It creates a DataArray of the resampled data.
        """

        tmpDT = xr.DataArray(self.values,
                             dims=('time_ref', self.vertCoord.name),
                             coords={'time_ref':self.timeRef, 
                                   self.vertCoord.name:self.vertCoord.values},
                             name=self.varName,
                             attrs=self.attrs)

        tmpDT[self.vertCoord.name].attrs = self.vertCoord.attrs


        return tmpDT


class dbsOperations:
    """
    This class extracts the variables required to
    retrieve the wind information from the DBS files.
    """

    def __init__(self, fileList, varList):
        """
        Parameters:
        ------------

        fileList: list of DBS files
        varList: list of variables to be extracted from the DBS files

        Returns:
        --------

        it returns an object containing an instance of the
        merged files (.mergedDS)
        """

        self.logger = logging.getLogger('lidarSuit.dataOperator.dbsOperations')
        self.logger.info('creating an instance of dbsOperations')

        self.mergedDS = xr.Dataset()
        self.fileList = fileList
        self.varList = varList

        self.mergeData()


    def mergeData(self):
        """
        This method merges all files from a list of DBS files
        """

        self.logger.info('merging all DBS files')

        if bool(self.fileList) == False:
            self.logger.info('FATAL: lidarSuit stopped due to an empty list of DBS files.')
            exit()

        for file in self.fileList:

            try:
                fileToMerge = getLidarData(file).openLidarFile()
            except:
                self.logger.warning('This file has a problem {0}'.format(file))

            fileToMerge = self.add_mean_time(fileToMerge)

            try:
                self.merge2DS(fileToMerge)
            except:
                self.logger.warning('Merging not possible {0}'.format(file))


    def add_mean_time(self, lidarDS):
        """
        This method adds the mean time to each file from
        the DBS scan strategy.
        """

        self.logger.info('calculating the mean DBS time for each file')

        meanTimeNS = np.array(lidarDS.time.values, np.float64).mean()
        meanTime = pd.to_datetime(np.ones(len(lidarDS.time.values)) * meanTimeNS)
        meanTimeDA = xr.DataArray(data=meanTime, dims=('time'),
                                  coords={'time':lidarDS.time},
                                  name='scan_mean_time')

        lidarDS = lidarDS.merge(meanTimeDA)

        return lidarDS


    def merge2DS(self, fileToMerge):
        """
        This method merges the variables extracted from
        the single DBS file with the storage dataset (mergedDS).
        """

        self.logger.info('merging single DBS file')

        for var in self.varList:

            self.mergedDS = xr.merge([self.mergedDS, fileToMerge[var]])

        self.mergedDS = xr.merge([self.mergedDS, fileToMerge['scan_mean_time']])