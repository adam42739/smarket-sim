import smarketsim
import datetime
import yfscraper
import json


TICKERS = "validation/tickers.json"
FAILED = "validation/failed.json"
BASE = "validation/base/"
SIM_FILES = "validation/v1/sim_files/"
SIM_PERCS = "validation/v1/sim_percs.json"

START_DATE = datetime.datetime(1990, 1, 1)
END_DATE = datetime.datetime(2024, 9, 1)


def get_tickers():
    tickers = None
    with open(TICKERS, "r") as file:
        tickers = list(json.load(file))
    return tickers


def download_all_tickers(end_date):
    tickers = get_tickers()
    failed = yfscraper.v2.download_data(tickers, BASE, end_date)
    with open(FAILED, "w") as file:
        json.dump(failed, file)
