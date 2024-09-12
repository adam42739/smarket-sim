from smarketsim.v2 import model
from smarketsim.v2 import mfeature
import json


class Simulation:
    def __init__(self):
        return

    def build(self, parq, tickers, desc, date):
        self.parq = parq
        self.date = date
        self.model = model.Model()
        self.model.fit_parq(parq, desc, tickers, date)

    def write_sim(self, folder, name):
        with open(folder + name + "-simdata.json", "w") as file:
            json.dump([self.parq, self.date], file)
        self.model.write_model(folder, name)

    def read_sim(self, folder, name):
        with open(folder + name + "-simdata.json", "r") as file:
            lst = json.load(file)
            self.parq = lst[0]
            self.date = lst[1]
        self.model = model.Model()
        self.model.read_model(folder, name)

    def sim(self):
        data_series = {}
        for ticker in self.model.indexes:
            mfeat = mfeature.MFeat()
            mfeat.from_parq(self.parq, ticker)
            data_series[ticker] = mfeat.df.loc[self.date]
        res = self.model.sample(data_series)
        return res
