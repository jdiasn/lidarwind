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

    def __init__(self, data, statusFilter=True, cnr=None, tolerance='8s'):

        """
        This class caculates the wind speeed and direction
        using the 5bean dataset (DBS files) as input.

        Parameters
        ----------

        data: merged xarray dataset (mergedDS) output from
        lst.dbsOperations()

        statusFilter: Data filtering based on the wind lidar
        wind status variable. If True, all data with status not
        equal to 1 are remove. If False, no filtering is applied.

        cnr: Filter based on the carrier to noise ratio.
        If None, no filtering is applied. I a cnr value is given,
        all data smaller than the cnr is removed.


        Retunrs:
        --------

        This class returns an object containing the
        derived wind speed (.horWindSpeed) and
        direction (.horWindDir).

        """


        if statusFilter:
            data['radial_wind_speed'] = data.radial_wind_speed.where(data.radial_wind_speed_status==1)

        if cnr != None:
            data['radial_wind_speed'] = data.radial_wind_speed.where(data.cnr >= cnr)

        elevation = data.elevation.round(1)

        time90 = elevation.time.where(elevation==90, drop=True)
        timeNon90 = elevation.time.where(elevation!=90, drop=True)

        azimuthNon90 = data.azimuth.sel(time=timeNon90, method='Nearest').round(1)
        azimuthNon90[azimuthNon90==360] = 0

        self.tolerance = tolerance

        self.azimuthNon90 = azimuthNon90
        self.elevetionNon90 = elevation.sel(time=timeNon90)

        self.rangeValNon90 = data.range.sel(time=timeNon90)
        self.radWindSpeedNon90 = data.radial_wind_speed.sel(time=timeNon90)

        self.rangeVal90 = data.range.sel(time=time90)
        self.radWindSpeed90 = data.radial_wind_speed.sel(time=time90)

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
        compVS = compWindSpeed.where(self.azimuthNon90==180, drop=True)
        compVS = compVS.reindex(time=compVN.time, method='Nearest', tolerance=self.tolerance)

        compUE = compWindSpeed.where(self.azimuthNon90==90, drop=True) 
        compUW = compWindSpeed.where(self.azimuthNon90==270, drop=True)
        compUW = compUW.reindex(time=compUE.time, method='Nearest', tolerance=self.tolerance)

        self.compV = compVN - compVS
        self.compU = compUE - compUW

        self.compU = self.compU.reindex(time = self.compV.time, method='Nearest', tolerance=self.tolerance)

        return self     

    def calcHorWindSpeed(self):

        """
        Function to calculate the wind speed.

        """

        horWindSpeed = np.sqrt(self.compV**2. + self.compU**2.)
        horWindSpeed.name = 'hor_wind_speed'
        horWindSpeed.attrs['long_name'] = 'wind_speed'
        horWindSpeed.attrs['units'] = 'm/s'

        horWindSpeed = horWindSpeed.rename({'gate_index':'range'})
        horWindSpeed = horWindSpeed.assign_coords({'range':self.rangeVal90.values[0]})
        horWindSpeed.range.attrs = self.rangeVal90.attrs

        self.horWindSpeed = horWindSpeed


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
        windDir.attrs['long_name'] = 'wind_direction'
        windDir.attrs['units'] = 'deg'

        windDir = windDir.rename({'gate_index':'range'})
        windDir = windDir.assign_coords({'range':self.rangeVal90.values[0]})
        windDir.range.attrs = self.rangeVal90.attrs

        self.horWindDir = windDir

        return self