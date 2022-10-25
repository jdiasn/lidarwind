import os
import gdown
import shutil
import glob
import pandas as pd
import numpy as np
import xarray as xr


class util:

    """
    This class contains useful tools
    """

    def getTimeBins(selDay, freq="10min"):
        """Bins estimation

        Creating time bins for a given day and time resolution

        """

        start = selDay.strftime("%Y%m%d")
        startTime = pd.to_datetime("{0} 00:00:00".format(start))

        end = (selDay + pd.to_timedelta(1, "D")).strftime("%Y%m%d")
        endTime = pd.to_datetime("{0} 00:00:00".format(end))

        timeBins = pd.date_range(startTime, endTime, freq=freq)

        return timeBins

    def get_sample_data(sample_path, file_type):
        """Downloading data

        It downloads the sample needed for the examples.

        """

        if file_type == "12-00":
            url = "https://drive.google.com/uc?export=download&id=1i6iX6KuZOkP_WLuPZHG5uCcvRjlWS-SU"

        if file_type == "dbs":
            url = "path"

        output = f"{sample_path}{file_type}.zip"
        gdown.download(url, output, quiet=False)

        print(f"Extracting: {output}")
        shutil.unpack_archive(output, sample_path)
        os.remove(output)

    def data_filenames():
        """Sample file list

        It searches for the sample files. If the files do not exist, it downloads them.

        """

        home = os.path.expanduser("~")
        sample_path = f"{home}/.lidarSuitrc/sample_data/"
        file_type = "12-00"  # change to 6 beam in the future

        if os.path.isdir(sample_path):

            if os.path.isdir(f"{sample_path}{file_type}/"):
                file_list = sorted(glob.glob(f"{sample_path}{file_type}/*.nc"))

                if bool(file_list) == False:
                    util.get_sample_data(sample_path, file_type)
                    file_list = sorted(
                        glob.glob(f"{sample_path}{file_type}/*.nc")
                    )

            else:
                util.get_sample_data(sample_path, file_type)
                file_list = sorted(glob.glob(f"{sample_path}{file_type}/*.nc"))

        else:
            os.makedirs(sample_path)
            util.get_sample_data(sample_path, file_type)
            file_list = sorted(glob.glob(f"{sample_path}{file_type}/*.nc"))

        return file_list


class cloudMask:

    """
    This class generates the time-height cloud mask
    and the temporal cloud mask using observations
    from lidar and ceilometer.
    """

    def __init__(self, wcData=None, ceiloData=None, radarData=None):

        self.ceiloData = ceiloData
        self.radarData = radarData
        self.wcData = wcData

        self.callMethods()

    def callMethods(self):

        if self.ceiloData is None or self.radarData is None:

            self.getTimeMask(maskType="aux")

        else:

            self.cleanCeilo()
            self.cleanRadar()
            self.getCloudMask2D()
            self.getTimeMask(maskType="real")

    def cleanCeilo(self):

        positiveBeta = self.ceiloData.beta_raw.where(
            self.ceiloData.beta_raw > 0
        )
        positiveBeta = positiveBeta.rolling(
            time=20, center=True, min_periods=13
        ).mean()
        positiveBeta = positiveBeta.rolling(
            range=10, center=True, min_periods=8
        ).mean()

        # grid interpolation: to lidar time
        self.cleanCeiloData = positiveBeta.interp({"time": self.wcData.time})

    def cleanRadar(self):

        positiveZe = self.radarData.radar_equivalent_reflectivity.where(
            self.radarData.radar_equivalent_reflectivity > 0
        )

        # grid interpolation: to lidar time, to ceilo range
        self.cleanRadarData = positiveZe.interp(
            {"time": self.wcData.time, "range": self.cleanCeiloData.range}
        )

    def getCloudMask2D(self):

        # CEILOMETER mask
        self.cleanCeiloData.values[np.isfinite(self.cleanCeiloData.values)] = 2
        self.cleanCeiloData.values[
            ~np.isfinite(self.cleanCeiloData.values)
        ] = 0

        # RADAR mask
        self.cleanRadarData.values[np.isfinite(self.cleanRadarData.values)] = 1
        self.cleanRadarData.values[
            ~np.isfinite(self.cleanRadarData.values)
        ] = 0

        # final mask
        self.cloudMask = self.cleanCeiloData + self.cleanRadarData

    def getTimeMask(self, maskType=None):

        if maskType == "aux":
            print("aux mask")

            auxCloudMask = xr.DataArray(
                np.ones(len(self.wcData.time)),
                dims="time",
                coords={"time": self.wcData.time.values},
            )

            self.timeCloudMask = auxCloudMask

        elif maskType == "real":
            print("real mask")

            # 6500 is the value I defined as maximum range
            highCloudLayer = self.cloudMask.where(self.cloudMask.range > 6500)

            timeCloudMask = highCloudLayer.sum(dim="range")

            # 1 indicates that there is a cloud above
            # the maximum range
            timeCloudMask.values[timeCloudMask.values > 0] = 1

            self.timeCloudMask = timeCloudMask

        else:
            print("maskType not defined")
