import smarketsim
import yfscraper
import json
import datetime
import random


TICKERS = "validation/tickers.json"
FAILED = "validation/failed.json"
BASE = "validation/base/"
SIM_FILES = "validation/sim_files/"
SIM_PERCS = "validation/sim_percs.json"

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


def get_lookback_date(date):
    look_back = 0
    for model_index in smarketsim.MODELS:
        back_req = (
            smarketsim.MODELS[model_index][smarketsim.STEP]
            + smarketsim.MODELS[model_index][smarketsim.LOOKBACK]
        )
        if back_req > look_back:
            look_back = back_req
    look_back = int(365 / 252 * look_back + 10)
    return date - datetime.timedelta(look_back)


def get_stocks_meta():
    return yfscraper.v2.get_metadata(BASE)


def get_avail_tickers(date):
    stocks = get_stocks_meta()
    first_date = get_lookback_date(date)
    tickers = []
    for ticker in stocks:
        if stocks[ticker]["start_date"] < first_date:
            tickers.append(ticker)
    return tickers


def random_port(date, port_size_max):
    tickers = get_avail_tickers(date)
    if len(tickers) > 0:
        random.shuffle(tickers)
        port = {}
        for i in range(0, random.randrange(2, min(port_size_max, len(tickers)))):
            port[tickers[i]] = random.random()
        return port
    else:
        return None


def get_changes(tickers, date, days_out):
    days_for = int(365 / 252 * days_out + 10)
    max_date = date + datetime.timedelta(days_for)
    changes = smarketsim.get_changes(BASE, tickers, 1, max_date)
    changes = changes[changes.index <= max_date]
    changes = changes[changes.index > date]
    return changes


def port_perf_real(port, date, days_out):
    changes = get_changes(list(port.keys()), date, days_out)
    changes["_INDEX"] = 1
    changes["_PORT"] = 0
    for ticker in changes.columns:
        if ticker != "_PORT" and ticker != "_INDEX":
            changes["_PORT"] += changes[ticker] * port[ticker]
    changes = changes[["_PORT", "_INDEX"]]
    last_index = None
    for date_index in changes.index.values:
        if last_index:
            changes.loc[date_index] += changes.loc[last_index]
        last_index = date_index
    changes = changes.set_index("_INDEX")
    return changes


def sim_port(port, date, port_num):
    _sim_port = smarketsim.Portfolio()
    _sim_port.init_sim(BASE, port, date)
    _sim_port.sim_models()
    return _sim_port


def sim_port_percs(_sim_port, changes):
    percs = {}
    for model_index in smarketsim.MODELS:
        forward = (
            smarketsim.MODELS[model_index][smarketsim.STEP]
            * smarketsim.MODELS[model_index][smarketsim.FORWARD]
        )
        perf_forward = changes["_PORT"][forward]
        perc_forward = _sim_port.sim_est_perc(perf_forward, model_index)
        percs[model_index] = perc_forward
    return percs


def validate(date, max_port_size):
    port = random_port(date, max_port_size)
    if port:
        changes = port_perf_real(port, date, 20 * 60)
        _sim_port = sim_port(port, date, 1)
        return sim_port_percs(_sim_port, changes)
    else:
        return None


def rng_date():
    forward = (
        smarketsim.MODELS[len(smarketsim.MODELS)][smarketsim.STEP]
        * smarketsim.MODELS[len(smarketsim.MODELS)][smarketsim.FORWARD]
    )
    forward_days = int(365 / 252 * forward + 10)
    return END_DATE - datetime.timedelta(forward_days)


def validate_random(max_port_size, num):
    percs = {}
    with open(SIM_PERCS, "r") as file:
        percs = dict(json.load(file))
    for i in range(0, num):
        date = rng_date()
        valid_perc = validate(date, max_port_size)
        if valid_perc:
            percs[len(percs)] = valid_perc
            with open(SIM_PERCS, "w") as file:
                json.dump(percs, file)


validate_random(30, 5)
