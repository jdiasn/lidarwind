import numpy as np
import pytest
import xarray as xr

from lidarwind.preprocessing import rpg_radar


def test_time_decoding_ds_type():

    with pytest.raises(TypeError):
        rpg_radar.time_decoding(ds=np.array([1, 2]))


def test_time_decoding_time():

    with pytest.raises(AssertionError):
        rpg_radar.time_decoding(ds=xr.Dataset({"Timems": [0]}))


def test_time_decoding_timems():

    with pytest.raises(AssertionError):
        rpg_radar.time_decoding(ds=xr.Dataset({"Time": [0]}))


def test_selecting_variables_ds_type():

    with pytest.raises(TypeError):
        rpg_radar.selecting_variables(ds=np.array([1, 2]))


def test_selecting_variables_time():

    with pytest.raises(AssertionError):
        rpg_radar.selecting_variables(ds=xr.Dataset({"Azm": [0], "Elv": [0]}))


def test_selecting_variables_azm():

    with pytest.raises(AssertionError):
        rpg_radar.selecting_variables(ds=xr.Dataset({"Time": [0], "Elv": [0]}))


def test_selecting_variables_elv():

    with pytest.raises(AssertionError):
        rpg_radar.selecting_variables(ds=xr.Dataset({"Time": [0], "Azm": [0]}))


def test_azimuth_offset_ds():

    with pytest.raises(TypeError):
        rpg_radar.azimuth_offset(ds=np.array([1, 2]))


def test_azimuth_offset_azm():

    with pytest.raises(AssertionError):
        rpg_radar.azimuth_offset(ds=xr.Dataset({"Time": [0], "Elv": [0]}))


def test_height_estimation_ds():

    with pytest.raises(TypeError):
        rpg_radar.height_estimation(ds=np.array([1, 2]))


def test_height_estimation_range_layers():

    with pytest.raises(AssertionError):
        rpg_radar.height_estimation(ds=xr.Dataset({"elevation": [0]}))


def test_height_estimation_elevation():

    with pytest.raises(AssertionError):
        rpg_radar.height_estimation(ds=xr.Dataset({"range_layers": [0]}))


def test_fill_nan_values_ds():

    with pytest.raises(TypeError):
        rpg_radar.fill_nan_values(ds=np.array([1, 2]))


def test_fill_nan_values_time():

    with pytest.raises(AssertionError):
        rpg_radar.fill_nan_values(ds=xr.Dataset({"range_layers": [0]}))
