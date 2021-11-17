# code to generate the quicklooks
# from the lidar observations
# 
# by: José Dias Neto
# date: 20.09.2021

import glob as gb
import pandas as pd
import matplotlib as mpl 

# append the path of the parent directory
import sys
sys.path.append("../")
import lidarSuit as lst

# matplotlib.use('Agg')

#--------------------------------------
# style 
mpl = lst.plotSettings(mpl).updateSettings() # dark
# mpl.style.use('seaborn') # seaborn
#------------------------------------------


# required parameters
def imputDicParam(selDay):

    dicParam = {}
    
    dicParam['dataPath']='/Users/jdiasneto/Data/windcube/{0}/wind_and_aerosols_data/*'.format(selDay.strftime('%Y-%m-%d'))
    dicParam['dataPathOut'] = '/Users/jdiasneto/Data/windcube/processed/{0}'.format(selDay.strftime('%Y/%m/%d'))
    dicParam['plotPathOut'] = '/Users/jdiasneto/Data/windcube/plots/{0}'.format(selDay.strftime('%Y/%m'))
    dicParam['outputPrefix'] = 'cmtrace_windcube_'
    dicParam['rangeRes'] = '50m'
    dicParam['selDay'] = selDay
#    
    return dicParam


#------------------------------------------
# main code

firstDay, lastDay, rangeRes  = pd.to_datetime('20210921'), pd.to_datetime('20210921'), '50m'
dates = pd.date_range(firstDay, lastDay)

fileType = 'fixed'
save=True

for selDay in dates:

    if rangeRes=='25m':
        fileList = gb.glob('{0}/*{1}*{2}.nc'.format(imputDicParam(selDay)['dataPathOut'], 
                                                    fileType, rangeRes))
    if rangeRes=='50m':
        fileList = gb.glob('{0}/*{1}*{2}.nc'.format(imputDicParam(selDay)['dataPathOut'], 
                                                    fileType, rangeRes))
    
    # loading the preProcessedData
    fileList = sorted(fileList)
    mergedData = lst.readProcessedData(fileList).mergeData()

    # plotting vertical spectrum width
    lst.visualizer(mergedData).viewOrigVar('doppler_spectrum_width90', vmin=0.6, vmax=1.5, 
                                   cmap='turbo', plotID='spec_width_elv_90', save=save, 
                                   figPath= imputDicParam(selDay)['plotPathOut'],  
                                   namePrefix ='vertical')

    # plotting vertical radial velocity
    lst.visualizer(mergedData).viewOrigVar('radial_wind_speed90', vmin=-2, vmax=0.5, 
                                   plotID='rad_wind_elv_90', save=save,
                                   figPath= imputDicParam(selDay)['plotPathOut'],  
                                   namePrefix ='vertical')

    # plotting vertical carrier to noise ratio
    lst.visualizer(mergedData).viewOrigVar('cnr90', vmin=-30, vmax=-5, cmap='turbo', 
                                   plotID='cnr_elv_90', save=save,
                                   figPath=imputDicParam(selDay)['plotPathOut'],
                                   namePrefix ='vertical')
    
    # restructuring the data for retrieval  
    transfdData = lst.getRestructuredData(mergedData)
    
    # plotting azimuthal radial velocities
    lst.visualizer(transfdData.dataTransf).viewOrigVar('radial_wind', vmin=-7, vmax=7, 
                                                    figPath= imputDicParam(selDay)['plotPathOut'],
                                                    save=save, plotID='rad_wind_speed_panel')
    
    # wind properties retrieval 
    windProp = lst.fftWindPropRet(transfdData.dataTransf).windProp()
    
    # plotting wind direction
    lst.visualizer(windProp).viewRetVar('windDir', vmin=0, vmax=360, cmap='hsv',
                                    plotID='hor_wind_dir', save=save,
                                    figPath= imputDicParam(selDay)['plotPathOut'], 
                                    elv = windProp.elv.values)

    # plotting horizontal wind speed
    lst.visualizer(windProp).viewRetVar('horWindSpeed', vmin=0, vmax=20, cmap='turbo',
                                    plotID='hor_wind_speed', save=save,
                                    figPath= imputDicParam(selDay)['plotPathOut'], 
                                    elv = windProp.elv.values)

#------------------------------------------