import numpy as np
import pandas as pd
import xarray as xr

from lidarwind.io import open_sweep


def wc_azimuth_elevation_correction(
    ds: xr.Dataset, azimuth_resolution: int = 1, elevation_resolution: int = 1
):

    """Azimuth and elevation correction

    This function corrects the azimuth ambiguity issue by
    replacing the 360 azimuth value with 0. It also rounds
    the elevation and azimuth according to a specified
    resolution

    Parameters
    ----------
    ds : xr.Dataset
        A dataset containing the WindCube's observations

    azimuth_resolution : int
        Azimuth resolution in degrees

    elevation_resolution : int
        Elevation resolution in degrees

    Returns
    -------
    xr.Dataset
        The same dataset, but the azimuth is corrected for the ambiguity

    """

    assert "azimuth" in ds
    assert ds["azimuth"].dims == ("time",)

    ds["azimuth"] = ds["azimuth"].round(azimuth_resolution)
    # Avoid ambiguity on 360 degrees
    ds["azimuth"] = ds["azimuth"].where(ds.azimuth != 360, 0)

    ds["elevation"] = ds["elevation"].round(elevation_resolution)

    return ds


def wc_fixed_files_restruc_dataset(ds: xr.Dataset):

    """Restructuring fixed type files

    This function restructures the WindCube fixed
    file type; it is needed to allow the merging
    of several fixed-type files. The function starts
    by swapping the range dimension with the gate_index.
    Then, the time dimension is added to the variables
    that do not have it. After that, elevation, azimuth
    and range are defined as new coordinates.

    Parameters
    ----------
    ds : xr.Dataset
        A dataset from the WindCube's fixed file type

    Returns
    -------
    xr.Dataset
        The same dataset, but restructured for merging.

    """

    if not isinstance(ds, xr.Dataset):
        raise TypeError

    assert "time" in ds
    assert "range" in ds
    assert "azimuth" in ds
    assert "elevation" in ds
    assert "gate_index" in ds

    ds["gate_index"] = ds["gate_index"].astype("i")
    ds = ds.swap_dims({"range": "gate_index"}).reset_coords()

    tmp_no_time = ds[
        [v for v in ds.variables if "time" not in ds[v].dims]
    ].expand_dims("time")
    tmp_time = ds[[v for v in ds.variables if "time" in ds[v].dims]]

    ds = xr.merge([tmp_no_time, tmp_time])
    ds = ds.set_coords(["elevation", "azimuth", "range"])

    return ds


def wc_fixed_merge_files(file_names: list):

    """Merging fixed type files

    This function merges multiple fixed files into a single dataset.

    Parameters
    ----------
    file_names : list
        A list of fixed files to be merged

    Returns
    -------
    xr.Dataset
        A dataset containing data from all files specified
        in the file_names list

    """

    zenith_list = []
    slanted_list = []

    if bool(file_names) is False:
        raise FileNotFoundError

    for file in file_names:

        tmp_ds = wc_fixed_files_restruc_dataset(open_sweep(file))

        if tmp_ds["elevation"] == 90:
            zenith_list.extend([tmp_ds])

        if tmp_ds["elevation"] != 90:
            slanted_list.extend([tmp_ds])

        tmp_ds.close()

    ds_zenith = xr.merge(zenith_list)
    ds_slanted = xr.merge(slanted_list)

    ds = xr.merge([ds_zenith, ds_slanted])

    return ds


def wc_slanted_radial_velocity_4_fft(ds: xr.Dataset):

    """Extraction of slanted radial velocities

    This function extracts the non-zenith pointing
    data from the dataset. Only the non-zenith pointing
    data is used to retrieve the horizontal wind speed and
    direction using the FFT method. Additionally, it sets
    azimuth as a new dimension and reindexes the data by
    proximity in time. The function identifies the duration
    of a complete scan cycle, and for a given time step,
    the time index is used as a central reference and
    assigned as the time index of all azimuthal observations
    within the duration of one cycle.


    Parameters
    ----------
    ds : xr.Dataset
        A dataset of fixed-type files merged,
        corrected for azimuth and elevation ambiguity
        and from a single elevation.


    Rerturns
    --------
    xr.Dataset
        A dataset of reindexed slanted observations with
        an extra dimension: azimuth

    """

    if len(np.unique(ds.elevation)) > 1:
        raise TypeError("This dataset contains multiple elevations")

    if 90 in np.unique(ds.elevation):
        raise ValueError(
            "90 degrees elevation: not valid for retrieving horizontal wind"
        )

    if (
        len(ds["azimuth"].where(ds["azimuth"] == ds["azimuth"][0], drop=True))
        < 2
    ):
        raise ValueError(
            "Not enough data to estimate the one scan cylce duration"
        )

    # initializing storage ds
    radial_velocities = xr.Dataset()

    # identify the mean duration of a complete scan cycle
    half_cycle = (
        ds.where(ds.azimuth == ds.azimuth[0], drop=True)
        .time.diff(dim="time")
        .mean()
        .values
    )
    half_cycle = pd.to_timedelta(half_cycle).seconds / 2

    # unique azimuths
    azimuth = np.unique(ds.azimuth)

    for azm in azimuth:

        # selecting the reference azimuthal slice
        azimuth_left_over = azimuth[azimuth != azm]
        tmp_reference_slice = ds["radial_wind_speed"].where(
            ds["azimuth"] == azm, drop=True
        )
        tmp_reference_slice = (
            tmp_reference_slice.drop(["azimuth"])
            .assign_coords({"azimuth": azm})
            .expand_dims(["azimuth"])
        )
        radial_velocities = xr.merge([radial_velocities, tmp_reference_slice])

        for azm_left in azimuth_left_over:

            tmp_azimuth_slice = ds["radial_wind_speed"].where(
                ds["azimuth"] == azm_left, drop=True
            )
            interp_azimuth_slice = tmp_azimuth_slice.reindex(
                time=tmp_reference_slice.time,
                method="nearest",
                tolerance=f"{half_cycle}s",
            )
            tmp_slice = (
                interp_azimuth_slice.drop(["azimuth"])
                .assign_coords({"azimuth": azm_left})
                .expand_dims(["azimuth"])
            )
            radial_velocities = xr.merge([radial_velocities, tmp_slice])

    radial_velocities["azimuth"].attrs = ds["azimuth"].attrs

    return radial_velocities
