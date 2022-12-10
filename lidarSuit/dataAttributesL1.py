"""Module for wrinting the Level 1 data attributes

"""

from .lstConfig import Configurations


class LoadAttributes:

    """Level 1 Attribute generator

    It defines and writes the attributes from the Level 1

    Parameters
    ----------
    data : xarray.Dataset
        A xarray dataset containing the Level 1 data
        generated by the lidarsuit

    Returns
    -------
    data : xarray.Dataset

        A dataset with corrected attributes

    """

    def __init__(self, data):

        self.data = data
        self.write_global_attrs()
        self.variables_attrs()
        self.write_coords_attrs()
        self.write_variables_attrs()

    def write_global_attrs(self):

        """Global attribute writer

        It loads and writes the global attributes from the Level 1 dataset.
        The global attributes are defiened in the configuration file.
        See lstConfig.generate_conf documentation for information about generating
        the configuration file.

        """

        config_info = Configurations(lst=None).load_conf_file()

        tmp_att = {
            "Conventions": "Cf/Radial 2.0",
            "title": "Wind properties",
            "references": config_info.references,
            "institution": config_info.institution,
            "instrument_name": config_info.instrument,
            "comments": config_info.comments,
            "site_name": config_info.site,
            "contact_person": config_info.contact,
            "email": config_info.email,
        }

        self.data.attrs = tmp_att

        return self

    def variables_attrs(self):

        """Variable attributes definitions

        All variables and coordinates attributes are defined here.

        """

        attrs_dic = {}

        attrs_dic["range"] = {
            "standard_name": "range",
            "units": "m",
            "comments": "Distance between the instrument and the center of each range gate",
        }

        attrs_dic["time"] = {
            "standard_name": "time",
            "reference": "seconds since 1970-01-01 00:00:00",
            "comments": "time of the horizotal observations",
        }

        attrs_dic["time90"] = {
            "standard_name": "time90",
            "reference": "seconds since 1970-01-01 00:00:00",
            "comments": "time of the vertical observations",
        }

        attrs_dic["horizontal_wind_speed"] = {
            "standard_name": "wind_speed",
            "units": "m/s",
            "comments": "horizontal wind speed retrived using the FFT method",
        }

        attrs_dic["horizontal_wind_direction"] = {
            "standard_name": "wind_direction",
            "units": "degrees",
            "comments": "horizontal wind direction retrived "
                        "using the FFT method with respect to true north",
            "info": "0=wind coming from the north, 90=east, 180=south, 270=west",
        }

        attrs_dic["zonal_wind"] = {
            "standard_name": "zonal_wind",
            "units": "m/s",
            "comments": "zonal wind retrived using the FFT method",
        }

        attrs_dic["meridional_wind"] = {
            "standard_name": "meridional_wind",
            "units": "m/s",
            "comments": "meridional wind retrived using the FFT method",
        }

        attrs_dic["vertical_wind_speed"] = {
            "standard_name": "vertical_wind_speed",
            "units": "m/s",
            "comments": "observed vertical wind speed (negative towards the ground)",
        }

        attrs_dic["lidar_relative_beta"] = {
            "standard_name": "volume_attenuated_backwards_scattering_function_in_air",
            "units": "m-1 sr-1",
            "comments": "Attenuated relative backscatter coefficient from the vertical beam",
        }

        self.attrs_dic = attrs_dic

        return self

    def write_coords_attrs(self):

        """Coordinate attribute writer

        It loops over the dataset coordinate and writes their attributes

        """

        for key in self.data.coords:

            try:
                self.data[key].attrs = self.attrs_dic[key]

            except KeyError:
                print(f"coord not found: {key}")

        return self

    def write_variables_attrs(self):

        """Variable attribute writer

        It loops over the dataset variables and writes their attributes

        """

        for key in self.data.keys():

            try:
                self.data[key].attrs = self.attrs_dic[key]

            except KeyError:
                print(f"variable not found: {key}")

        return self
