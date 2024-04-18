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


def test_update_structure_ds():

    with pytest.raises(TypeError):
        rpg_radar.update_structure(ds=np.array([1, 2]))


def test_update_structure_time():

    with pytest.raises(AssertionError):
        rpg_radar.update_structure(
            ds=xr.Dataset(
                {
                    "azimuth": [0],
                    "elevation": [0],
                    "mean_time": [0],
                    "nan_percentual": [0],
                }
            )
        )


def test_update_structure_azimuth():

    with pytest.raises(AssertionError):
        rpg_radar.update_structure(
            ds=xr.Dataset(
                {
                    "time": [0],
                    "elevation": [0],
                    "mean_time": [0],
                    "nan_percentual": [0],
                }
            )
        )


def test_update_structure_elevation():

    with pytest.raises(AssertionError):
        rpg_radar.update_structure(
            ds=xr.Dataset(
                {
                    "time": [0],
                    "azimuth": [0],
                    "mean_time": [0],
                    "nan_percentual": [0],
                }
            )
        )


def test_update_structure_nan_percentual():

    with pytest.raises(AssertionError):
        rpg_radar.update_structure(
            ds=xr.Dataset(
                {
                    "time": [0],
                    "azimuth": [0],
                    "elevation": [0],
                    "mean_time": [0],
                }
            )
        )


def test_get_chirp_information_ds():

    with pytest.raises(TypeError):
        rpg_radar.get_chirp_information(ds=np.array([1, 2]))


def test_get_chirp_information_chirp_dim():

    with pytest.raises(AssertionError):
        rpg_radar.get_chirp_information(ds=xr.Dataset({"range": [0]}))


def test_update_range_ds():

    with pytest.raises(TypeError):
        rpg_radar.update_range(ds=np.array([1, 2]))


def test_update_range_range():

    with pytest.raises(AssertionError):
        rpg_radar.update_range(ds=xr.Dataset({"time": [0]}))


def test_count_nan_values_ds():

    with pytest.raises(TypeError):
        rpg_radar.count_nan_values(ds=np.array([0]))


def test_count_nan_values_time():

    with pytest.raises(AssertionError):
        rpg_radar.count_nan_values(ds=xr.Dataset({"MeanVel": [0]}))


def test_count_nan_values_MeanVel():

    with pytest.raises(AssertionError):
        rpg_radar.count_nan_values(ds=xr.Dataset({"time": [0]}))


def test_azimuth_regular_grid_interp_ds():

    with pytest.raises(TypeError):
        rpg_radar.azimuth_regular_grid_interp(ds=np.array([0]))


def test_azimuth_regular_grid_interp_azm_coord():

    with pytest.raises(AssertionError):
        rpg_radar.azimuth_regular_grid_interp(ds=xr.Dataset({"time": [0]}))


def test_nan_leftover_to_mean_ds():

    with pytest.raises(TypeError):
        rpg_radar.nan_leftover_to_mean(ds=np.array([1]))


def test_nan_leftover_to_mean_azimuth():

    with pytest.raises(AssertionError):
        rpg_radar.nan_leftover_to_mean(ds=xr.Dataset({"MeanVel": [0]}))


def test_nan_leftover_to_mean_meanvel():

    with pytest.raises(AssertionError):
        rpg_radar.nan_leftover_to_mean(ds=xr.Dataset({"azimuth": [0]}))


def test_rpg_slanted_radial_velocity_4_fft_ds():

    with pytest.raises(TypeError):
        rpg_radar.rpg_slanted_radial_velocity_4_fft(ds=np.array([0]))
