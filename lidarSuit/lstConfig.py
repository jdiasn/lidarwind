
"""Module for configuring the data global attribute

"""

import json


class configurations:
    """Global attributes definition

    This class defines all global attributes
    that will be writen on the dataset

    Parameters
    ----------
    lst : object
        an instance of the lidarSuit package

    """

    def __init__(self, lst=None):

        self.loadVersion(lst)
        self.loadReference()
        self.loadInstitution()
        self.loadInstrument()
        self.loadSite()
        self.loadContact()
        self.loadEmail()
        self.loadComments()

    def loadVersion(self, lst):
        """
        It identifies the lidarSuit version
        and writes it to the configuration file

        Parameters
        ----------
        lst : object
            a instance of the lidarSuit package

        """

        if lst == None:
            self.lstVersion = "temporary config file"
        else:
            self.lstVersion = lst.__version__

        return self

    def loadInstitution(self, institution="institution name"):
        """
        It defines the institution affiliation name

        Parameters
        ----------
        institution : str
            institution name

        """

        self.institution = institution

        return self

    def loadInstrument(self, instrument="instrument name"):
        """
        It defines the instrument name

        Parameters
        ----------
        instrument : str
            name of the instrument used during the experiment

        """

        self.instrument = instrument

        return self

    def loadSite(self, site="site name"):
        """
        It defines the name of the experimental site

        Parameters
        ----------
        site : str
            name of the experimental site

        """

        self.site = site

        return self

    def loadContact(self, contact="contact person"):
        """
        It defines the author's name

        Parameters
        ----------
        contact : str
            name of the contact person

        """

        self.contact = contact

        return self

    def loadEmail(self, email="contact email"):
        """
        It defines the contacting email

        Parameters
        ----------
        email : str
            contact email

        """
        self.email = email

        return self

    def loadReference(self, reference="Generated by lidarSuit version: {0}"):
        """
        It loads the lidarSuit's version used for
        processing the data

        Parameters
        ----------
        reference : str
            lidarSuit version used to process the data

        """

        self.references = reference.format(self.lstVersion)

        return self

    def loadComments(self, comments="General comments"):
        """
        It defines additional comments

        Parameters
        ----------
        comments : str
            additional comments

        """
        self.comments = comments

        return self

    def generateConf(self):
        """
        It writes and saves all defined global attributes.

        """

        config_dic = {}

        config_dic["references"] = self.references
        config_dic["institution"] = self.institution
        config_dic["instrument_name"] = self.instrument
        config_dic["site_name"] = self.site
        config_dic["comments"] = self.comments
        config_dic["contact_person"] = self.contact
        config_dic["email"] = self.email

        configJS = json.dumps(config_dic)
        config_file = open("config.json", "w")
        config_file.write(configJS)
        config_file.close()

    def load_conf_file(self, file_path="config.json"):
        """
        It loads the pre-defined global attributes
        from the config.json, if it exists.

        Parameters
        ----------
        file_path : str
            the path to the configuration file (config.json)

        """

        try:
            config_dic = json.load(open(file_path))

        except FileNotFoundError:

            print("You do not have a config file yet")
            print("a temporary config file was generated")
            print("See the documentation for generating it")
            self.generateConf()
            config_dic = json.load(open(file_path))

        self.loadReference(config_dic["references"])
        self.loadInstitution(config_dic["institution"])
        self.loadInstrument(config_dic["instrument_name"])
        self.loadComments(config_dic["comments"])
        self.loadSite(config_dic["site_name"])
        self.loadContact(config_dic["contact_person"])
        self.loadEmail(config_dic["email"])

        return self
