import pytest
import numpy as np
import xarray as xr

import lidarSuit as lst


def test_dataOperator_dataOperations_dataPaths():

    with pytest.raises(FileNotFoundError):
        lst.dataOperations(dataPaths=None)


def test_dataOperator_readProcessedData_file_list():

    with pytest.raises(FileNotFoundError):
        lst.readProcessedData(file_list=None)


def test_dataOperator_GetRestructuredData_data():

    with pytest.raises(TypeError):
        lst.GetRestructuredData(data=xr.DataArray(np.array([0, 1])))


def test_dataOperator_getResampled_xr_data_array_none():

    with pytest.raises(TypeError):
        lst.GetResampledData(xr_data_array=np.array([0, 1]))


def test_dataOperator_DbsOperations_file_list_none():

    with pytest.raises(FileNotFoundError):
        lst.DbsOperations(file_list=None, var_list=["range"])


def test_dataOperator_DbsOperations_varList_none():

    with pytest.raises(KeyError):
        lst.DbsOperations(file_list=["file_path"], var_list=None)
