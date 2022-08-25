import logging

import numpy as np
import xarray as xr
import xrft

from .filters import filtering
from .dataAttributesL1 import loadAttributes
from .dataOperator import getRestructuredData

module_logger = logging.getLogger('lidarSuit.windPropRetrieval')
module_logger.debug('loading windPropRetrieval')



class fftWindPropRet:
    """FFT wind retrieval method
        
    It is a fft wind retrieval method. It was proposed 
    by Ishwardat (2017). For more details see 
    http://resolver.tudelft.nl/uuid:a659654b-e76a-4513-a656-ecad761bdbc8
    
    Parameters
    ----------
    dopplerObs : xarray.DataArray
        It should be a DataArray of slanted Doppler velocity
        observations as function of the azimuthal angle.
        It must have a coordinate called azm.

    Returns
    -------
    windProp : xarray.Dataset 
        A Dataset containing the horizontal wind speed 
        and direction. It also includes the zonal and 
        meridional wind components
         
    """

    def __init__(self, dopplerObs: xr.DataArray):

        self.logger = logging.getLogger('lidarSuit.windPropRetrieval.fftWindPropRet')
        self.logger.info('creating an instance of fftWindPropRet')

        if not isinstance(dopplerObs, xr.DataArray):
            self.logger.error('wrong data type: expecting a xr.DataArray')
            raise TypeError

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
        """
        It calculates the complex amplitudes from the 
        first harmonic from the observations along the 
        azm coordinate
        """

        self.logger.info('calculating the complex amplitude')

        self.compAmp = xrft.fft(self.dopplerObs, dim=['azm']).isel(freq_azm=-2)

        return self

    def getPhase(self):
        """
        It calculates the phase of the first harmonic 
        for retrieving wind direction
        """

        self.logger.info('calculating the phase from the complex amplitude')

        self.phase = -np.rad2deg(np.arctan2(self.compAmp.imag, self.compAmp.real))
        # self.phase.attrs = {'standard_name': 'retrived_phase',
        #                       'units': 'deg',
        #                       'comments': 'phase derived using the FFT method'}

        return self

    def getWindDir(self):
        """
        It calculates the wind direction based on the 
        phase of the first harmonic
        """

        self.logger.info('retrieving wind direction from the phase')

        self.windDir = self.phase + 180
        # self.windDir.attrs = {'standard_name': 'retrived_wind_direction',
        #                       'units': 'deg',
        #                       'comments': 'wind direction retrived using the FFT method'}

        return self

    def getRadWindSpeed(self):
        """
        It calculates the wind speed using the first harmonic
        """

        self.logger.info('calculating the radial wind speed from the complex amplitude')

        self.radWindSpeed = 2 * np.abs(self.compAmp)/self.dopplerObs.azm.shape[0]
        # self.radWindSpeed.attrs = {'standard_name': 'retrived_radial_wind_velocity',
        #                            'units': 'm s-1',
        #                            'comments': 'radial wind velocity retrived using the FFT method'}

        return self

    def getHorWindSpeed(self):
        """
        It corrects the magnitude of the wind speed using
        the elevation angle
        """

        self.logger.info('retrieving the horizontal wind speed')

        self.horWindSpeed = self.radWindSpeed/np.cos(np.deg2rad(self.dopplerObs.elv))
        # self.horWindSpeed.attrs = {'standard_name': 'retrived_horizontal_wind_velocity',
        #                            'units': 'm s-1',
        #                            'comments': 'horizontal wind velocity retrived using the FFT method'}

        return self

    def getAzmWind(self, azm):
        """
        It retrieves the wind speed for a given azimuthal angle.
        It cam be used to calculate the meridional and zonal wind
        components
        
        Parameters
        ----------
        azm : float
            an azimuth for retrieving the wind
        
        """

        self.logger.info('calculating wind speed for a give azimuth')

        azmHorWind = self.radWindSpeed * np.sin(np.deg2rad(azm) + np.deg2rad(self.phase.values + 180))
        azmHorWind = azmHorWind/np.cos(np.deg2rad(self.dopplerObs.elv))

        return azmHorWind

    def getWindConpU(self):

        """
        It retrives the zonal wind component
        the -1 multiplication is for comply with the
        conventions used in meteorology 
        """


        self.logger.info('retrieving the zonal wind speed component')

        self.compU = self.getAzmWind(0) * -1
        # self.compU.name = 'compU'
        # self.compU.attrs = {'standard_name': 'retrived_u_component',
        #                     'units': 'm s-1',
        #                     'comments': 'u wind component retrieved using the FFT method'}

        return self

    def getWindConpV(self):

        """
        It retrieves the meridional wind component
        the -1 multiplication is for comply with the
        conventions used in meteorology 
        """

        self.logger.info('retrieving the meridional wind speed component')

        self.compV = self.getAzmWind(90) * -1
        # self.compV.name = 'compV'
        # self.compV.attrs = {'standard_name': 'retrived_v_component',
        #                     'units': 'm s-1',
        #                     'comments': 'v wind component retrieved using the FFT method'}

        return self

    def windProp(self):
        """
        It creates the returned dataset containing 
        the wind, direction, and components
        """

        self.logger.info('creating a xarray dataset from the retrieved wind properties')

        windProp = xr.Dataset()
        windProp['horizontal_wind_direction'] = self.windDir
        windProp['horizontal_wind_speed'] = self.horWindSpeed
        windProp['zonal_wind'] = self.compU
        windProp['meridional_wind'] = self.compV

        return windProp


class getWindProperties5Beam:
    """DBS wind retrieval
    
    This class caculates the wind speeed and direction
    using the 5bean dataset (DBS files) as input.

    Parameters
    ----------
    data : xarray.Dataset
        merged xarray dataset (mergedDS) output from
        lst.dbsOperations()

    statusFilter : bolean
        Data filtering based on the wind lidar
        wind status variable. If True, all data with status not
        equal to 1 are removed. If False, no filtering is applied.

    cnr : int, optional
        Filter based on the carrier to noise ratio.
        If None, no filtering is applied. If a cnr value is given,
        all data smaller than the cnr is removed.

    method : str
        It can be 'single_dbs' (default) or 'continuous'.
        If single_dbs: the wind information is retrieved
        from comple sets of DBS profiles. If continuos:
        it uses the nearest 4 observations to retrieve 
        the wind information, a tolerance wind has to 
        be specified.

    tolerance : str
        It defines the tolerance window that the method will 
        use for identify the nearest profile. Example: '8s'
        for 8 seconds. 

    Returns
    -------
    object : object
        This class returns an object containing the
        derived wind speed (.horWindSpeed) and
        direction (.horWindDir).

    """
    

    def __init__(self, data: xr.Dataset, statusFilter=True, cnr=None, method='single_dbs', tolerance='8s'):

        self.logger = logging.getLogger('lidarSuit.windPropRetrieval.getWindProperties5Beam')
        self.logger.info('creating an instance of getWindProperties5Beam')

        if not isinstance(data, xr.Dataset):
            self.logger.error('wrong data type: expecting a xr.Dataset')
            raise TypeError

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
        
        Parameters
        ----------
        comp : xarray.DataArray
            a variable from the original dataset
        
        Returns
        -------
        comp : xarray.DataArray
            updated variable
        
        """

        self.logger.info('replacing the gate_index coordinate by range: {0}'.format(comp.name))

        comp = comp.rename({'gate_index':'range'})
        comp = comp.assign_coords({'range':self.rangeVal90.values[0]})
        comp.range.attrs = self.rangeVal90.attrs

        return comp


    def correctVertWindComp(self):
        """
        This function replaces the original coordinate from the vertical
        wind component by the measurement_height.
        """

        self.logger.info('replacing coordinate from the vertical measurement')

        self.verWindSpeed.name = 'compW'
        verWindSpeed = self.correctWindComp(self.verWindSpeed)
        self.verWindSpeed = verWindSpeed

        return self


    def calcHorWindComp_single_dbs(self):
        """
        This method derives v and u components from the
        WindCube DBS files. The components are caculated
        from each individual DBS file. The mean time from each
        scan complete scan is used as identification tag.
        """


        self.logger.info('calculating the horizontal wind using the SINGLE DBS method')

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

        self.compV.name = 'compV'
        self.compU.name = 'compU'

        self.compV = self.correctWindComp(self.compV)
        self.compU = self.correctWindComp(self.compU)

        return None


    def calcHorWindComp_continuous(self):
        """
        Function to derive wind v and u components. 
        It folows the same approach used by the lidar software.
        """

        self.logger.info('calculating the horizontal wind using the CONTINUOUS DBS method')

        compWindSpeed = self.radWindSpeedNon90/(2*np.cos(np.deg2rad(self.elevetionNon90)))

        self.compVN = compWindSpeed.where(self.azimuthNon90==0, drop=True)
        self.compVS = compWindSpeed.where(self.azimuthNon90==180, drop=True)
        compVS = self.compVS.reindex(time=self.compVN.time, method='Nearest', tolerance=self.tolerance)

        self.compUE = compWindSpeed.where(self.azimuthNon90==90, drop=True)
        self.compUW = compWindSpeed.where(self.azimuthNon90==270, drop=True)
        compUW = self.compUW.reindex(time=self.compUE.time, method='Nearest', tolerance=self.tolerance)

        self.compV = -(self.compVN - compVS)
        self.compU = -(self.compUE - compUW)

        self.compV.name = 'compV'
        self.compU.name = 'compU'

        self.compV = self.correctWindComp(self.compV)
        self.compU = self.correctWindComp(self.compU)

        self.compU = self.compU.reindex(time = self.compV.time, method='Nearest',
                                        tolerance=self.tolerance)

        return self     


    def calcHorWindSpeed(self):
        """
        Function to calculate the wind speed.
        """

        self.logger.info('calculating the horizontal wind speed using DBS observations')

        horWindSpeed = np.sqrt(self.compV**2. + self.compU**2.)
        horWindSpeed.name = 'hor_wind_speed'
        horWindSpeed.attrs['long_name'] = 'wind_speed'
        horWindSpeed.attrs['units'] = 'm/s'

        self.horWindSpeed = horWindSpeed


        return self


    def calcHorWindDir(self):
        """
        Function to derive wind direction. If folows the same 
        approach used by the lidar sftware. 
        """

        self.logger.info('retrieving the wind direction using DBS observation')

        windDir = 180 + np.rad2deg(np.arctan2(-self.compU, -self.compV))

        windDir.name = 'hor_wind_dir'
        windDir.attrs['long_name'] = 'wind_direction'
        windDir.attrs['units'] = 'deg'

        self.horWindDir = windDir


        return self


class retrieveWind:
    """6 beam wind retrieval
        
    Wind retrieval based on the FFT method for
    the 6 beam observations. 
    
    Parameters
    ----------
    transfdData : object
        An instance of the re-structured data, it 
        should be preferentially filtered for artefacts.

    Returns
    -------
    object : object
        An object containing an dataset of the retrieved wind 
        speed, direction, wind components (meridional, zonal 
        and vertical) and the relative beta    
    
    """

    def __init__(self, transfdData: getRestructuredData):

        self.logger = logging.getLogger('lidarSuit.windPropRetrieval.fftWindPropRet')
        self.logger.info('creating an instance of fftWindPropRet')

        if not isinstance(transfdData, getRestructuredData):
            self.logger.error('wrong data type: expecting a lst.getRestructuredData instance')
            raise TypeError

        self.transfdData = transfdData
        self.retHorWindData()
        self.retVertWindData()
        self.getBeta()
        self.loadAttrs()

        return None

    def retHorWindData(self):
        """
        It applies the FFT based method to retrieve 
        the horizontal wind information
        """

        self.logger.info('retrieving horizontal wind from the 6 beam data')

        tmpWindProp = fftWindPropRet(self.transfdData.dataTransf).windProp()
        tmpWindProp = tmpWindProp.squeeze(dim='elv')
        tmpWindProp = tmpWindProp.drop(['elv','freq_azm'])
        self.windProp = tmpWindProp

        # loadAttributes(tmpWindProp).data

        return self

    def retVertWindData(self):
        """
        It copies the vertical wind from the observations
        """

        self.logger.info('selecting the vertical wind observations')

        tmpWindW = self.transfdData.dataTransf90
        tmpWindW = tmpWindW.rename({'time':'time90', 'range90':'range'})
        self.windProp['vertical_wind_speed'] = tmpWindW
        # self.windProp = loadAttributes(self.windProp).data

        return self

    def getBeta(self):
        """
        It copies the raw beta from the vertical observations
        """

        self.logger.info('selcting beta from vertical observations')

        tmpBeta = self.transfdData.relative_beta90
        tmpBeta = tmpBeta.rename({'time':'time90', 'range90':'range'})
        self.windProp['lidar_relative_beta'] = tmpBeta

        return self

    def loadAttrs(self):
        """
        It loads the attributes from all variables
        into the dataset
        """

        self.logger.info('loading data attributes')

        self.windProp = loadAttributes(self.windProp).data

        return self