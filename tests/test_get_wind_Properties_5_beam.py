import pytest
import xarray as xr
import numpy as np

import lidarwind as lst


def get_dummy_dbs():

    wind = (
        np.sin(np.deg2rad(np.array([0, 180, 270, 90])))
        * 1
        / np.sin(np.deg2rad(45))
    )

    elv = np.array([45, 45, 45, 45, 90])
    data_elv = xr.DataArray(
        elv, dims=("time"), coords={"time": np.arange(len(elv))}
    )

    azm = np.array([0, 180, 270, 90, 0])
    data_azm = xr.DataArray(
        azm, dims=("time"), coords={"time": np.arange(len(elv))}
    )

    data = xr.DataArray(
        np.append(wind, 0)[:, np.newaxis],
        dims=("time", "gate_index"),
        coords={"time": np.arange(len(elv)), "gate_index": [1]},
    )

    data_status = xr.DataArray(
        np.array([1, 1, 1, 1, 1])[:, np.newaxis],
        dims=("time", "gate_index"),
        coords={"time": np.arange(len(elv)), "gate_index": [1]},
    )

    data_mean_time = xr.DataArray(
        np.array([1, 1, 1, 1, 1]),
        dims=("time"),
        coords={"time": np.arange(len(elv))},
    )

    test_ds = xr.Dataset(
        {
            "elevation": data_elv,
            "azimuth": data_azm,
            "cnr": data_status,
            "measurement_height": data_status,
            "radial_wind_speed": data,
            "radial_wind_speed_status": data_status,
            "scan_mean_time": data_mean_time,
        }
    )

    return test_ds


@pytest.fixture
def get_wind_profiles():
    return lst.GetWindProperties5Beam(get_dummy_dbs())


def test_get_wind_properties_5_beam_vert_wind_dim(get_wind_profiles):
    assert "gate_index" not in get_wind_profiles.ver_wind_speed.dims


def test_get_wind_properties_5_beam_comp_u_dim(get_wind_profiles):
    assert "gate_index" not in get_wind_profiles.comp_u.dims


def test_get_wind_properties_5_beam_comp_v_dim(get_wind_profiles):
    assert "gate_index" not in get_wind_profiles.comp_v.dims


def test_get_wind_properties_5_beam_comp_u_value(get_wind_profiles):
    assert np.round(get_wind_profiles.comp_u.values, 1) == -2.0


def test_get_wind_properties_5_beam_comp_v_value(get_wind_profiles):
    assert np.round(get_wind_profiles.comp_v.values, 1) == 0


def test_get_wind_properties_5_beam_wind_speed_value(get_wind_profiles):
    assert np.round(get_wind_profiles.hor_wind_speed.values, 1) == 2


def test_get_wind_properties_5_beam_wind_dir_value(get_wind_profiles):
    assert np.round(get_wind_profiles.hor_wind_dir.values, 1) == 270


def test_get_wind_properties_5_beam_vert_wind_value(get_wind_profiles):
    assert np.round(get_wind_profiles.ver_wind_speed.values, 1) == 0
