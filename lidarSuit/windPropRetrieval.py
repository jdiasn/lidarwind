import numpy as np
import xarray as xr
import xrft


class fftWindPropRet:

    def __init__(self, dopplerObs):

        self.dopplerObs = dopplerObs
#         self.elv = elv
        self.getCompAmp()
        self.getPhase()
        self.getRadWindSpeed()
        self.getHorWindSpeed()
        self.getWindDir()
        self.getWindConpU()
        self.getWindConpV()

        return None

    def getCompAmp(self):

        self.compAmp = xrft.fft(self.dopplerObs, dim=['azm']).isel(freq_azm=-2)

        return self

    def getPhase(self):

        self.phase = -np.rad2deg(np.arctan2(self.compAmp.imag, self.compAmp.real))
        self.phase.attrs = {'standard_name': 'retrived_phase',
                              'units': 'deg',
                              'comments': 'phase derived using the FFT method'}

        return self

    def getWindDir(self):

        self.windDir = self.phase + 180
        self.windDir.attrs = {'standard_name': 'retrived_wind_direction',
                              'units': 'deg',
                              'comments': 'wind direction retrived using the FFT method'}

        return self

    def getRadWindSpeed(self):

        self.radWindSpeed = 2 * np.abs(self.compAmp)/self.dopplerObs.azm.shape[0]
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

    def getAzmWind(self, azm):

        azmHorWind = self.radWindSpeed * np.sin(np.deg2rad(azm) + np.deg2rad(self.phase.values + 180))
        azmHorWind = azmHorWind/np.cos(np.deg2rad(self.dopplerObs.elv))

        return azmHorWind

    def getWindConpU(self):

        self.compU = self.getAzmWind(0)
        self.compU.attrs = {'standard_name': 'retrived_u_component',
                            'units': 'm s-1',
                            'comments': 'u wind component retrieved using the FFT method'}

        return self

    def getWindConpV(self):

        self.compV = self.getAzmWind(90)
        self.compV.attrs = {'standard_name': 'retrived_v_component',
                            'units': 'm s-1',
                            'comments': 'v wind component retrieved using the FFT method'}

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

        # replace range by measurement_height
        # self.rangeValNon90 = data.range.sel(time=timeNon90)
        self.rangeValNon90 = data.measurement_height.sel(time=timeNon90)
        self.radWindSpeedNon90 = data.radial_wind_speed.sel(time=timeNon90)

        # self.rangeVal90 = data.range.sel(time=time90)
        self.rangeVal90 = data.measurement_height.sel(time=time90)
        self.verWindSpeed = data.radial_wind_speed.sel(time=time90)
        self.correctVertWindComp()

        self.calcHorWindComp()
        self.calcHorWindSpeed()
        self.calcHorWindDir()

        return None


    def correctWindComp(self, comp):

        """
        This function replaces the gate_index coordinate
        by the measurement_height.
        (For any component)
        """

        comp = comp.rename({'gate_index':'range'})
        comp = comp.assign_coords({'range':self.rangeVal90.values[0]})
        comp.range.attrs = self.rangeVal90.attrs

        return comp


    def correctVertWindComp(self):

        """
        This function replaces the original from the vertical
        wind component with the gate_index by the measurement_height.
        """

        verWindSpeed = self.correctWindComp(self.verWindSpeed)
        verWindSpeed.name = 'compW'
        self.verWindSpeed = verWindSpeed

        return self


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

        self.compV = -(compVN - compVS)
        self.compU = -(compUE - compUW)

        self.compV = self.correctWindComp(self.compV)
        self.compU = self.correctWindComp(self.compU)

        self.compV.name = 'compV'
        self.compU.name = 'compU'

        self.compU = self.compU.reindex(time = self.compV.time, method='Nearest',
                                        tolerance=self.tolerance)


        return self     


    def calcHorWindSpeed(self):

        """
        Function to calculate the wind speed.

        """

        horWindSpeed = np.sqrt(self.compV**2. + self.compU**2.)
        horWindSpeed.name = 'hor_wind_speed'
        horWindSpeed.attrs['long_name'] = 'wind_speed'
        horWindSpeed.attrs['units'] = 'm/s'

#         horWindSpeed = horWindSpeed.rename({'gate_index':'range'})
#         horWindSpeed = horWindSpeed.assign_coords({'range':self.rangeVal90.values[0]})
#         horWindSpeed.range.attrs = self.rangeVal90.attrs

        self.horWindSpeed = horWindSpeed


        return self


    def calcHorWindDir(self):

        """
        Function to derive wind direction. If folows the same 
        approach used by the lidar sftware. 

        """

############################################
        windDir = 180 + np.rad2deg(np.arctan2(-self.compU, -self.compV))

        windDir.name = 'hor_wind_dir'
        windDir.attrs['long_name'] = 'wind_direction'
        windDir.attrs['units'] = 'deg'

        self.horWindDir = windDir
############################################


#         windDirTmp = np.rad2deg(np.arctan(self.compV/self.compU))

#         windDir = windDirTmp.copy()*np.nan

#         compV = self.compV.values * -1
#         compU = self.compU.values * -1

#         # arctan > 0
#         windDir.values[(compU > 0) & (compV > 0)] = 270 - windDirTmp.values[(compU > 0) & (compV > 0)] #ok
#         windDir.values[(compU < 0) & (compV > 0)] = 90 - windDirTmp.values[(compU < 0) & (compV > 0)]

#         # arctan < 0
#         windDir.values[(compU < 0) & (compV < 0)] = 90 - windDirTmp.values[(compU < 0) & (compV < 0)] #ok
#         windDir.values[(compU > 0) & (compV < 0)] = 270 - windDirTmp.values[(compU > 0) & (compV < 0)] #

#         # arctan = 0
#         windDir.values[(compU > 0) & (compV == 0)] = 270 + windDirTmp.values[(compU > 0) & (compV == 0)] #ok
#         windDir.values[(compU < 0) & (compV == 0)] = 90 + windDirTmp.values[(compU < 0) & (compV == 0)] #ok


#         windDir.name = 'hor_wind_dir'
#         windDir.attrs['long_name'] = 'wind_direction'
#         windDir.attrs['units'] = 'deg'

#         self.horWindDir = windDir



#         windDir = windDir.rename({'gate_index':'range'})
#         windDir = windDir.assign_coords({'range':self.rangeVal90.values[0]})
#         windDir.range.attrs = self.rangeVal90.attrs

        return self
