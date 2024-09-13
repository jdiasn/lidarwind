import numpy as np
import pytest
import xarray as xr

import lidarwind as lst


def test_wind_prop_retrieval_ffWindPropRet_doppler_obs():

    with pytest.raises(TypeError):
        lst.FourierTransfWindMethod(doppler_obs=np.array([0, 1]))


def test_wind_prop_retrieval_GetWindProperties5Beam_data():

    with pytest.raises(TypeError):
        lst.GetWindProperties5Beam(data=xr.DataArray(np.array([0, 1])))


def test_wind_prop_retrieval_GetWindProperties5Beam_data_cont():

    with pytest.raises(AttributeError):  # with pytest.raises(TypeError):
        lst.GetWindProperties5Beam(
            xr.Dataset({"radial_wind_speed": xr.DataArray(np.array([0, 1]))}),
            method="continuous",
        )


def test_wind_prop_retrieval_RetriveWindFFT_tranfdData():

    with pytest.raises(TypeError):
        lst.RetriveWindFFT(transfd_data=np.array([0, 1]))
