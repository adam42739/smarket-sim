import numpy
import random


def _quantile_kth_term(y, k):
    if k == 1:
        return 1
    elif k == 2:
        return numpy.log(y / (1 - y))
    elif k == 3:
        return (y - 0.5) * numpy.log(y / (1 - y))
    elif k == 4:
        return y - 0.5
    elif k % 2 == 1:
        return pow(y - 0.5, (k - 1) / 2)
    else:
        return pow(y - 0.5, k / 2 - 1) * numpy.log(y / (1 - y))


def _get_X_lstsqr(Y, dim):
    X = numpy.zeros((len(Y), dim))
    for i in range(0, len(Y)):
        for k in range(0, dim):
            X[i][k] = _quantile_kth_term(Y[i], k + 1)
    return X


def _get_quantile_vector(x):
    x = numpy.sort(x, kind="quicksort")
    Y = numpy.zeros(len(x))
    for i in range(0, len(x)):
        Y[i] = (i + 0.5) / (len(x) + 1.0)
    return x, Y


class Metalog:
    def __init__(self, dim):
        self._alpha = None
        self._dim = dim

    def cdf(self, x):
        PRECISION = 0.0000001
        l = PRECISION
        r = 1 - PRECISION
        lv = self.quantile(l)
        rv = self.quantile(r)
        if x < lv:
            return PRECISION
        elif x > rv:
            return 1 - PRECISION
        else:
            m = None
            for i in range(0, int(numpy.log2(1 / PRECISION))):
                m = (r + l) / 2
                mv = self.quantile(m)
                if x < mv:
                    r = m
                    rv = mv
                else:
                    l = m
                    lv = mv
            return m

    def quantile(self, y):
        value = 0
        for k in range(0, len(self._alpha)):
            value += self._alpha[k] * _quantile_kth_term(y, k + 1)
        return value

    def sample(self):
        rng = random.random()
        while rng == 0:
            rng = random.random()
        return self.quantile(rng)

    def fit(self, x):
        x, Y = _get_quantile_vector(x)
        X = _get_X_lstsqr(Y, self._dim)
        self._alpha = numpy.linalg.lstsq(X, x, rcond=None)[0]
