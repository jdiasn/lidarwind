import pytest
import numpy as np
import xarray as xr

import lidarwind as lst


def get_dummy_six_beam_obj():

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
def get_wind_profiles():

    return lst.RetriveWindFFT(get_dummy_six_beam_obj())


def test_retrieve_wind_fft_dim_elv(get_wind_profiles):
    assert "elv" not in get_wind_profiles.wind_prop.dims


def test_retrieve_wind_fft_variabe_realtive_beta(get_wind_profiles):
    assert "lidar_relative_beta" in get_wind_profiles.wind_prop


def test_retrieve_wind_fft_variable_vertical_wind(get_wind_profiles):
    assert "vertical_wind_speed" in get_wind_profiles.wind_prop


def test_retrieve_wind_fft_variable_wind_direction(get_wind_profiles):
    assert "horizontal_wind_direction" in get_wind_profiles.wind_prop


def test_retrieve_wind_fft_variable_wind_speed(get_wind_profiles):
    assert "horizontal_wind_speed" in get_wind_profiles.wind_prop


def test_retrieve_wind_fft_variable_zonal_wind(get_wind_profiles):
    assert "zonal_wind" in get_wind_profiles.wind_prop


def test_retrieve_wind_fft_variable_meridional_wind(get_wind_profiles):
    assert "meridional_wind" in get_wind_profiles.wind_prop


def test_retrieve_wind_fft_relative_beta_val(get_wind_profiles):
    assert get_wind_profiles.wind_prop["lidar_relative_beta"] == 1


def test_retrieve_wind_fft_vertical_wind_val(get_wind_profiles):
    assert get_wind_profiles.wind_prop["vertical_wind_speed"] == 1


def test_retrieve_wind_fft_global_attrs(get_wind_profiles):
    assert len(get_wind_profiles.wind_prop.attrs) > 0


def test_retrieve_wind_fft_time_len(get_wind_profiles):
    assert len(get_wind_profiles.wind_prop.time) == 5


def test_retrieve_wind_fft_time90_len(get_wind_profiles):
    assert len(get_wind_profiles.wind_prop.time90) == 1


def test_retrieve_wind_fft_range_len(get_wind_profiles):
    assert len(get_wind_profiles.wind_prop.range) == 1
