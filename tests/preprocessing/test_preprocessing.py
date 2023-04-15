import numpy as np
import pytest

import lidarwind
from lidarwind import preprocessing

files = lidarwind.sample_data("wc_6beam")
files = sorted(files)


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


@pytest.fixture
def test_wc_fixed_merge_files_ds_structure(file_names=files[0:6]):

    ds = preprocessing.wc_fixed_merge_files(file_names)

    assert len(ds.time) > 1
    assert len(ds.gate_index) > 1

    return ds


def test_wc_slanted_radial_velocity_4_fft_90_deg_elevation(
    test_wc_fixed_merge_files_ds_structure,
):

    ds = test_wc_fixed_merge_files_ds_structure.copy()
    ds = preprocessing.wc_azimuth_elevation_correction(ds)
    ds = ds.where(ds["elevation"] == 90, drop=True)

    with pytest.raises(ValueError):
        preprocessing.wc_slanted_radial_velocity_4_fft(ds)

    ds.close()


def test_wc_slanted_radial_velocity_4_fft_multiple_elevation(
    test_wc_fixed_merge_files_ds_structure,
):

    ds = test_wc_fixed_merge_files_ds_structure.copy()
    ds = preprocessing.wc_azimuth_elevation_correction(ds)

    with pytest.raises(TypeError):
        preprocessing.wc_slanted_radial_velocity_4_fft(ds)

    ds.close()


def test_wc_slanted_radial_velocity_4_fft_few_data(
    test_wc_fixed_merge_files_ds_structure,
):

    ds = test_wc_fixed_merge_files_ds_structure.copy()
    ds = preprocessing.wc_azimuth_elevation_correction(ds)
    unique_elevation = np.unique(ds.elevation)[np.unique(ds.elevation) != 90]
    ds = ds.where(ds.elevation == unique_elevation, drop=True)

    with pytest.raises(ValueError):
        preprocessing.wc_slanted_radial_velocity_4_fft(ds)

    ds.close()
