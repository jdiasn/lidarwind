import numpy as np

from lidarwind import preprocessing
from lidarwind.synthetic_data import wc_synthetic_data
from lidarwind.wind_retrieval import fft_wind_retrieval


def get_radial_velocities_4_test():

    ds = wc_synthetic_data.synthetic_data(step=72, elevation=75)
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
