import numpy as np


class getWindProperties:

    def __init__(self, data):

        self.azimuthNon90 = data.azimuth.where(data.elevation!=90, drop=True)
        self.elevetionNon90 = data.elevation.where(data.elevation!=90, drop=True)

        self.rangeVal90 = data.range.where(data.elevation==90, drop=True)[0]
        self.radWindSpeed90 = data.radial_wind_speed.where(data.elevation==90, drop=True)[0]

        self.rangeValNon90 = data.range.where(data.elevation!=90, drop=True)
        self.radWindSpeedNon90 = data.radial_wind_speed.where(data.elevation!=90, drop=True)

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

        compVN = compWindSpeed.where(self.azimuthNon90==0, drop=True)[0]  
        compVS = compWindSpeed.where(self.azimuthNon90==180, drop=True)[0]

        compUE = compWindSpeed.where(self.azimuthNon90==90, drop=True)[0] 
        compUW = compWindSpeed.where(self.azimuthNon90==270, drop=True)[0]

        self.compV = compVN - compVS
        self.compU = compUE - compUW 

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