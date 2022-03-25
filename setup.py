#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages


setup(
    include_package_data=True,
    packages=find_packages(include=["lidarSuit", "lidarSuit.*"]),
    zip_safe=False,
)
