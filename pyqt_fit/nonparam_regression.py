"""
:Author: Pierre Barbier de Reuille <pierre.barbierdereuille@gmail.com>

Module implementing non-parametric regressions using kernel methods.
"""

from __future__ import division, absolute_import, print_function
from scipy import stats
from scipy.linalg import sqrtm, solve
import scipy
import numpy as np
from .compat import irange
from . import npr_methods, kernels
from .utils import numpy_method_idx

class NonParamRegression(object):
    r"""
    Class performing kernel-based non-parametric regression.

    The calculation is split in three parts:

        - The kernel (:py:attr:`kernel`)
        - Bandwidth computation (:py:attr:`bandwidth`, :py:attr:`covariance`)
        - Regression method (:py:attr:`method`)
    """

    def __init__(self, xdata, ydata, **kwords):
        self._xdata = np.atleast_2d(xdata)
        self._ydata = np.atleast_1d(ydata)
        self._kernel_class = None
        self._covariance = None
        self._cov_fct = None
        self._bandwidth = None
        self._bw_fct = None
        self._method = None
        self._fitted = False
        self._kernel = None
        self._lower = None
        self._upper = None
        self._n = None
        self._d = None

        for kw in kwords:
            setattr(self, kw, kwords[kw])

        if self._kernel is None:
            self.kernel_class = kernels.normal_kernel

        if self._method is None:
            self._method = npr_methods.default_method

    def copy(self):
        res = NonParamRegression.__new__(NonParamRegression)
        # Copy private members: start with a single '_'
        for m in self.__dict__:
            if len(m) > 1 and m[0] == '_' and m[1] != '_':
                obj = getattr(self, m)
                try:
                    setattr(res, m, obj.copy())
                except AttributeError:
                    setattr(res, m, obj)
        return res

    @property
    def kernel(self):
        r"""
        Kernel object. Should provide the following methods:

        ``kernel.pdf(xs)``
            Density of the kernel, denoted :math:`K(x)`
        """
        return self._kernel

    @kernel.setter
    def kernel(self, k):
        self._kernel_class = None
        self._kernel = k

    @property
    def kernel_class(self):
        r"""
        Kernel class. This is useful for kernels whose instance depend on the
        dimension. The constructor of the class should take as argument the
        dimension of the kernel.
        """
        return self._kernel_class

    @kernel_class.setter
    def kernel_class(self, k):
        self._kernel = None
        self._kernel_class = k

    @property
    def bandwidth(self):
        r"""
        Bandwidth of the kernel.

        This is defined as the square root of the covariance matrix
        """
        return self._bandwidth

    @bandwidth.setter
    def bandwidth(self, bw):
        self._bw_fct = None
        self._cov_fct = None
        if callable(bw):
            self._bw_fct = bw
        else:
            self._bandwidth = bw
            self._covariance = None

    @property
    def covariance(self):
        r"""
        Covariance matrix of the kernel.

        It must be of the right dimension!
        """
        return self._covariance

    @covariance.setter
    def covariance(self, cov):
        self._bw_fct = None
        self._cov_fct = None
        if callable(cov):
            self._cov_fct = cov
        else:
            self._covariance = cov
            self._bandwidth = None

    @property
    def lower(self):
        """
        Lower bound of the domain for each dimension
        """
        return self._lower

    @lower.setter
    def lower(self, l):
        l = np.atleast_1d(l)
        assert len(l.shape) == 1, "The lower bound must be at most a 1D array"
        self._lower = l

    @lower.deleter
    def lower(self):
        self._lower = None

    @property
    def upper(self):
        """
        Lower bound of the domain for each dimension
        """
        return self._upper

    @upper.setter
    def upper(self, l):
        l = np.atleast_1d(l)
        assert len(l.shape) == 1, "The upper bound must be at most a 1D array"
        self._upper = l

    @upper.deleter
    def upper(self):
        self._upper = None

    @property
    def xdata(self):
        """
        2D array (D,N) with D the dimension of the domain and N the number of points.
        """
        return self._xdata

    @xdata.setter
    def xdata(self, xd):
        xd = np.atleast_2d(xd)
        assert len(xd.shape) == 2, "The xdata must be at most a 2D array"
        self._xdata = xd

    @property
    def ydata(self):
        """
        1D array (N,) of values for each point in xdata
        """
        return self._ydata

    @ydata.setter
    def ydata(self, yd):
        yd = np.atleast_1d(yd)
        assert len(yd.shape) == 1, "The ydata must be at most a 1D array"
        self._ydata = yd

    @property
    def method(self):
        """
        Regression method itself. It should follow the template of
        :py:class:`pyqt_fit.npr_methods.RegressionKernelMethod`.
        """
        return self._method

    @method.setter
    def method(self, m):
        self._method = m

    @property
    def N(self):
        """
        Number of points in the dataset (set by the fitting)
        """
        return self._n

    @property
    def dim(self):
        """
        Dimension of the domain (set by the fitting)
        """
        return self._d

    def fit(self):
        """
        Method to call to fit the parameters of the fitting
        """
        D, N == self._xdata.shape
        assert self._ydata.shape[0] == N, "There must be as many points for X and Y"
        if self._lower is None:
            self._lower = -np.inf * np.ones((N,), dtype=float)
        if self._upper is None:
            self._upper = np.inf * np.ones((N,), dtype=float)
        self._n = N
        self._d = D
        self._method.fit(self)
        self._fitted = True

    def evaluate(self, points, out=None):
        points = np.asanyarray(points)
        real_shape = points.shape
        assert len(real_shape) < 3, "The input points can be at most a 2D array"
        if len(real_shape) == 0:
            points = points.reshape(1,1)
        elif len(real_shape) == 1:
            points = points.reshape(1, real_shape[0])
        if out is None:
            out = np.empty((points.shape[-1],), dtype=type(y.dtype.type() + 0.))
        else:
            out.shape = (points.shape[-1],)
        self._method.evaluate(self, points, out)
        out.shape = real_shape[-1:]
        return out

    def __call__(self, points, out=None):
        return self.evaluate(points, out)
