from smarketsim import metalog
import numpy
import pandas
import datetime
import scipy.stats


def _get_change_subset(changes, date, look_back):
    changes.index = pandas.to_datetime(changes.index)
    date_min = pandas.Timestamp(changes.index.min())
    changes = changes[changes.index <= date]
    start_date = date
    found = 0
    while found < look_back and start_date >= date_min:
        if start_date in changes.index:
            found += 1
        start_date -= datetime.timedelta(1)
    changes = changes[changes.index > start_date]
    return changes


class Model:
    def __init__(self):
        return

    def _fit_model(self):
        self.metadata = {}
        stacker = []
        i = 0
        for ticker in self.changes.columns:
            series = self.changes[ticker]
            numna = series.isna().sum()
            series = series.fillna(0)
            stacker.append(series)
            mlog = metalog.Metalog(self.mlog_dim)
            mlog.fit(series.values)
            self.metadata[i] = {"ticker": ticker, "num_na": numna, "mlog": mlog}
            i += 1
        X = numpy.stack(stacker, axis=0)
        self.mu = numpy.mean(X, axis=1)
        self.cov = numpy.corrcoef(X)

    def fit(self, changes, date, look_back, mlog_dim):
        self.changes = _get_change_subset(changes, date, look_back)
        self.date = date
        self.mlog_dim = mlog_dim
        if len(self.changes) == look_back:
            self._fit_model()
            return True
        else:
            return False

    def sample(self):
        y = numpy.random.multivariate_normal(self.mu, self.cov)
        y = scipy.stats.norm.cdf(y)
        samp = {}
        for i in range(0, len(y)):
            samp[self.metadata[i]["ticker"]] = self.metadata[i]["mlog"].quantile(y[i])
        return samp
