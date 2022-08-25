"""Module to open the lidar original output

"""

# code to open lidar files
# by José Dias Neto, 17.03.2021
#

import xarray as xr


class getLidarData:
    """Windcube's data reader
    
    It opens and reads the original NetCDF output
    from the Windcube lidar
    
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
        """

        tmpData = xr.open_dataset(self.fileName)
        grpName = tmpData.sweep_group_name.values[0]
        tmpData.close()

        # retrieving the group dataset
        tmpData = xr.open_dataset(self.fileName, group=grpName,
                                  decode_times=False)

        # decoding time
        timeRef = tmpData.time_reference.values
        tmpData.time.attrs['units'] = 'seconds since {0}'.format(timeRef)
        tmpData = xr.decode_cf(tmpData)

        return tmpData