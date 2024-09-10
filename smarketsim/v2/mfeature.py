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
        df = df.set_index("Date")
        return df

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
