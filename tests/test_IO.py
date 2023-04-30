import pytest

import lidarwind as lst

from .data import data_filenames  # , get_sample_data


@pytest.fixture
# @pytest.mark.skip("deactivating to isolate sef fault error")
def test_DataOperations(data_filenames):

    tmp_object = lst.DataOperations(data_filenames)

    return tmp_object.merged_data


# @pytest.mark.skip("deactivating to isolate sef fault error")
def test_GetRestructuredData(test_DataOperations):

    lst.GetRestructuredData(test_DataOperations)
