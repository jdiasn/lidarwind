import os
import xarray as xr
import pandas as pd
import glob as gb

import lidarSuit as lst
import matplotlib.pyplot as plt

# multi-core lib
# This parameter is used for setting the number of cores used.
import ray
ray.init(num_cpus=4, ignore_reinit_error=True)
# ------------------------------------------------------------


def imputDicParam(selDay, rangeRes, fileType):
    """
    This function creates a dictionary with 
    some basic useful parameters
    
    """
    
    dicParam = {}
    
    # path to the daily files
    dicParam['dataPath']='/Users/jdiasneto/Data/windcube/{0}/wind_and_aerosols_data/*'.format(selDay.strftime('%Y-%m-%d'))
    # variables required for processing
    dicParam['varList'] = ['azimuth', 'elevation', 'radial_wind_speed', 'radial_wind_speed_status', 'measurement_height', 'cnr']
    # range resolution
    dicParam['rangeRes'] = rangeRes
    # tipe of file
    dicParam['fileType'] = fileType
    # selected day 
    dicParam['selDay'] = selDay
    
    return dicParam


def getHourlyPathList(path, parameters): 
    
    """
    This function creates a list containing 
    all data paths from a given hourly path.
    
    """
    
    hour = path.split('/')[-1].split('-')[0] 
    date = pd.to_datetime('{0} {1}:00'.format(parameters['selDay'].strftime('%Y%m%d'), hour))
    
    genFileName = os.path.join(path,'*{0}*{1}.nc'.format(parameters['fileType'], parameters['rangeRes']))
        
    fileList = gb.glob(genFileName)
    fileList = sorted(fileList)

    return fileList


# ray.remote is a decorator that allows 
# executing the function mergeHourly 
# using multi-cores
@ray.remote
def mergeHourly(path, parameters):

    """
    This function merges all data from a given hourly path
    and it returns the merged dataset.
    """
    
    print(path)
    lidarData = xr.Dataset()
    tmpPathList = getHourlyPathList(path, parameters)

    tmpLidarData = lst.dbsOperations(tmpPathList, parameters['varList']).mergedDS
    lidarData = xr.merge([lidarData, tmpLidarData])

    return lidarData



def getDaylyDS(parameters):
    """
    This function gives a daly merged dataset cotaining 
    all variables required for derivbing wind speed and 
    direction from a given set of parameters
    """

    lidarData = xr.Dataset()
    hourlyDataPath = sorted(gb.glob(parameters['dataPath']))

    # ----- This is the only multi-core part of the code -----
    futures = [mergeHourly.remote(path, parameters) for path in hourlyDataPath]
    outputDataList = ray.get(futures)
    # ----- -------------------------------------------- -----
    
    for tmpData in outputDataList:
        
        lidarData = xr.merge([lidarData, tmpData]) 


    return lidarData


# main code

startProcess = pd.to_datetime('20210417')
endProcess = pd.to_datetime('20210417')
rangeRes = '25m'
fileType = 'dbs'

for selDay in pd.date_range(startProcess, endProcess):
    
    print(selDay)
    
    parameters = imputDicParam(selDay, rangeRes, fileType)
    lidarData = getDaylyDS(parameters)


windProp = lst.getWindProperties5Beam(lidarData.copy(), statusFilter=False,
                                      cnr=None, method='single_dbs')
#windProp = lst.getWindProperties5Beam(lidarData.copy(), statusFilter=True,
#                                      cnr=None, method='continuous', tolerance='9s')

windSpeed = lst.getResampledData(windProp.horWindSpeed).resampled
windDir = lst.getResampledData(windProp.horWindDir).resampled


plt.figure(figsize=(18,6))
windSpeed.plot(x='time_ref', cmap='turbo', vmin=0, vmax=20)
plt.grid(b=True)
plt.show()

plt.figure(figsize=(18,6))
windDir.plot(x='time_ref', cmap='turbo', vmin=50, vmax=300)
plt.grid(b=True)
plt.show()