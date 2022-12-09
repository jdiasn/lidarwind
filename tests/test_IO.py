import os
import gdown
import shutil
import glob
import matplotlib.pyplot as plt
import pytest

import lidarSuit as lst
from .data import get_sample_data


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
def test_DataOperations(data_filenames):

    tmp_object = lst.DataOperations(data_filenames)

    return tmp_object.merged_data


def test_GetRestructuredData(test_DataOperations):

    restruct_data = lst.GetRestructuredData(test_DataOperations)
