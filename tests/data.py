import os
import shutil
import glob
from typing import Optional

import pytest
import gdown

from lidarSuit.io import open_sweep

GDRIVE_ID = "1i6iX6KuZOkP_WLuPZHG5uCcvRjlWS-SU"


def lidarsuitrc(subdir: Optional[str] = None):
    """Standard path for Lidar Suit configurations

    This might be moved into lidarSuit.utils if used somewhere else
    """
    path = os.getenv("LIDARSUIT_DIR", os.path.join("~", ".lidarSuitrc"))
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


@pytest.fixture
def data_filenames():

    file_type = "12-00"  # change to 6 beam in the future
    sample_path = os.path.join(lidarsuitrc("sample_data"), file_type)

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
        os.makedirs(sample_path)
        get_sample_data(sample_path, file_type)
        file_list = sorted(glob.glob(f"{sample_path}/*.nc"))

    return file_list


def sample_dataset(filename: str):
    """Single xr.Dataset for testing

    For a given identifier, for now it is the filename, download if needed,
    and return already as an xarray Dataset ready to be used.

    @jdiasn will refactor how these testing data is managed, so let's leave
    optimizations for later as long as thid function keep returning a
    Dataset.
    """
    path = os.path.join(lidarsuitrc("sample_data"), "12-00", filename)

    ds = open_sweep(path)
    return ds
