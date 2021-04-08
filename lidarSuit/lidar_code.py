# code to open lidar files
# by José Dias Neto, 17.03.2021
#

import matplotlib.pyplot as plt
import xarray as xr


def openLidarFile(fileName):

    # reading the group name
    tmpData = xr.open_dataset(fileName)
    grpName = tmpData.sweep_group_name.values[0] 
    tmpData.close()

    # retrieving the group dataset
    tmpData = xr.open_dataset(fileName, group=grpName, 
                              decode_times=False)
   
    # decoding time 
    timeRef = tmpData.time_reference.values
    tmpData.time.attrs['units'] = 'seconds since {0}'.format(timeRef)
    tmpData = xr.decode_cf(tmpData)
    
    return tmpData


data = openLidarFile('WLS200s-218_2021-03-11_07-53-41_rhi_166_25m.nc')

# printing list of keys
for key in data.keys():
    print(key)

# quick visualization
data.radial_wind_speed.plot(y='range')
plt.show()
