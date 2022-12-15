import pytest
import xarray as xr
import numpy as np

import lidarSuit as lst


def test_windPropRetrieval_ffWindPropRet_dopplerObs():

    with pytest.raises(TypeError):
        lst.FourierTransfWindMethod(dopplerObs=np.array([0, 1]))


def test_windPropRetrieval_GetWindProperties5Beam_data():

    with pytest.raises(TypeError):
        lst.GetWindProperties5Beam(data=xr.DataArray(np.array([0, 1])))


def test_windPropRetrieval_RetriveWindFFT_tranfdData():

    with pytest.raises(TypeError):
        lst.RetriveWindFFT(transfd_data=np.array([0, 1]))
