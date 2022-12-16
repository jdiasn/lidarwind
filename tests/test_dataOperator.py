import pytest
import numpy as np
import xarray as xr

import lidarSuit as lst


def test_data_operator_DataOperations_data_paths():

    with pytest.raises(FileNotFoundError):
        lst.DataOperations(data_paths=None)


def test_data_operator_ReadProcessedData_file_list():

    with pytest.raises(FileNotFoundError):
        lst.ReadProcessedData(file_list=None)


def test_data_operator_GetRestructuredData_data():

    with pytest.raises(TypeError):
        lst.GetRestructuredData(data=xr.DataArray(np.array([0, 1])))


def test_data_operator_getResampled_xr_data_array_none():

    with pytest.raises(TypeError):
        lst.GetResampledData(xr_data_array=np.array([0, 1]))


def test_data_operator_DbsOperations_file_list_none():

    with pytest.raises(FileNotFoundError):
        lst.DbsOperations(file_list=None, var_list=["range"])


def test_data_operator_DbsOperations_varList_none():

    with pytest.raises(KeyError):
        lst.DbsOperations(file_list=["file_path"], var_list=None)
