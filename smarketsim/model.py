from smarketsim import metalog
import numpy
from numpy.random import multivariate_normal
import pandas
import datetime


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

    def fit(self, changes, date, look_back, mlog_dim):
        changes = _get_change_subset(changes, date, look_back)
        if len(changes) == look_back:
            for ticker in changes.columns:
                series = changes[ticker]
                numna = series.isna().sum()
                print(series.head())
                print(series.isna().sum())
            a = 0
            return True
        else:
            return False
