---
title: 'A Framework to Quality Control Oceanographic Data'

tags:
  - Python
  - meteorology
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

Wind is one of the essential components of the atmospheric system. For example, it modulates the precipitation on larger scales, transports moisture and heat, and contributes to dispersing aerosols. Due to the urgent need to replace fossil fuel-based power plants with systems based on renewable energy sources, the wind has become one of the primary energy sources. Understanding how the wind blows at a given place became imperative, whether for improving Numerical weather prediction models or for planning wind farms. However, the number of currently available wind observations is still reduced, and most of the available observations are from radiosondes or meteorological towers (met-towers). Those observational systems are restricted to a particular time (radiosondes) or height (met-towers). Wind lidars have been used to minimise those limitations, allowing monitoring of wind constantly from near the surface up to, for example,  5 km.  

Several wind lidars are currently available on the market, but for some of them, the software for retrieving horizontal wind profiles is proprietary and with predefined scanning strategies (e.g. DBS, VAD, [@lhermitte1962; @eberhard1989]). Whenever the lidar is to scan in a non-predefined strategy (e.g. 6beam, [@sathe2015]), the retrievals of horizontal wind profiles are unavailable in the proprietary software.

# Statement of need 


lidarSuit is a python package that allows retrieving horizontal wind speed and direction profiles from the non-predefined scanning strategy (e.g. 6beam), and it also includes routines to process files from the standard Doppler beam swing strategy. This package was initially developed for retrieving wind profiles from the WindCube's NetCDF files output, but it can be extended to other lidar's NetCDF output. lidarSuit reproduces the data filtering based on WindCube's manual [@windcube2020] and allows the user to define the signal-to-noise ratio threshold for filtering noise data. In addition, it was developed to be easy to use and flexible, allowing it to be used operationally to retrieve continuously wind profiles. Thanks to its flexibility, this package has been used for processing WindCube's data from the CMTRACE experiment [@diasneto2022a].


# Acknowledgements

This publication is part of the NWO Talent Scheme Vidi project CMTRACE with project number 192.050, financed by the Dutch Research Council (NWO). 


# References
