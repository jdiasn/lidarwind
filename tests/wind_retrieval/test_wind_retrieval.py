import numpy as np
import pandas as pd
import xarray as xr

from lidarwind import preprocessing
from lidarwind.wind_retrieval import fft_wind_retrieval


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


def get_radial_velocities_4_test():

    ds = sintetic_data(step=72, elevation=75)
    slanted_elevation = np.unique(ds.elevation)[np.unique(ds.elevation) != 90]
    ds_slanted = ds.where(ds.elevation == slanted_elevation, drop=True)
    radial_velocities = preprocessing.wc_slanted_radial_velocity_4_fft(
        ds_slanted
    )

    return radial_velocities


def test_fisrt_harmonic_amplitude_size():

    tmp_amp = fft_wind_retrieval.first_harmonic_amplitude(
        get_radial_velocities_4_test().radial_wind_speed
    )
    assert tmp_amp.size > 0


def test_first_harmonic_amplitude_magnitude():

    tmp_amp = fft_wind_retrieval.first_harmonic_amplitude(
        get_radial_velocities_4_test().radial_wind_speed
    )
    assert np.round(np.absolute(tmp_amp.values[1, 1]), 2) == 12.94


def test_first_harmonic_amplitude_direction():

    tmp_amp = fft_wind_retrieval.first_harmonic_amplitude(
        get_radial_velocities_4_test().radial_wind_speed
    )
    assert fft_wind_retrieval.wind_direction(tmp_amp).values[1, 1] == 180


def test_first_harmonic_amplitude_wind_speed():

    tmp_amp = fft_wind_retrieval.first_harmonic_amplitude(
        get_radial_velocities_4_test().radial_wind_speed
    )
    assert np.isclose(fft_wind_retrieval.wind_speed(tmp_amp).values[1, 1], 20)


def test_first_harmonic_amplitude_meridional_wind():

    tmp_amp = fft_wind_retrieval.first_harmonic_amplitude(
        get_radial_velocities_4_test().radial_wind_speed
    )
    assert np.isclose(
        fft_wind_retrieval.meridional_wind(tmp_amp).values[1, 1], 20
    )


def test_first_harmonic_amplitude_zonal_wind():

    tmp_amp = fft_wind_retrieval.first_harmonic_amplitude(
        get_radial_velocities_4_test().radial_wind_speed
    )
    assert np.isclose(fft_wind_retrieval.zonal_wind(tmp_amp).values[1, 1], 0)


def test_first_harmonic_amplitude_projected_wind():

    tmp_amp = fft_wind_retrieval.first_harmonic_amplitude(
        get_radial_velocities_4_test().radial_wind_speed
    )
    assert np.isclose(
        fft_wind_retrieval.wind_projected_to_azimuth(tmp_amp, 0).values[1, 1],
        -20,
    )


def test_first_harmonic_amplitude_horizontal_wind_speed_var():

    tmp_ds = fft_wind_retrieval.get_wind_properties(
        get_radial_velocities_4_test().radial_wind_speed
    )
    assert "horizontal_wind_speed" in tmp_ds


def test_first_harmonic_amplitude_horizontal_wind_dir_var():

    tmp_ds = fft_wind_retrieval.get_wind_properties(
        get_radial_velocities_4_test().radial_wind_speed
    )
    assert "horizontal_wind_direction" in tmp_ds


def test_first_harmonic_amplitude_meridional_wind_dir_var():

    tmp_ds = fft_wind_retrieval.get_wind_properties(
        get_radial_velocities_4_test().radial_wind_speed
    )
    assert "meridional_wind" in tmp_ds


def test_first_harmonic_amplitude_zonal_wind_dir_var():

    tmp_ds = fft_wind_retrieval.get_wind_properties(
        get_radial_velocities_4_test().radial_wind_speed
    )
    assert "zonal_wind" in tmp_ds
