from smarketsim.v2 import mfeature
import pandas
import random
import numpy


class Dataset:
    def __init__(self):
        return

    def load_from_parq(self, parq):
        self.parq = parq
        self.tickers = mfeature.get_metadata(parq)

    def split(self, date):
        self.split_date = date

    def rng_sample_pop(self, N, stock_packet, prior=True):
        size = 0
        while size < N:
            index = random.randrange(0, len(self.tickers))
            ticker = self.tickers[index]
            mfeat = mfeature.MFeat()
            mfeat.from_parq(self.parq, ticker)
            if prior:
                mfeat.df = mfeat.df[mfeat.df.index < self.split_date]
            else:
                mfeat.df = mfeat.df[mfeat.df.index > self.split_date]
            mfeat.df = mfeat.df.reindex()
            for i in range(0, stock_packet):
                index = random.randrange(0, len(mfeat.df))
                if size == 0:
                    self.df = pandas.DataFrame(columns=mfeat.df.columns)
                self.df.loc[size] = mfeat.df.iloc[index]
                size += 1


class ChangeAlign:
    def __init__(self):
        return

    def add_date(self, date, changes):
        self.df.loc[date] = changes
        self.df = self.df.sort_index(ascending=False)

    def create(self, parq, tickers, date, LC):
        self.df = pandas.DataFrame()
        for ticker in tickers:
            mfeat = mfeature.MFeat()
            mfeat.from_parq(parq, ticker)
            changes = mfeat.df[[LC]]
            changes = changes[changes.index <= date]
            changes = changes.rename({LC: ticker}, axis="columns")
            if self.df.empty:
                self.df = changes
            else:
                self.df = self.df.merge(changes, left_on="Date", right_on="Date")
        self.df = self.df.dropna()

    def compute_corr(self, size):
        partition = self.df.head(size)
        stacker = []
        for ticker in partition.columns:
            stacker.append(partition[ticker])
        X = numpy.stack(stacker, axis=0)
        return numpy.corrcoef(X)
