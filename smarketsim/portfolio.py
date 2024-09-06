from smarketsim import simulation
import math

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
    def __init__(self, base, downloads, stocks, date):
        self.base = base
        self.downloads = downloads
        self.stocks = stocks
        self.date = date
        self.samps = {i: [] for i in MODELS}

    def _fit_model(self, model_index):
        self.sim = simulation.Simulation()
        return self.sim.fit_sim(
            self.base,
            self.downloads,
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
            val += raw_samp[ticker] * self.stocks[ticker]
        return val

    def _sim_model(self, model_index):
        if self._fit_model(model_index):
            for i in range(0, MONTE_SIM_NUM):
                raw_samp = self.sim.sim_forward(MODELS[model_index][FORWARD])
                self.samps[model_index].append(self._raw_to_value(raw_samp))
        else:
            self.samps[model_index] = None

    def sim_models(self):
        for i in MODELS:
            self._sim_model(i)
