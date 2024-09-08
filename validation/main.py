import smarketsim
import yfscraper
import json
import datetime


TICKERS = "validation/tickers.json"
FAILED = "validation/failed.json"
BASE = "validation/base/"

END_DATE = datetime.datetime(2024, 9, 1)


def _get_tickers():
    tickers = None
    with open(TICKERS, "r") as file:
        tickers = list(json.load(file))
    return tickers


def download_all_tickers(end_date):
    tickers = _get_tickers()
    tickers = tickers[0:5]
    failed = yfscraper.v2.download_data(tickers, BASE, end_date)
    with open(FAILED, "w") as file:
        json.dump(failed, file)


download_all_tickers(END_DATE)
