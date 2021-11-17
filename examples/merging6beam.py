# code to pre process
# the lidar observations
# 
# by: José Dias Neto
# date: 20.09.2021


import os 
import glob as gb
import pandas as pd

# append the path of the parent directory
import sys
sys.path.append("../")

import lidarSuit as lst

#------------------------------------------
# multi-core lib
# This parameter is used for setting the number of cores used.
import ray
ray.init(num_cpus=5, ignore_reinit_error=True)
#------------------------------------------


# required parameters
def imputDicParam(selDay, rangeRes, fileType):
    """
    This function creates a dictionary with 
    some basic useful parameters
    
    """
    
    dicParam = {}
    
    dicParam['dataPath']='/Users/jdiasneto/Data/windcube/{0}/wind_and_aerosols_data/*'.format(selDay.strftime('%Y-%m-%d'))
    dicParam['dataPathOut'] = '/Users/jdiasneto/Data/windcube/processed/{0}'.format(selDay.strftime('%Y/%m/%d'))
    dicParam['outputPrefix'] = 'cmtrace_windcube_'
    dicParam['rangeRes'] = rangeRes
    dicParam['selDay'] = selDay
    dicParam['fileType'] = fileType
    
    return dicParam



# ray.remote is a decorator that allows 
# executing the function mergeHourly 
# using multi-cores
@ray.remote
def processOneHour(path, parameters, verbose=False): 

    fileList = []
    
    hour = path.split('/')[-1].split('-')[0] 
    date = pd.to_datetime('{0} {1}:00'.format(parameters['selDay'].strftime('%Y%m%d'), hour))
    
    
    genFileName = os.path.join(path,'*{0}*{1}.nc'.format(parameters['fileType'], parameters['rangeRes']))
        
    fileListTmp = sorted(gb.glob(genFileName))
    fileList.extend(fileListTmp)
    
    outputFileName = '{0}{1}_{2}_{3}.nc'.format(parameters['outputPrefix'], date.strftime('%Y%m%d_%H'),
                                                parameters['fileType'], parameters['rangeRes'])
    
    outputFilePath = os.path.join(parameters['dataPathOut'], outputFileName)
    
#     varList = parameters['varList']
    mergedDS = lst.dataOperations(fileList, verbose=verbose).mergedData
    mergedDS.to_netcdf(outputFilePath)
    
    if verbose:
        print(outputFilePath)
    
    return outputFilePath


#--------------------------------------------------
# main code

startProcess = pd.to_datetime('20210921')
endProcess = pd.to_datetime('20210921')

rangeRes = '50m'
fileType = 'fixed'


for selDay in pd.date_range(startProcess, endProcess):
    
    print('processing: {0}'.format(selDay))
    parameters = imputDicParam(selDay, rangeRes, fileType)
    hourlyDataPath = gb.glob(parameters['dataPath'])
    futures = [processOneHour.remote(path, parameters) for path in hourlyDataPath]
    outputFileList = ray.get(futures)
#------------------------------------------
