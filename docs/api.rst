.. currentmodule:: lidarSuit

#############
API reference
#############

The public API resources are listed below.

Data Manager
============

.. autosummary::
   :toctree: _autosummary
   
   dataOperator.dataOperations
   dataOperator.dbsOperations
   dataOperator.readProcessedData
   dataOperator.getRestructuredData

Data Attributes
===============

.. autosummary::
   :toctree: _autosummary/

   dataAttributesL1.loadAttributes

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

