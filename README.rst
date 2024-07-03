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


.. note::
    Now lidarwind supports data from RPG cloud radars. If you are interested, have a look at Radar usage section.


lidarwind is an open-source Python project that retrieves wind speed and direction profiles from Doppler velocity observations recorded by Doppler-capable instruments. Initially, this package was developed to work with observations from the WindCube-200s lidar, but with this new release, lidarwind starts to support data from RPG Cloud Radars. Currently, It can retrieve wind profiles from the PPI, 6-beam and DBS scanning strategies and calculate the Reynolds stress tensor matrix elements from the 6-beam observation. The package can be further extended to process data from other Doppler lidar and radar and from other scanning strategies.

lidarwind results from an effort to create a flexible and easy-to-use package to process observations recorded by the WindCube Doppler lidar. The package development started in 2021 when I had to retrieve wind profiles from the 6-beam observations.


--------
Citation
--------

If you use lidarwind, or replicate part of it, in your work/package, please consider including the reference:

Neto, J. D. and Castelão, G. P., (2023). lidarwind: A Python package for retrieving wind profiles from Doppler lidar observations. Journal of Open Source Software, 8(82), 4852, https://doi.org/10.21105/joss.04852

::

  @article{Neto2023,
  doi = {10.21105/joss.04852},
  url = {https://doi.org/10.21105/joss.04852},
  year = {2023}, publisher = {Journal of Open Source Software},
  volume = {8}, number = {82}, pages = {4852},
  author = {José Dias Neto and Guilherme P. Castelao},
  title = {lidarwind: A Python package for retrieving wind profiles from Doppler lidar observations},
  journal = {Journal of Open Source Software}
  }



-------------
Documentation
-------------

The lidarwind's documentation is available at https://lidarwind.readthedocs.io. There you can find the steps needed for installing the package. You can also find a short description of how lidarwind derives the wind speed and direction from observations.


Notebooks
=========

An introductory set of rendered notebooks are available at https://nbviewer.org/github/jdiasn/lidarwind/tree/main/docs/examples/ or at https://github.com/jdiasn/lidarwind/tree/main/docs/examples. If you want to try the package without installing it locally, click on the binder badge above. You will be redirected to a virtual environment where you can also access the same notebooks and test the package.

.. warning::

    Beware that between versions 0.1.6 and 0.2.0, the package underwent significant refactoring. Now the classes' names
    follow the Pascal case, while module names, functions and attributes follow the snake case. Codes developed using the previous
    version will need revision.
