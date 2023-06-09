import numpy as np
import pytest
import xarray as xr

import lidarwind
from lidarwind import preprocessing

files = lidarwind.sample_data("wc_6beam")
files = sorted(files)


def get_sintetic_6_beam_data():

    elv = np.array([75, 75, 90, 75, 75, 75, 75])
    data_elv = xr.DataArray(
        elv, dims=("time"), coords={"time": np.arange(len(elv))}
    )

    azm = np.array([0, 72, 0, 144, 216, 288, 0])
    data_azm = xr.DataArray(
        azm, dims=("time"), coords={"time": np.arange(len(elv))}
    )

    gate = np.array([104, 104, 100, 104, 104, 104, 104])
    data_range = xr.DataArray(
        gate, dims=("time"), coords={"time": np.arange(len(elv))}
    )

    data = xr.DataArray(
        np.array([1, 1, 1, 1, 1, 1, 1])[:, np.newaxis],
        dims=("time", "gate_index"),
        coords={
            "time": np.arange(len(elv)),
            "gate_index": [1],
        },
    )

    sintetic_data = xr.Dataset(
        {
            "range": data_range,
            "elevation": data_elv,
            "azimuth": data_azm,
            "cnr": data,
            "radial_wind_speed": data,
            "radial_wind_speed_status": data,
        }
    )

    sintetic_data = sintetic_data.set_coords(["azimuth", "elevation", "range"])

    return sintetic_data


def test_wc_fixed_files_restruc_dataset_ds_type():

    with pytest.raises(TypeError):
        preprocessing.wc_fixed_files_restruc_dataset(ds=np.array([0, 1]))


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


# @pytest.fixture
def test_wc_fixed_merge_files_ds_structure(file_names=files[0:6]):

    ds = preprocessing.wc_fixed_merge_files(file_names)

    assert len(ds.time) > 1
    assert len(ds.gate_index) > 1

    ds.close()


# @pytest.mark.skip("skip 1")
def test_wc_slanted_radial_velocity_4_fft_90_deg_elevation():

    ds = get_sintetic_6_beam_data()
    ds = preprocessing.wc_azimuth_elevation_correction(ds)
    ds = ds.where(ds["elevation"] == 90, drop=True)

    assert ds["elevation"].size > 0

    with pytest.raises(ValueError):
        preprocessing.wc_slanted_radial_velocity_4_fft(ds)

    ds.close()


# @pytest.mark.skip("skip 1")
def test_wc_slanted_radial_velocity_4_fft_multiple_elevation():

    ds = get_sintetic_6_beam_data()
    ds = preprocessing.wc_azimuth_elevation_correction(ds)

    with pytest.raises(TypeError):
        preprocessing.wc_slanted_radial_velocity_4_fft(ds)

    ds.close()


# @pytest.mark.skip("skip 1")
def test_wc_slanted_radial_velocity_4_fft_few_data():

    ds = get_sintetic_6_beam_data()
    ds = preprocessing.wc_azimuth_elevation_correction(ds)
    unique_elevation = np.unique(ds.elevation)[np.unique(ds.elevation) != 90]

    with pytest.raises(ValueError):
        preprocessing.wc_slanted_radial_velocity_4_fft(
            ds.where(ds.elevation == unique_elevation, drop=True)
        )

    ds.close()
