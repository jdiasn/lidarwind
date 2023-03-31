import xarray as xr

from lidarwind.io import open_sweep

def wc_azimuth_correction(ds: xr.Dataset, azimuth_resolution: int = 1):
    
    """Removal of 360 deg ambiguity 
    
    This function corrects the azimuth ambiguity issue. 
    It replaces the 360 azimuth value with 0.
    
    Parameters
    ----------
    ds : xr.Dataset
        A dataset containing the WindCube's observations
    
    Returns
    -------
    ds : xr.Dataset
        The same dataset, but the azimuth is corrected for the ambiguity 
    
    """
    
    assert "azimuth" in ds
    assert ds["azimuth"].dims == ("time",)
    
    ds["azimuth"] = ds["azimuth"].round(azimuth_resolution)
    # Avoid ambiguity on 360 degrees
    ds["azimuth"] = ds["azimuth"].where(ds.azimuth != 360, 0)
    
    return ds

def wc_fixed_files_restruc_dataset(ds: xr.Dataset):
    
    """Restructuring fixed type files
    
    This function restructures the WindCube fixed 
    file type; it is needed to allow the merging 
    of several fixed-type files. The function starts 
    by swapping the range dimension with the gate_index. 
    Then, the time dimension is added to the variables 
    that do not have it. After that, elevation, azimuth 
    and range are defined as new coordinates. 
    
    Parameters
    ----------
    ds : xr.Dataset
        A dataset from the WindCube's fixed file type
    
    Returns
    -------
    ds : xr.Dataset
        The same dataset, but restructured for merging. 
    
    """
    
    
    if not isinstance(ds, xr.Dataset):
        raise TypeError
    
    assert "time" in ds
    assert "range" in ds
    assert "azimuth" in ds
    assert "elevation" in ds
    assert "gate_index" in ds

    ds["gate_index"] = ds['gate_index'].astype("i")
    ds = ds.swap_dims({'range':'gate_index'}).reset_coords()

    tmp_no_time = ds[[v for v in ds.variables if "time" not in ds[v].dims]].expand_dims('time')
    tmp_time = ds[[v for v in ds.variables if "time" in ds[v].dims]]

    ds = xr.merge([tmp_no_time, tmp_time])
    ds = ds.set_coords(["elevation", "azimuth", "range"])
    
    return ds

def wc_fixed_merge_files(file_names: list):
    
    """Merging fixed type files
    
    This function merges multiple fixed files into a single dataset.
    
    Parameters
    ----------
    file_names : list  
        A list of fixed files to be merged
    
    Returns
    -------
    ds : xr.Dataset
        A dataset containing data from all files specified 
        in the file_names list
    
    """
    

    if bool(file_names) is False:
        raise FileNotFoundError
    
    ds = xr.merge([wc_fixed_files_restruc_dataset(open_sweep(file)) for file in file_names])
    
    return ds