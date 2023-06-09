import numpy as np
import xarray as xr
import xrft


def first_harmonic_amplitude(
    radial_velocity: xr.DataArray, dim="azimuth"
) -> xr.DataArray:
    """First harmonic amplitude

    This function calculates the complex amplitudes
    along the azimuth coordinate and returns
    the amplitude of the first harmonic.

    Parameters
    ----------
    radial_velocity : xr.DataArray
        A data array of slanted Doppler velocities

    dim : string
        Name of the azimuthal dimension

    Returns
    -------
        A data array of the amplitudes of the first harmonic

    """

    complex_amplitudes = xrft.fft(
        radial_velocity, dim=dim, true_amplitude=False
    )
    complex_amplitudes = complex_amplitudes.assign_coords(
        {f"{dim}_length": len(radial_velocity[dim])}
    )

    # determination of the first harmonic position
    # harmonic_index = int(radial_velocity[dim].size / 2) + 1
    first_harmonic_index = (
        complex_amplitudes[f"freq_{dim}"]
        .where(complex_amplitudes[f"freq_{dim}"] > 0)
        .argmin()
    )

    return complex_amplitudes.isel({f"freq_{dim}": first_harmonic_index})


def harmonic_phase(amplitude: xr.DataArray) -> xr.DataArray:
    """First harmonic phase

    It calculates the phase of a given complex harmonic amplitude.

    Parameters
    ----------
    amplitude : xr.DataArray
        A data array of complex amplitudes from a given harmonic

    Returns
    -------
        harmonic phase

    """

    phase = np.rad2deg(np.arctan2(amplitude.imag, amplitude.real))

    return phase


def wind_direction(amplitude: xr.DataArray) -> xr.DataArray:
    """wind direction

    It calculates the wind direction of a given complex harmonic amplitude.

    Parameters
    ----------
    amplitude : xr.DataArray
        A data array of complex amplitudes from a given harmonic

    Returns
    -------
        The wind direction

    """

    wind_direction = -harmonic_phase(amplitude) + 180

    return wind_direction


def wind_speed(
    amplitude: xr.DataArray, coord="elevation", azimuth_name="azimuth"
) -> xr.DataArray:
    """Wind speed

    It calculates the wind speed using the first harmonic.

    Parameters
    ----------
    amplitude : xr.DataArray
        A data array of complex amplitudes from the first harmonic

    coord : string
        Name of the elevation coordinate


    Returns
    -------
        The wind speed

    """

    radial_wind_speed = (
        2 * np.abs(amplitude) / amplitude[f"{azimuth_name}_length"]
    )
    horizontal_wind_speed = radial_wind_speed / np.cos(
        np.deg2rad(amplitude[coord])
    )

    return horizontal_wind_speed


def wind_projected_to_azimuth(
    amplitude: xr.DataArray,
    azimuth: float,
    coord="elevation",
    azimuth_name="azimuth",
) -> xr.DataArray:
    """Wind speed from an azimuth

    It calculates the wind speed from a given azimuth.

    Parameters
    ----------
    amplitude : xr.DataArray
        A data array of complex amplitudes from the first harmonic

    azimuth : float
        Azimuth value

    coord : string
        Name of the elevation coordinate

    Returns
    -------
        The projection of the horizontal

    """

    radial_wind_speed = (
        2 * np.abs(amplitude) / amplitude[f"{azimuth_name}_length"]
    )
    projected_radial_wind = radial_wind_speed * np.cos(
        np.deg2rad(azimuth) + np.deg2rad(-harmonic_phase(amplitude) + 180)
    )
    projected_horizontal_wind = projected_radial_wind / np.cos(
        np.deg2rad(amplitude[coord])
    )

    return projected_horizontal_wind


def zonal_wind(
    amplitude: xr.DataArray, elevation_name="elevation", azimuth_name="azimuth"
) -> xr.DataArray:
    """zonal wind

    It calculates the zonal wind component.

    Parameters
    ----------
    amplitude : xr.DataArray
        A data array of complex amplitudes from the first harmonic

    Returns
    -------
        The zonal wind component

    """

    zonal_wind = (
        wind_projected_to_azimuth(
            amplitude, 90, coord=elevation_name, azimuth_name=azimuth_name
        )
        * -1
    )

    return zonal_wind


def meridional_wind(
    amplitude: xr.DataArray, elevation_name="elevation", azimuth_name="azimuth"
) -> xr.DataArray:
    """meridional wind

    It calculates the meridional wind component.

    Parameters
    ----------
    amplitude : xr.DataArray
        A data array of complex amplitudes from the first harmonic

    Returns
    -------
        The meridional wind component

    """

    meridional_wind = (
        wind_projected_to_azimuth(
            amplitude, 0, coord=elevation_name, azimuth_name=azimuth_name
        )
        * -1
    )

    return meridional_wind


def get_wind_properties(
    radial_velocity: xr.DataArray,
    elevation_name="elevation",
    azimuth_name="azimuth",
) -> xr.Dataset:
    """Wind dataset

    It retrieves the wind properties from the slanted observations.

    Parameters
    ----------
    radial_velocities : xr.DataArray
        A data array of the slanted Doppler velocities observations.

    Returns
    -------
        A dataset containing the wind speed, direction, meridional
        and zonal components

    """

    amplitude = first_harmonic_amplitude(radial_velocity, dim=azimuth_name)

    wind_properties = xr.Dataset()
    wind_properties["horizontal_wind_direction"] = wind_direction(amplitude)
    wind_properties["horizontal_wind_speed"] = wind_speed(
        amplitude, coord=elevation_name, azimuth_name=azimuth_name
    )
    wind_properties["meridional_wind"] = meridional_wind(
        amplitude, elevation_name=elevation_name, azimuth_name=azimuth_name
    )
    wind_properties["zonal_wind"] = zonal_wind(
        amplitude, elevation_name=elevation_name, azimuth_name=azimuth_name
    )

    return wind_properties
