---
title: 'lidarwind: A Python package for retrieving wind profiles from Doppler lidar observations'

tags:
  - Python
  - meteorology
  - Doppler wind lidar
  - lidar remote sensing
  - wind profile retrievals

authors:
  - name: José Dias Neto
    orcid: 0000-0002-8488-8486
    affiliation: 1

  - name: Guilherme P. Castelao
    orcid: 0000-0002-6765-0708
    affiliation: 2 # (Multiple affiliations must be quoted)

affiliations:
 - name: Delft University of Technology
   index: 1

 - name: Scripps Institution of Oceanography
   index: 2

date: 4 August 2022
bibliography: paper.bib
---


# Summary

Wind is one of the essential components of the atmospheric system, modulating precipitation on larger scales,
transporting moisture and heat, and contributing to dispersing aerosols. Due to the urgent need to replace
fossil fuel-based power plants with systems based on renewable energy sources, wind has become one of
the primary energy sources. Understanding wind variability is imperative for improving numerical weather
prediction models and for planning wind farms. However, the number of currently available wind observations
is still limited, and most of the available observations are from radiosondes or meteorological towers (met-towers).
Those observational systems are restricted to a particular time (radiosondes) or height (met-towers).
Wind lidar has been used to minimise those limitations, allowing monitoring of wind constantly from near
the surface up to, for example, 5 km.

Several wind lidar models are commercially available, but their operating software is often proprietary.
Although different scanning strategies for retrieving wind exist, for example, the  Doppler beam swing
[DBS, [@vanZandt2000]], the velocity azimuth display [VAD,  [@lhermitte1962; @eberhard1989]] and the
6-beam introduced by [@sathe2015] most of the lidar operating software provides horizontal wind speed
and direction profile retrievals for the DBS and VAD scanning strategies. However, the retrievals of
horizontal wind profiles are unavailable if the lidar is set to scan using the 6-beam strategy. In addition,
in the case of the WindCube 200s, the different scanning strategies also generate NetCDF files with
different structures.

# Statement of need

lidarwind is a Python package for retrieving horizontal wind speed and direction profiles from the
6-beam scanning strategy but also includes routines for retrieving wind profiles from the DBS. This
package was developed for retrieving wind profiles from WindCube's NetCDF output, but it can be
extended to process NetCDF [@rew1990] output from other Doppler lidar systems. lidarwind reproduces the data
filtering described in WindCube's manual [@windcube2020] and allows the user to define the signal-to-noise
ratio threshold for filtering noisy measurements or using the status variable. In addition, two experimental
filters to minimise the presence of second trip echoes on the observations are included in the package.


lidarwind was developed to be easy to use and flexible, allowing it to be used operationally to retrieve
wind profiles continuously. With this package, the user can read and merge a list of WindCube's files
and choose to retrieve wind using the DBS or the 6-beam dedicated modules. In particular, for the 6-beam
observations,  the wind is retrieved using the Fast Fourier Wind Vector Algorithm [@Ishwardat2017]. Since
the 6-beam strategy is idealised for studying turbulence, lidarwind also contains a module for calculating
the Reynolds stress tensor according to the methodology introduced by @sathe2015. lidarwind also includes
a basic visualisation module, allowing a quick inspection of the retrieved wind speed and direction profiles.
Thanks to its flexibility, this package was used to process WindCube's data from The Tracing Convective
Momentum Transport in Complex Cloudy Atmospheres Experiment [@diasneto2022a].


# Visualizing the 6-beam retrieved wind


As an example of the usage of this package, the vertical wind speed measured by the WindCube and the
horizontal wind speed and direction retrieved using the Fast Fourier Wind Vector Algorithm are shown
in panels a, b, and c from \autoref{fig:wind_panel}.


![Time-height plots of the vertical wind speed (a), horizontal wind speed (b), and horizontal wind
direction (c) derived from the 6-beam observations.\label{fig:wind_panel}](wind_panel.png)


Panel a, in the lowest 2 km, reveals the daily evolution of the vertical wind. Before 9:00 UTC and after 17:00 UTC,
the measured vertical wind is mainly 0 m/s, indicating the stable period of the atmospheric boundary layer.
Between 9:00 UTC and 17:00 UTC, the range of the vertical velocities increases, spaning values between -1 and 1 m/s,
which indicates the formation of the turbulent layer, also known as the mixing layer [@Stull2003].
Panel a also shows a measurement gap between 3 UTC and  8 UTC. This gap is due to the absence of a
backscattered signal caused by the extremely low amount of lidar scatterers in the atmosphere [aerosol].
Panel b, in the lowest 2 km, shows that for the whole day, the magnitude of the horizontal wind is mainly
distributed between 0 and 10 m/s. This panel also reveals variabilities in the magnitude of the horizontal
wind related to the presence of different temporal scales. During the stable period, the scales of the
horizontal wind variability seem to be in the order of hours, while during the turbulent period, the temporal
scales are in the order of minutes. In the lowest 2 km from panel c, the wind direction indicates a wind
rotation along the day. Before 2 UTC, the wind is from the southeast; around 12:00 UTC, the wind is from
the southwest; later, after 20:00 UTC, the wind is from the northwest. Similar to that noticed for the two
previous variables, the wind direction indicates the presence of small-scale variabilities during the
turbulent period. In contrast, during the stable period, the change in direction is only apparent between
different heights (e.g. near the surface and around 1000 m).


Above 2000 m, all three variables suggest that the lidar was able to obtain observations from within the clouds.
Even though the observations are from clouds, their heights are wrong. This mispositioning of those clouds is
related to the WindCube operating settings used during the measurements. A methodology for removing those wrong
clouds, introduced in [@diasneto2022b], is also available in this package, but ceilometer observations are required for applying it.



# Acknowledgements

This publication is part of the NWO Talent Scheme Vidi project CMTRACE with project number 192.050,
financed by the Dutch Research Council (NWO). The authors thank Steven Knoop for suggesting improvements
to the code.


# References
