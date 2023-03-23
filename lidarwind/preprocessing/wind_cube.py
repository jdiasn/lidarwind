import xarray as xr


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

def wc_set_new_coordinates(ds: xr.Dataset):
    
    """New coords azimuth and elevation
    
    This function defines azimuth and elevations as 
    new coordinates.
    
    Parameters
    ----------
    ds : xr.Dataset
        A dataset containing the WindCube's observations
        
    Returns
    -------
    ds : xr.Dataset
        The same dataset, but the azimuth and elevation are defined as 
        new coordinates.
    
    """

    assert "elevation" in ds
    assert "azimuth" in ds

    ds = ds.set_coords("elevation")
    ds = ds.set_coords("azimuth")
    
    return ds 

def wc_set_time_dim_to_dimless_var(ds: xr.Dataset):
    
    """Time as new dim
    
    This function adds time as a new dimension to 
    dimensionless variables.
    
    Parameters
    ----------
    ds : xr.Dataset 
        A dataset containing the WindCube's observations
    
    Returns
    -------
    ds : xr.Dataset
        The same dataset, but all variables have time 
        as a dimension
    
    """
        
    assert "time" in ds
    
    for variable in ds.variables:
        if len(ds[variable].dims) == 0:
            ds[variable] = ds[variable].expand_dims("time")
            
    return ds

def wc_replace_dim_range_by_gate_index(ds: xr.Dataset):
    
    """Defines gate_index vertical dim
    
    This function drops the range as vertical dimension
    and defines gate_index as new vertical dimension
    
    Parameters
    ----------
    ds : xr.Dataset
        A dataset containing the WindCube's observations
        
    Returns
    -------
    ds : xr.Dataset
        A dataset set with gate_index as vertical dimension
    
    """

    tmp_gate_index = ds.gate_index.copy()
    tmp_range = ds.range.copy()

    ds = ds.drop('gate_index')
    ds = ds.rename({'range':'gate_index'})
    ds = ds.assign_coords({'gate_index':tmp_gate_index.values})
    
    new_range = tmp_range.rename({'range':'gate_index'})
    new_range = new_range.assign_coords({'gate_index':tmp_gate_index.values})
    new_range = new_range.expand_dims({'time':ds.time.values})
    
    ds['ramge'] = new_range
    ds['gate_index'].attrs = tmp_gate_index.attrs
    

    return ds