"""Module for estimating turbulence

"""

import numpy as np
import xarray as xr

from .utilities import util


class SixBeamMethod:

    """6 beam method

    Implementation of the 6 beam method
    to retrieve the Reynolds stress tensor
    components based on the 6 Beam method
    developed by Sathe at all 2015.
    See: https://doi.org/10.5194/amt-8-729-2015

    Parameters
    ----------
    data : object
        an instance of the object generated by the
        lst.getRestructuredData()

    freq : int
        number of profiles used to calculate
        the variance

    freq90 : int
        number of profiles used to calculate
        the variance

    Returns
    -------
    var_comp_ds : xarray.DataSet
        a dataset of the eynolds stress tensor
        matrix elementes

    """

    def __init__(self, data, freq=10, freq90=10):

        #         self.elv = 45
        self.elv = data.dataTransf.elv.values
        self.azm = data.dataTransf.azm.values
        # self.timeFreq = freq
        # self.timeFreq = freq

        self.get_M()
        self.get_M_inv()
        self.radial_variances = {}
        self.calcVariances(data, freq, freq90)

        self.get_S()
        self.get_SIGMA()
        self.get_variance_ds()

    def get_M(self):

        """
        This method populates the coefficient matrix (M).
        Each element of M is one of the coefficients from
        equation 3 from Newman et. all 2016. The lines 0 to 4
        in M are the radial velocities coefficients from the
        non 90 deg elevation and different azimuths. Line 6
        in M has the coefficients from the radial velocity
        at 90 deg elevation.
        See: https://doi.org/10.5194/amt-9-1993-2016


        M x SIGMA = S
        """

        phis = np.append(np.ones_like(self.azm) * self.elv, np.array([90]))
        phisRad = np.deg2rad(phis)

        thetas = np.append(self.azm, np.array([0]))
        thetasRad = np.deg2rad(thetas)

        M = np.ones((len(phis), len(thetas))) * np.nan

        for i, theta in enumerate(thetasRad):

            phi = phisRad[i]

            ci1 = np.cos(phi) ** 2 * np.sin(theta) ** 2
            ci2 = np.cos(phi) ** 2 * np.cos(theta) ** 2

            ci3 = np.sin(phi) ** 2
            ci4 = np.cos(phi) ** 2 * np.cos(theta) * np.sin(theta)

            ci5 = np.cos(phi) * np.sin(phi) * np.sin(theta)
            ci6 = np.cos(phi) * np.sin(phi) * np.cos(theta)

            Mline = np.array([ci1, ci2, ci3, ci4 * 2, ci5 * 2, ci6 * 2])

            M[i] = Mline

        self.M = M

        return self

    def get_M_inv(self):

        """
        This method calculates the inverse matrix of M.
        """

        self.M_inv = np.linalg.inv(self.M)

        return self

    ### new approach to calculate the variances ##############
    #
    #
    def calcVariances(self, data, freq, freq90):

        interpDataTransf = data.dataTransf.interp(
            time=data.dataTransf90.time, method="nearest"
        )
        self.getVariance(interpDataTransf, freq=freq)
        self.getVariance(
            -1 * data.dataTransf90, freq=freq90, name="rVariance90"
        )  # think about the -1 coefficient

        return self

    def getVariance(self, data, freq=10, name="rVariance"):

        """
        This method calculates the variance from the
        observed radial velocities within a time window.
        The default size of this window is 10 minutes.

        Parameters
        ----------
        data : xarray.DataArray
            a dataarray of the slanted azimuthal observations

        freq : int
            number of profiles used to calculate
            the variance

        """

        variance = data.rolling(
            time=freq, center=True, min_periods=int(freq * 0.3)
        ).var()

        self.radial_variances[name] = variance
        # self.radial_variances['{0}_counts'.format(name)] = groupedData.count(dim='time')

        return self

    #
    #
    ### new approach to calculate the variances ##############

    ### old approach to calculate the variances
    #     def getVariance(self, data, name='rVariance'):

    #         """
    #         This method calculates the variance from the
    #         observed radial velocities within a time window.
    #         The default size of this window is 10 minutes.
    #         """

    #         timeBins = util.getTimeBins(pd.to_datetime(data.time.values[0]), freq=self.timeFreq)
    #         groupedData = data.groupby_bins('time', timeBins)

    #         self.radial_variances[name] = groupedData.var(dim='time')#.apply(calcGroupVar)
    #         self.radial_variances['{0}_counts'.format(name)] = groupedData.count(dim='time')

    #         return self
    #####################################################

    def get_S(self):

        """
        This method fills the observation variance matrix (S).
        """

        S = np.dstack(
            (
                self.radial_variances["rVariance"].values,
                self.radial_variances["rVariance90"].values[
                    :, :, np.newaxis, np.newaxis
                ],
            )
        )

        self.S = S

    def get_SIGMA(self):

        """
        This method calculates the components of the
        Reynolds stress tensor (SIGMA).

        SIGMA = M^-1 x S
        """

        self.SIGMA = np.matmul(self.M_inv, self.S)

        return self

    def get_variance_ds(self):

        """
        This method converts the SIGMA into a xarray dataset.
        """

        var_comp_ds = xr.Dataset()
        var_comp_name = ["u", "v", "w", "uv", "uw", "vw"]

        for i, var_comp in enumerate(var_comp_name):

            tmp_data = xr.DataArray(
                self.SIGMA[:, :, i, 0],
                dims=("time", "range"),
                coords={
                    "time": self.radial_variances["rVariance90"].time,
                    "range": self.radial_variances["rVariance"].range,
                },
                name=f"var_{var_comp}",
            )

            var_comp_ds = xr.merge([var_comp_ds, tmp_data])

        self.var_comp_ds = var_comp_ds
