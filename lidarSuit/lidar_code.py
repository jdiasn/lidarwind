"""Module to open the lidar original output

"""

# code to open lidar files
# by José Dias Neto, 17.03.2021
#

import warnings

import xarray as xr

from .io import open_sweep


class getLidarData:
    """Windcube's data reader


    ATENTION, please move to io.open_sweep(). This getLidarData will
    be eventually removed.

    It opens and reads the original NetCDF output from the Windcube lidar

    Parameters
    ----------

    fileName : str
        name of the file that will be open

    """

    def __init__(self, fileName):

        self.fileName = fileName

        return None

    def openLidarFile(self):

        """
        Function to read the lidar NetCDF files

        Returns
        -------
        tmpData : xarray.DataSet
            a dataset from the original NetCDF files

        Note
        ----
        Alias to io.open_sweep() so upper functions don't break until we
        finished the transition to new I/O.
        """
        warnings.warn(
            "getLidarData will be removed eventually. Please use io module instead",
            DeprecationWarning,
            stacklevel=2,
        )

        return open_sweep(self.fileName)
