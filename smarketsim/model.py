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

    def sample(self):
        y = numpy.random.multivariate_normal(numpy.zeros(len(self.metadata)), self.cov)
        y = scipy.stats.norm.cdf(y)
        samp = {}
        for i in range(0, len(y)):
            samp[self.metadata[i]["ticker"]] = self.metadata[i]["mlog"].quantile(y[i])
        return samp
