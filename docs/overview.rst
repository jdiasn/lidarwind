==========================
Scanning strategy overview
==========================

.. _overview:

Due to the current transition from fossil fuel-based power plants to renewable sources, wind has become one of the main energy sources. However, to identify the places where wind harvest is suitable for power production, an understanding of how the wind blows in the possible places is needed. Wind Doppler lidars are often used to survey the winds in those places and to estimate turbulence.

Wind Doppler lidars work by transmitting laser pulses and measuring the shift in frequency of the backscattered signal, the Doppler effect. If the scatterers are moving towards the lidar, the backscattered signal's frequency is higher than that of the transmitted signal and the other way around.

There are different scanning strategies for estimating wind profiles using Wind Doppler lidars, but two are used more often: the 6-beam and the DBS.

-------
6-beam:
-------

.. _six-beam:

Reynolds stress tensor calculation
----------------------------------

The 6-beam is a scanning strategy that is idealised for retrieving turbulence. This method measures the radial velocity at five azimuths (0, 72, 144, 216, 288º) with a certain elevation angle and one additional observation at 90º elevation. The cartoon below illustrates the geometry of this strategy.

.. figure:: /figures/six_beam.png
	:scale: 15%
	:align: center

`Sathe et al.,2015 <https://amt.copernicus.org/articles/8/729/2015/>`_  suggested that the variance of each radial observation can be expressed in terms of variances and co-variances of u (zonal wind), v (meridional wind), and w (vertical wind), as indicated below. :math:`\theta` and :math:`\phi` are the azimuth and elevation angles, respectively.

.. math::

    var(v_{\theta}) = var(u)cos^2(\phi)sin^2(\theta) + var(v)cos^2(\phi)cos^2(\theta) + var(w)sin^2(\phi) \\
    + 2cov(u,v)cos^2(\phi)cos(\theta)sin(\theta) + 2cov(u,w)cos(\phi)sin(\phi)sin(\theta) \\
    + 2 cov(v,w)cos(\phi)sin(\phi)cos(\theta)


Combining all the equations for each one of the six observations makes it possible to solve this equation system for the variances and co-variances of u, v, and W, which are the Reynolds stress tensor components.

.. math::

    \stackrel{\Sigma}{\mathrm{M}
    \begin{bmatrix} var(u)\\ var(v)\\ var(w)\\
                    cov(u,v)\\ cov(u,w)\\ cov(v,w)\end{bmatrix}} =
    \stackrel{S}{\begin{bmatrix} var(v_{0})\\ var(v_{72})\\ var(v_{144})\\
                    var(v_{216})\\ var(v_{288})\\ var(v_{zenith})
    \end{bmatrix}}




The calculation is made by solving the following equation: :math:`\Sigma = M^{-1}S`, and it is implemented in SixBeamMethod class.



Wind speed and direction estimation
-----------------------------------

Even though the 6-beam strategy makes it possible to calculate the Reynolds stress tensor directly, the horizontal wind speed and direction estimation is not straightforward. One of the possible ways to estimate the wind speed and direction is using the Fast Fourier Wind Vector Algorithm (FFWVA) developed by `Ishwardat, 2017 <http://resolver.tudelft.nl/uuid:a659654b-e76a-4513-a656-ecad761bdbc8>`_.

The FFWVA uses Fast Fourier Transform (FFT) digital signal-processing algorithms to decompose the radial Doppler observations in terms of amplitude and phase of their harmonic frequencies. The wind speed :math:`V_{s}` and direction :math:`V_{d}` can be calculated using the amplitude and phase from the first harmonic, as indicated below.

.. math::
    a + bi = \mathrm{FFT}(v_{\theta})|_{1st}

.. math::
    V_{s} = \frac{2|a+bi|}{Ncos(\phi)}

.. math::
    V_{d} = -arctan2(a/b)+180\\



a and b are the real and imaginary parts from the first harmonic. :math:`v_{\theta}` is the radial velocity from each azimuth. N is the number of data points used to calculate the FFT decomposition. Note: the `arctan2 <https://numpy.org/doc/stable/reference/generated/numpy.arctan2.html>`_ function returns the correct quadrant. This method is implemented in the class RetriveWindFFT.


--------
The DBS:
--------

.. _DBS:

DBS stands for Doppler beam swing. This scanning strategy consists in measuring the radial velocity at four particular azimuths using a slanted beam swinging from North to South and from East to West. The carton below illustrates how those observations are collected.

.. figure:: /figures/dbs.png
	:scale: 15%
	:align: center

As the measurements are taken using beams with a specific elevation angle :math:`\phi`, all four observed radial velocities contain information from the vertical and horizontal wind, as indicated by the equations listed below. The indexes N, S, E, and W, stand for North, South, East and West :math:`u` and :math:`v` are the zonal and meridional wind components.

.. math::

    V_{rN} = v_{N}cos(\phi) + w_{N}sin(\phi) \\
    V_{rS} = -v_{S}cos(\phi) + w_{S}sin(\phi) \\
    V_{rE} = u_{E}cos(\phi) + w_{E}sin(\phi) \\
    V_{rW} = -u_{W}cos(\phi) + w_{W}sin(\phi) \\

For estimating the meridional (south-north) and zonal (west-est) wind components, it is assumed that the meridional and zonal wind components remain constant during the entire scanning cycle, which implies that :math:`v_{N} = v_{S} = v` and :math:`u_{E} = u_{W} = u`. Applying this assumption to the set of equations listed above and then subtracting the South from the North component and the West from the East component, it is possible to estimate the mean zonal and meridional wind.

.. math::
    v = \frac{v_{N} - v_{S}}{2 cos(\phi)} \\
    u = \frac{u_{E} - u_{W}}{2 cos(\phi)} \\

From those components, it is also possible to estimate the magnitude of the horizontal :math:`V_{h}` wind and its direction :math:`V_{d}`. Note: the `arctan2 <https://numpy.org/doc/stable/reference/generated/numpy.arctan2.html>`_ function returns the correct quadrant.


.. math::
    V_{s} = \sqrt(u^{2} + v^{2}) \\
    V_{d} = 180 + arctan2(-u,-v))

This method is also implemented in this package and is available in class GetWindProperties5Beam.
