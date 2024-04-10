import numpy as np
import xarray as xr


def time_decoding(
    ds: xr.Dataset, time_name: str = "Time", time_ms_name: str = "Timems"
) -> xr.Dataset:

    """Time decoder

    This function decodes the time variable from the RPG radar.

    Parameters
    ----------
    ds : xr.Dataset
        A xarray dataset of the original RPG radar files.

    time_name : str
        Name of the time variable

    time_ms_name : str
        Name of the millisecond time variable

    Returns
    -------
    xr.Dataset
        The same dataset, but time is decoded using CF conventions

    """

    if not isinstance(ds, xr.Dataset):
        raise TypeError

    assert time_name in ds
    assert time_ms_name in ds

    ds[time_name] = ds[time_name] + ds[time_ms_name] * 1e-3
    ds[time_name].attrs["units"] = "seconds since 20010101 00:00:00"
    ds = xr.decode_cf(ds)

    return ds


def selecting_variables(
    ds: xr.Dataset,
    chirp_var: list = ["MeanVel", "ZDR"],
    other_var: list = ["Azm", "Elv"],
) -> xr.Dataset:

    """RPG variable selection

    Parameters
    ----------
    ds : xr.Dataset
        A xarray dataset of the original RPG radar files

    chirp_var : list
        Variables that are chirp dependent

    other_var : list
        Variables that are not chirp dependent

    Returns
    -------
    xr.Dataset
        A set of variables needed for the wind retrieval

    """

    if not isinstance(ds, xr.Dataset):
        raise TypeError

    assert "Time" in ds
    assert "Azm" in ds
    assert "Elv" in ds

    tmp_ds = []

    for v in chirp_var:
        for chirp_number in range(ds["ChirpNum"].values):

            chirp_name = f"C{chirp_number+1}"

            tmp_data = ds[f"{chirp_name}{v}"].rename(
                {f"{chirp_name}Range": "range"}
            )

            tmp_data.name = v

            tmp_ds.extend([tmp_data])

    for v in other_var:
        tmp_ds.extend([ds[v]])

    tmp_ds = xr.merge(tmp_ds)
    tmp_ds.where(tmp_ds != -999)

    tmp_ds["range_layers"] = tmp_ds["range"]
    tmp_ds = tmp_ds.assign_coords({"range": np.arange(len(tmp_ds["range"]))})

    tmp_ds = tmp_ds.rename(
        {"Time": "time", "Azm": "azimuth", "Elv": "elevation"}
    )

    return tmp_ds


def azimuth_offset(ds, variable="MeanVel"):
    # those offset values where retrieved using
    # the windcube lidar as reference

    result = ds.azimuth[-1] - ds.azimuth[0]

    # increasing azm
    if result > 0:

        # ds[variable].attrs['azmOff_c3'] = '4.88'
        # ds[variable].attrs['azmOff_c2'] = '4.23'
        # ds[variable].attrs['azmOff_c1'] = '2.08'
        ds["azm_seq"] = 1

    # decreasing azm
    if result < 0:

        # ds[variable].attrs['azmOff_c3'] = '0'
        # ds[variable].attrs['azmOff_c2'] = '0'
        # ds[variable].attrs['azmOff_c1'] = '0'
        ds["azm_seq"] = -1

    return ds


def height_estimation(ds):

    # height estimation
    correc_fact = np.sin(np.deg2rad(ds["elevation"].values[0]))
    ds["range_layers"] = ds.range_layers * correc_fact

    return ds


def fill_nan_values(ds):

    """

    It does more than fill the NaNs by interpolation.
    It replaces the time coordinate by the azimuths.
    It also drops some time or azimuth duplicates.

    MDV[range, time] --> MDV[range, azimuth]

    """

    tmp_ds = ds.drop_duplicates(dim="time")
    tmp_ds = tmp_ds.interpolate_na(dim="time")

    return tmp_ds


def update_structure(ds):

    """

    It does more than fill the NaNs by interpolation.
    It replaces the time coordinate by the azimuths.
    It also drops some time or azimuth duplicates.

    MDV[range, time] --> MDV[range, azimuth]

    """

    # tmp_ds = ds.MeanVel.drop_duplicates(dim='time')
    # tmp_ds = tmp_ds.interpolate_na(dim='time')

    tmp_ds = (
        ds.swap_dims({"time": "azimuth"})
        .reset_coords()
        .drop_duplicates(dim="azimuth")
    )
    tmp_ds = tmp_ds.assign_coords({"elevation": ds.elevation.values[0]})

    tmp_ds = tmp_ds.assign_coords({"mean_time": ds.time.mean()})

    # in the future, I have to use an external function for it
    start_scan = (
        ds.time[0].assign_coords({"mean_time": tmp_ds.mean_time}).drop("time")
    )
    start_scan.name = "start_scan"
    end_scan = (
        ds.time[-1].assign_coords({"mean_time": tmp_ds.mean_time}).drop("time")
    )
    end_scan.name = "end_scan"

    max_zdr = ds.ZDR.max("time").assign_coords({"mean_time": tmp_ds.mean_time})
    max_zdr.name = "zdr_max"

    nan_percent = ds.nan_percentual.assign_coords(
        {"mean_time": tmp_ds.mean_time}
    )

    tmp_ds = xr.merge([tmp_ds, start_scan, end_scan, max_zdr, nan_percent])

    return tmp_ds


def get_chirp_information(ds):

    chirp_start = [ds[f"C{c+1}Range"].values.min() for c in ds["Chirp"].values]
    chirp_end = [ds[f"C{c+1}Range"].values.max() for c in ds["Chirp"].values]

    chirp_start = xr.DataArray(
        chirp_start,
        coords={"chirp": ds["Chirp"].values + 1},
        name="chirp_start",
    )
    chirp_end = xr.DataArray(
        chirp_end, coords={"chirp": ds["Chirp"].values + 1}, name="chirp_end"
    )
    chirp_dir_bias = xr.DataArray(
        np.zeros_like(ds["Chirp"]),
        coords={"chirp": ds["Chirp"].values + 1},
        name="chirp_azimuth_bias",
    )

    return xr.merge([chirp_start, chirp_end, chirp_dir_bias])


def rpg_slanted_radial_velocity_4_fft(ds):

    chirp_info = get_chirp_information(ds)

    # pre-processing
    ds = time_decoding(ds)
    ds = selecting_variables(ds)
    ds = azimuth_offset(ds)
    ds = height_estimation(ds)

    ds = update_range(ds)
    ds = count_nan_values(ds)
    ds = fill_nan_values(ds)

    ds = update_structure(ds)
    ds = azimuth_regular_grid_interp(ds)
    ds = nan_leftover_to_mean(ds)

    ds = ds.merge(chirp_info)

    return ds


def update_range(ds):

    """

    It replaces the original range numbers stored in the
    range coordinate with the values stored in variable
    range_layers. range_layers stores the distance from
    the antenna to the centre of each range gate

    """

    ds["range"] = ds.range_layers

    return ds


def count_nan_values(ds):

    """

    It counts the number of NaNs present in the MDV per
    range gate and returns the percentual of NaN.

    """

    total_nan = ds.time.shape - (ds["MeanVel"] / ds["MeanVel"]).sum(dim="time")
    percent_nan = 100 * total_nan / ds.time.shape
    percent_nan.name = "nan_percentual"

    ds = ds.merge(percent_nan)

    return ds


def azimuth_regular_grid_interp(ds):

    """

    It interpolates MDV[range, azimuth] from a
    irregular azimuth grid to a regular azimuth
    grid. The resolution of the new azimuth coordinate
    is 5 degrees, which is close to the original
    resolution.

    This step is required in order to use the FFT for
    retrieving wind speed and direction.

    """

    azimuths = np.arange(0, 360, 5)  # 5
    ds = ds.interp(azimuth=azimuths)

    return ds


def nan_leftover_to_mean(ds):

    """

    For each range, It replaces all remaining NaNs from
    the interpolated MDV by the mean values.

    This step is also required in order to use the FFT for
    retrieving wind speed and direction.

    """

    mean_rad_vel = ds.MeanVel.mean(dim="azimuth")

    for r in range(ds.range.shape[0]):

        nan_index = ~np.isfinite(ds.MeanVel[:, r])
        ds.MeanVel[:, r][nan_index] = mean_rad_vel[r]

    return ds
