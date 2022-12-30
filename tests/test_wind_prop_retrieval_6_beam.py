import pytest
import numpy as np
import xarray as xr

import lidarwind as lst


def test_six_beam_method_input():

    with pytest.raises(TypeError):
        lst.SixBeamMethod(data=xr.DataArray(np.array([0, 1])))


def test_get_dummy_six_beam_obj():

    elv = np.array([75, 75, 90, 75, 75, 75])
    data_elv = xr.DataArray(
        elv, dims=("time"), coords={"time": np.arange(len(elv))}
    )

    azm = np.array([0, 72, 0, 144, 216, 288])
    data_azm = xr.DataArray(
        azm, dims=("time"), coords={"time": np.arange(len(elv))}
    )

    data = xr.DataArray(
        np.array([1, 1, 1, 1, 1, 1])[:, np.newaxis],
        dims=("time", "range"),
        coords={"time": np.arange(len(elv)), "range": [1]},
    )

    data90 = xr.DataArray(
        np.array([1, 1, 1, 1, 1, 1])[:, np.newaxis],
        dims=("time", "range90"),
        coords={"time": np.arange(len(elv)), "range90": [1]},
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
            "radial_wind_speed_status": data,
            "relative_beta": data,
        }
    )

    return lst.GetRestructuredData(test_ds)


@pytest.fixture
def test_get_six_beam_obj():

    six_beam_obj = lst.SixBeamMethod(
        test_get_dummy_six_beam_obj(), freq=6, freq90=6
    )

    return six_beam_obj


def test_six_beam_method_m_matrix(test_get_six_beam_obj):

    assert np.all(np.isfinite(test_get_six_beam_obj.m_matrix))


def test_six_beam_method_m_matrix_inv(test_get_six_beam_obj):

    assert np.all(np.isfinite(test_get_six_beam_obj.m_matrix_inv))


def test_six_beam_method_variance_dic(test_get_six_beam_obj):

    assert len(test_get_six_beam_obj.radial_variances.keys()) == 2


def test_six_beam_method_radial_variances90(test_get_six_beam_obj):

    assert np.all(
        test_get_six_beam_obj.radial_variances["rVariance90"].values == 0
    )


def test_six_beam_method_radial_variances(test_get_six_beam_obj):

    assert np.all(
        test_get_six_beam_obj.radial_variances["rVariance"].values == 0
    )


def test_six_beam_method_sigma_matrix(test_get_six_beam_obj):

    assert np.all(test_get_six_beam_obj.sigma_matrix == 0)


def test_six_beam_method_variance_dim_time(test_get_six_beam_obj):

    assert len(test_get_six_beam_obj.var_comp_ds.time.values) == 1


def test_six_beam_method_variance_dim_range(test_get_six_beam_obj):

    assert len(test_get_six_beam_obj.var_comp_ds.range.values) == 1
