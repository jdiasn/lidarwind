"""Module to manage and prepare the data for other modules

"""


import logging

import xarray as xr
import datetime as dt
import pandas as pd
import numpy as np

# import lidarSuit as lst
from .filters import Filtering
from .filters import SecondTripEchoFilter

from .lidar_code import GetLidarData

module_logger = logging.getLogger("lidarSuit.dataOperator")
module_logger.debug("loading dataOperator")


class dataOperations:

    """Basic data manager

    It performs some basic operations. For example: rounds
    the values from the azimuth coordinate and separates
    the vertical observations from the slanted observations.

    It is helpful first use this class to process all data
    and then save the data as NetCDF files to speed up the
    derivation of wind properties later.

    Examples
    --------
    >>> mergedDS = lidarSuit.dataOperations(fileList).mergedData
    >>> mergedDS.to_netcdf(outputFilePath)

    Parameters
    ----------
    dataPaths : list
       List of paths of the original WindCube's output.

    Returns
    -------
    object : object
        it returns an object containing an instance of the
        original files merged (.mergedData)

    """

    def __init__(self, dataPaths, verbose=False):

        self.logger = logging.getLogger(
            "lidarSuit.dataOperator.dataOperations"
        )
        self.logger.info("creating an instance of dataOperations")

        if bool(dataPaths) == False:
            self.logger.error(
                "lidarSuit stopped due to an empty list of files."
            )
            raise FileNotFoundError

        self.verbose = verbose
        self.dataPaths = dataPaths
        self.tmp90 = xr.Dataset()
        self.tmpNon90 = xr.Dataset()

        self.elevationFilter()
        self.renameVar90()
        self.getMergeData()

    def elevationFilter(self):
        """
        It groups the data from the vertical and slanted observations
        and rounds the azimuth coordinate
        """

        self.logger.info("coverting azimuth: from 360 to 0 degrees")

        for filePath in self.dataPaths:

            try:
                tmpFile = GetLidarData(filePath).OpenLidarFile()
                self.logger.debug(f"reading file: {filePath}")
            except:
                self.logger.warning(f"This file has a problem: {filePath}")

            try:
                elevation = tmpFile.elevation.round(1)
                tmpFile["elevation"] = elevation
                tmpFile["azimuth"] = tmpFile.azimuth.round(1)
                tmpFile["azimuth"][tmpFile.azimuth == 360] = 0
            except:
                self.logger.info(f"Problems reading elv and axm: {filePath}")

            try:
                self.tmp90 = xr.merge(
                    [self.tmp90, tmpFile.where(elevation == 90, drop=True)]
                )
            except:
                self.logger.info(f"This file does not have 90 elv: {filePath}")

            try:
                self.tmpNon90 = xr.merge(
                    [self.tmpNon90, tmpFile.where(elevation != 90, drop=True)]
                )
            except:
                self.logger.info(f"This file only has 90 elv: {filePath}")

        return self

    def renameVar90(self):
        """
        It renames the vertical coordinate
        """

        self.logger.info(
            "renaming range coordinate from vertical measurements"
        )

        self.tmp90 = self.tmp90.rename_dims({"range": "range90"})

        for var in self.tmp90.variables:

            if "range90" in self.tmp90[var].dims:

                self.tmp90 = self.tmp90.rename({var: f"{var}90"})

        return self

    def getMergeData(self):
        """
        It merges all readable data
        """

        self.logger.info("merging vertical and non-vertical measurements")

        self.mergedData = xr.merge([self.tmp90, self.tmpNon90])

        return self


class readProcessedData:
    """Pre-processed data reader

    It reads all data pre-processed by dataOperator.dbsOperations
    and merges them.

    Examples
    --------
    >>> mergedData = lidarSuit.readProcessedData(fileList).mergeData()

    Parameters
    ----------
    fileList : list
        list of pre-processed NetCDF files

    Returns
    -------
    object : object
        an instance of all pre-processed data

    """

    def __init__(self, fileList):

        self.logger = logging.getLogger(
            "lidarSuit.dataOperator.readProcessedData"
        )
        self.logger.info("creating an instance of readProcessedData")

        if bool(fileList) == False:
            self.logger.error(
                "lidarSuit stopped due to an empty list of files."
            )
            raise FileNotFoundError

        self.fileList = fileList

    def mergeData(self):
        """
        It merges all data from the fileList. It can choose between
        two different methods. One uses xr.open_mfdataset and the other
        uses xr.open_dataset.
        """

        # open_msfdataset was massing up the dimensions
        # from radial observations.

        self.logger.info("merging pre-processed data")

        try:
            tmpMerged = self.mergeDataM1()

        except:
            print("switching from xr.open_mfdataset to xr.open_dataset")
            tmpMerged = self.mergeDataM2()

        return tmpMerged

    def mergeDataM1(self):
        """
        It merges data using xr.open_mfdatset
        """

        self.logger.info("mergin files using xr.open_mfdataset")

        tmpMerged = xr.open_mfdataset(self.fileList, parallel=True)

        return tmpMerged

    def mergeDataM2(self):
        """
        It merges data using xr.open_dataset
        """

        self.logger.info("mergin files using xr.open_dataset")

        tmpMerged = xr.Dataset()

        for fileName in sorted(self.fileList):

            try:
                self.logger.info(f"opening {fileName}")
                tmpMerged = xr.merge([tmpMerged, xr.open_dataset(fileName)])

            except:
                self.logger.info(f"problems with: {fileName}")
                pass

        return tmpMerged


class getRestructuredData:

    """Data re-structurer

    It prepares the data structure for using the wind retrieval
    modules.

    Examples
    --------
    >>> windProp = lidarSuit.getRestructuredData(mergedData)

    Parameters
    ----------
    data : xr.Dataset
        a xr.Dataset of pre-processed data

    snr : bool, int, optional
        if an interger is given it is used to
        as threshold to filter the data based on
        the signal to noise ratio

    status : bool, optional
        if true it filters the data using the status
        variable generated by the WindCube's software

    sProf : int, optional
        number of profiles used to calculate the anomaly for
        partially filter the second trip echoes
        (IT GOES TO FILTER MODULE)

    center : bool, optional
        (IT GOES TO FILTER MODULE)

    min_periods : int, optional
        (IT GOES TO FILTER MODULE)

    n_std : int, optional
        size of the standard deviation window used
        to partially remove the second trip echoes
        (IT GOES TO FILTER MODULE)

    check90 : bool, optional
        If True, it checks if the vertical observations
        are available. If False, the verification is ignored.

    Returns
    -------
    object : object

        an instance of the prepared for the retrieval

    """

    def __init__(
        self,
        data: xr.Dataset,
        snr=False,
        status=True,
        n_prof=500,
        center=True,
        min_periods=30,
        n_std=2,
        check90=True,
    ):

        self.logger = logging.getLogger(
            "lidarSuit.dataOperator.getRestructuredData"
        )
        self.logger.info("creating an instance of getRestructuredData")

        if not isinstance(data, xr.Dataset):
            self.logger.error("wrong data type: expecting a xr.Dataset")
            raise TypeError

        self.data = data
        self.snr = snr
        self.status = status
        self.n_prof = n_prof
        self.center = center
        self.min_periods = min_periods
        self.n_std = n_std

        self.vertical_component_check(check90)
        self.getCoordNon90()
        self.dataTransform()
        self.dataTransform90()

    def getCoordNon90(self):

        """
        It identifies and selects the slanted data
        """

        self.logger.info("identifying and selecting the slanted observations")

        self.elvNon90 = np.unique(
            self.data.elevation.where(self.data.elevation != 90, drop=True)
        )
        self.azmNon90 = np.unique(
            self.data.azimuth.where(self.data.elevation != 90, drop=True)
        )
        self.azmNon90 = np.sort(self.azmNon90)

        self.timeNon90 = self.data.time.where(
            self.data.elevation != 90, drop=True
        )
        self.rangeNon90 = self.data.range

        return self

    def dataTransform(self):

        """
        It creates an xr.DataArray from all slanted observations
        """

        self.logger.info("creating a DataArray of the slanted observations")

        dopWindArr = np.empty(
            (
                self.timeNon90.shape[0],
                self.rangeNon90.shape[0],
                len(self.azmNon90),
                len(self.elvNon90),
            )
        )

        for j, elv in enumerate(self.elvNon90):

            for i, azm in enumerate(self.azmNon90):

                tmpRadWind = Filtering(self.data).get_radial_obs_comp(
                    "radial_wind_speed", azm, snr=self.snr, status=self.status
                )

                dopWindArr[:, :, i, j] = tmpRadWind.sel(
                    time=self.timeNon90, method="Nearest"
                ).values

        newRange = self.data.range90.values[: len(self.data.range)]
        respDopVel = xr.DataArray(
            data=dopWindArr,
            dims=("time", "range", "azm", "elv"),
            coords={
                "time": self.timeNon90,
                "range": newRange,
                "azm": self.azmNon90,
                "elv": self.elvNon90,
            },
        )

        respDopVel.attrs = {
            "standard_name": "radial_wind_speed",
            "units": "m s-1",
            "comments": "radial wind speed vector.",
        }

        self.dataTransf = respDopVel
        # (maybe all STE filter should be in the same class)
        # self.dataTransf = secondTripEchoFilter(respDopVel, n_prof=self.n_prof, center=self.center,
        #                                        min_periods=self.min_periods, n_std=self.n_std).data

        return self

    def dataTransform90(self):

        """
        It creates an xr.DataArray from all vertically pointing observations
        """

        self.logger.info("selcting zenith observations")

        tmpData = Filtering(self.data).get_vertical_obs_comp(
            "radial_wind_speed90", snr=self.snr, status=self.status
        )
        tmpData = tmpData.isel(range90=slice(0, len(self.rangeNon90)))
        self.dataTransf90 = tmpData

        tmpData = Filtering(self.data).get_vertical_obs_comp(
            "relative_beta90", snr=self.snr, status=self.status
        )
        tmpData = tmpData.isel(range90=slice(0, len(self.rangeNon90)))
        self.relative_beta90 = tmpData

        return self

    def vertical_component_check(self, check90):

        if check90:
            if not hasattr(self.data, "radial_wind_speed90"):
                raise KeyError
        else:
            print("Vertical component check was ignored.")


class getResampledData:
    """Alternative basic data resample

    This class is used to resample the data
    into a given temporal grid.

    It mainly used internal processings of
    the package.

    Parameters
    -----------
    xrDataArray : xr.DataArray
        varaiable that will be resampled

    vertCoord : str
        name of the vertical coordinate

    timeFreq : str
        size of the window e.g.: '15s'

    tolerance : int
        maximum separation from the reference

    timeCoord : str
        name of the time coordinate

    Returns
    -------
    data : xr.DataArray

        time resampled variable

    """

    def __init__(
        self,
        xrDataArray: xr.DataArray,
        vertCoord="range",
        timeFreq="15s",
        tolerance=10,
        timeCoord="time",
    ):

        self.logger = logging.getLogger(
            "lidarSuit.dataOperator.getResampledData"
        )
        self.logger.info("creating an instance of getResampledData")

        if not isinstance(xrDataArray, xr.DataArray):
            self.logger.error("wrong data type: expecting a xr.DataArray")
            raise TypeError

        self.varName = xrDataArray.name
        self.attrs = xrDataArray.attrs
        data = xrDataArray
        date = pd.to_datetime(data[timeCoord].values[0])

        self.timeRef = self.getTimeRef(date, timeFreq)
        self.vertCoord = data[vertCoord]

        timeRefSec = np.array(self.timeRef, float) * 10 ** (-9)
        timeOrigSec = np.array(data[timeCoord].values, float) * 10 ** (-9)

        deltaGrid = self.calcDeltaGrid(timeRefSec, timeOrigSec)
        timeIndexArray = self.getNearestIndexM2(deltaGrid, tolerance)

        self.values = self.timeResample(data, timeIndexArray, self.vertCoord)
        self.resampled = self.toDataArray()

    def getTimeRef(self, date, timeFreq="1s"):
        """
        Genetates the time reference grid used for
        resampling the data

        Parameters
        ----------
            date : Timestamp
                date for resampling (pandas Timestamp)

            dateFreq: str
                resolution of the reference grid (str, default=1s)

        Returns
        -------
        timeRef : DatetimeIndex
            time reference grid (DatetimeIndex)

        """

        self.logger.info("defining the reference time")

        start = dt.datetime(date.year, date.month, date.day, 0, 0, 0)

        end = dt.datetime(date.year, date.month, date.day, 23, 59, 59)

        timeRef = pd.date_range(start, end, freq=timeFreq)

        return timeRef

    def calcDeltaGrid(self, refGrid, origGrid):
        """
        Calculates the distance between the reference grid
        and the radar grid (time or range)

        Parameters
        ----------
        refGrid : numpy.array
            reference grid (array[n])

        radarGrid : numpy.array
            radar grid (array[m])

        Returns
        -------
        deltaGrid : numpy.array

            distance between each element from
            the reference grid to each element from the
            radar grid
        """

        self.logger.info("calculating the distance to the reference")

        tmpGrid2d = np.ones((len(refGrid), len(origGrid))) * origGrid

        deltaGrid = tmpGrid2d - np.reshape(refGrid, (len(refGrid), 1))

        return deltaGrid

    def getNearestIndexM2(self, deltaGrid, tolerance):
        """
        Identify the index of the deltaGrid that fulfil
        the resampling tolerance

        Parameters
        ----------
        deltaGrid : numpy.array
            output from calcRadarDeltaGrid

        tolerance : int
            tolerance distance for detecting
            the closest neighbour (time or range)

        Returns
        -------
        gridIndex : np.array

            array of indexes that fulfil the resampling
            tolerance

        """

        self.logger.info("identifying index that fulfil the tolerance")

        gridIndex = np.argmin(abs(deltaGrid), axis=1)
        deltaGridMin = np.min(abs(deltaGrid), axis=1)
        gridIndex = np.array(gridIndex, float)
        gridIndex[deltaGridMin > tolerance] = np.nan

        return gridIndex

    def timeResample(self, data, timeIndexArray, vertCoord):
        """
        It resamples a given radar variable using the
        time and range index calculated by getNearestIndexM2

        Parameters
        ----------
        var : str
            radar variable name to be resampled

        xrDataset : xarray.dataset
            xarray dataset containing the variables to
            be resampled

        timeIdexArray : np.array
            time resampling index (output from getNearestIndexM2)

        rangeIndexArray : np.array
            range resampling index (output from getNearestIndexM2)

        Returns
        -------
        resampledArr : xarray.dataArray
            time/range resampled numpy array
        """

        self.logger.info(f"time resampling of: {self.varName}")

        resampledTimeArr = (
            np.ones((timeIndexArray.shape[0], self.vertCoord.shape[0]))
            * np.nan
        )

        for t, timeIndex in enumerate(timeIndexArray):

            try:
                resampledTimeArr[t] = data.values[int(timeIndex)]

            except:
                pass

        return resampledTimeArr

    def toDataArray(self):
        """
        It creates a DataArray of the resampled data.
        """

        self.logger.info(
            f"generating the new resampled DataArray: {self.varName}"
        )

        tmpDT = xr.DataArray(
            self.values,
            dims=("time_ref", self.vertCoord.name),
            coords={
                "time_ref": self.timeRef,
                self.vertCoord.name: self.vertCoord.values,
            },
            name=self.varName,
            attrs=self.attrs,
        )

        tmpDT[self.vertCoord.name].attrs = self.vertCoord.attrs

        return tmpDT


class dbsOperations:
    """DBS file manager

    This class extracts the variables required to
    retrieve the wind information from the DBS files.

    Parameters
    ----------
    fileList : list
        list of DBS files
    varList : list
        list of variables to be extracted from the DBS files

    Returns
    -------
    object : object

        it returns an object containing an instance of the
        merged files (.mergedDS)

    """

    def __init__(self, fileList, varList):

        self.logger = logging.getLogger("lidarSuit.dataOperator.dbsOperations")
        self.logger.info("creating an instance of dbsOperations")

        self.mergedDS = xr.Dataset()
        self.fileList = fileList
        self.varList = varList

        self.mergeData(fileList, varList)

    def mergeData(self, file_list, var_list):
        """
        This method merges all files from a list of DBS files

        Parameters
        ----------
        file_list : list
            list of files to be merged

        var_list : list
            list of variables to be merged

        """

        self.logger.info("merging all DBS files")

        if bool(file_list) == False:
            self.logger.error(
                "lidarSuit stopped due to an empty list of DBS files."
            )
            raise FileNotFoundError

        if bool(var_list) == False:
            self.logger.error(
                "lidarSuit stopped due to an empty list of variable"
            )
            raise KeyError

        for file in file_list:

            try:
                fileToMerge = GetLidarData(file).OpenLidarFile()
                self.logger.debug(f"reading file: {file}")
            except:
                self.logger.warning(f"This file has a problem: {file}")
                raise

            fileToMerge = self.mean_time_derivation(fileToMerge)
            # fileToMerge = self.add_mean_time(fileToMerge)

            try:
                self.merge2DS(fileToMerge, var_list)
            except:
                self.logger.warning(f"Merging not possible: {file}")
                # raise

    def add_mean_time(self, lidarDS):
        """
        This method adds the mean time to each file from
        the DBS scan strategy.

        Parameters
        ----------
        lidarDS : xarray.DataSet
            a dataset from a sequence of scans

        """

        self.logger.info("calculating the mean DBS time for each file")

        meanTimeNS = np.array(lidarDS.time.values, np.float64).mean()
        meanTime = pd.to_datetime(
            np.ones(len(lidarDS.time.values)) * meanTimeNS
        )
        meanTimeDA = xr.DataArray(
            data=meanTime,
            dims=("time"),
            coords={"time": lidarDS.time},
            name="scan_mean_time",
        )

        lidarDS = lidarDS.merge(meanTimeDA)

        return lidarDS

    def merge2DS(self, fileToMerge, var_list):
        """
        This method merges the variables extracted from
        the single DBS file with the storage dataset (mergedDS).

        Parameters
        ----------
        fileToMerge : xarray.DataSet
            a single file dataset

        var_list : list
            a list of variables to be merged

        """

        self.logger.info("merging single DBS file")

        for var in var_list:

            self.mergedDS = xr.merge([self.mergedDS, fileToMerge[var]])

        self.mergedDS = xr.merge(
            [self.mergedDS, fileToMerge["scan_mean_time"]]
        )

    def mean_time_derivation(self, data):

        data.azimuth.values = np.round(data.azimuth.values)
        data.azimuth.values[data.azimuth.values == 360] = 0

        azm_ref = data.azimuth.values[0]
        index_new_scan = data.ray_index.where(
            (data.elevation != 90) & (data.azimuth == azm_ref)
        )
        index_complete_scans = index_new_scan.values[
            np.isfinite(index_new_scan.values)
        ]

        if not len(data.time) in index_complete_scans:
            index_complete_scans = np.append(
                index_complete_scans, len(data.time)
            )

        groups = data.groupby_bins(
            "ray_index", index_complete_scans, right=False
        )

        new_data = xr.Dataset()
        for grp in groups.groups:

            new_data = xr.merge([new_data, self.add_mean_time(groups[grp])])

        return new_data
