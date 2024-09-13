from smarketsim.v2 import model
from smarketsim.v2 import mfeature
import json
import datetime
import numpy
import pickle


def _max_head(desc):
    maxh = 0
    for lcf in desc:
        for col in desc[lcf]["X_cols"]:
            if col[0:4] == "PERC":
                head = mfeature.perc_compute_head(int(col[4:]))
                if head > maxh:
                    maxh = head
            else:
                vind = col.find("V")
                head = mfeature.vol_compute_head(int(col[2:vind]), int(col[vind + 3 :]))
                if head > maxh:
                    maxh = head
        head = mfeature.corr_compute_head(
            int(desc[lcf]["LC"][2:]), desc[lcf]["corr_size"]
        )
        if head > maxh:
            maxh = head
    return maxh


def _advance_date(date):
    new_date = datetime.datetime.strptime(date, "%Y-%m-%d")
    if new_date.weekday() == 4:
        new_date += datetime.timedelta(3)
    else:
        new_date += datetime.timedelta(1)
    return datetime.datetime.strftime(new_date, "%Y-%m-%d")


def _compute_vol_desc(desc):
    vols = {}
    for y_col in desc:
        for col in desc[y_col]["X_cols"]:
            if "VOL" in col:
                vind = col.find("V")
                lc = int(col[2:vind])
                size = int(col[vind + 3 :])
                if lc not in vols:
                    vols[lc] = []
                if size not in vols[lc]:
                    vols[lc].append(size)
    return vols


def _compute_perc_desc(desc):
    percs = []
    for y_col in desc:
        for col in desc[y_col]["X_cols"]:
            if "PERC" in col:
                size = int(col[4:])
                if size not in percs:
                    percs.append(size)
    return percs


def _compute_vol(df, vols):
    for step in vols:
        for size in vols[step]:
            datei = max(df.index)
            df.at[datei, "LC" + str(step) + "VOL" + str(size)] = numpy.std(
                df.head(size)["LC" + str(step)]
            )
    return df


def _compute_perc(df, percs):
    for size in percs:
        datei = max(df.index)
        low = numpy.min(df.head(size)["Low"])
        high = numpy.max(df.head(size)["High"])
        if high == low:
            df.at[datei, "PERC" + str(size)] = 0.5
        else:
            P = df.at[datei, "Close"]
            df.at[datei, "PERC" + str(size)] = (P - low) / (high - low)
    return df


class MFeatSim:
    def __init__(self):
        return

    def write(self, folder, name):
        with open(folder + name + "-metadata.json", "w") as file:
            json.dump(
                {
                    "vol": self.vols,
                    "perc": self.percs,
                    "tickers": list(self.mfeats.keys()),
                },
                file,
            )
        for ticker in self.mfeats:
            with open(folder + name + "-" + ticker + ".pickle", "wb") as file:
                pickle.dump(self.mfeats[ticker], file)

    def read(self, folder, name):
        with open(folder + name + "-metadata.json", "r") as file:
            mdata = json.load(file)
            self.vols = dict(mdata["vol"])
            self.percs = list(mdata["perc"])
            self.mfeats = {ticker: None for ticker in list(mdata["tickers"])}
        for ticker in self.mfeats:
            with open(folder + name + "-" + ticker + ".pickle", "rb") as file:
                self.mfeats[ticker] = pickle.load(file)

    def add(self, date, res):
        for y_col in res:
            for ticker in res[y_col]:
                date_bef = max(self.mfeats[ticker].index)
                self.mfeats[ticker].at[date, y_col] = res[y_col][ticker]
                self.mfeats[ticker].at[date, "Open"] = (
                    numpy.exp(res["LCF1"][ticker])
                    * self.mfeats[ticker].at[date_bef, "Open"]
                )
                self.mfeats[ticker].at[date, "High"] = (
                    numpy.exp(res["LCF1"][ticker])
                    * self.mfeats[ticker].at[date_bef, "High"]
                )
                self.mfeats[ticker].at[date, "Low"] = (
                    numpy.exp(res["LCF1"][ticker])
                    * self.mfeats[ticker].at[date_bef, "Low"]
                )
                self.mfeats[ticker].at[date, "Close"] = (
                    numpy.exp(res["LCF1"][ticker])
                    * self.mfeats[ticker].at[date_bef, "Close"]
                )
                self.mfeats[ticker] = self.mfeats[ticker].sort_index(ascending=False)
                self.mfeats[ticker] = _compute_vol(self.mfeats[ticker], self.vols)
                self.mfeats[ticker] = _compute_perc(self.mfeats[ticker], self.percs)

    def create(self, parq, tickers, date, desc):
        self.vols = _compute_vol_desc(desc)
        self.percs = _compute_perc_desc(desc)
        self.mfeats = {}
        for ticker in tickers:
            mfeat = mfeature.MFeat()
            mfeat.from_parq(parq, ticker)
            mfeat.df = mfeat.df[mfeat.df.index <= date]
            mfeat.df = mfeat.df.head(_max_head(desc))
            self.mfeats[ticker] = mfeat.df


class Simulation:
    def __init__(self):
        return

    def build(self, parq, tickers, desc, date):
        self.parq = parq
        self.date = date
        self.model = model.Model()
        self.model.fit_parq(parq, desc, tickers, date)
        self.mfs = MFeatSim()
        self.mfs.create(parq, tickers, date, desc)

    def write_sim(self, folder, name):
        with open(folder + name + "-simdata.json", "w") as file:
            json.dump([self.parq, self.date], file)
        self.mfs.write(folder + name + "-", "mfs")
        self.model.write_model(folder + name + "-", "mod")

    def read_sim(self, folder, name):
        with open(folder + name + "-simdata.json", "r") as file:
            lst = json.load(file)
            self.parq = lst[0]
            self.date = lst[1]
        self.model = model.Model()
        self.model.read_model(folder + name + "-", "mod")
        self.mfs = MFeatSim()
        self.mfs.read(folder + name + "-", "mfs")

    def _advance(self, res):
        self.date = _advance_date(self.date)
        self.mfs.add(self.date, res)

    def sim(self):
        data_series = {}
        for ticker in self.model.indexes:
            mfdf = self.mfs.mfeats[ticker]
            data_series[ticker] = mfdf.loc[self.date]
        res = self.model.sample(data_series)
        self._advance(res)
