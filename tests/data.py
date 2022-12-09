import os
import shutil
import glob
import pytest

import gdown

from lidarSuit.io import open_sweep


def lidarsuitrc(subdir: str | None = None):
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
        url = "https://drive.google.com/uc?export=download&id=1i6iX6KuZOkP_WLuPZHG5uCcvRjlWS-SU"

    if file_type == "dbs":
        url = "path"

    output = f"{sample_path}{file_type}.zip"
    gdown.download(url, output, quiet=False)

    print(f"Extracting: {output}")
    shutil.unpack_archive(output, sample_path)
    os.remove(output)


@pytest.fixture
def data_filenames():

    home = os.path.expanduser("~")
    sample_path = f"{home}/.lidarSuitrc/sample_data/"
    file_type = "12-00"  # change to 6 beam in the future

    if os.path.isdir(sample_path):

        if os.path.isdir(f"{sample_path}{file_type}/"):
            file_list = sorted(glob.glob(f"{sample_path}{file_type}/*.nc"))

            if bool(file_list) == False:
                get_sample_data(sample_path, file_type)
                file_list = sorted(glob.glob(f"{sample_path}{file_type}/*.nc"))

        else:
            get_sample_data(sample_path, file_type)
            file_list = sorted(glob.glob(f"{sample_path}{file_type}/*.nc"))

    else:
        os.makedirs(sample_path)
        get_sample_data(sample_path, file_type)
        file_list = sorted(glob.glob(f"{sample_path}{file_type}/*.nc"))

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
