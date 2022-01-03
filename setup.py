#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

test_requirements = ['pytest>=3', ]

setup(
    author="Jose Dias",
    author_email='jdiasn@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="LIDAR procedures",
    entry_points={
        'console_scripts': [
            'lidarSuit=lidarSuit.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='lidarSuit',
    name='lidarSuit',
    packages=find_packages(include=['lidarSuit', 'lidarSuit.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/jdiasn/lidarSuit',
    version='0.0.1',
    zip_safe=False,
)
