import numpy as np
import xarray as xr
import pandas as pd

from .utilities import util

class sixBeamMethod:

    """
    Implementation of the 6 beam method
    to retrieve the Reynolds stress tensor
    components based on the 6 Beam method
    developed by Sathe at all 2015.
    """

    def __init__(self, data, freq='30min'):

#         self.elv = 45
        self.elv = data.dataTransf.elv.values
        self.azm = data.dataTransf.azm.values
        self.timeFreq = freq

        self.get_M()
        self.get_M_inv()
        self.rVariances = {}
        self.getVariance(data.dataTransf)
        self.getVariance(data.dataTransf90, name='rVariance90')
        self.get_S()
        self.get_SIGMA()
        self.getVarianceDS()

        return None


    def get_M(self):

        """
        This method populates the coefficient matrix (M).
        Each element of M is one of the coefficients from
        equation 3 from Newman et. all 2016. The lines 0 to 4
        in M are the radial velocities coefficients from the
        non 90 deg elevation and different azimuths. Line 6
        in M has the coefficients from the radial velocity
        at 90 deg elevation.

        M x SIGMA = S
        """

        phis = np.append(np.ones_like(self.azm)*self.elv, np.array([90]))
        phisRad = np.deg2rad(phis)

        thetas = np.append(self.azm, np.array([0]))
        thetasRad = np.deg2rad(thetas)

        M = np.ones((len(phis),len(thetas)))*np.nan

        for i, theta in enumerate(thetasRad):

            phi = phisRad[i]

            ci1 = np.cos(phi)**2 * np.sin(theta)**2
            ci2 = np.cos(phi)**2 * np.cos(theta)**2

            ci3 = np.sin(phi)**2
            ci4 = np.cos(phi)**2 * np.cos(theta) * np.sin(theta)

            ci5 = np.cos(phi) * np.sin(phi) * np.sin(theta)
            ci6 = np.cos(phi) * np.sin(phi) * np.cos(theta)

            Mline = np.array([ci1, ci2, ci3, ci4*2, ci5*2, ci6*2])

            M[i] = Mline

        self.M = M

        return self


    def get_M_inv(self):

        """
        This method calculates the inverse matrix of M.
        """

        self.M_inv = np.linalg.inv(self.M)

        return self



    def getVariance(self, data , name='rVariance'):

        """
        This method calculates the variance from the
        observed radial velocities within a time window.
        The default size of this window is 10 minutes.
        """

        timeBins = util.getTimeBins(pd.to_datetime(data.time.values[0]), freq=self.timeFreq)
        groupedData = data.groupby_bins('time', timeBins)

        self.rVariances[name] = groupedData.var(dim='time')#.apply(calcGroupVar)
        self.rVariances['{0}_counts'.format(name)] = groupedData.count(dim='time')

        return self


    def get_S(self):

        """
        This method fills the observation variance matrix (S).
        """

        S = np.dstack((self.rVariances['rVariance'].values,
                       self.rVariances['rVariance90'].values[:,:,np.newaxis, np.newaxis]))

        self.S = S


    def get_SIGMA(self):

        """
        This method calculates the components of the
        Reynolds stress tensor (SIGMA).

        SIGMA = M^-1 x S
        """

        self.SIGMA = np.matmul(self.M_inv, self.S)

        return self


    def getVarianceDS(self):

        """
        This method converts the SIGMA into a xarray dataset.
        """

        varCompDS = xr.Dataset()
        varCompName = ['u','v','w','uv','uw','vw']

        for i, varComp in enumerate(varCompName):

            tmpData = xr.DataArray(self.SIGMA[:,:,i,0],
                                   dims=('time_bins', 'range'),
                                   coords={'time_bins':self.rVariances['rVariance90'].time_bins,
                                           'range':self.rVariances['rVariance'].range},
                                   name='var_{0}'.format(varComp))

            varCompDS = xr.merge([varCompDS, tmpData])

        self.varCompDS = varCompDS

        return self