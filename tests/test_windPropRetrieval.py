import pytest
import xarray as xr
import numpy as np

import lidarSuit as lst

def test_windPropRetrieval_getWindProperties5Beam_data():

    with pytest.raises(TypeError):

        lst.getWindProperties5Beam(data=xr.DataArray(np.array([0,1])))