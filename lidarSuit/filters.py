"""Module for keep all filtering functionalities

"""

import pandas as pd
import numpy as np


class filtering:
    """SNR and Status filter

    It uses the carrier to noise ratio (SNR) and status
    variables available in the WindCube's data. It is
    similar to the filter described in the manual

    Parameters
    ----------
    data : xrarray.Dataset
        Dataset containing the original WindCube's data

    """

    def __init__(self, data):

        self.data = data

    def getVerticalObsComp(self, variable, snr=False, status=True):
        """Vertical data filter

        It uses the SNR and status variables to filter out
        the data from vertical observations

        Parameters
        ----------
        variable : str
            name of the variable that will be filtered

        snr : bool, int, optional
            if an interger is given it is used to
            as threshold to filter the data based on
            the signal to noise ratio

        status : bool, optional
            if true it filters the data using the status
            variable generated by the WindCube's software

        Returns
        -------
        tmpData : xarray.DataSet
            an instance of the variable filtered using
            SNR or status variable

        """

        tmpData = self.data[variable]

        if status:
            tmpData = tmpData.where(self.data.radial_wind_speed_status90 == 1)

        if snr != False:
            tmpData = tmpData.where(self.data.cnr90 > snr)

        tmpData = tmpData.where(self.data.elevation == 90, drop=True)

        return tmpData

    def getRadialObsComp(self, variable, azm, snr=False, status=True):
        """Slanted data filter

        It uses the SNR and status variables to filter out
        the data from slanted observations

        Parameters
        ----------
        variable : str
            name of the variable that will be filtered

        snr : bool, int, optional
            if an interger is given it is used to
            as threshold to filter the data based on
            the signal to noise ratio

        status : bool, optional
            if true it filters the data using the status
            variable generated by the WindCube's software

        Returns
        -------
        tmpaData : xarray.DataSet

            an instance of the variable filtered using
            SNR or status variable

        """

        tmpData = self.data[variable]

        if status:
            tmpData = tmpData.where(self.data.radial_wind_speed_status == 1)

        if snr != False:
            tmpData = tmpData.where(self.data.cnr > snr)

        tmpData = tmpData.where(
            (self.data.elevation != 90) & (self.data.azimuth == azm), drop=True
        )

        return tmpData


# it removes the STE below cloud layer
class secondTripEchoFilter:
    """Boundary layer second trip echoes filter

    This filter minimises the presence of second
    trip echoes (STE). This filter is based on the
    standard deviation of the anomaly of the observaions.
    It is applicable in regions where there is a contrast
    between the real data and the STE.

    Parameters
    ----------
    data : object
        the object returned from the getRestructuredData

    timeCloudMaks : xarray.DataArray
        it is a time series for indicating the presence
        of clouds above the maximum WinCube range.
        1 indicates cloud and 0 indicates no cloud.
        (THIS MAKS IS NOT NEEDED NOW)

    nProf : int
        number of profiles used to calculating the anomaly

    center : bool, optional
        it defines how the mean value for the anomaly will
        be calculated

    min_periods : int
        minimum number of profiles used for calculating the
        mean value

    nStd : int
        Multiplication factor for defining the size of the
        window to keep the data. The filter removes any
        anomaly larger than nStd * std

    strH : str
        starting hour for calculating the anomaly

    endH : str
        end hour for calculating the anomaly

    Returns
    -------
    object : object
        an object containing data filtered for STE

    """

    def __init__(
        self,
        data,
        timeCloudMask,
        nProf=500,
        center=True,
        min_periods=30,
        nStd=2,
        strH="09",
        endH="16",
    ):

        self.lidar = data
        # self.timeCloudMask = timeCloudMask
        self.nProf = nProf
        self.center = center
        self.min_periods = min_periods
        self.nStd = nStd

        self.getTimeEdges()
        self.calMeanAndAnomSlant()
        self.calMeanAndAnom90()
        self.cleaning()
        self.cleaning90()

    def getTimeEdges(self, strH="09", endH="16"):
        """
        It creates the time boundaries for the STD anomaly calculation

        Parameters
        ----------
        strH : str
            starting hour for calculating the anomaly

        endH : str
            end hour for calculating the anomaly

        """

        selTime = pd.to_datetime(self.lidar.dataTransf.time.values[0])
        selTime = selTime.strftime("%Y%m%d")
        self.startTime = pd.to_datetime(f"{selTime} {strH}")
        self.endTime = pd.to_datetime(f"{selTime} {endH}")

    def calMeanAndAnomSlant(self):
        """
        It calculates the anomaly from the slanted observations
        """

        # slanted beam
        tmpSelData = self.lidar.dataTransf

        self.dataMean = tmpSelData.rolling(
            time=self.nProf, center=self.center, min_periods=self.min_periods
        ).mean()

        self.dataAnom = self.lidar.dataTransf - self.dataMean

    def calMeanAndAnom90(self):
        """
        It calculates the anomaly from the vertical observations
        """

        # vertical beam
        tmpSelData90 = self.lidar.dataTransf90

        self.dataMean90 = tmpSelData90.rolling(
            time=self.nProf, center=self.center, min_periods=self.min_periods
        ).mean()

        self.dataAnom90 = self.lidar.dataTransf90 - self.dataMean90

    def cleaning(self):
        """
        It removes the data that is larger than the nStd * anomaly
        from the slanted observations
        """

        tmpAnom = self.dataAnom.where(
            (self.lidar.dataTransf.time > self.startTime)
            & (self.lidar.dataTransf.time < self.endTime)
        )

        anomStd = tmpAnom.std(dim=["time", "range", "elv"])

        # Cross check if this commented part is still needed for
        # for filter the slanted profiles

        # tmpNoCloud = self.lidar.dataTransf.where(self.timeCloudMask == 0).copy()
        # tmpCloud = self.lidar.dataTransf.where(self.timeCloudMask == 1).copy()

        # tmpCloud = tmpCloud.where(np.abs(self.dataAnom) < self.nStd * anomStd)

        # tmpCleanData = tmpNoCloud.copy()
        # tmpCleanData.values[np.isfinite(tmpCloud)] = tmpCloud.values[np.isfinite(tmpCloud)]

        tmpCleanData = self.lidar.dataTransf.copy()
        tmpCleanData = tmpCleanData.where(
            np.abs(self.dataAnom) < self.nStd * anomStd
        )
        self.lidar.dataTransf.values = tmpCleanData.values

    def cleaning90(self):
        """
        It removes the data that is larger than the nStd * anomaly
        from the vertical observations
        """

        tmpAnom = self.dataAnom90.where(
            (self.lidar.dataTransf90.time > self.startTime)
            & (self.lidar.dataTransf90.time < self.endTime)
        )

        anomStd = tmpAnom.std(dim=["time", "range90"])

        # tmpNoCloud = self.lidar.dataTransf90.where(self.timeCloudMask == 0).copy()
        # tmpCloud = self.lidar.dataTransf90.where(self.timeCloudMask == 1).copy()

        # tmpCloud = tmpCloud.where(np.abs(self.dataAnom90) < self.nStd * anomStd)

        # tmpCleanData = tmpNoCloud.copy()
        # tmpCleanData.values[np.isfinite(tmpCloud)] = tmpCloud.values[np.isfinite(tmpCloud)]

        tmpCleanData = self.lidar.dataTransf90.copy()
        tmpCleanData = tmpCleanData.where(
            np.abs(self.dataAnom90) < self.nStd * anomStd
        )

        self.lidar.dataTransf90.values = tmpCleanData.values


# it removes STE and clouds contamination
# from above the aerosol loaded region
class windCubeCloudRemoval:
    """Above boundary layer second trip echoes filter

    This filter reduces the second trip echoes contamination
    and clouds from regions above the boundary layer. It
    requires information from the ceilometer.
    IT IS STILL EXPERIMENTAL

    Parameters
    ----------
    ceilo : xarray.Dataset
        A dataset of the CHM15k Nimbus ceilometer observations.

    lidar : xarray.Dataset
        An instance of the re-structured WindCube dataset

    Returns
    -------
    object : object
        an object containing an instance of the noise
        height interface and the re-structured dataset
        filtered for STE and clouds.

    """

    def __init__(self, ceilo, lidar=None):

        self.lidar = lidar
        self.ceilo = ceilo

        self.get_noise_free_beta()
        self.get_height_interface()

        if lidar is not None:
            self.get_interp_interf_height()
            self.remove_cloud()

    def get_noise_free_beta(self):
        """
        It removes the noise from the backscattered signal
        """
        positive_beta = self.ceilo.beta_raw.where(self.ceilo.beta_raw > 0)

        positive_beta = positive_beta.rolling(
            range=10, center=True, min_periods=10
        ).mean()
        positive_beta = positive_beta.rolling(
            time=15, center=True, min_periods=15
        ).mean()

        self.noise_free_beta = positive_beta

        return self

    def get_height_interface(self):
        """
        It identifies the height of the separation between
        the noise and the non-noise data from the ceilometer
        backscattered signal
        """
        positive_beta = self.ceilo.beta_raw.where(self.ceilo.beta_raw > 0)

        tmp_ceilo_hgt = positive_beta.copy()
        tmp_values = tmp_ceilo_hgt.values
        tmp_values[np.isfinite(tmp_values)] = 1
        tmp_ceilo_hgt.values = tmp_values
        tmp_ceilo_hgt = tmp_ceilo_hgt * self.ceilo.range

        lowest_beta = self.noise_free_beta.where(tmp_ceilo_hgt < 4e3)

        tmp_ceilo_hgt = tmp_ceilo_hgt.where(np.isfinite(lowest_beta))

        self.interf_height = tmp_ceilo_hgt.max(dim="range")
        self.interf_height = self.interf_height.rolling(
            time=7, center=True, min_periods=5
        ).mean()

        return self

    def get_interp_interf_height(self):
        """
        It interpolates the noise height interface to the same
        temporal resolution from the windcube data
        """
        self.interp_interf_height = self.interf_height.interp(
            time=self.lidar.dataTransf.time
        )
        self.interp_interf_height_90 = self.interf_height.interp(
            time=self.lidar.dataTransf90.time
        )

        return self

    def remove_cloud(self):
        """
        It removes from the windcube's observation all
        data above the noise height interface
        """

        tmp_height = self.lidar.dataTransf.copy()
        tmp_values = tmp_height.values
        tmp_values[np.isfinite(tmp_values)] = 1
        tmp_height.values = tmp_values
        tmp_height = tmp_height * self.lidar.dataTransf.range
        self.lidar.dataTransf = self.lidar.dataTransf.where(
            tmp_height < self.interp_interf_height
        )

        tmp_height = self.lidar.dataTransf90.copy()
        tmp_values = tmp_height.values
        tmp_values[np.isfinite(tmp_values)] = 1
        tmp_height.values = tmp_values
        tmp_height = tmp_height * self.lidar.dataTransf90.range90
        self.lidar.dataTransf90 = self.lidar.dataTransf90.where(
            tmp_height < self.interp_interf_height_90
        )
        self.lidar.relative_beta90 = self.lidar.relative_beta90.where(
            tmp_height < self.interp_interf_height_90
        )

        return self
