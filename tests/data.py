import os
import shutil
import glob
from typing import Optional

import pytest
import gdown

from lidarwind.io import open_sweep

GDRIVE_ID = "1i6iX6KuZOkP_WLuPZHG5uCcvRjlWS-SU"


def lidarwindrc(subdir: Optional[str] = None):
    """Standard path for Lidar Suit configurations

    This might be moved into lidarwind.utils if used somewhere else
    """
    path = os.getenv("LIDARWIND_DIR", os.path.join("~", ".lidarwindrc"))
    path = os.path.expanduser(path)

    if subdir is not None:
        path = os.path.join(path, subdir)

    return path


def get_sample_data(sample_path, file_type):

    if file_type == "12-00":
        url = f"https://drive.google.com/uc?export=download&id={GDRIVE_ID}"

    if file_type == "dbs":
        url = "path"

    output = f"{sample_path}{file_type}.zip"
    gdown.download(url, output, quiet=False)

    print(f"Extracting: {output}")
    shutil.unpack_archive(output, sample_path)
    os.remove(output)


def download_samples():
    file_type = "12-00"  # change to 6 beam in the future
    sample_path = lidarwindrc("sample_data")

    if not os.path.isdir(sample_path):
        os.makedirs(sample_path)
        get_sample_data(sample_path, file_type)


@pytest.fixture
def data_filenames():

    file_type = "12-00"  # change to 6 beam in the future
    sample_path = os.path.join(lidarwindrc("sample_data"), file_type)

    if os.path.isdir(sample_path):

        if os.path.isdir(sample_path):
            file_list = sorted(glob.glob(f"{sample_path}/*.nc"))

            if bool(file_list) is False:
                get_sample_data(sample_path, file_type)
                file_list = sorted(glob.glob(f"{sample_path}/*.nc"))

        else:
            get_sample_data(sample_path, file_type)
            file_list = sorted(glob.glob(f"{sample_path}/*.nc"))

    else:
        download_samples()
        file_list = sorted(glob.glob(f"{sample_path}/*.nc"))

    return file_list


def sample_dataset(key: str):
    """Single xr.Dataset for testing

    For a given identifier, for now it is the filename, download if needed,
    and return already as an xarray Dataset ready to be used.

    !!ATENTION!!! the data_filenames as an argument is a requirement while
    the download of sample data is not refactored. This function only access
    a file that was expected to have been previously downlaoded.
    """
    path = os.path.join(lidarwindrc("sample_data"), "12-00", key)

    ds = open_sweep(path)
    return ds
