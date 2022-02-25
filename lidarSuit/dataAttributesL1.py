from .lstConfig import configurations

class loadAttributes:

    def __init__(self, data):

        self.data = data
        self.writeGlobalAttrs()
        self.variablesAttrs()
        self.writeCoordsAttrs()
        self.writeVariablesAttrs()
        
        return None

    def writeGlobalAttrs(self):

        configInfo = configurations(lst=None).loadConfFile()

        tmpAtt = {'Conventions':'Cf/Radial 2.0',
                  'title': 'Wind properties',
                  'references':configInfo.references,
                  'institution':configInfo.institution,
                  'instrument_name':configInfo.instrument,
                  'comments':configInfo.comments,
                  'site_name':configInfo.site,
                  'contact_person':configInfo.contact,
                  'email':configInfo.email}

        self.data.attrs = tmpAtt
        
        return self
    
    def variablesAttrs(self):

        attrsDic = {}

        attrsDic['range']=\
            {'standard_name':'range',
             'units':'m',
             'comments': 'Distance between the instrument and the center of each range gate'}

        attrsDic['time']=\
            {'standard_name':'time',
             'reference':'seconds since 1970-01-01 00:00:00',
             'comments': 'time of the horizotal observations'}

        attrsDic['time90']=\
            {'standard_name':'time90',
             'reference':'seconds since 1970-01-01 00:00:00',
             'comments': 'time of the vertical observations'}

        attrsDic['horizontal_wind_speed']=\
            {'standard_name':'wind_speed',
             'units':'m/s',
             'comments': 'horizontal wind speed retrived using the FFT method'}

        attrsDic['horizontal_wind_direction']=\
            {'standard_name':'wind_direction',
             'units':'degrees',
             'comments': 'horizontal wind direction retrived using the FFT method with respect to true north',
             'info': '0=wind coming from the north, 90=east, 180=south, 270=west'}

        attrsDic['zonal_wind']=\
            {'standard_name':'zonal_wind',
             'units':'m/s',
             'comments': 'zonal wind retrived using the FFT method (positive if it blows from the west)'}

        attrsDic['meridional_wind']=\
            {'standard_name':'meridional_wind',
             'units':'m/s',
             'comments': 'meridional wind retrived using the FFT method (positive if it blows from the shouth)'}

        attrsDic['vertical_wind_speed']=\
            {'standard_name':'vertical_wind_speed',
             'units':'m/s',
             'comments': 'observed vertical wind speed (negative towards the ground)'}

        attrsDic['lidar_relative_beta']=\
            {'standard_name':'volume_attenuated_backwards_scattering_function_in_air',
             'units':'m-1 sr-1',
             'comments': 'Attenuated relative backscatter coefficient from the vertical beam'}

        self.attrsDic = attrsDic

        return self
            
    def writeCoordsAttrs(self):

        for key in self.data.coords:

            try:
                self.data[key].attrs = self.attrsDic[key]

            except:
                print('coord not found: {0}'.format(key))

        return self
            
    def writeVariablesAttrs(self):

        for key in self.data.keys():

            try:
                self.data[key].attrs = self.attrsDic[key]

            except:
                print('variable not found: {0}'.format(key))

        return self