from . import simulation
import math
import json
import datetime
import numpy
import yfscraper

YEAR_LR_RATE = 1.07
DAILY_LR_RATE = math.log(1.07) / 252

MLOG_DIM = 5

STEP = 0
LOOKBACK = 1
FORWARD = 2
NUMNA = 3

MODELS = {
    1: {STEP: 1, LOOKBACK: 100, FORWARD: 20, NUMNA: 3},
    2: {STEP: 5, LOOKBACK: 400, FORWARD: 20, NUMNA: 12},
    3: {STEP: 20, LOOKBACK: 1000, FORWARD: 20, NUMNA: 30},
    4: {STEP: 60, LOOKBACK: 2000, FORWARD: 20, NUMNA: 60},
}

MONTE_SIM_NUM = 1000


class Portfolio:
    def __init__(self):
        return

    def from_file(self, _dir, name):
        path = _dir + name + ".json"
        write_dict = {}
        with open(path, "r") as file:
            write_dict = json.load(file)
        self.stocks = write_dict["stocks"]
        self.date = datetime.datetime.strptime(write_dict["date"], "%Y%m%d")
        self.samps = dict(write_dict["samps"])
        self.samps = {int(i): self.samps[i] for i in self.samps}

    def init_sim(self, base, stocks, date):
        self.base = base
        self.stocks = {
            yfscraper.v2.yahoo_ticker_format(ticker): stocks[ticker]
            for ticker in stocks
        }
        self.date = date
        self.samps = {i: [] for i in MODELS}

    def _fit_model(self, model_index):
        self.sim = simulation.Simulation()
        return self.sim.fit_sim(
            self.base,
            list(self.stocks.keys()),
            self.date,
            MODELS[model_index][STEP],
            MODELS[model_index][LOOKBACK],
            DAILY_LR_RATE,
            MLOG_DIM,
            MODELS[model_index][NUMNA],
        )

    def _raw_to_value(self, raw_samp):
        val = 0
        for ticker in self.stocks:
            val += numpy.exp(raw_samp[ticker]) * self.stocks[ticker]
        return val

    def _sim_model(self, model_index):
        if self._fit_model(model_index):
            for i in range(0, MONTE_SIM_NUM):
                raw_samp = self.sim.sim_forward(MODELS[model_index][FORWARD])
                self.samps[model_index].append(float(self._raw_to_value(raw_samp)))
        else:
            self.samps[model_index] = None

    def sim_models(self):
        for i in MODELS:
            self._sim_model(i)

    def to_file(self, _dir, name):
        path = _dir + name + ".json"
        write_dict = {
            "stocks": self.stocks,
            "date": datetime.datetime.strftime(self.date, "%Y%m%d"),
            "samps": self.samps,
        }
        with open(path, "w") as file:
            json.dump(write_dict, file)

    def sim_summarize(self):
        for i in MODELS:
            if self.samps[i]:
                print(
                    "Analysis: Next "
                    + str(MODELS[i][FORWARD] * MODELS[i][STEP])
                    + " Days:"
                )
                starting_val = numpy.sum(list(self.stocks.values()))
                vol = numpy.std(self.samps[i]) / pow(starting_val, 2) * 100
                print("    Volatility: ", "{:.2f}".format(vol), "%")
                bot = (numpy.percentile(self.samps[i], 5) / starting_val - 1) * 100
                print("    Bottom 5% Performance: ", "{:.2f}".format(bot), "%")
                top = (numpy.percentile(self.samps[i], 95) / starting_val - 1) * 100
                print("    Top 5% Performance: ", "{:.2f}".format(top), "%")
            else:
                print(
                    "Failed to get analysis for the next "
                    + str(MODELS[i][FORWARD] * MODELS[i][STEP])
                    + " Days."
                )

    def sim_est_perc(self, x, model_index):
        if self.samps[model_index]:
            count = 0
            for samp in self.samps[model_index]:
                if x > samp:
                    count += 1
            return (count + 0.5) / (len(self.samps[model_index]) + 1.0)
        else:
            return None
