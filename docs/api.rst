.. currentmodule:: lidarSuit

#############
API reference
#############

The public API resources are listed below.

Basic data reader
=================

.. autosummary::
    :toctree: _autosummary
    
    lidar_code.getLidarData

Data Manager
============

.. autosummary::
   :toctree: _autosummary/
   
   dataOperator.dataOperations
   dataOperator.readProcessedData
   dataOperator.getRestructuredData
   dataOperator.dbsOperations

Filters
=======

.. autosummary::
   :toctree: _autosummary/
   
   filters.filtering
   filters.secondTripEchoFilter
   filters.windCubeCloudRemoval
   
Wind Retrieval
==============

.. autosummary::
    :toctree: _autosummary/
    
    windPropRetrieval.retrieveWind
    windPropRetrieval.getWindProperties5Beam

Turbulence estimation
=====================

.. autosummary::
    :toctree: _autosummary/

    windPropRetrieval6Beam.sixBeamMethod
    
Data Attributes
===============

.. autosummary::
   :toctree: _autosummary/

   dataAttributesL1.loadAttributes
   
Global Attributes Definitions
=============================

.. autosummary::
   :toctree: _autosummary/
   
   lstConfig.configurations