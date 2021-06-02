import numpy as np
import xarray as xr
import xrft


class fftWindPropRet:

    def __init__(self, dopplerObs):

        self.dopplerObs = dopplerObs
#         self.elv = elv
        self.getCompAmp()
        self.getRadWindSpeed()
        self.getHorWindSpeed()
        self.getWindDir()

        return None

    def getCompAmp(self):

        self.compAmp = xrft.fft(self.dopplerObs, dim=['azm']).isel(freq_azm=-2)

        return self

    def getWindDir(self):

        self.windDir = -np.rad2deg(np.arctan2(self.compAmp.imag, self.compAmp.real))+180
        self.windDir.attrs = {'standard_name': 'retrived_wind_direction',
                              'units': 'deg',
                              'comments': 'wind direction retrived using the FFT method'}

        return self

    def getRadWindSpeed(self):

        self.radWindSpeed = 2* np.abs(self.compAmp)/self.dopplerObs.azm.shape[0]
        self.radWindSpeed.attrs = {'standard_name': 'retrived_radial_wind_velocity',
                                   'units': 'm s-1',
                                   'comments': 'radial wind velocity retrived using the FFT method'}

        return self

    def getHorWindSpeed(self):

        self.horWindSpeed = self.radWindSpeed/np.cos(np.deg2rad(self.dopplerObs.elv))
        self.horWindSpeed.attrs = {'standard_name': 'retrived_horizontal_wind_velocity',
                                   'units': 'm s-1',
                                   'comments': 'horizontal wind velocity retrived using the FFT method'}

        return self


class getWindProperties5Beam:

    def __init__(self, data):


        elevation = data.elevation.round(1)

        azimuthNon90 = data.azimuth.where(elevation!=90, drop=True).round(1)
        azimuthNon90[azimuthNon90==360] = 0
        self.azimuthNon90 = azimuthNon90

        self.elevetionNon90 = elevation.where(elevation!=90, drop=True)

        self.rangeVal90 = data.range.where(elevation==90, drop=True)
        self.radWindSpeed90 = data.radial_wind_speed.where(elevation==90, drop=True)
        self.windSpeedFlag90 = data.radial_wind_speed_status.where(elevation==90, drop=True)


        self.rangeValNon90 = data.range.where(elevation!=90, drop=True)
        self.radWindSpeedNon90 = data.radial_wind_speed.where(elevation!=90, drop=True)
        self.windSpeedFlagNon90 = data.radial_wind_speed_status.where(elevation!=90, drop=True)


        self.calcHorWindComp()
        self.calcHorWindSpeed()
        self.calcHorWindDir()

        return None

    def calcHorWindComp(self):

        """
        Function to derive wind v and u components. 
        It folows the same approach used by the lidar software.
        
        """

        compWindSpeed = self.radWindSpeedNon90/(2*np.cos(np.deg2rad(self.elevetionNon90)))

        compVN = compWindSpeed.where(self.azimuthNon90==0, drop=True)  
#         self.compVN = compVN
        compVS = compWindSpeed.where(self.azimuthNon90==180, drop=True)
#         self.compVS = compVS

        compUE = compWindSpeed.where(self.azimuthNon90==90, drop=True) 
#         self.compUE = compUE

        compUW = compWindSpeed.where(self.azimuthNon90==270, drop=True)
#         self.compUW = compUW

        compV = compUW.copy()
        compV.values = compVN.values - compVS.values

        compU = compUW.copy()
        compU.values = compUE.values - compUW.values

        self.compV = compV #compVN - compVS
        self.compU = compU #compUE - compUW 

        return self     

    def calcHorWindSpeed(self):

        """
        Function to calculate the wind speed.
        
        """

        self.horWindSpeed = np.sqrt(self.compV**2. + self.compU**2.)
        self.horWindSpeed.name = 'hor_wind_speed'

        return self

    def calcHorWindDir(self):

        """
        Function to derive wind direction. If folows the same 
        approach used by the lidar sftware. 
        
        """

        windDirTmp = np.rad2deg(np.arctan(self.compV/self.compU))
        windDir = windDirTmp.copy()*np.nan

        compV = self.compV.values
        compU = self.compU.values

        # arctan > 0 
        windDir.values[(compU > 0) & (compV > 0)] = 270 - windDirTmp.values[(compU > 0) & (compV > 0)] #ok
        windDir.values[(compU < 0) & (compV > 0)] = 90 - windDirTmp.values[(compU < 0) & (compV > 0)] 

        # arctan < 0 
        windDir.values[(compU < 0) & (compV < 0)] = 90 - windDirTmp.values[(compU < 0) & (compV < 0)] #ok
        windDir.values[(compU > 0) & (compV < 0)] = 270 - windDirTmp.values[(compU > 0) & (compV < 0)] #

        # arctan = 0
        windDir.values[(compU > 0) & (compV == 0)] = 270 + windDirTmp.values[(compU > 0) & (compV == 0)] #ok
        windDir.values[(compU < 0) & (compV == 0)] = 90 + windDirTmp.values[(compU < 0) & (compV == 0)] #ok

        windDir.name = 'hor_wind_dir'
        self.horWindDir = windDir

        return self
