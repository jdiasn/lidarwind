import numpy as np
import pandas as pd
import xarray as xr

from lidarwind import postprocessing, preprocessing


def sintetic_data(step=90, elevation=75) -> xr.Dataset:
    """Sintect data

    Function to create synthetic data for testing the package

    Parameters
    ----------
    step : int
        separation in degree between the data points

    elevation : int
        elevation of the observation

    Returns
    -------
        A synthetic dataset

    """

    azimuths = np.arange(0, 360, step)

    wind = np.cos(np.deg2rad(azimuths + 0)) * 20 * np.cos(np.deg2rad(75))

    elv = np.append(np.ones_like(azimuths) * elevation, [90, 75])

    time = pd.to_datetime("11/11/2017") + pd.to_timedelta(
        np.arange(len(elv)), unit="seconds"
    )

    data_elv = xr.DataArray(elv, dims=("time"), coords={"time": time})

    azm = np.append(azimuths, [0, 0])
    data_azm = xr.DataArray(azm, dims=("time"), coords={"time": time})

    data = xr.DataArray(
        (np.ones((2, 7)) * np.append(wind, [0, wind[0]])).T,
        dims=("time", "gate_index"),
        coords={"time": time, "gate_index": [1, 2]},
    )

    ranges = xr.DataArray(
        np.ones((2, 7)).T
        * np.array([100, 150])
        / np.sin(np.deg2rad(elevation)),
        dims=("time", "gate_index"),
        coords={"time": time, "gate_index": [1, 2]},
    )

    data_status = xr.DataArray(
        np.ones_like(data.values),
        dims=("time", "gate_index"),
        coords={"time": time, "gate_index": [1, 2]},
    )

    test_ds = xr.Dataset(
        {
            "elevation": data_elv,
            "azimuth": data_azm,
            "cnr": data,
            "range": ranges,
            "radial_wind_speed": data,
            "radial_wind_speed_status": data_status,
            "relative_beta": data,
        }
    )

    test_ds = test_ds.set_coords(
        {
            "elevation": test_ds.elevation,
            "azimuth": test_ds.azimuth,
            "range": ranges,
        }
    )

    test_ds["range"].values[test_ds.elevation == 90] = np.array([100, 150])

    return test_ds


def ds_for_test():

    ds = sintetic_data(step=72, elevation=75)
    ds = preprocessing.wc_azimuth_elevation_correction(ds)
    ds = ds.where(ds.radial_wind_speed_status == 1)

    return ds


def test_post_wind_cube_get_horizontal_wind_dim_size():

    tmp_ds = postprocessing.get_horizontal_wind(ds_for_test())
    assert len(tmp_ds.dims) > 0


def test_post_wind_cube_get_horizontal_wind_time():

    tmp_ds = postprocessing.get_horizontal_wind(ds_for_test())
    assert "time" in tmp_ds.dims


def test_post_wind_cube_get_horizontal_wind_gate_index():

    tmp_ds = postprocessing.get_horizontal_wind(ds_for_test())
    assert "gate_index" in tmp_ds.dims


def test_post_wind_cube_get_horizontal_wind_coord_range():

    tmp_ds = postprocessing.get_horizontal_wind(ds_for_test())
    assert "range" in tmp_ds.coords


def test_post_wind_cube_get_horizontal_wind_coord_elevation():

    tmp_ds = postprocessing.get_horizontal_wind(ds_for_test())
    assert "elevation" in tmp_ds.coords


def test_post_wind_cube_get_horizontal_wind_coord_azimuth():

    tmp_ds = postprocessing.get_horizontal_wind(ds_for_test())
    assert "azimuth" in tmp_ds.coords


def test_post_wind_cube_get_horizontal_wind_speed():

    tmp_ds = postprocessing.get_horizontal_wind(ds_for_test())
    assert "horizontal_wind_speed" in tmp_ds.variables


def test_post_wind_cube_get_horizontal_wind_direction():

    tmp_ds = postprocessing.get_horizontal_wind(ds_for_test())
    assert "horizontal_wind_direction" in tmp_ds.variables


def test_post_wind_cube_get_horizontal_wind_zonal():

    tmp_ds = postprocessing.get_horizontal_wind(ds_for_test())
    assert "zonal_wind" in tmp_ds.variables


def test_post_wind_cube_get_horizontal_wind_meridional():

    tmp_ds = postprocessing.get_horizontal_wind(ds_for_test())
    assert "meridional_wind" in tmp_ds.variables
