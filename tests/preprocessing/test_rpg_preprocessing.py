import numpy as np
import pytest
import xarray as xr

from lidarwind.preprocessing import rpg_radar


def test_time_decoding_ds_type():

    with pytest.raises(TypeError):
        rpg_radar.time_decoding(ds=np.array([1, 2]))


def test_time_decoding_time():

    with pytest.raises(AssertionError):
        rpg_radar.time_decoding(ds=xr.Dataset({"Timems": [0]}))


def test_time_decoding_timems():

    with pytest.raises(AssertionError):
        rpg_radar.time_decoding(ds=xr.Dataset({"Time": [0]}))
