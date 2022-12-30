import logging

import numpy as np
import xarray as xr
import xrft

from .data_attributes import LoadAttributes
from .data_operator import GetRestructuredData

module_logger = logging.getLogger("lidarwind.wind_prop_retrieval")
module_logger.debug("loading wind_prop_retrieval")


class FourierTransfWindMethod:
    """FFT wind retrieval method

    It is a fft wind retrieval method. It was proposed
    by Ishwardat (2017). For more details see
    http://resolver.tudelft.nl/uuid:a659654b-e76a-4513-a656-ecad761bdbc8

    Parameters
    ----------
    doppler_obs : xarray.DataArray
        It should be a DataArray of slanted Doppler velocity
        observations as function of the azimuthal angle.
        It must have a coordinate called azm.

    Returns
    -------
    wind_prop : xarray.Dataset
        A Dataset containing the horizontal wind speed
        and direction. It also includes the zonal and
        meridional wind components

    """

    def __init__(self, doppler_obs: xr.DataArray):

        self.logger = logging.getLogger(
            "lidarwind.wind_prop_retrieval.FourierTransfWindMethod"
        )
        self.logger.info("creating an instance of FourierTransfWindMethod")

        if not isinstance(doppler_obs, xr.DataArray):
            self.logger.error("wrong data type: expecting a xr.DataArray")
            raise TypeError

        self.doppler_obs = doppler_obs

        self.get_comp_amp()
        self.get_phase()
        self.get_rad_wind_speed()
        self.get_hor_wind_speed()
        self.get_wind_dir()
        self.get_wind_comp_u()
        self.get_wind_comp_v()

    def get_comp_amp(self):
        """First harmonic amplitude

        It calculates the complex amplitudes from the
        first harmonic from the observations along the
        azm coordinate
        """

        self.logger.info("calculating the complex amplitude")

        self.comp_amp = xrft.fft(
            self.doppler_obs, dim=["azm"], true_amplitude=False
        ).isel(freq_azm=-2)

        return self

    def get_phase(self):
        """First harmonic phase

        It calculates the phase of the first harmonic from the complex
        amplitude used for retrieving wind direction, i.e. comp_amp.
        """

        self.logger.info("calculating the phase from the complex amplitude")

        self.phase = -np.rad2deg(
            np.arctan2(self.comp_amp.imag, self.comp_amp.real)
        )

        self.phase.attrs = {
            "long_name": "Retrived phase",
            "units": "degree",
            "comments": "Phase derived from comp_amp "
            "variable using the FFT method.",
        }

        return self

    def get_wind_dir(self):
        """Wind direction calculation

        It calculates the wind direction based on the
        phase of the first harmonic
        """

        self.logger.info("retrieving wind direction from the phase")

        self.wind_dir = self.phase + 180
        self.wind_dir.attrs = {
            "long_name": "Wind direction",
            "standard_name": "wind_from_direction",
            "units": "degree",
            "comments": "Wind direction retrived using the FFT method.",
        }

        return self

    def get_rad_wind_speed(self):
        """Wind speed calculation

        It calculates the wind speed using the first harmonic
        """

        self.logger.info(
            "calculating the radial wind speed from the complex amplitude"
        )

        self.rad_wind_speed = (
            2 * np.abs(self.comp_amp) / self.doppler_obs.azm.shape[0]
        )

        self.rad_wind_speed.attrs = {
            "long_name": "wind speed not corrected for the elevation",
            "units": "m s-1",
            "comments": "Radial wind velocity retrived using "
            "the FFT method not corrected for the elevation.",
        }

        return self

    def get_hor_wind_speed(self):
        """Wind speed elevation correction

        It corrects the magnitude of the wind speed using
        the elevation angle
        """

        self.logger.info("retrieving the horizontal wind speed")

        self.hor_wind_speed = self.rad_wind_speed / np.cos(
            np.deg2rad(self.doppler_obs.elv)
        )

        self.hor_wind_speed.attrs = {
            "long_name": "horizontal wind speed",
            "standard_name": "wind_speed",
            "units": "m s-1",
            "comments": "Horizontal wind velocity retrived using "
            "the FFT method corrected for the elevation.",
        }

        return self

    def get_azm_wind(self, azm):
        """Wind speed for a given azimuth

        It retrieves the wind speed for a given azimuthal angle.
        It cam be used to calculate the meridional and zonal wind
        components

        Parameters
        ----------
        azm : float
            an azimuth for retrieving the wind
        """

        self.logger.info("calculating wind speed for a give azimuth")

        azm_hor_wind = self.rad_wind_speed * np.sin(
            np.deg2rad(azm) + np.deg2rad(self.phase.values + 180)
        )
        azm_hor_wind = azm_hor_wind / np.cos(np.deg2rad(self.doppler_obs.elv))

        return azm_hor_wind

    def get_wind_comp_u(self):
        """Zonal wind calculation

        It retrives the zonal wind component
        the -1 multiplication is for comply with the
        conventions used in meteorology
        """

        self.logger.info("retrieving the zonal wind speed component")

        self.comp_u = self.get_azm_wind(0) * -1
        self.comp_u.name = "comp_u"
        self.comp_u.attrs = {
            "long_name": "Zonal wind component",
            "units": "m s-1",
            "comments": "Zonal wind component retrieved using the FFT method.",
        }

        return self

    def get_wind_comp_v(self):
        """Meridional wind calculation

        It retrieves the meridional wind component
        the -1 multiplication is for comply with the
        conventions used in meteorology
        """

        self.logger.info("retrieving the meridional wind speed component")

        self.comp_v = self.get_azm_wind(90) * -1
        self.comp_v.name = "comp_v"
        self.comp_v.attrs = {
            "long_name": "Meridional wind component",
            "units": "m s-1",
            "comments": "Meridional wind component "
            "retrieved using the FFT method.",
        }

        return self

    def wind_prop(self):
        """Wind dataset

        It creates and returnes a dataset containing
        the wind speed, direction, and components
        """

        self.logger.info(
            "creating a xarray dataset from the retrieved wind properties"
        )

        wind_prop = xr.Dataset()
        wind_prop["horizontal_wind_direction"] = self.wind_dir
        wind_prop["horizontal_wind_speed"] = self.hor_wind_speed
        wind_prop["zonal_wind"] = self.comp_u
        wind_prop["meridional_wind"] = self.comp_v

        return wind_prop


class GetWindProperties5Beam:
    """DBS wind retrieval

    This class caculates the wind speeed and direction
    using the 5bean dataset (DBS files) as input.

    Parameters
    ----------
    data : xarray.Dataset
        merged xarray dataset (merged_ds) output from
        lidarwind.DbsOperations()

    status_filter : bolean
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
        derived wind speed (.hor_wind_speed) and
        direction (.hor_wind_dir).

    """

    def __init__(
        self,
        data: xr.Dataset,
        status_filter=True,
        cnr=None,
        method="single_dbs",
        tolerance="8s",
    ):

        self.logger = logging.getLogger(
            "lidarwind.wind_prop_retrieval.GetWindProperties5Beam"
        )
        self.logger.info("creating an instance of GetWindProperties5Beam")

        if not isinstance(data, xr.Dataset):
            self.logger.error("wrong data type: expecting a xr.Dataset")
            raise TypeError

        if status_filter:
            data["radial_wind_speed"] = data.radial_wind_speed.where(
                data.radial_wind_speed_status == 1
            )

        if cnr is not None:
            data["radial_wind_speed"] = data.radial_wind_speed.where(
                data.cnr >= cnr
            )

        elevation = data.elevation.round(1)

        time90 = elevation.time.where(elevation == 90, drop=True)
        time_non_90 = elevation.time.where(elevation != 90, drop=True)

        azimuth_non_90 = data.azimuth.sel(
            time=time_non_90, method="Nearest"
        ).round(1)
        azimuth_non_90[azimuth_non_90 == 360] = 0

        self.tolerance = tolerance

        self.azimuth_non_90 = azimuth_non_90
        self.elevation_non_90 = elevation.sel(time=time_non_90)

        # replace range by measurement_height
        self.range_val_non_90 = data.measurement_height.sel(time=time_non_90)
        self.rad_wind_speed_non_90 = data.radial_wind_speed.sel(
            time=time_non_90
        )
        self.mean_time_non_90 = data.scan_mean_time.sel(time=time_non_90)

        self.range_val_90 = data.measurement_height.sel(time=time90)
        self.ver_wind_speed = data.radial_wind_speed.sel(time=time90)
        self.correct_vert_wind_comp()

        if method == "continuous":
            self.calc_hor_wind_comp_continuous()

        if method == "single_dbs":
            self.calc_hor_wind_comp_single_dbs()

        self.calc_hor_wind_speed()
        self.calc_hor_wind_dir()

    def correct_wind_comp(self, comp):
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

        self.logger.info(
            f"replacing the gate_index coordinate by range: {comp.name}"
        )

        comp = comp.rename({"gate_index": "range"})
        comp = comp.assign_coords({"range": self.range_val_90.values[0]})
        comp.range.attrs = self.range_val_90.attrs

        return comp

    def correct_vert_wind_comp(self):
        """
        This function replaces the original coordinate from the vertical
        wind component by the measurement_height.
        """

        self.logger.info("replacing coordinate from the vertical measurement")

        self.ver_wind_speed.name = "compW"
        ver_wind_speed = self.correct_wind_comp(self.ver_wind_speed)
        self.ver_wind_speed = ver_wind_speed

        return self

    def calc_hor_wind_comp_single_dbs(self):
        """
        This method derives v and u components from the
        WindCube DBS files. The components are caculated
        from each individual DBS file. The mean time from each
        scan complete scan is used as identification tag.
        """

        self.logger.info(
            "calculating the horizontal wind using the SINGLE DBS method"
        )

        comp_wind_speed = self.rad_wind_speed_non_90 / (
            2 * np.cos(np.deg2rad(self.elevation_non_90))
        )

        comp_vn = comp_wind_speed.where(self.azimuth_non_90 == 0, drop=True)
        mean_time_vn = self.mean_time_non_90.where(
            self.azimuth_non_90 == 0, drop=True
        )
        comp_vn = comp_vn.assign_coords({"time": mean_time_vn})

        comp_vs = comp_wind_speed.where(self.azimuth_non_90 == 180, drop=True)
        mean_time_vs = self.mean_time_non_90.where(
            self.azimuth_non_90 == 180, drop=True
        )
        comp_vs = comp_vs.assign_coords({"time": mean_time_vs})

        comp_ue = comp_wind_speed.where(self.azimuth_non_90 == 90, drop=True)
        mean_time_ue = self.mean_time_non_90.where(
            self.azimuth_non_90 == 90, drop=True
        )
        comp_ue = comp_ue.assign_coords({"time": mean_time_ue})

        comp_uw = comp_wind_speed.where(self.azimuth_non_90 == 270, drop=True)
        mean_time_uw = self.mean_time_non_90.where(
            self.azimuth_non_90 == 270, drop=True
        )
        comp_uw = comp_uw.assign_coords({"time": mean_time_uw})

        self.comp_v = -(comp_vn - comp_vs)
        self.comp_u = -(comp_ue - comp_uw)

        self.comp_v.name = "comp_v"
        self.comp_u.name = "comp_u"

        self.comp_v = self.correct_wind_comp(self.comp_v)
        self.comp_u = self.correct_wind_comp(self.comp_u)

    def calc_hor_wind_comp_continuous(self):
        """
        Function to derive wind v and u components.
        It folows the same approach used by the lidar software.
        """

        self.logger.info(
            "calculating the horizontal wind using the CONTINUOUS DBS method"
        )

        comp_wind_speed = self.rad_wind_speed_non_90 / (
            2 * np.cos(np.deg2rad(self.elevation_non_90))
        )

        self.comp_vn = comp_wind_speed.where(
            self.azimuth_non_90 == 0, drop=True
        )
        self.comp_vs = comp_wind_speed.where(
            self.azimuth_non_90 == 180, drop=True
        )
        comp_vs = self.comp_vs.reindex(
            time=self.comp_vn.time, method="Nearest", tolerance=self.tolerance
        )

        self.comp_ue = comp_wind_speed.where(
            self.azimuth_non_90 == 90, drop=True
        )
        self.comp_uw = comp_wind_speed.where(
            self.azimuth_non_90 == 270, drop=True
        )
        comp_uw = self.comp_uw.reindex(
            time=self.comp_ue.time, method="Nearest", tolerance=self.tolerance
        )

        self.comp_v = -(self.comp_vn - comp_vs)
        self.comp_u = -(self.comp_ue - comp_uw)

        self.comp_v.name = "comp_v"
        self.comp_u.name = "comp_u"

        self.comp_v = self.correct_wind_comp(self.comp_v)
        self.comp_u = self.correct_wind_comp(self.comp_u)

        self.comp_u = self.comp_u.reindex(
            time=self.comp_v.time, method="Nearest", tolerance=self.tolerance
        )

        return self

    def calc_hor_wind_speed(self):
        """
        Function to calculate the wind speed.
        """

        self.logger.info(
            "calculating the horizontal wind speed using DBS observations"
        )

        hor_wind_speed = np.sqrt(self.comp_v**2.0 + self.comp_u**2.0)
        hor_wind_speed.name = "hor_wind_speed"
        hor_wind_speed.attrs["long_name"] = "wind_speed"
        hor_wind_speed.attrs["units"] = "m/s"

        self.hor_wind_speed = hor_wind_speed

        return self

    def calc_hor_wind_dir(self):
        """
        Function to derive wind direction. If folows the same
        approach used by the lidar sftware.
        """

        self.logger.info("retrieving the wind direction using DBS observation")

        wind_dir = 180 + np.rad2deg(np.arctan2(-self.comp_u, -self.comp_v))

        wind_dir.name = "hor_wind_dir"
        wind_dir.attrs["long_name"] = "wind_direction"
        wind_dir.attrs["units"] = "deg"

        self.hor_wind_dir = wind_dir

        return self


class RetriveWindFFT:
    """6 beam wind retrieval

    Wind retrieval based on the FFT method for
    the 6 beam observations.

    Parameters
    ----------
    transfd_data : object
        An instance of the re-structured data, it
        should be preferentially filtered for artefacts.

    Returns
    -------
    object : object
        An object containing an dataset of the retrieved wind
        speed, direction, wind components (meridional, zonal
        and vertical) and the relative beta

    """

    def __init__(self, transfd_data: GetRestructuredData):

        self.logger = logging.getLogger(
            "lidarwind.wind_prop_retrieval.FourierTransfWindMethod"
        )
        self.logger.info("creating an instance of FourierTransfWindMethod")

        if not isinstance(transfd_data, GetRestructuredData):
            self.logger.error(
                "wrong data type: expecting a lidarwind.GetRestructuredData instance"
            )
            raise TypeError

        self.transfd_data = transfd_data
        self.ret_hor_wind_data()
        self.ret_vert_wind_data()
        self.get_beta()
        self.load_attrs()

    def ret_hor_wind_data(self):
        """
        It applies the FFT based method to retrieve
        the horizontal wind information
        """

        self.logger.info("retrieving horizontal wind from the 6 beam data")

        tmp_wind_prop = FourierTransfWindMethod(
            self.transfd_data.data_transf
        ).wind_prop()
        tmp_wind_prop = tmp_wind_prop.squeeze(dim="elv")
        tmp_wind_prop = tmp_wind_prop.drop(["elv", "freq_azm"])
        self.wind_prop = tmp_wind_prop

        return self

    def ret_vert_wind_data(self):
        """
        It copies the vertical wind from the observations
        """

        self.logger.info("selecting the vertical wind observations")

        tmp_wind_w = self.transfd_data.data_transf_90
        tmp_wind_w = tmp_wind_w.rename({"time": "time90", "range90": "range"})
        self.wind_prop["vertical_wind_speed"] = tmp_wind_w

        return self

    def get_beta(self):
        """
        It copies the raw beta from the vertical observations
        """

        self.logger.info("selcting beta from vertical observations")

        tmp_beta = self.transfd_data.relative_beta90
        tmp_beta = tmp_beta.rename({"time": "time90", "range90": "range"})
        self.wind_prop["lidar_relative_beta"] = tmp_beta

        return self

    def load_attrs(self):
        """
        It loads the attributes from all variables
        into the dataset
        """

        self.logger.info("loading data attributes")

        self.wind_prop = LoadAttributes(self.wind_prop).data

        return self
