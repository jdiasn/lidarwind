import numpy as np
import pytest
import xarray as xr

from lidarwind.postprocessing import post_rpg_radar


def get_test_ds():
    test_ds = xr.Dataset(
        {
            "start_scan": [0],
            "end_scan": [0],
            "zdr_max": [0],
            "nan_percentual": [0],
            "chirp_start": [0],
            "chirp_end": [0],
            "chirp_azimuth_bias": [0],
            "azm_seq": [0],
            "mean_time": [0],
        }
    )
    return test_ds


def test_get_horizontal_wind_ds_type():

    with pytest.raises(TypeError):
        post_rpg_radar.get_horizontal_wind(ds=np.array([1, 2]))


def test_get_horizontal_wind_start_scan():

    ds = get_test_ds()
    del ds["start_scan"]

    with pytest.raises(KeyError):
        post_rpg_radar.get_horizontal_wind(ds)


def test_get_horizontal_wind_end_scan():

    ds = get_test_ds()
    del ds["end_scan"]

    with pytest.raises(KeyError):
        post_rpg_radar.get_horizontal_wind(ds)


def test_get_horizontal_wind_zdr_max():

    ds = get_test_ds()
    del ds["zdr_max"]

    with pytest.raises(KeyError):
        post_rpg_radar.get_horizontal_wind(ds)


def test_get_horizontal_wind_nan_percentual():

    ds = get_test_ds()
    del ds["nan_percentual"]

    with pytest.raises(KeyError):
        post_rpg_radar.get_horizontal_wind(ds)


def test_get_horizontal_wind_chirp_start():

    ds = get_test_ds()
    del ds["chirp_start"]

    with pytest.raises(KeyError):
        post_rpg_radar.get_horizontal_wind(ds)


def test_get_horizontal_wind_chirp_end():

    ds = get_test_ds()
    del ds["chirp_end"]

    with pytest.raises(KeyError):
        post_rpg_radar.get_horizontal_wind(ds)


def test_get_horizontal_wind_chirp_azimuth_bias():

    ds = get_test_ds()
    del ds["chirp_azimuth_bias"]

    with pytest.raises(KeyError):
        post_rpg_radar.get_horizontal_wind(ds)


def test_get_horizontal_wind_azm_seq():

    ds = get_test_ds()
    del ds["azm_seq"]

    with pytest.raises(KeyError):
        post_rpg_radar.get_horizontal_wind(ds)


def test_get_horizontal_wind_mean_time():

    ds = get_test_ds()
    del ds["mean_time"]

    with pytest.raises(KeyError):
        post_rpg_radar.get_horizontal_wind(ds)
