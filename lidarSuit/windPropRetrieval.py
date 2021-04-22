import numpy as np


class getWindProperties:

    def __init__(self, data):

        
        elevation = data.elevation.round(1)
        
        azimuthNon90 = data.azimuth.where(elevation!=90, drop=True).round(1)
        azimuthNon90[azimuthNon90==360] = 0
        self.azimuthNon90 = azimuthNon90
        
        self.elevetionNon90 = elevation.where(elevation!=90, drop=True)

        self.rangeVal90 = data.range.where(elevation==90, drop=True)
        self.radWindSpeed90 = data.radial_wind_speed.where(elevation==90, drop=True)

        self.rangeValNon90 = data.range.where(elevation!=90, drop=True)
        self.radWindSpeedNon90 = data.radial_wind_speed.where(elevation!=90, drop=True)

        self.calcHorWindComp()
        self.calcHorWindSpeed()
#         self.calcHorWindDir()

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

        return self

    def calcHorWindDir(self):
        
        """
        Function to derive wind direction. If folows the same 
        approach used by the lidar sftware. 
        
        """

        compV = self.compV
        compU = self.compU
        windDirTmp = np.rad2deg(np.arctan(compV/compU))
        windDir = windDirTmp.copy()*np.nan

        # arctan > 0 
        windDir.values[(compU > 0) & (compV > 0)] = 270 - windDirTmp.values[(compU > 0) & (compV > 0)] #ok
        windDir.values[(compU < 0) & (compV > 0)] = 90 - windDirTmp.values[(compU < 0) & (compV > 0)] 

        # arctan < 0 
        windDir.values[(compU < 0) & (compV < 0)] = 90 - windDirTmp.values[(compU < 0) & (compV < 0)] #ok
        windDir.values[(compU > 0) & (compV < 0)] = 270 - windDirTmp.values[(compU > 0) & (compV < 0)] #

        # arctan = 0
        windDir.values[(compU > 0) & (compV == 0)] = 270 + windDirTmp.values[(compU > 0) & (compV == 0)] #ok
        windDir.values[(compU < 0) & (compV == 0)] = 90 + windDirTmp.values[(compU < 0) & (compV == 0)] #ok

        self.horWindDir = windDir

        return self