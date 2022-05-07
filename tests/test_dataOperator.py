import pytest
import numpy as np
import xarray as xr

import lidarSuit as lst

def test_dataOperator_dataOperations_dataPaths():

    with pytest.raises(FileNotFoundError):
        lst.dataOperations(dataPaths=None)


def test_dataOperator_readProcessedData_fileList():

    with pytest.raises(FileNotFoundError):
        lst.readProcessedData(fileList=None)


def test_dataOperator_getRestructuredData_data():

    with pytest.raises(TypeError):
        lst.getRestructuredData(data=xr.DataArray(np.array([0,1])))

def test_dataOperator_getResampled_xrDataArray_none():

    with pytest.raises(TypeError):
        lst.getResampledData(xrDataArray=np.array([0,1]))


def test_dataOperator_dbsOperations_fileList_none():

    with pytest.raises(FileNotFoundError):
        lst.dbsOperations(fileList=None, varList=['range'])

def test_dataOperator_dbsOperations_varList_none():

    with pytest.raises(KeyError):
        lst.dbsOperations(fileList=['file_path'], varList=None)