import xarray as xr

from ..wind_retrieval.fft_wind_retrieval import get_wind_properties


def get_horizontal_wind(ds: xr.Dataset) -> xr.Dataset:

    """Horizontal wind dataset

    This function creates the wind dataset.
    It uses the preprocessed dataset to
    extract the needed information and
    applies the fft wind retrieval.


    Parameters:
    -----------
    ds : xr.Dataset
        A preprocessed dataset: output from
        rpg_slanted_radial_velocity_4_fft

    Returns:
    --------
    xr.Dataset
        Final horizontal wind dataset
        including auxiliary information
        to help to characterise the
        dataset.

    """

    if not isinstance(ds, xr.Dataset):
        raise TypeError(f"{ds} is not an instance of xr.Dataset")

    required_variables = [
        "start_scan",
        "end_scan",
        "zdr_max",
        "nan_percentual",
        "chirp_start",
        "chirp_end",
        "chirp_azimuth_bias",
        "azm_seq",
    ]

    for v in required_variables + ["mean_time"]:
        if v not in ds:
            raise KeyError(f"{v} is not available in the provided dataset")

    wind_ds = get_wind_properties(ds.MeanVel)
    wind_ds = wind_ds.merge(ds[required_variables])
    wind_ds = wind_ds.expand_dims(["mean_time"])

    return wind_ds
