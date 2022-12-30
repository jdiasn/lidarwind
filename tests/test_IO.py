import pytest

import lidarwind as lst
from .data import data_filenames, get_sample_data


@pytest.fixture
def test_DataOperations(data_filenames):

    tmp_object = lst.DataOperations(data_filenames)

    return tmp_object.merged_data


def test_GetRestructuredData(test_DataOperations):

    restruct_data = lst.GetRestructuredData(test_DataOperations)
