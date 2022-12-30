import pytest
import numpy as np
import xarray as xr

from lidarwind.data_operator import wc_fixed_preprocessing
import lidarwind as lst

from .data import sample_dataset


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


def test_wc_fixed_preprocessing_vertical():
    """Pre-process a vertical WC dataset"""
    ds = sample_dataset("WLS200s-218_2021-05-13_12-00-14_fixed_399_50m.nc")
    # Sanity check. Is it indeed a vertical example?
    assert (ds.elevation == 90).all()

    ds = wc_fixed_preprocessing(ds)
    assert "elevation" in ds.dims


def test_wc_fixed_preprocessing_slanted():
    """Pre-process a slanted WC dataset"""
    ds = sample_dataset("WLS200s-218_2021-05-13_12-00-08_fixed_381_50m.nc")
    # Sanity check. Is it indeed a slanted example?
    assert (ds.elevation != 90).all()

    ds = wc_fixed_preprocessing(ds)
    assert "elevation" in ds.dims


def test_wc_fixed_preprocessing_without_elevation():
    """It should raise an error with a Dataset missing elevation

    It would be best to raise a specific error in wc_fixed_preprocessing().
    """
    ds = sample_dataset("WLS200s-218_2021-05-13_12-00-08_fixed_381_50m.nc")
    ds = ds.drop("elevation")

    with pytest.raises(AssertionError):
        ds = wc_fixed_preprocessing(ds)
