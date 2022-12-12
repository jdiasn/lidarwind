import datatree
import pandas as pd
import xarray as xr


def open_sweep(file_name):
    """Windcube's data reader

    It opens and reads the original NetCDF output
    from the Windcube lidar.

    Parameters
    ----------

    file_name : str
        path to the file that will be opened

    Returns
    -------
    ds : xarray.DataSet

        a dataset from the original NetCDF files
    """

    raw_data = datatree.open_datatree(file_name, decode_times=False)

    assert (
        "sweep_group_name" in raw_data
    ), "missing sweep group variable in input file"
    sweep_group_name = raw_data["sweep_group_name"].values[0]
    ds = raw_data[f"/{sweep_group_name}"].to_dataset()

    assert "time_reference" in ds, "missing time_reference in input sweep"
    # Guarantee that it is a valid datetime
    reference_time = pd.to_datetime(ds["time_reference"].values).isoformat()
    ds["time"].attrs["units"] = f"seconds since {reference_time}"

    ds = xr.decode_cf(ds)

    return ds
