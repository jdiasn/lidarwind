import pandas as pd
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
    


# it removes the STE below cloud layer
class secondTripEchoFilter:

    
    def __init__(self, data, timeCloudMask, nProf=500,
                 center=True, min_periods=30, nStd=2, strH='09', endH='16'):
        
        self.lidar = data
        self.timeCloudMask = timeCloudMask
        self.nProf = nProf
        self.center = center
        self.min_periods = min_periods
        self.nStd = nStd
        
        self.getTimeEdges()
        self.calMeanAndAnomSlant()
        self.calMeanAndAnom90()
        self.cleaning()
        self.cleaning90()
        
        return None
        
        
    def getTimeEdges(self, strH='09', endH='16'):

        selTime = pd.to_datetime(self.lidar.dataTransf.time.values[0])
        selTime = selTime.strftime("%Y%m%d")
        self.startTime =  pd.to_datetime("{0} {1}".format(selTime, strH))
        self.endTime = pd.to_datetime("{0} {1}".format(selTime, endH))

        return None


    def calMeanAndAnomSlant(self):

        # slanted beam
        tmpSelData = self.lidar.dataTransf

        self.dataMean = tmpSelData.rolling(time=self.nProf, center=self.center,
                                          min_periods=self.min_periods).mean()

        self.dataAnom = self.lidar.dataTransf - self.dataMean

        return None


    def calMeanAndAnom90(self):

        # vertical beam
        tmpSelData90 = self.lidar.dataTransf90

        self.dataMean90 = tmpSelData90.rolling(time=self.nProf, center=self.center,
                                          min_periods=self.min_periods).mean()

        self.dataAnom90 = self.lidar.dataTransf90 - self.dataMean90

        return None


    def cleaning(self):

        tmpAnom = self.dataAnom.where((self.lidar.dataTransf.time>self.startTime) &
                                      (self.lidar.dataTransf.time < self.endTime))

        anomStd = tmpAnom.std(dim=['time', 'range', 'elv'])

        tmpNoCloud = self.lidar.dataTransf.where(self.timeCloudMask == 0).copy()
        tmpCloud = self.lidar.dataTransf.where(self.timeCloudMask == 1).copy()

        tmpCloud = tmpCloud.where(np.abs(self.dataAnom) < self.nStd * anomStd)

        tmpCleanData = tmpNoCloud.copy()
        tmpCleanData.values[np.isfinite(tmpCloud)] = tmpCloud.values[np.isfinite(tmpCloud)]

        self.lidar.dataTransf.values = tmpCleanData

        return None



    def cleaning90(self):

        tmpAnom = self.dataAnom90.where((self.lidar.dataTransf90.time>self.startTime) &
                                      (self.lidar.dataTransf90.time < self.endTime))

        anomStd = tmpAnom.std(dim=['time', 'range90'])

        #tmpNoCloud = self.lidar.dataTransf90.where(self.timeCloudMask == 0).copy()
        #tmpCloud = self.lidar.dataTransf90.where(self.timeCloudMask == 1).copy()
        
        #tmpCloud = tmpCloud.where(np.abs(self.dataAnom90) < self.nStd * anomStd)

        #tmpCleanData = tmpNoCloud.copy()
        #tmpCleanData.values[np.isfinite(tmpCloud)] = tmpCloud.values[np.isfinite(tmpCloud)]

        tmpCleanData = self.lidar.dataTransf90.copy()
        tmpCleanData = tmpCleanData.where(np.abs(self.dataAnom90) < self.nStd * anomStd)

        self.lidar.dataTransf90.values = tmpCleanData.values

        return None



#     def __init__(self, data, nProf=500, center=True, min_periods=30, nStd=2):

#         self.data = data
#         self.nProf = nProf
#         self.center = center
#         self.min_periods = min_periods
#         self.nStd = nStd

#         self.calMeanAndAnom()
#         self.cleaning()

#         return None


#     def calMeanAndAnom(self):

#         self.dataMean = self.data.rolling(time=self.nProf, center=self.center,
#                                           min_periods=self.min_periods).mean()
#         self.dataAnom = self.data - self.dataMean

#         return self


#     def cleaning(self):

#         anomStd = self.dataAnom.std(dim=['time', 'range', 'elv'])
#         self.data = self.data.where(np.abs(self.dataAnom) < self.nStd * anomStd)

#         return self


# import numpy as np



# it removes STE and clouds contamination
# from above the aerosol loaded region
class windCubeCloudRemoval:


    def __init__(self, ceilo, lidar=None):


        self.lidar = lidar
        self.ceilo = ceilo

        self.getNoiseFreeBeta()
        self.getHeightInterface()

        if lidar != None:
            self.getInterpInterfHeight()
            self.removeCloud()

        return None


    def getNoiseFreeBeta(self):

        positiveBeta = self.ceilo.beta_raw.where(self.ceilo.beta_raw > 0)

        positiveBeta = positiveBeta.rolling(range=10,center=True, min_periods=10).mean()
        positiveBeta = positiveBeta.rolling(time=15,center=True, min_periods=15).mean()

        self.noiseFreeBeta = positiveBeta

        return self


    def getHeightInterface(self):

        positiveBeta = self.ceilo.beta_raw.where(self.ceilo.beta_raw > 0)

        tmpCeiloHgt = positiveBeta.copy()
        tmpValues = tmpCeiloHgt.values
        tmpValues[np.isfinite(tmpValues)] = 1
        tmpCeiloHgt.values = tmpValues
        tmpCeiloHgt = tmpCeiloHgt * self.ceilo.range

        lowestBeta =  self.noiseFreeBeta.where(tmpCeiloHgt < 4e3)

        tmpCeiloHgt = tmpCeiloHgt.where(np.isfinite(lowestBeta))

        self.interfHeight = tmpCeiloHgt.max(dim='range')
        self.interfHeight = self.interfHeight.rolling(time=7, center=True, min_periods=5).mean()

        return self


    def getInterpInterfHeight(self):

        self.interpInterfHeight = self.interfHeight.interp(time=self.lidar.dataTransf.time)
        self.interpInterfHeight90 = self.interfHeight.interp(time=self.lidar.dataTransf90.time)

        return self


    def removeCloud(self):

        tmpHeight = self.lidar.dataTransf.copy()
        tmpValues = tmpHeight.values
        tmpValues[np.isfinite(tmpValues)] = 1
        tmpHeight.values = tmpValues
        tmpHeight = tmpHeight * self.lidar.dataTransf.range
        self.lidar.dataTransf = self.lidar.dataTransf.where(tmpHeight < self.interpInterfHeight)


        tmpHeight = self.lidar.dataTransf90.copy()
        tmpValues = tmpHeight.values
        tmpValues[np.isfinite(tmpValues)] = 1
        tmpHeight.values = tmpValues
        tmpHeight = tmpHeight * self.lidar.dataTransf90.range90
        self.lidar.dataTransf90 = self.lidar.dataTransf90.where(tmpHeight < self.interpInterfHeight90)
        self.lidar.relative_beta90 = self.lidar.relative_beta90.where(tmpHeight < self.interpInterfHeight90)

        return self