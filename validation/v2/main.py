import smarketsim.v2 as smarketsim
import datetime
import yfscraper.v2 as yfscraper
import json
import pandas
import random


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


def get_start_stops():
    return yfscraper.get_metadata(BASE)


def avail_tickers(start_date: datetime.datetime):
    metadata = yfscraper.get_metadata(BASE)
    tickers = []
    for ticker in metadata:
        if metadata[ticker]["start_date"] < start_date:
            tickers.append(ticker)
    return tickers


def get_ticker_price(ticker: str, date: datetime.datetime):
    df = yfscraper.get_data(ticker, BASE)
    return df[df["Date"] == date]["Close"].values[0]


def get_tickers_prices(tickers: list[str], date: datetime.datetime):
    prices = {}
    for ticker in tickers:
        prices[ticker] = get_ticker_price(ticker, date)
    return prices


AVAIL_FORWARD_DAYS = 100


def random_start_date():
    mdays = get_mdays()
    new_mdays = []
    min_day = min(mdays) + datetime.timedelta(smarketsim.AVAIL_BACK_DAYS)
    max_day = max(mdays) - datetime.timedelta(AVAIL_FORWARD_DAYS)
    for day in mdays:
        if day > min_day and day < max_day:
            new_mdays.append(day)
    random.shuffle(new_mdays)
    return datetime.datetime(new_mdays[0].year, new_mdays[0].month, new_mdays[0].day)


def compute_avail_date(date: datetime.datetime):
    return date - datetime.timedelta(smarketsim.AVAIL_BACK_DAYS)


MIN_PORT_SIZE = 5
MAX_PORT_SIZE = 30


def random_port() -> dict:
    start_date = None
    avail_date = None
    tickers = []
    while len(tickers) < MIN_PORT_SIZE:
        start_date = random_start_date()
        avail_date = compute_avail_date(start_date)
        tickers = avail_tickers(avail_date)
        psize = random.randrange(MIN_PORT_SIZE, MAX_PORT_SIZE)
        random.shuffle(tickers)
        tickers = tickers[0:psize]
    port = {}
    t_port_v = 0
    for ticker in tickers:
        port[ticker] = random.random()
        t_port_v += port[ticker]
    prices = get_tickers_prices(tickers, start_date)
    for ticker in port:
        port[ticker] = (port[ticker] / t_port_v) / prices[ticker]
    return {"PORT": port, "DATE": start_date}


def write_port(sim_name: str, port: dict):
    port["DATE"] = datetime.datetime.strftime(port["DATE"], "%Y-%m-%d")
    with open(SIM_FILES + sim_name + "-port.json", "w") as file:
        json.dump(port, file)


def read_port(sim_name: str) -> dict:
    port = None
    with open(SIM_FILES + sim_name + "-port.json", "r") as file:
        port = json.load(file)
    port["DATE"] = datetime.datetime.strptime(port["DATE"], "%Y-%m-%d")
    return port


SIM_DAYS = 50


def build_rng_port(sim_name: str):
    port = random_port()
    sim = smarketsim.Simulation()
    sim.build(
        PARQ_FOLDER,
        list(port["PORT"].keys()),
        datetime.datetime.strftime(port["DATE"], "%Y-%m-%d"),
    )
    sim.write_sim(SIM_FILES, sim_name)
    write_port(sim_name, port)


def port_value(sim_name: str, days: int) -> float:
    sim = smarketsim.Simulation()
    sim.read_sim(SIM_FILES, sim_name)
    sim.sim(days)
    df = sim.last_ntcloses(1)
    series = df.loc[df.index.values[0]]
    port = read_port(sim_name)
    value = 0
    for ticker in df.columns:
        value += series[ticker] * port["PORT"][ticker]
    return value


def port_sdists(sim_name: str, days: list[int], N: int) -> dict:
    sdists = {}
    for day in days:
        sdists[day] = []
        for i in range(0, N):
            sdists[day].append(port_value(sim_name, day))
    return sdists


def port_prices(sim_name: str, days: int) -> dict:
    sim = smarketsim.Simulation()
    sim.read_sim(SIM_FILES, sim_name)
    sim.sim(days)
    df = sim.last_ntcloses(1)
    series = df.loc[df.index.values[0]]
    prices = {}
    for ticker in df.columns:
        prices[ticker] = series[ticker]
    return prices


def port_pdists(sim_name: str, days: list[int], N: int) -> dict:
    pdists = {}
    for day in days:
        pdists[day] = {}
        for i in range(0, N):
            prices = port_prices(sim_name, day)
            if i == 0:
                for ticker in prices:
                    pdists[day][ticker] = []
            else:
                for ticker in prices:
                    pdists[day][ticker].append(prices[ticker])
    return pdists


def write_pdists(pdists: dict, sim_name: str, pdists_name: str):
    with open(SIM_FILES + sim_name + "-pdists-" + pdists_name + ".json", "w") as file:
        json.dump(pdists, file)


def read_pdists(sim_name: str, pdists_name: str) -> dict:
    pdists = None
    with open(SIM_FILES + sim_name + "-pdists-" + pdists_name + ".json", "r") as file:
        pdists = json.load(file)
    return pdists


# download_all_tickers(END_DATE)
# build_parq()
