from smarketsim import metalog
import numpy
import scipy.stats


class Model:
    def __init__(self):
        return

    def _fit_model(self):
        self.metadata = {}
        stacker = []
        i = 0
        for ticker in self.changes.columns:
            series = self.changes[ticker]
            stacker.append(series)
            mlog = metalog.Metalog(self.mlog_dim)
            mlog.fit(series.values, self.lr_avg)
            self.metadata[i] = {"ticker": ticker, "mlog": mlog}
            i += 1
        X = numpy.stack(stacker, axis=0)
        self.cov = numpy.corrcoef(X)

    def fit(self, changes, mlog_dim, lr_avg):
        self.lr_avg = lr_avg
        self.changes = changes
        self.mlog_dim = mlog_dim
        self._fit_model()

    def _sample_ndarray(self):
        y = numpy.random.multivariate_normal(numpy.zeros(len(self.metadata)), self.cov)
        y = scipy.stats.norm.cdf(y)
        for i in range(0, len(y)):
            y[i] = self.metadata[i]["mlog"].quantile(y[i])
        return y

    def _init_sample(self):
        samp = {}
        for i in self.metadata:
            samp[self.metadata[i]["ticker"]] = 0
        return samp

    def sample(self, amount):
        samp = self._init_sample()
        for i in range(0, amount):
            y = self._sample_ndarray()
            for j in self.metadata:
                samp[self.metadata[j]["ticker"]] += y[j]
        return samp
