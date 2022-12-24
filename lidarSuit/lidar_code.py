"""Module to open the lidar original output

"""


import warnings


from .io import open_sweep


class GetLidarData:
    """Windcube's data reader


    ATENTION, please move to io.open_sweep(). This GetLidarData will
    be eventually removed.

    It opens and reads the original NetCDF output from the Windcube lidar

    Parameters
    ----------

    file_name : str
        name of the file that will be open

    """

    def __init__(self, file_name):

        self.file_name = file_name

    def open_lidar_file(self):

        """
        Function to read the lidar NetCDF files

        Returns
        -------
        ds: xarray.DataSet
            a dataset from the original NetCDF files

        Note
        ----
        Alias to io.open_sweep() so upper functions don't break until we
        finished the transition to new I/O.
        """
        warnings.warn(
            "GetLidarData will be removed eventually. "
            "Please use io module instead",
            DeprecationWarning,
            stacklevel=2,
        )

        return open_sweep(self.file_name)
