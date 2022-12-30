"""Module to manage and prepare the data for other modules

"""


import logging

import xarray as xr
import datetime as dt
import pandas as pd
import numpy as np

from .filters import Filtering

from .lidar_code import GetLidarData

module_logger = logging.getLogger("lidarwind.data_operator")
module_logger.debug("loading data_operator")


def wc_fixed_preprocessing(ds: xr.Dataset, azimuth_resolution: int = 1):

    ds["azimuth"] = ds["azimuth"].round(azimuth_resolution)
    # Avoid ambiguity on 360 degrees
    ds["azimuth"] = ds["azimuth"].where(ds.azimuth != 360, 0)

    assert "elevation" in ds
    assert ds["elevation"].dims == ("time",)
    assert ds.dims["time"] == 1

    ds["elevation"] = ds["elevation"].squeeze()
    return ds.expand_dims("elevation").set_coords("elevation")


class DataOperations:

    """Basic data manager

    It performs some basic operations. For example: rounds
    the values from the azimuth coordinate and separates
    the vertical observations from the slanted observations.

    It is helpful first use this class to process all data
    and then save the data as NetCDF files to speed up the
    derivation of wind properties later.

    Examples
    --------
    >>> merged_ds = lidarwind.DataOperations(file_list).merged_data
    >>> merged_ds.to_netcdf(output_file_path)

    Parameters
    ----------
    data_paths : list
       List of paths of the original WindCube's output.

    Returns
    -------
    object : object
        it returns an object containing an instance of the
        original files merged (.merged_data)

    """

    def __init__(self, data_paths, verbose=False):

        self.logger = logging.getLogger(
            "lidarwind.data_operator.DataOperations"
        )
        self.logger.info("creating an instance of DataOperations")

        if bool(data_paths) is False:
            self.logger.error(
                "lidarwind stopped due to an empty list of files."
            )
            raise FileNotFoundError

        self.verbose = verbose
        self.data_paths = data_paths
        self.tmp90 = xr.Dataset()
        self.tmp_non_90 = xr.Dataset()

        self.elevation_filter()
        self.rename_var_90()
        self.get_merge_data()

    def elevation_filter(self):
        """
        It groups the data from the vertical and slanted observations
        and rounds the azimuth coordinate
        """

        self.logger.info("coverting azimuth: from 360 to 0 degrees")

        for file_path in self.data_paths:

            try:
                tmp_file = GetLidarData(file_path).open_lidar_file()
                self.logger.debug(f"reading file: {file_path}")
            except:
                self.logger.warning(f"This file has a problem: {file_path}")

            try:
                elevation = tmp_file.elevation.round(1)
                tmp_file["elevation"] = elevation
                tmp_file["azimuth"] = tmp_file.azimuth.round(1)
                tmp_file["azimuth"][tmp_file.azimuth == 360] = 0
            except:
                self.logger.info(f"Problems reading elv and axm: {file_path}")

            try:
                self.tmp90 = xr.merge(
                    [self.tmp90, tmp_file.where(elevation == 90, drop=True)]
                )
            except:
                self.logger.info(
                    f"This file does not have 90 elv: {file_path}"
                )

            try:
                self.tmp_non_90 = xr.merge(
                    [
                        self.tmp_non_90,
                        tmp_file.where(elevation != 90, drop=True),
                    ]
                )
            except:
                self.logger.info(f"This file only has 90 elv: {file_path}")

        return self

    def rename_var_90(self):
        """
        It renames the vertical coordinate
        """

        self.logger.info(
            "renaming range coordinate from vertical measurements"
        )

        self.tmp90 = self.tmp90.rename_dims({"range": "range90"})

        for var in self.tmp90.variables:

            if "range90" in self.tmp90[var].dims:

                self.tmp90 = self.tmp90.rename({var: f"{var}90"})

        return self

    def get_merge_data(self):
        """
        It merges all readable data
        """

        self.logger.info("merging vertical and non-vertical measurements")

        self.merged_data = xr.merge([self.tmp90, self.tmp_non_90])

        return self


class ReadProcessedData:
    """Pre-processed data reader

    It reads all data pre-processed by data_operator.DbsOperations
    and merges them.

    Examples
    --------
    >>> merged_data = lidarwind.ReadProcessedData(file_list).merge_data()

    Parameters
    ----------
    file_list : list
        list of pre-processed NetCDF files

    Returns
    -------
    object : object
        an instance of all pre-processed data

    """

    def __init__(self, file_list):

        self.logger = logging.getLogger(
            "lidarwind.data_operator.ReadProcessedData"
        )
        self.logger.info("creating an instance of ReadProcessedData")

        if bool(file_list) is False:
            self.logger.error(
                "lidarwind stopped due to an empty list of files."
            )
            raise FileNotFoundError

        self.file_list = file_list

    def merge_data(self):
        """
        It merges all data from the file_list. It can choose between
        two different methods. One uses xr.open_mfdataset and the other
        uses xr.open_dataset.
        """

        # open_msfdataset was massing up the dimensions
        # from radial observations.

        self.logger.info("merging pre-processed data")

        try:
            tmp_merged = self.merge_data_method_1()

        except:
            print("switching from xr.open_mfdataset to xr.open_dataset")
            tmp_merged = self.merge_data_method_2()

        return tmp_merged

    def merge_data_method_1(self):
        """
        It merges data using xr.open_mfdatset
        """

        self.logger.info("mergin files using xr.open_mfdataset")

        tmp_merged = xr.open_mfdataset(self.file_list, parallel=True)

        return tmp_merged

    def merge_data_method_2(self):
        """
        It merges data using xr.open_dataset
        """

        self.logger.info("mergin files using xr.open_dataset")

        tmp_merged = xr.Dataset()

        for file_name in sorted(self.file_list):

            try:
                self.logger.info(f"opening {file_name}")
                tmp_merged = xr.merge([tmp_merged, xr.open_dataset(file_name)])

            except:
                self.logger.info(f"problems with: {file_name}")
                pass

        return tmp_merged


class GetRestructuredData:

    """Data re-structurer

    It prepares the data structure for using the wind retrieval
    modules.

    Examples
    --------
    >>> wind_prop = lidarwind.GetRestructuredData(merged_data)

    Parameters
    ----------
    data : xr.Dataset
        a xr.Dataset of pre-processed data

    snr : bool, int, optional
        if an interger is given it is used to
        as threshold to filter the data based on
        the signal to noise ratio

    status : bool, optional
        if true it filters the data using the status
        variable generated by the WindCube's software

    sProf : int, optional
        number of profiles used to calculate the anomaly for
        partially filter the second trip echoes
        (IT GOES TO FILTER MODULE)

    center : bool, optional
        (IT GOES TO FILTER MODULE)

    min_periods : int, optional
        (IT GOES TO FILTER MODULE)

    n_std : int, optional
        size of the standard deviation window used
        to partially remove the second trip echoes
        (IT GOES TO FILTER MODULE)

    check90 : bool, optional
        If True, it checks if the vertical observations
        are available. If False, the verification is ignored.

    Returns
    -------
    object : object

        an instance of the prepared for the retrieval

    """

    def __init__(
        self,
        data: xr.Dataset,
        snr=False,
        status=True,
        n_prof=500,
        center=True,
        min_periods=30,
        n_std=2,
        check90=True,
    ):

        self.logger = logging.getLogger(
            "lidarwind.data_operator.GetRestructuredData"
        )
        self.logger.info("creating an instance of GetRestructuredData")

        if not isinstance(data, xr.Dataset):
            self.logger.error("wrong data type: expecting a xr.Dataset")
            raise TypeError

        self.data = data
        self.snr = snr
        self.status = status
        self.n_prof = n_prof
        self.center = center
        self.min_periods = min_periods
        self.n_std = n_std

        self.vertical_component_check(check90)
        self.get_coord_non_90()
        self.data_transform()
        self.data_transform_90()

    def get_coord_non_90(self):

        """
        It identifies and selects the slanted data
        """

        self.logger.info("identifying and selecting the slanted observations")

        self.elv_non_90 = np.unique(
            self.data.elevation.where(self.data.elevation != 90, drop=True)
        )
        self.azm_non_90 = np.unique(
            self.data.azimuth.where(self.data.elevation != 90, drop=True)
        )
        self.azm_non_90 = np.sort(self.azm_non_90)

        self.time_non_90 = self.data.time.where(
            self.data.elevation != 90, drop=True
        )
        self.range_non_90 = self.data.range

        return self

    def data_transform(self):

        """
        It creates an xr.DataArray from all slanted observations
        """

        self.logger.info("creating a DataArray of the slanted observations")

        dop_wind_arr = np.empty(
            (
                self.time_non_90.shape[0],
                self.range_non_90.shape[0],
                len(self.azm_non_90),
                len(self.elv_non_90),
            )
        )

        for j, elv in enumerate(self.elv_non_90):

            for i, azm in enumerate(self.azm_non_90):

                tmp_rad_wind = Filtering(self.data).get_radial_obs_comp(
                    "radial_wind_speed", azm, snr=self.snr, status=self.status
                )

                dop_wind_arr[:, :, i, j] = tmp_rad_wind.sel(
                    time=self.time_non_90, method="Nearest"
                ).values

        new_range = self.data.range90.values[: len(self.data.range)]
        resampled_dop_vel = xr.DataArray(
            data=dop_wind_arr,
            dims=("time", "range", "azm", "elv"),
            coords={
                "time": self.time_non_90,
                "range": new_range,
                "azm": self.azm_non_90,
                "elv": self.elv_non_90,
            },
        )

        resampled_dop_vel.attrs = {
            "standard_name": "radial_wind_speed",
            "units": "m s-1",
            "comments": "radial wind speed vector.",
        }

        self.data_transf = resampled_dop_vel

        return self

    def data_transform_90(self):

        """
        It creates an xr.DataArray from all vertically pointing observations
        """

        self.logger.info("selcting zenith observations")

        tmp_data = Filtering(self.data).get_vertical_obs_comp(
            "radial_wind_speed90", snr=self.snr, status=self.status
        )
        tmp_data = tmp_data.isel(range90=slice(0, len(self.range_non_90)))
        self.data_transf_90 = tmp_data

        tmp_data = Filtering(self.data).get_vertical_obs_comp(
            "relative_beta90", snr=self.snr, status=self.status
        )
        tmp_data = tmp_data.isel(range90=slice(0, len(self.range_non_90)))
        self.relative_beta90 = tmp_data

        return self

    def vertical_component_check(self, check90):

        if check90:
            if not hasattr(self.data, "radial_wind_speed90"):
                raise KeyError
        else:
            print("Vertical component check was ignored.")


class GetResampledData:
    """Alternative basic data resample

    This class is used to resample the data
    into a given temporal grid.

    It mainly used internal processings of
    the package.

    Parameters
    -----------
    xr_data_array : xr.DataArray
        varaiable that will be resampled

    vert_coord : str
        name of the vertical coordinate

    time_freq : str
        size of the window e.g.: '15s'

    tolerance : int
        maximum separation from the reference

    time_coord : str
        name of the time coordinate

    Returns
    -------
    data : xr.DataArray

        time resampled variable

    """

    def __init__(
        self,
        xr_data_array: xr.DataArray,
        vert_coord="range",
        time_freq="15s",
        tolerance=10,
        time_coord="time",
    ):

        self.logger = logging.getLogger(
            "lidarwind.data_operator.GetResampledData"
        )
        self.logger.info("creating an instance of GetResampledData")

        if not isinstance(xr_data_array, xr.DataArray):
            self.logger.error("wrong data type: expecting a xr.DataArray")
            raise TypeError

        self.var_name = xr_data_array.name
        self.attrs = xr_data_array.attrs
        data = xr_data_array
        date = pd.to_datetime(data[time_coord].values[0])

        self.time_ref = self.get_time_ref(date, time_freq)
        self.vert_coord = data[vert_coord]

        time_ref_sec = np.array(self.time_ref, float) * 10 ** (-9)
        time_orig_sec = np.array(data[time_coord].values, float) * 10 ** (-9)

        delta_grid = self.calc_delt_grid(time_ref_sec, time_orig_sec)
        time_index_array = self.get_nearest_index_method_2(
            delta_grid, tolerance
        )

        self.values = self.time_resample(
            data, time_index_array, self.vert_coord
        )
        self.resampled = self.convert_to_data_array()

    def get_time_ref(self, date, time_freq="1s"):
        """
        Genetates the time reference grid used for
        resampling the data

        Parameters
        ----------
            date : Timestamp
                date for resampling (pandas Timestamp)

            dateFreq: str
                resolution of the reference grid (str, default=1s)

        Returns
        -------
        time_ref : DatetimeIndex
            time reference grid (DatetimeIndex)

        """

        self.logger.info("defining the reference time")

        start = dt.datetime(date.year, date.month, date.day, 0, 0, 0)

        end = dt.datetime(date.year, date.month, date.day, 23, 59, 59)

        time_ref = pd.date_range(start, end, freq=time_freq)

        return time_ref

    def calc_delt_grid(self, ref_grid, orig_grid):
        """
        Calculates the distance between the reference grid
        and the radar grid (time or range)

        Parameters
        ----------
        ref_grid : numpy.array
            reference grid (array[n])

        radarGrid : numpy.array
            radar grid (array[m])

        Returns
        -------
        delta_grid : numpy.array

            distance between each element from
            the reference grid to each element from the
            radar grid
        """

        self.logger.info("calculating the distance to the reference")

        tmp_grid_2_d = np.ones((len(ref_grid), len(orig_grid))) * orig_grid

        delta_grid = tmp_grid_2_d - np.reshape(ref_grid, (len(ref_grid), 1))

        return delta_grid

    def get_nearest_index_method_2(self, delta_grid, tolerance):
        """
        Identify the index of the delta_grid that fulfil
        the resampling tolerance

        Parameters
        ----------
        delta_grid : numpy.array
            output from calcRadarDeltaGrid

        tolerance : int
            tolerance distance for detecting
            the closest neighbour (time or range)

        Returns
        -------
        grid_index : np.array

            array of indexes that fulfil the resampling
            tolerance

        """

        self.logger.info("identifying index that fulfil the tolerance")

        grid_index = np.argmin(abs(delta_grid), axis=1)
        delta_grid_min = np.min(abs(delta_grid), axis=1)
        grid_index = np.array(grid_index, float)
        grid_index[delta_grid_min > tolerance] = np.nan

        return grid_index

    def time_resample(self, data, time_index_array, vert_coord):
        """
        It resamples a given radar variable using the
        time and range index calculated by get_nearest_index_method_2

        Parameters
        ----------
        var : str
            radar variable name to be resampled

        xrDataset : xarray.dataset
            xarray dataset containing the variables to
            be resampled

        timeIdexArray : np.array
            time resampling index (output from get_nearest_index_method_2)

        rangeIndexArray : np.array
            range resampling index (output from get_nearest_index_method_2)

        Returns
        -------
        resampledArr : xarray.dataArray
            time/range resampled numpy array
        """

        self.logger.info(f"time resampling of: {self.var_name}")

        resampled_time_arr = (
            np.ones((time_index_array.shape[0], self.vert_coord.shape[0]))
            * np.nan
        )

        for position, time_index in enumerate(time_index_array):

            try:
                resampled_time_arr[position] = data.values[int(time_index)]

            except:
                pass

        return resampled_time_arr

    def convert_to_data_array(self):
        """
        It creates a DataArray of the resampled data.
        """

        self.logger.info(
            f"generating the new resampled DataArray: {self.var_name}"
        )

        tmp_dt = xr.DataArray(
            self.values,
            dims=("time_ref", self.vert_coord.name),
            coords={
                "time_ref": self.time_ref,
                self.vert_coord.name: self.vert_coord.values,
            },
            name=self.var_name,
            attrs=self.attrs,
        )

        tmp_dt[self.vert_coord.name].attrs = self.vert_coord.attrs

        return tmp_dt


class DbsOperations:
    """DBS file manager

    This class extracts the variables required to
    retrieve the wind information from the DBS files.

    Parameters
    ----------
    file_list : list
        list of DBS files
    var_list : list
        list of variables to be extracted from the DBS files

    Returns
    -------
    object : object

        it returns an object containing an instance of the
        merged files (.merged_ds)

    """

    def __init__(self, file_list, var_list):

        self.logger = logging.getLogger(
            "lidarwind.data_operator.DbsOperations"
        )
        self.logger.info("creating an instance of DbsOperations")

        self.merged_ds = xr.Dataset()
        self.file_list = file_list
        self.var_list = var_list

        self.merge_data(file_list, var_list)

    def merge_data(self, file_list, var_list):
        """
        This method merges all files from a list of DBS files

        Parameters
        ----------
        file_list : list
            list of files to be merged

        var_list : list
            list of variables to be merged

        """

        self.logger.info("merging all DBS files")

        if bool(file_list) is False:
            self.logger.error(
                "lidarwind stopped due to an empty list of DBS files."
            )
            raise FileNotFoundError

        if bool(var_list) is False:
            self.logger.error(
                "lidarwind stopped due to an empty list of variable"
            )
            raise KeyError

        for file in file_list:

            try:
                file_to_merge = GetLidarData(file).open_lidar_file()
                self.logger.debug(f"reading file: {file}")
            except:
                self.logger.warning(f"This file has a problem: {file}")
                raise

            file_to_merge = self.mean_time_derivation(file_to_merge)
            # file_to_merge = self.add_mean_time(file_to_merge)

            try:
                self.merge_2_ds(file_to_merge, var_list)
            except:
                self.logger.warning(f"Merging not possible: {file}")
                # raise

    def add_mean_time(self, lidar_ds):
        """
        This method adds the mean time to each file from
        the DBS scan strategy.

        Parameters
        ----------
        lidar_ds : xarray.DataSet
            a dataset from a sequence of scans

        """

        self.logger.info("calculating the mean DBS time for each file")

        mean_time_ns = np.array(lidar_ds.time.values, np.float64).mean()
        mean_time = pd.to_datetime(
            np.ones(len(lidar_ds.time.values)) * mean_time_ns
        )
        mean_time_da = xr.DataArray(
            data=mean_time,
            dims=("time"),
            coords={"time": lidar_ds.time},
            name="scan_mean_time",
        )

        lidar_ds = lidar_ds.merge(mean_time_da)

        return lidar_ds

    def merge_2_ds(self, file_to_merge, var_list):
        """
        This method merges the variables extracted from
        the single DBS file with the storage dataset (merged_ds).

        Parameters
        ----------
        file_to_merge : xarray.DataSet
            a single file dataset

        var_list : list
            a list of variables to be merged

        """

        self.logger.info("merging single DBS file")

        for var in var_list:

            self.merged_ds = xr.merge([self.merged_ds, file_to_merge[var]])

        self.merged_ds = xr.merge(
            [self.merged_ds, file_to_merge["scan_mean_time"]]
        )

    def mean_time_derivation(self, data):

        data.azimuth.values = np.round(data.azimuth.values)
        data.azimuth.values[data.azimuth.values == 360] = 0

        azm_ref = data.azimuth.values[0]
        index_new_scan = data.ray_index.where(
            (data.elevation != 90) & (data.azimuth == azm_ref)
        )
        index_complete_scans = index_new_scan.values[
            np.isfinite(index_new_scan.values)
        ]

        if not len(data.time) in index_complete_scans:
            index_complete_scans = np.append(
                index_complete_scans, len(data.time)
            )

        groups = data.groupby_bins(
            "ray_index", index_complete_scans, right=False
        )

        new_data = xr.Dataset()
        for grp in groups.groups:

            new_data = xr.merge([new_data, self.add_mean_time(groups[grp])])

        return new_data
