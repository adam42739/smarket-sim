from smarketsim.v2 import mfeature
import pandas
import random


class Dataset:
    def __init__(self):
        return

    def load_from_base(self, base, desc, highs, parq):
        mfeature.compute_base(base, desc, highs, parq)
        self.load_from_parq(parq)

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
            df = mfeature.from_parquet(self.parq, ticker)
            if prior:
                df = df[df.index < self.split_date]
            else:
                df = df[df.index > self.split_date]
            df = df.reindex()
            for i in range(0, stock_packet):
                index = random.randrange(0, len(df))
                if size == 0:
                    self.df = pandas.DataFrame(columns=df.columns)
                self.df.loc[size] = df.iloc[index]
                size += 1
