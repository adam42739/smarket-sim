from smarketsim.v2 import mfeature
import pandas
import random


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
