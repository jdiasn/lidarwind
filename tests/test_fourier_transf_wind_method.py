import pytest
import numpy as np
import xarray as xr

import lidarwind as lst


def test_get_dummy_six_beam_obj():

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

    return lst.GetRestructuredData(test_ds)


@pytest.fixture
def test_get_fft_obj():

    test_ds = test_get_dummy_six_beam_obj()
    fft_obj = lst.FourierTransfWindMethod(test_ds.data_transf)

    return fft_obj


def test_fourier_transf_wind_method_pase(test_get_fft_obj):

    assert np.all(np.round(test_get_fft_obj.phase.values, 2) == 90)


def test_fourier_transf_wind_method_wind_dir(test_get_fft_obj):

    assert np.all(np.round(test_get_fft_obj.wind_dir.values, 2) == 270)


def test_fourier_transf_wind_method_rad_wind_speed(test_get_fft_obj):
    print(test_get_fft_obj.rad_wind_speed.values)
    assert np.all(
        np.round(test_get_fft_obj.rad_wind_speed.values, 2)
        == np.round(1 / np.sin(np.deg2rad(45)), 2)
    )


def test_fourier_transf_wind_method_hor_wind_speed(test_get_fft_obj):

    assert np.all(np.round(test_get_fft_obj.hor_wind_speed.values, 2) == 2)


def test_fourier_transf_wind_method_comp_u(test_get_fft_obj):

    assert np.all(np.round(test_get_fft_obj.comp_u.values, 2) == 2)


def test_fourier_transf_wind_method_comp_v(test_get_fft_obj):

    assert np.all(np.round(test_get_fft_obj.comp_v.values, 2) == 0)


def test_fourier_transf_wind_method_dim_tim(test_get_fft_obj):

    assert "time" in test_get_fft_obj.wind_prop().dims


def test_fourier_transf_wind_method_dim_range(test_get_fft_obj):

    assert "range" in test_get_fft_obj.wind_prop().dims


def test_fourier_transf_wind_method_dim_elv(test_get_fft_obj):

    assert "elv" in test_get_fft_obj.wind_prop().dims


def test_fourier_transf_wind_method_variable_wind_direction(test_get_fft_obj):

    assert "horizontal_wind_direction" in test_get_fft_obj.wind_prop()


def test_fourier_transf_wind_method_variable_wind_speed(test_get_fft_obj):

    assert "horizontal_wind_speed" in test_get_fft_obj.wind_prop()


def test_fourier_transf_wind_method_variable_zonal_wind(test_get_fft_obj):

    assert "zonal_wind" in test_get_fft_obj.wind_prop()


def test_fourier_transf_wind_method_variable_zonal_meridional(
    test_get_fft_obj,
):

    assert "meridional_wind" in test_get_fft_obj.wind_prop()
