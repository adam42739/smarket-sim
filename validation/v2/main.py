import smarketsim.v2 as smarketsim
import datetime
import yfscraper.v2 as yfscraper
import json
import pandas


TICKERS = "validation/tickers.json"
FAILED = "validation/failed.json"
BASE = "validation/base/"
SIM_FILES = "validation/v2/sim_files/"
SIM_PERCS = "validation/v2/sim_percs.json"

START_DATE = datetime.datetime(1990, 1, 1)
END_DATE = datetime.datetime(2024, 9, 1)

PARQ_FOLDER = "validation/v2/parqs/"


def get_tickers():
    tickers = None
    with open(TICKERS, "r") as file:
        tickers = list(json.load(file))
    return tickers


def download_all_tickers(end_date):
    tickers = get_tickers()
    failed = yfscraper.download_data(tickers, BASE, end_date)
    with open(FAILED, "w") as file:
        json.dump(failed, file)


def build_parq():
    smarketsim.build_parq(BASE, PARQ_FOLDER)


MDAY_TIKS = ["AA", "AAON"]


def get_mdays():
    dates = []
    for ticker in MDAY_TIKS:
        df = yfscraper.get_data(ticker, BASE)
        series_dates = pandas.to_datetime(df["Date"]).apply(lambda x: x.date())
        for date in series_dates:
            if date not in dates:
                dates.append(date)
    return dates


# download_all_tickers(END_DATE)
# build_parq()

# sim = smarketsim.Simulation()
# sim.build(PARQ_FOLDER, ["a", "aaon", "aal", "aap", "aa"], "2020-01-03")
# sim.sim(10)
# print(sim.last_ntcloses(12))
