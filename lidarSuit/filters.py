import numpy as np

class filtering:
    
    def __init__(self, data):
        
        self.data = data
        
        return None
    
    def getVerticalObsComp(self, variable, snr=False, status=True):
    
        tmpData = self.data[variable]
    
        if status:
            tmpData = tmpData.where(self.data.radial_wind_speed_status90==1)
        
        else:
            pass

        if snr != False:
            tmpData = tmpData.where(self.data.cnr90 > snr)
            
        else:
            pass

        tmpData = tmpData.where(self.data.elevation==90, drop=True)
        
    
        return tmpData
    
    def getRadialObsComp(self, variable, azm, snr=False, status=True):
    
        tmpData = self.data[variable]
    
        if status:
            tmpData = tmpData.where(self.data.radial_wind_speed_status==1)
            
        else:
            pass
        
        if snr != False:
            tmpData = tmpData.where(self.data.cnr > snr)
            
        else:
            pass
        
        tmpData = tmpData.where((self.data.elevation!=90) & (self.data.azimuth==azm), drop=True)
    
        return tmpData
    
    

class secondTripEchoFilter:
    
    def __init__(self, data, nProf=500, center=True, min_periods=30, nStd=2):
        
        self.data = data
        self.nProf = nProf
        self.center = center
        self.min_periods = min_periods
        self.nStd = nStd
        
        self.calMeanAndAnom()
        self.cleaning()
        
        return None
        
        
    def calMeanAndAnom(self):
        
        self.dataMean = self.data.rolling(time=self.nProf, center=self.center, 
                                          min_periods=self.min_periods).mean()
        self.dataAnom = self.data - self.dataMean

        return self

    
    def cleaning(self):

        anomStd = self.dataAnom.std(dim=['time', 'range', 'elv'])
        self.data = self.data.where(np.abs(self.dataAnom) < self.nStd * anomStd)
        
        return self