import yfscraper
import numpy
import pandas
import tqdm
import json
import os


class MFeat:
    def __init__(self):
        return

    def from_parq(self, folder, ticker):
        path = folder + ticker + ".parquet"
        self.df = pandas.read_parquet(path)

    def to_parq(self, folder, ticker):
        path = folder + ticker + ".parquet"
        self.df.to_parquet(path)

    def from_price(self, base, ticker):
        self.df = yfscraper.v2.get_data(ticker, base)

    def add_LCF(self, steps):
        for step in steps:
            self.df["Close_step"] = self.df["Close"].shift(periods=step)
            self.df["LCF" + str(step)] = numpy.log(
                self.df["Close"] / self.df["Close_step"]
            )

    def add_LC(self, steps):
        for step in steps:
            self.df["Close_step"] = self.df["Close"].shift(periods=-step)
            self.df["LC" + str(step)] = numpy.log(
                self.df["Close"] / self.df["Close_step"]
            )

    def add_vol(self, vols):
        for step in vols:
            for size in vols[step]:
                self.df["LC" + str(step) + "VOL" + str(size)] = 0.0
                for i in self.df.index:
                    self.df.at[i, "LC" + str(step) + "VOL" + str(size)] = numpy.std(
                        self.df[(self.df.index >= i) & (self.df.index < i + size)][
                            "LC" + str(step)
                        ]
                    )

    def add_percs(self, percs):
        for size in percs:
            self.df["PERC" + str(size)] = 0.0
            for i in self.df.index:
                low = numpy.min(
                    self.df[(self.df.index >= i) & (self.df.index < i + size)]["Low"]
                )
                high = numpy.max(
                    self.df[(self.df.index >= i) & (self.df.index < i + size)]["High"]
                )
                if high == low:
                    self.df.at[i, "PERC" + str(size)] = 0.5
                else:
                    P = self.df.at[i, "Close"]
                    self.df.at[i, "PERC" + str(size)] = (P - low) / (high - low)

    def final_clean(self):
        self.df = self.df.dropna()
        self.df = self.df.set_index("Date")


def get_metadata(parq_folder):
    data = []
    path = parq_folder + "_metadata.json"
    if os.path.exists(path):
        with open(path, "r") as file:
            data = json.load(file)
    return data


def write_metadata(data, parq_folder):
    with open(parq_folder + "_metadata.json", "w") as file:
        json.dump(data, file)


def mfeat_from_base(base, lc_steps, lcf_steps, vol_sizes, percs, parqs):
    tickers = yfscraper.v2.get_metadata(base)
    data = get_metadata(parqs)
    for ticker in tqdm.tqdm(tickers):
        if ticker not in data:
            feat = MFeat()
            feat.from_price(base, ticker)
            feat.add_LC(lc_steps)
            feat.add_LCF(lcf_steps)
            feat.add_vol(vol_sizes)
            feat.add_percs(percs)
            feat.final_clean()
            feat.to_parq(parqs, ticker)
            data.append(ticker)
            write_metadata(data, parqs)
