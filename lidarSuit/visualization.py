import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# import matplotlib as mpl


class plotSettings:
    
    def __init__(self, mpl):
        
        self.mpl = mpl
        #self.updateSettings()
        
        return None
    
    def updateSettings(self):
        
        fs = 16
        
        # mpl.style.use('seaborn')
        self.mpl.style.use('dark_background')
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


class filtering:
    
    def __init__(self, data):
        
        self.data = data
        
        return None
    
    def getVerticalObsComp(self, variable, snr=False):
    
        tmpData = self.data[variable].where(self.data.radial_wind_speed_status90==1)

        if snr != False:
            tmpData = tmpData.where(self.data.cnr90 > snr)
            
        else:
            pass

        tmpData = tmpData.where(self.data.elevation==90, drop=True)
        
    
        return tmpData
    
    def getRadialObsComp(self, variable, azm, snr=False):
    
        tmpData = self.data[variable].where(self.data.radial_wind_speed_status==1)
        
        if snr != False:
            tmpData = tmpData.where(self.data.cnr > snr)
            
        else:
            pass
        
        tmpData = tmpData.where((self.data.elevation!=90) & (self.data.azimuth==azm), drop=True)
    
        return tmpData
    
    
