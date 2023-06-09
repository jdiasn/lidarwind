import numpy as np
import xarray as xr

from ..preprocessing.wind_cube import wc_slanted_radial_velocity_4_fft
from ..wind_retrieval.fft_wind_retrieval import get_wind_properties


def get_horizontal_wind(ds: xr.Dataset) -> xr.Dataset:
    """Apply fft retrieval

    This function applies the fft wind retrieval method
    to the preprocessed dataset

    Parameters
    ----------
    ds : xr.Dataset
        A dataset of preprocessed observations

    Returns
    -------
        The input dataset, but including the horizontal
        wind profiles.

    """

    unique_elevation = np.unique(ds.elevation)[np.unique(ds.elevation) != 90]
    ds_slanted = ds.where(ds.elevation == unique_elevation, drop=True)

    radial_velocities = wc_slanted_radial_velocity_4_fft(ds_slanted)
    horizontal_wind = get_wind_properties(radial_velocities.radial_wind_speed)

    ds = ds.merge(horizontal_wind)

    return ds


# Post processing
def wc_extract_wind(ds: xr.Dataset, method="full") -> xr.Dataset:
    """Wind profiles extraction

    This function extracts the wind information from
    the processed dataset.

    Parameters
    ----------
    ds : xr.Dataset
        A dataset processed and containing the retrieved
        horizontal wind.

    method : string
        Method for extracting the wind dataset.
        If "full", the data is merged, preserving all information.
        If "compact", the data is merged, but only the horizontal
        wind profiles that are almost simultaneous to the
        vertical observations are merged.

    Returns
    -------
        The wind dataset

    """

    vertical_velocity = ds.radial_wind_speed.where(
        ds["elevation"] == 90, drop=True
    )
    vertical_velocity.name = "vertical_wind_speed"
    vertical_velocity = (
        vertical_velocity.drop(["gate_index", "range"])
        .assign_coords(
            {"gate_index": vertical_velocity.range.isel(time=0).values}
        )
        .rename({"gate_index": "range"})
    )

    variables = [
        "horizontal_wind_speed",
        "horizontal_wind_direction",
        "meridional_wind",
        "zonal_wind",
    ]

    horizontal_wind = ds[variables]

    horizontal_wind = horizontal_wind.where(
        horizontal_wind["elevation"] != 90, drop=True
    )
    horizontal_wind = horizontal_wind.where(
        np.isfinite(horizontal_wind.range), drop=True
    )
    new_range = (
        np.sin(np.deg2rad(horizontal_wind.elevation)) * horizontal_wind.range
    )
    horizontal_wind = (
        horizontal_wind.drop(["gate_index", "range"])
        .assign_coords({"gate_index": new_range.isel(time=0).values})
        .rename({"gate_index": "range"})
    )

    horizontal_wind = horizontal_wind.interp(
        {"range": vertical_velocity.range}, method="nearest"
    )

    if method == "full":
        wind = horizontal_wind.merge(vertical_velocity)

    if method == "compact":

        wind = (
            horizontal_wind.interp(
                {"time": vertical_velocity["time"]}, method="nearest"
            )
            .drop(["elevation"])
            .merge(vertical_velocity)
        )

    wind = wind.drop(["azimuth", "azimuth_length", "freq_azimuth"])

    return wind
