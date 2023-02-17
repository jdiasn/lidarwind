#!/usr/bin/env python

"""The setup script."""

from setuptools import find_packages, setup

setup(
    include_package_data=True,
    packages=find_packages(include=["lidarwind", "lidarwind.*"]),
    zip_safe=False,
)
