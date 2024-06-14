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

    time_attrs = ds[time_name].attrs
    ds[time_name] = ds[time_name] + ds[time_ms_name] * 1e-3
    ds[time_name].attrs["units"] = "seconds since 20010101 00:00:00"
    ds = xr.decode_cf(ds)
    ds[time_name].attrs = time_attrs

    return ds


def selecting_variables(
    ds: xr.Dataset,
    chirp_var: list = ["MeanVel", "ZDR"],
    other_var: list = ["Azm", "Elv"],
) -> xr.Dataset:

    """RPG variable selection

    It extracts the variables needed for retrieving
    wind profiles from the radar PPI data and returns
    them as a dataset.

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

    # selecting chirp dependent variables
    for v in chirp_var:
        for chirp_number in range(ds["ChirpNum"].values):

            chirp_name = f"C{chirp_number+1}"

            tmp_data = ds[f"{chirp_name}{v}"].rename(
                {f"{chirp_name}Range": "range"}
            )

            # writing variable name
            tmp_data.name = v

            # re-writing attributes
            tmp_att = ds[f"{chirp_name}{v}"].attrs["Name"]
            if "Chirp" in tmp_att:
                r = tmp_att.split("Chirp")[0]
                tmp_data.attrs["Name"] = f"{r}Chirp Merged"

            tmp_ds.extend([tmp_data])

    # selecting other variables
    for v in other_var:
        tmp_ds.extend([ds[v]])

    # filtering out -999
    tmp_ds = xr.merge(tmp_ds)
    tmp_ds.where(tmp_ds != -999)

    # preparing range variale for estimation
    tmp_ds["range_layers"] = tmp_ds["range"]
    tmp_ds = tmp_ds.assign_coords({"range": np.arange(len(tmp_ds["range"]))})
    tmp_ds["range"].attrs = {"name": "range index"}
    tmp_ds["range_layers"].attrs = {
        "units": "m",
        "name": "range",
        "comment": "distance from the centre of each range to the receiver",
    }

    # variable name correction
    tmp_ds = tmp_ds.rename(
        {"Time": "time", "Azm": "azimuth", "Elv": "elevation"}
    )

    tmp_ds.attrs = ds.attrs
    tmp_ds.attrs["Comment"] = "Variables selected for wind estimation"

    return tmp_ds


def azimuth_offset(ds: xr.Dataset, azm: str = "azimuth") -> xr.Dataset:

    """Azimuth offset correction

    This function is intended to correct the
    chirp-dependent bias that affects the
    radar measurements. Additional information
    from the radar operation is still needed
    to allow full correction. Currently, it
    only identifies if the azimuths are
    increasing or decreasing with time.
    IT SHOULD BE APPLIED TO SINGLE PPI FILES.

    Parameters
    ----------
    ds : xr.Dataset
        A single PPI dataset

    azm : string
        Name of the azimuth variable

    Returns
    -------
    xr.Dataset
        An azimuth-corrected dataset

    """

    if not isinstance(ds, xr.Dataset):
        raise TypeError

    assert f"{azm}" in ds

    # The offset values listed below were
    # retrieved using the wind cube lidar
    # as reference

    result = ds[azm][-1] - ds[azm][0]

    # increasing azimuth
    if result > 0:

        # -> reference for future development
        # ds[var].attrs['azmOff_c3'] = '4.88'
        # ds[var].attrs['azmOff_c2'] = '4.23'
        # ds[var].attrs['azmOff_c1'] = '2.08'

        ds["azm_seq"] = 1

    # decreasing azimuth
    if result < 0:

        # ds[var].attrs['azmOff_c3'] = '0'
        # ds[var].attrs['azmOff_c2'] = '0'
        # ds[var].attrs['azmOff_c1'] = '0'

        ds["azm_seq"] = -1

    ds["azm_seq"].attrs = {
        "comment": " 1: azimuth increasing; -1: azimuth decreasing"
    }

    return ds


def height_estimation(ds: xr.Dataset) -> xr.Dataset:

    """Data height estimation

    Calculation of the height of the observations.
    It uses the elevation and the range to calculate
    the height of the observations.

    Parameters
    ----------
    ds : xr.Dataset
        A dataset of selected variables generated
        by selecting_variables function.

    Returns
    -------
    xr.Dataset
        Height corrected dataset

    """

    if not isinstance(ds, xr.Dataset):
        raise TypeError

    assert "range_layers" in ds
    assert "elevation" in ds

    # height estimation
    correc_fact = np.sin(np.deg2rad(ds["elevation"].values[0]))
    ds["range_layers"] = ds.range_layers * correc_fact
    ds["range_layers"].attrs = {
        "units": "m",
        "name": "range",
        "comment": "height estimated from the original range and elevation",
    }

    return ds


def fill_nan_values(ds: xr.Dataset) -> xr.Dataset:

    """Data problems reduction

    It drops some possible time duplicates that
    are often present and interpolate some of the
    NaNs if they are there.

    Parameters
    ----------
    ds : xr.Dataset
        A PPI dataset

    Returns
    -------
    xr.Dataset
        A dataset corrected for possible problems

    """

    if not isinstance(ds, xr.Dataset):
        raise TypeError

    assert "time" in ds

    tmp_ds = ds.drop_duplicates(dim="time")
    tmp_ds = tmp_ds.interpolate_na(dim="time")

    return tmp_ds


def update_structure(ds: xr.Dataset) -> xr.Dataset:

    """Coordinate transformation

    It transforms the oservations coordiante from
    range and time to range and azimuth. The
    ranges/azimuth coordinate system is needed for
    estimating wind profiles using the FFT based method.
    It also drops possible duplicates from the azimuth
    coordinate.

    transformation:
    DS[range, time] --> DS[range, azimuth]

    Parameters
    ----------
    ds : xr.Dataset
        A RPG PPI dataset

    Returns
    -------
    xr.Dataset
        A coordinate transformed dataset

    """

    if not isinstance(ds, xr.Dataset):
        raise TypeError

    assert "time" in ds
    assert "azimuth" in ds
    assert "elevation" in ds
    assert "nan_percentual" in ds

    tmp_ds = (
        ds.swap_dims({"time": "azimuth"})
        .reset_coords()
        .drop_duplicates(dim="azimuth")
    )

    tmp_ds = tmp_ds.assign_coords({"elevation": ds.elevation.values[0]})
    tmp_ds["elevation"].attrs = ds["elevation"].attrs

    tmp_ds = tmp_ds.assign_coords({"mean_time": ds.time.mean()})
    tmp_ds["mean_time"].attrs[
        "comment"
    ] = "mean time (seconds) from each PPI scan"

    # in the future, an external function will do it
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
    max_zdr.attrs["Name"] = "Maximum ZDR"
    max_zdr.attrs["units"] = "dB"
    max_zdr.attrs["Comment"] = "Maximum ZDR per complete PPI scan"

    nan_percent = ds.nan_percentual.assign_coords(
        {"mean_time": tmp_ds.mean_time}
    )

    tmp_ds = xr.merge([tmp_ds, start_scan, end_scan, max_zdr, nan_percent])

    return tmp_ds


def get_chirp_information(ds: xr.Dataset) -> xr.Dataset:

    """Chirp extension

    It identifies the extension of each
    chirp region and stores the maximum
    and minimum height. For the future,
    it will also store the chirp azimuth
    bias

    Parameters
    ----------
    ds: xr.Dataset
        An original RPG PPI dataset

    Returns
    -------
    xr.Dataset
        A dataset indicating the extension of the
        individual chirps.

    """

    if not isinstance(ds, xr.Dataset):
        raise TypeError

    assert "Chirp" in ds.dims

    chirp_start = [ds[f"C{c+1}Range"].values.min() for c in ds["Chirp"].values]
    chirp_end = [ds[f"C{c+1}Range"].values.max() for c in ds["Chirp"].values]

    chirp_start = xr.DataArray(
        chirp_start,
        coords={"chirp": ds["Chirp"].values + 1},
        name="chirp_start",
    )

    chirp_start.attrs["units"] = "m"
    chirp_start.attrs["comment"] = "starting height from each chirp sequence"

    chirp_end = xr.DataArray(
        chirp_end, coords={"chirp": ds["Chirp"].values + 1}, name="chirp_end"
    )

    chirp_end.attrs["units"] = "m"
    chirp_end.attrs["comment"] = "ending height from each chirp sequence"

    chirp_dir_bias = xr.DataArray(
        np.zeros_like(ds["Chirp"]),
        coords={"chirp": ds["Chirp"].values + 1},
        name="chirp_azimuth_bias",
    )

    chirp_dir_bias.attrs["units"] = "deg"
    chirp_dir_bias.attrs["comment"] = "wind direction bias correcting factor"

    return xr.merge([chirp_start, chirp_end, chirp_dir_bias])


def update_range(ds: xr.Dataset) -> xr.Dataset:

    """Range update

    It replaces the original range numbers stored in the
    range coordinate with the values stored in the variable
    range_layers. range_layers stores the distance from
    the antenna to the centre of each range gate or the
    estimated height.

    Parameters
    ----------
    ds : xr.Dataset
        A PPI dataset corrected for the height estimation

    Returns
    -------
    xr.Dataset
        A range updated dataset

    """

    if not isinstance(ds, xr.Dataset):
        raise TypeError

    assert "range" in ds

    ds["range"] = ds.range_layers

    return ds


def count_nan_values(ds: xr.Dataset) -> xr.Dataset:

    """Counts NAN

    It counts the number of NaNs present in the MDV per
    range gate and returns the percentual of NaN.

    Parameters
    ----------
    ds : xr.Dataset
       An original RPG PPI dataset

    Returns
    -------
    xr.Dataset
        The original dataset extended with the
        number of NAN percentual

    """

    if not isinstance(ds, xr.Dataset):
        raise TypeError

    assert "time" in ds.dims
    assert "MeanVel" in ds

    total_nan = ds["time"].shape - (ds["MeanVel"] / ds["MeanVel"]).sum(
        dim="time"
    )
    percent_nan = 100 * total_nan / ds["time"].shape
    percent_nan.name = "nan_percentual"
    percent_nan.attrs["comment"] = "Percentual of NaN per single PPI scan"

    ds = ds.merge(percent_nan)

    return ds


def azimuth_regular_grid_interp(
    ds: xr.Dataset,
    azimuth_coord: str = "azimuth",
    azimuth_resolution: float = 5,
) -> xr.Dataset:

    """Azimuth interpolation

    It interpolates MDV[range, azimuth] from an
    irregular azimuth grid to a regular azimuth
    grid. The default resolution of the new azimuth
    coordinate is 5 degrees, which is close to the
    original resolution used during CMTRACE campaigns.
    This step is required to allow using the FFT method
    to retrieve wind speed and direction .

    Parameters
    ----------
    ds : xr.Dataset
        A coordinate transformed dataset ds[range, azimuth].
        An output from update_structure.

    azimuth_coordinate : str
        Name used for the azimuth coordinate

    azimuth_resolution : float
        Resolution of the new azimuth coordinate

    Returns
    -------
    xr.Dataset
        A dataset interpolated to a regular azimuth grid.

    """

    if not isinstance(ds, xr.Dataset):
        raise TypeError

    assert azimuth_coord in ds

    azimuth = np.arange(0, 360, azimuth_resolution)
    ds = ds.interp({azimuth_coord: azimuth})

    return ds


def nan_leftover_to_mean(ds: xr.Dataset) -> xr.Dataset:

    """Remain NAN filling

    For each range, It replaces all remaining NaNs
    that are still present in the MDV variable.
    This step is also required in order to use the
    FFT for retrieving wind speed and direction.

    Parameters
    ----------
    ds : xr.Dataset
        A structure updated dataset and interpolated
        to regular azimuth grid. An output from
        azimuth_regular_grid_interp.

    Returns
    -------
    xr.Dataset
        An dataset where the MDV is NAN free

    """

    if not isinstance(ds, xr.Dataset):
        raise TypeError

    assert "azimuth" in ds.dims
    assert "MeanVel" in ds

    mean_rad_vel = ds["MeanVel"].mean(dim="azimuth")

    for r in range(ds.range.shape[0]):

        nan_index = ~np.isfinite(ds["MeanVel"][:, r])
        ds["MeanVel"][:, r][nan_index] = mean_rad_vel[r]

    ds["MeanVel"].attrs["Comment"] = "NaN were replaced with the mean value"
    return ds


def rpg_slanted_radial_velocity_4_fft(ds):

    """RPG preprocessing template

    It is a processing template for the RPG PPI
    output dataset.

    Parameters
    ----------
    ds : xr.Dataset
        An original PPI RPG dataset

    Returns
    -------
    xr.Dataset
        A dataset preprocessed for the wind retrieval

    """

    if not isinstance(ds, xr.Dataset):
        raise TypeError

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
