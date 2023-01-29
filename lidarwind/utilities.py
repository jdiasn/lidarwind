"""Utilities module

"""

import os
import shutil
import glob

import gdown
import pandas as pd
import pooch
import numpy as np
import xarray as xr



def sample_data(key: str):
    if key == "wc_6beam":
        file_list = pooch.retrieve(
            url="doi:10.5281/zenodo.7312960/wc_6beam.zip",
            known_hash="md5:a7ea3c10a6d2f4a97ff955dc4398f930",
            processor=pooch.Unzip(),
        )
    elif key == "wc_long_dbs":
        file_list = pooch.retrieve(
            url="doi:10.5281/zenodo.7312960/wc_long_dbs.zip",
            known_hash="md5:53b4eb6e5dad6dfdaddfbb718dcf8910",
            processor=pooch.Unzip(),
        )
    elif key == "wc_short_dbs":
        file_list = pooch.retrieve(
            url="doi:10.5281/zenodo.7312960/wc_short_dbs.zip",
            known_hash="md5:9cbd93f89052d6c6f4407bcce415e277",
            processor=pooch.Unzip(),
        )
    else:
        raise ValueError

    return file_list


class Util:

    """
    This class contains useful tools
    """

    def get_time_bins(sel_day, freq="10min"):
        """Bins estimation

        Creating time bins for a given day and time resolution

        """

        start = sel_day.strftime("%Y%m%d")
        start_time = pd.to_datetime(f"{start} 00:00:00")

        end = (sel_day + pd.to_timedelta(1, "D")).strftime("%Y%m%d")
        end_time = pd.to_datetime(f"{end} 00:00:00")

        time_bins = pd.date_range(start_time, end_time, freq=freq)

        return time_bins

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

        It searches for the sample files.
        If the files do not exist, it downloads them.

        """

        home = os.path.expanduser("~")
        sample_path = f"{home}/.lidarwindrc/sample_data/"
        file_type = "12-00"  # change to 6 beam in the future

        if os.path.isdir(sample_path):

            if os.path.isdir(f"{sample_path}{file_type}/"):
                file_list = sorted(glob.glob(f"{sample_path}{file_type}/*.nc"))

                if bool(file_list) is False:
                    Util.get_sample_data(sample_path, file_type)
                    file_list = sorted(
                        glob.glob(f"{sample_path}{file_type}/*.nc")
                    )

            else:
                Util.get_sample_data(sample_path, file_type)
                file_list = sorted(glob.glob(f"{sample_path}{file_type}/*.nc"))

        else:
            os.makedirs(sample_path)
            Util.get_sample_data(sample_path, file_type)
            file_list = sorted(glob.glob(f"{sample_path}{file_type}/*.nc"))

        return file_list


class CloudMask:

    """
    This class generates the time-height cloud mask
    and the temporal cloud mask using observations
    from lidar and ceilometer.
    """

    def __init__(self, wc_data=None, ceilo_data=None, radar_data=None):

        self.ceilo_data = ceilo_data
        self.radar_data = radar_data
        self.wc_data = wc_data

        self.call_methods()

    def call_methods(self):

        if self.ceilo_data is None or self.radar_data is None:

            self.get_time_mask(mask_type="aux")

        else:

            self.clean_ceilo()
            self.clean_radar()
            self.get_cloud_mask_2d()
            self.get_time_mask(mask_type="real")

    def clean_ceilo(self):

        positive_beta = self.ceilo_data.beta_raw.where(
            self.ceilo_data.beta_raw > 0
        )
        positive_beta = positive_beta.rolling(
            time=20, center=True, min_periods=13
        ).mean()
        positive_beta = positive_beta.rolling(
            range=10, center=True, min_periods=8
        ).mean()

        # grid interpolation: to lidar time
        self.clean_ceilo_data = positive_beta.interp(
            {"time": self.wc_data.time}
        )

    def clean_radar(self):

        positive_ze = self.radar_data.radar_equivalent_reflectivity.where(
            self.radar_data.radar_equivalent_reflectivity > 0
        )

        # grid interpolation: to lidar time, to ceilo range
        self.clean_radar_data = positive_ze.interp(
            {"time": self.wc_data.time, "range": self.clean_ceilo_data.range}
        )

    def get_cloud_mask_2d(self):

        # CEILOMETER mask
        self.clean_ceilo_data.values[
            np.isfinite(self.clean_ceilo_data.values)
        ] = 2
        self.clean_ceilo_data.values[
            ~np.isfinite(self.clean_ceilo_data.values)
        ] = 0

        # RADAR mask
        self.clean_radar_data.values[
            np.isfinite(self.clean_radar_data.values)
        ] = 1
        self.clean_radar_data.values[
            ~np.isfinite(self.clean_radar_data.values)
        ] = 0

        # final mask
        self.cloud_mask = self.clean_ceilo_data + self.clean_radar_data

    def get_time_mask(self, mask_type=None):

        if mask_type == "aux":
            print("aux mask")

            aux_cloud_mask = xr.DataArray(
                np.ones(len(self.wc_data.time)),
                dims="time",
                coords={"time": self.wc_data.time.values},
            )

            self.time_cloud_mask = aux_cloud_mask

        elif mask_type == "real":
            print("real mask")

            # 6500 is the value I defined as maximum range
            high_cloud_layer = self.cloud_mask.where(
                self.cloud_mask.range > 6500
            )

            time_cloud_mask = high_cloud_layer.sum(dim="range")

            # 1 indicates that there is a cloud above
            # the maximum range
            time_cloud_mask.values[time_cloud_mask.values > 0] = 1

            self.time_cloud_mask = time_cloud_mask

        else:
            print("mask_type not defined")
