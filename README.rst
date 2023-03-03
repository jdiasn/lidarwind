======================
lidarwind introduction
======================

.. image:: https://joss.theoj.org/papers/28430a0c6a79e6d1ff33579ff13458f7/status.svg
   :target: https://doi.org/10.21105/joss.04852

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7026548.svg
   :target: https://doi.org/10.5281/zenodo.7026548

.. image:: https://readthedocs.org/projects/lidarwind/badge/?version=latest
    :target: https://lidarwind.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://mybinder.org/badge_logo.svg
   :target: https://mybinder.org/v2/gh/jdiasn/lidarwind/main?labpath=docs%2Fexamples

.. image:: https://img.shields.io/pypi/v/lidarwind.svg
   :target: https://pypi.python.org/pypi/lidarwind/

.. image:: https://codecov.io/gh/jdiasn/lidarwind/branch/main/graph/badge.svg?token=CEZM17YY3I
   :target: https://codecov.io/gh/jdiasn/lidarwind

lidarwind is an open-source Python project to retrieve wind speed and direction profiles from Doppler lidar observations from the WindCube-200s, and it was developed to be easy to use. It can retrieve wind profiles from the 6-beam and DBS scanning strategies and allow users to set the signal-to-noise ratio threshold to reduce the noise. It also calculates the Reynolds stress tensor matrix elements from the 6-beam observations.

lidarwind is a result of an effort to create an environment where it would be flexible and easy to process the observations from the WindCube Doppler lidar. Its development started in 2021 when I had to retrieve wind profiles from the 6-beam observations.

This current version focuses on the WindCube's observations, and the wind retrievals are dedicated to the 6-beam and DBS observations. However, it can be expanded to other Doppler lidar observations and scanning strategies.


-------------
Documentation
-------------

The lidarwind's documentation is available at https://lidarwind.readthedocs.io. There you can find the steps needed for installing the package. You can also find a short description of how the lidar wind derives the wind speed and direction from WindCube's observations.


Notebooks
=========

An introductory set of rendered notebooks are available at https://nbviewer.org/github/jdiasn/lidarwind/tree/main/docs/examples/ or at https://github.com/jdiasn/lidarwind/tree/main/docs/examples. If you want to try the package without installing it locally, click on the binder badge above. You will be redirected to a virtual environment where you can also access the same notebooks and test the package.

.. warning::

    Beware that between versions 0.1.6 and 0.2.0, the package underwent significant refactoring. Now the classes' names
    follow the Pascal case, while module names, functions and attributes follow the snake case. Codes developed using the previous
    version will need revision.
    
--------
Citation
--------

If you use lidarwind, or replicate part of it, in your work/package, please consider including the reference:

Neto, J. D. and Castelão, G. P., (2023). lidarwind: A Python package for retrieving wind profiles from Doppler lidar observations. Journal of Open Source Software, 8(82), 4852, https://doi.org/10.21105/joss.04852

::

  @article{Neto2023,
  doi = {10.21105/joss.04852},
  url = {https://doi.org/10.21105/joss.04852},
  year = {2023}, publisher = {The Open Journal},
  volume = {8}, number = {82}, pages = {4852},
  author = {José Dias Neto and Guilherme P. Castelao},
  title = {lidarwind: A Python package for retrieving wind profiles from Doppler lidar observations},
  journal = {Journal of Open Source Software}
  }