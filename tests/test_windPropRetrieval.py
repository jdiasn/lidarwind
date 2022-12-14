import pytest
import xarray as xr
import numpy as np

import lidarSuit as lst


def test_windPropRetrieval_ffWindPropRet_dopplerObs():

    with pytest.raises(TypeError):
        lst.fftWindPropRet(dopplerObs=np.array([0, 1]))


def test_windPropRetrieval_getWindProperties5Beam_data():

    with pytest.raises(TypeError):
        lst.getWindProperties5Beam(data=xr.DataArray(np.array([0, 1])))


def test_windPropRetrieval_retrieve_wind_tranfdData():

    with pytest.raises(TypeError):
        lst.retrieve_wind(transfd_data=np.array([0, 1]))
