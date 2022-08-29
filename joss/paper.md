---
title: 'lidarSuit: A python package for retrieving wind profiles from Doppler lidar observations'

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
fossil fuel-based power plants with systems based on renewable energy sources, the wind has become one of
the primary energy sources. Understanding wind variability is imperative for improving numerical weather
prediction models and for planning wind farms. However, the number of currently available wind observations
is still limited, and most of the available observations are from radiosondes or meteorological towers (met-towers).
Those observational systems are restricted to a particular time (radiosondes) or height (met-towers).
Wind lidars have been used to minimise those limitations, allowing monitoring of wind constantly from near
the surface up to, for example, 5 km.

Several wind lidar models are commercially available, but their operating software is often proprietary.
Although different scanning strategies for retrieving wind exist, for example, the  Doppler beam swing
(DBS, [@vanZandt2000]), the velocity azimuth display (VAD,  [@lhermitte1962; @eberhard1989]) and the
6-beam introduced by [@sathe2015] most of the lidar operating software provides horizontal wind speed
and direction profile retrievals for the DBS and VAD scanning strategies. However, the retrievals of
horizontal wind profiles are unavailable if the lidar is set to scan using the 6-beam strategy. In addition,
in the case of the WindCube 200s, the different scanning strategies also generate NetCDF files with
different structures.

# Statement of need

lidarSuit is a python package for retrieving horizontal wind speed and direction profiles from the
6-beam scanning strategy but also includes routines for retrieving wind profiles from the DBS. This
package was developed for retrieving wind profiles from WindCube's NetCDF files output, but it can be
extended to process NetCDF output from other Doppler lidar systems. lidarSuit reproduces the data
filtering described in WindCube's manual [@windcube2020] and allows the user to define the signal-to-noise
ratio threshold for filtering noisy measurements or using the status variable. In addition, two experimental
filters to minimise the presence of second trip echoes on the observations are included in the package.


lidarSuit was developed to be easy to use and flexible, allowing it to be used operationally to retrieve
wind profiles continuously. With this package, the user can read and merge a list of WindCube's files
and choose to retrieve wind using the DBS or the 6-beam dedicated modules. In particular, for the 6-beam
observations,  the wind is retrieved using the Fast Fourier Wind Vector Algorithm [@Ishwardat2017]. Since
the 6-beam strategy is idealised for studying turbulence, lidarSuit also contains a module for calculating
the Reynolds stress tensor according to the methodology introduced by @sathe2015. lidarSuit also includes
a basic visualisation module, allowing a quick inspection of the retrieved wind speed and direction profiles.
Thanks to its flexibility, this package was used to process WindCube's data from The Tracing Convective
Momentum Transport in Complex Cloudy Atmospheres Experiment [@diasneto2022a]. In the future, a module for
estimating the Reynolds stress tensor for the VAD and DBS will be added, and a compatibility module
allowing wind retrievals from other wind Doppler lidars.


# Acknowledgements

This publication is part of the NWO Talent Scheme Vidi project CMTRACE with project number 192.050,
financed by the Dutch Research Council (NWO). The authors thank Steven Knoop for suggesting improvements
to the code.


# References
