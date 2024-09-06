from smarketsim import model
from smarketsim import stocks
import pandas
import datetime


import numpy


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


class Simulation:
    def __init__(self):
        return

    def _get_changes(self, base, downloads, tickers, date, step, look_back):
        self.changes = stocks.get_changes(base, tickers, step, date, downloads)
        self.changes = _get_change_subset(self.changes, date, look_back)
        if len(self.changes) == look_back:
            self.numna = {}
            for ticker in self.changes:
                numna = self.changes[ticker].isna().sum()
                self.changes[ticker] = self.changes[ticker].fillna(0)
                self.numna[ticker] = numna
            return True
        else:
            return False

    def fit_sim(
        self, base, downloads, tickers, date, step, look_back, lr_rate, mlog_dim
    ):
        self._get_changes(base, downloads, tickers, date, step, look_back)
        self.model = model.Model()
        self.model.fit(self.changes, mlog_dim, lr_rate)

    def sim_days(self, days):
        return self.model.sample(days)
