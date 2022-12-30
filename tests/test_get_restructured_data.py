import pytest
import numpy as np
import xarray as xr

import lidarSuit as lst


@pytest.fixture
def get_dummy_six_beam_data():

    wind = (
        np.sin(np.deg2rad(np.array([0, 72, 144, 216, 288]) + 0))
        * 1
        / np.sin(np.deg2rad(45))
    )

    elv = np.array([45, 45, 45, 45, 45, 90])
    data_elv = xr.DataArray(
        elv, dims=("time"), coords={"time": np.arange(len(elv))}
    )

    azm = np.array([0, 72, 144, 216, 288, 0])
    data_azm = xr.DataArray(
        azm, dims=("time"), coords={"time": np.arange(len(elv))}
    )

    data = xr.DataArray(
        np.append(wind, 0)[:, np.newaxis],
        dims=("time", "range"),
        coords={"time": np.arange(len(elv)), "range": [1]},
    )

    data90 = xr.DataArray(
        np.array([1, 1, 1, 1, 1, 1])[:, np.newaxis],
        dims=("time", "range90"),
        coords={"time": np.arange(len(elv)), "range90": [1]},
    )

    data_status = xr.DataArray(
        np.array([1, 1, 1, 1, 1, 1])[:, np.newaxis],
        dims=("time", "range"),
        coords={"time": np.arange(len(elv)), "range": [1]},
    )

    test_ds = xr.Dataset(
        {
            "elevation": data_elv,
            "azimuth": data_azm,
            "cnr90": data90,
            "gate_index90": data90,
            "radial_wind_speed90": data90,
            "radial_wind_speed_status90": data90,
            "relative_beta90": data90,
            "cnr": data,
            "gate_index": data,
            "radial_wind_speed": data,
            "radial_wind_speed_status": data_status,
            "relative_beta": data,
        }
    )

    return test_ds


@pytest.fixture
def get_restruc_obj(get_dummy_six_beam_data):
    return lst.GetRestructuredData(get_dummy_six_beam_data)


def test_get_resctructured_data_range_non_90_size(get_restruc_obj):
    assert len(get_restruc_obj.range_non_90.values) == 1


def test_get_resctructured_data_range_non_90_values(get_restruc_obj):
    assert np.round(get_restruc_obj.range_non_90.values, 1) == 1


def test_get_resctructured_data_data_transf_time_dim(get_restruc_obj):
    assert "time" in get_restruc_obj.data_transf.dims


def test_get_resctructured_data_data_transf_range_dim(get_restruc_obj):
    assert "range" in get_restruc_obj.data_transf.dims


def test_get_resctructured_data_data_transf_azm_dim(get_restruc_obj):
    assert "azm" in get_restruc_obj.data_transf.dims


def test_get_resctructured_data_data_transf_elv_dim(get_restruc_obj):
    assert "elv" in get_restruc_obj.data_transf.dims


def test_get_resctructured_data_data_transf_elv_value(get_restruc_obj):
    assert np.round(get_restruc_obj.data_transf.elv.values, 1) == 45


def test_get_resctructured_data_data_transf_azm_value(get_restruc_obj):
    assert (
        np.round(get_restruc_obj.data_transf.azm.values, 1)
        == np.array([0, 72, 144, 216, 288])
    ).all()


def test_get_resctructured_data_data_transf_90_time_dim(get_restruc_obj):
    assert "time" in get_restruc_obj.data_transf_90.dims


def test_get_resctructured_data_data_transf_90_range90_dim(get_restruc_obj):
    assert "range90" in get_restruc_obj.data_transf_90.dims


def test_get_resctructured_data_data_transf_90_name(get_restruc_obj):
    assert "radial_wind_speed90" in get_restruc_obj.data_transf_90.name


def test_get_resctructured_data_data_transf_90_time_dim_size(get_restruc_obj):
    assert len(get_restruc_obj.data_transf_90.time) == 1


def test_get_resctructured_data_data_transf_90_range90_dim_size(
    get_restruc_obj,
):
    assert len(get_restruc_obj.data_transf_90.range90) == 1
