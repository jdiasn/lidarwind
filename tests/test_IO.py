import os
import gdown
import shutil
import glob
import matplotlib.pyplot as plt
import pytest

import lidarSuit as lst


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


@pytest.fixture
def test_dataOperations(data_filenames):

    tmp_object = lst.dataOperations(data_filenames)

    return tmp_object.mergedData


def test_getRestructuredData(test_dataOperations):

    restruct_data = lst.getRestructuredData(test_dataOperations)
