import os
import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# import matplotlib as mpl


class plotSettings:
    
    def __init__(self, mpl, style='dark_background'):
        
        self.mpl = mpl
        self.style = style
        #self.updateSettings()
        
        return None
    
    def updateSettings(self):
        
        fs = 16
        
        # mpl.style.use('seaborn')
        self.mpl.style.use(self.style)
        self.mpl.rcParams['figure.figsize'] = [6, 6]
        self.mpl.rcParams['figure.dpi'] = 80
        self.mpl.rcParams['savefig.dpi'] = 100

        self.mpl.rcParams['font.size'] = fs
        self.mpl.rcParams['legend.fontsize'] = fs
        self.mpl.rcParams['figure.titlesize'] = fs

        self.mpl.rcParams['ytick.labelsize'] = fs
        self.mpl.rcParams['xtick.labelsize'] = fs
        self.mpl.rcParams['axes.titlesize'] = fs
        self.mpl.rcParams['axes.labelsize'] = fs

        self.mpl.rcParams['legend.fancybox'] = True
        self.mpl.rcParams['legend.framealpha'] = 0.7
        self.mpl.rcParams['legend.facecolor']='silver'
        self.mpl.rcParams['legend.frameon']=True

        self.mpl.rcParams['lines.linewidth'] = 5
        
        return self
    
    
    def plotSetup(plot):

        plt.setp(plot.axes.xaxis.get_majorticklabels(),rotation=0)
        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        plot.axes.xaxis.set_major_formatter(formatter)

        plt.grid(b=True)

        return plot

# class filtering:
    
#     def __init__(self, data):
        
#         self.data = data
        
#         return None
    
#     def getVerticalObsComp(self, variable, snr=False, status=True):
    
#         tmpData = self.data[variable]
    
#         if status:
#             tmpData = tmpData.where(self.data.radial_wind_speed_status90==1)
        
#         else:
#             pass

#         if snr != False:
#             tmpData = tmpData.where(self.data.cnr90 > snr)
            
#         else:
#             pass

#         tmpData = tmpData.where(self.data.elevation==90, drop=True)
        
    
#         return tmpData
    
#     def getRadialObsComp(self, variable, azm, snr=False, status=True):
    
#         tmpData = self.data[variable]
    
#         if status:
#             tmpData = tmpData.where(self.data.radial_wind_speed_status==1)
            
#         else:
#             pass
        
#         if snr != False:
#             tmpData = tmpData.where(self.data.cnr > snr)
            
#         else:
#             pass
        
#         tmpData = tmpData.where((self.data.elevation!=90) & (self.data.azimuth==azm), drop=True)
    
#         return tmpData

class visualizer:

    def __init__(self, data):

        self.data = data

        return None

    def viewOrigVar(self, varName, cmap='Spectral', vmin=-1, vmax=1,
                     elv='90', azm='-', save=False, plotID=None,
                     figPath=None, namePrefix=None, show=False):

        if plotID == 'rad_wind_speed_panel':

            tmpData = self.data
            self.plotDataAZM(dataNon90=tmpData, cmap=cmap, vmin=vmin,
                             vmax=vmax, plotID=plotID, figPath=figPath,
                             save=save, show=show)


        else:
            tmpData = filtering(self.data).getVerticalObsComp(varName)

            if namePrefix:
                strName = '{0}_{1}'.format(namePrefix, tmpData.attrs['standard_name'])

            else:
                strName = tmpData.attrs['standard_name']

            self.plotData(tmpData=tmpData, cmap=cmap, vmin=vmin, vmax=vmax,
                          elv=elv, azm=azm, save=save, plotID=plotID,
                          strName=strName, figPath=figPath, show=show)

        return None

    def viewRetVar(self, varName, cmap='Spectral', vmin=-1, vmax=1,
                     elv='90', azm='-', save=False, plotID=None,
                     figPath=None, namePrefix=None, show=False):


        tmpData = self.data[varName]

        strName = tmpData.attrs['standard_name']

        self.plotData(tmpData=tmpData, cmap=cmap, vmin=vmin, vmax=vmax,
                      elv=elv, azm=azm, save=save, plotID=plotID,
                      strName=strName, figPath=figPath, show=show)

        return None

    def plotData(self, tmpData, cmap='Spectral', vmin=-1, vmax=1,
                 elv='90', azm='-', save=False, plotID=None,
                 figPath=None, strName=None, show=False):

        selDay = pd.to_datetime(tmpData.time[0].values)
        maxTime = pd.to_datetime(pd.to_datetime(tmpData.time[0].values).strftime('%Y%m%d 23:59:59'))
        tmpData = tmpData.sel(time=slice(pd.to_datetime(tmpData.time[0].values), maxTime))

        if strName:
            tmpData.attrs['standard_name']= strName

        plt.figure(figsize=(18,8))
        plot = tmpData.plot(x='time', cmap=cmap, vmin=vmin, vmax=vmax)
        plot = plotSettings.plotSetup(plot)

        plt.grid(b=True)
        plt.ylim(0,12e3)
        plt.xlim(pd.to_datetime(selDay.strftime('%Y%m%d')), maxTime)
        plt.title('elv: {0}, azm: {1}'.format(elv, azm))

        if plotID == 'hor_wind_dir':
            plot.colorbar.set_ticks(np.linspace(0, 360, 9))

        if save:
            fileName = '{0}_{1}.png'.format(selDay.strftime('%Y%m%d'), plotID)
            outputFileName = os.path.join(figPath, fileName)
            print(outputFileName)
            plt.savefig(outputFileName, bbox_inches='tight')

        if show:
            plt.show()

        plt.close()

        return None

    def plotDataAZM(self, dataNon90, cmap='Spectral', vmin=-1, vmax=1,
                    figPath=None, save=False, plotID=None, show=False):

        elv = dataNon90.elv.values[0]
        fig, axes = plt.subplots(5, 1, sharex=True, figsize=(18,25))

        for axN, i in enumerate(dataNon90.azm.values):

            tmpData = dataNon90.sel(azm=i)

            selDay = pd.to_datetime(tmpData.time[0].values)
            maxTime = pd.to_datetime(pd.to_datetime(tmpData.time[0].values).strftime('%Y%m%d 23:59:59'))
            tmpData = tmpData.sel(time=slice(pd.to_datetime(tmpData.time[0].values), maxTime))


            plot = tmpData.plot(x='time', cmap=cmap, vmin=vmin, vmax=vmax, ax=axes[axN])
            plot = plotSettings.plotSetup(plot)

            axes[axN].grid(b=True)
            axes[axN].set_ylim(0,12e3)
            axes[axN].set_xlim(pd.to_datetime(tmpData.time[0].values), maxTime)
            axes[axN].set_title('elv: {0}, azm: {1}'.format(elv, i))

        if save:
            fileName = '{0}_{1}.png'.format(selDay.strftime('%Y%m%d'), plotID)
            outputFileName = os.path.join(figPath, fileName)
            print(outputFileName)
            plt.savefig(outputFileName, bbox_inches='tight')

        if show:
            plt.show()

        plt.close()

        return None