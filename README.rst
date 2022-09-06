=========
lidarSuit
=========

.. image:: https://zenodo.org/badge/355915578.svg
   :target: https://zenodo.org/badge/latestdoi/355915578

.. image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/jdiasn/lidarSuit/main?labpath=docs%2Fnotebooks

.. image:: https://readthedocs.org/projects/lidarsuit/badge/?version=latest
    :target: https://lidarsuit.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/lidarSuit.svg
   :target: https://pypi.python.org/pypi/lidarSuit/

lidarSuit is an open-source python project to retrieve wind speed and direction profiles from Doppler lidar observations from the WindCube-200s, and it was developed to be easy to use. It can retrieve wind profiles from the 6-beam and DBS scanning strategies and allow users to set the signal-to-noise ratio threshold to reduce the noise. It also calculates the Reynolds stress tensor matrix elements from the 6-beam observations.

luidarSuit is a result of an effort to create an environment where it would be flexible and easy to process the observations from the WindCube Doppler lidar. Its development started in 2021 when I had to retrieve wind profiles from the 6-beam observations.

This current version focuses on the WindCube's observations, and the wind retrievals are dedicated to the 6-bean and DBS observations. However, it can be expanded to other Doppler lidar observations and scanning strategies.


=============
Documentation
=============

The lidarSuit's documentation is available at https://lidarsuit.readthedocs.io, and an introductory set of notebooks are available at https://nbviewer.org/github/jdiasn/lidarSuit/tree/main/docs/notebooks/.


==========
Suggestion
==========

If you want to try using this package without instaling first, you can do it by clicking on the binder badge.