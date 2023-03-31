import pytest
import numpy as np

import lidarwind
from lidarwind import preprocessing

files = lidarwind.sample_data("wc_6beam")
files = sorted(files)

        
def test_wc_fixed_files_restruc_dataset_ds_type():
    
    with pytest.raises(TypeError):
        preprocessing.wc_fixed_files_restruc_dataset(ds=np.array([0,1]))        


def test_wc_fixed_files_restruc_dataset(file_name=files[0]):
    
    ds = lidarwind.open_sweep(file_name)
    ds = preprocessing.wc_fixed_files_restruc_dataset(ds)
    
    assert "time" in ds.dims
    assert "gate_index" in ds.dims

    assert "azimuth" in ds.coords
    assert "elevation" in ds.coords
    assert "gate_index" in ds.coords

    assert len(ds.variables) > 0
    
    ds.close()

    
def test_wc_fixed_merge_files_empty_file_names():

    with pytest.raises(FileNotFoundError):
        preprocessing.wc_fixed_merge_files(file_names=[])
    
    
def test_wc_fixed_merge_files_ds_structure(file_names=files[0:2]):
    
    ds = preprocessing.wc_fixed_merge_files(file_names)
    
    assert len(ds.time) > 1
    assert len(ds.gate_index) > 1
    
    ds.close()