import numpy as np
import xarray as xr

class getWindProperties6Beam:

    def __init__(self, data):

        self.elevation = data.elevation.round(1)
        self.calcVerticalWindComp(data)

        return None

    def calcVerticalWindComp(self, data):

        self.verticalWind = data.radial_wind_speed.where(self.elevation==90,
                                                         drop=True)

        return self
