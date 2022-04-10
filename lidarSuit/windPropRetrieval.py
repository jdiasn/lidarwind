import numpy as np
import xarray as xr
import xrft

from .filters import filtering
from .dataAttributesL1 import loadAttributes

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
        # self.phase.attrs = {'standard_name': 'retrived_phase',
        #                       'units': 'deg',
        #                       'comments': 'phase derived using the FFT method'}

        return self

    def getWindDir(self):

        self.windDir = self.phase + 180
        # self.windDir.attrs = {'standard_name': 'retrived_wind_direction',
        #                       'units': 'deg',
        #                       'comments': 'wind direction retrived using the FFT method'}

        return self

    def getRadWindSpeed(self):

        self.radWindSpeed = 2 * np.abs(self.compAmp)/self.dopplerObs.azm.shape[0]
        # self.radWindSpeed.attrs = {'standard_name': 'retrived_radial_wind_velocity',
        #                            'units': 'm s-1',
        #                            'comments': 'radial wind velocity retrived using the FFT method'}

        return self

    def getHorWindSpeed(self):

        self.horWindSpeed = self.radWindSpeed/np.cos(np.deg2rad(self.dopplerObs.elv))
        # self.horWindSpeed.attrs = {'standard_name': 'retrived_horizontal_wind_velocity',
        #                            'units': 'm s-1',
        #                            'comments': 'horizontal wind velocity retrived using the FFT method'}

        return self

    def getAzmWind(self, azm):

        azmHorWind = self.radWindSpeed * np.sin(np.deg2rad(azm) + np.deg2rad(self.phase.values + 180))
        azmHorWind = azmHorWind/np.cos(np.deg2rad(self.dopplerObs.elv))

        return azmHorWind

    def getWindConpU(self):

        self.compU = self.getAzmWind(0)
        # self.compU.name = 'compU'
        # self.compU.attrs = {'standard_name': 'retrived_u_component',
        #                     'units': 'm s-1',
        #                     'comments': 'u wind component retrieved using the FFT method'}

        return self

    def getWindConpV(self):

        self.compV = self.getAzmWind(90)
        # self.compV.name = 'compV'
        # self.compV.attrs = {'standard_name': 'retrived_v_component',
        #                     'units': 'm s-1',
        #                     'comments': 'v wind component retrieved using the FFT method'}

        return self

    def windProp(self):

        windProp = xr.Dataset()
        windProp['horizontal_wind_direction'] = self.windDir
        windProp['horizontal_wind_speed'] = self.horWindSpeed
        windProp['zonal_wind'] = self.compU
        windProp['meridional_wind'] = self.compV

        return windProp


class getWindProperties5Beam:

    def __init__(self, data, statusFilter=True, cnr=None, method='single_dbs', tolerance='8s'):

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
        self.meanTimeNon90 =  data.scan_mean_time.sel(time=timeNon90)

        # self.rangeVal90 = data.range.sel(time=time90)
        self.rangeVal90 = data.measurement_height.sel(time=time90)
        self.verWindSpeed = data.radial_wind_speed.sel(time=time90)
        self.correctVertWindComp()

        if method == 'continuous':
            self.calcHorWindComp_continuous()

        if method == 'single_dbs':
            self.calcHorWindComp_single_dbs()

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


    def calcHorWindComp_single_dbs(self):

        """
        This method derives v and u components from the
        WindCube DBS files. The components are caculated
        from each individual DBS file. The mean time from each
        scan complete scan is used as identification tag.
        """

        compWindSpeed = self.radWindSpeedNon90/(2*np.cos(np.deg2rad(self.elevetionNon90)))

        compVN = compWindSpeed.where(self.azimuthNon90==0, drop=True)
        meanTimeVN = self.meanTimeNon90.where(self.azimuthNon90==0, drop=True)
        compVN = compVN.assign_coords({'time':meanTimeVN})

        compVS = compWindSpeed.where(self.azimuthNon90==180, drop=True)
        meanTimeVS = self.meanTimeNon90.where(self.azimuthNon90==180, drop=True)
        compVS = compVS.assign_coords({'time':meanTimeVS})

        compUE = compWindSpeed.where(self.azimuthNon90==90, drop=True)
        meanTimeUE = self.meanTimeNon90.where(self.azimuthNon90==90, drop=True)
        compUE = compUE.assign_coords({'time':meanTimeUE})

        compUW = compWindSpeed.where(self.azimuthNon90==270, drop=True)
        meanTimeUW = self.meanTimeNon90.where(self.azimuthNon90==270, drop=True)
        compUW = compUW.assign_coords({'time':meanTimeUW})

        self.compV = -(compVN - compVS)
        self.compU = -(compUE - compUW)

        self.compV = self.correctWindComp(self.compV)
        self.compU = self.correctWindComp(self.compU)

        self.compV.name = 'compV'
        self.compU.name = 'compU'

        return None


    def calcHorWindComp_continuous(self):

        """
        Function to derive wind v and u components. 
        It folows the same approach used by the lidar software.

        """

        compWindSpeed = self.radWindSpeedNon90/(2*np.cos(np.deg2rad(self.elevetionNon90)))

        self.compVN = compWindSpeed.where(self.azimuthNon90==0, drop=True)
        self.compVS = compWindSpeed.where(self.azimuthNon90==180, drop=True)
        compVS = self.compVS.reindex(time=self.compVN.time, method='Nearest', tolerance=self.tolerance)

        self.compUE = compWindSpeed.where(self.azimuthNon90==90, drop=True)
        self.compUW = compWindSpeed.where(self.azimuthNon90==270, drop=True)
        compUW = self.compUW.reindex(time=self.compUE.time, method='Nearest', tolerance=self.tolerance)

        self.compV = -(self.compVN - compVS)
        self.compU = -(self.compUE - compUW)

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


class retrieveWind:

    def __init__(self, transfdData):

        self.transfdData = transfdData
        self.retHorWindData()
        self.retVertWindData()
        self.getBeta()
        self.loadAttrs()

        return None

    def retHorWindData(self):

        tmpWindProp = fftWindPropRet(self.transfdData.dataTransf).windProp()
        tmpWindProp = tmpWindProp.squeeze(dim='elv')
        tmpWindProp = tmpWindProp.drop(['elv','freq_azm'])
        self.windProp = tmpWindProp

        # loadAttributes(tmpWindProp).data

        return self

    def retVertWindData(self):

        tmpWindW = self.transfdData.dataTransf90
        tmpWindW = tmpWindW.rename({'time':'time90', 'range90':'range'})
        self.windProp['vertical_wind_speed'] = tmpWindW
        # self.windProp = loadAttributes(self.windProp).data

        return self

    def getBeta(self):

        tmpBeta = self.transfdData.relative_beta90
        tmpBeta = tmpBeta.rename({'time':'time90', 'range90':'range'})
        self.windProp['lidar_relative_beta'] = tmpBeta

        return self

    def loadAttrs(self):

        self.windProp = loadAttributes(self.windProp).data

        return self