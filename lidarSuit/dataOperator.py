import lidarSuit as lst
import xarray as xr
import datetime as dt
import pandas as pd
import numpy as np


class dataOperations:
    
    def __init__(self, fileList, varList):
        
        self.mergedDS = xr.Dataset()
        self.fileList = fileList
        self.varList = varList
    
        self.mergeData()
        
        return None

    def mergeData(self):
        
        for file in self.fileList:
            
            fileToMerge = lst.getLidarData(file).openLidarFile()
            
            try:
                self.merge2DS(fileToMerge)
                
            except:
                print('There is a problem in {0}'.format(file))
        
        return self
   
    def merge2DS(self, fileToMerge):
        
        for var in self.varList:
            
            self.mergedDS = xr.merge([self.mergedDS, fileToMerge[var]])
            
        return self
    
    
    
class getResampledData:
    
    def __init__(self, xrDataArray, vertCoord = 'gate_index',
                 timeFreq = '15s', tolerance=10):
    
        
        self.varName = xrDataArray.name
        data = xrDataArray
        date = pd.to_datetime(data.time.values[0])
        
        self.timeRef = self.getTimeRef(date, timeFreq)
        self.vertCoord = data[vertCoord]
        
        
        timeRefSec = np.array(self.timeRef, float)*10**(-9)
        timeOrigSec = np.array(data.time.values, float)*10**(-9)

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
                            date.hour, 0, 0)

        end = dt.datetime(date.year,
                          date.month,
                          date.day,
                          date.hour, 59, 59)

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
        
        tmpDT = xr.DataArray(self.values,
                             dims=('time_ref', self.vertCoord.name),
                             coords={'time_ref':self.timeRef, 
                                   self.vertCoord.name:self.vertCoord.values},
                             name=self.varName)

        
        return tmpDT
                             
                             
                             
                             
    
    