import yfscraper
import math


def _ticker_to_get(base, tickers, date):
    metadata = yfscraper.get_metadata(base)
    to_get = []
    for ticker in tickers:
        if ticker not in metadata:
            to_get.append(ticker)
        elif metadata[ticker] < date:
            to_get.append(ticker)
    return to_get


def _update_prices(base, tickers, date, downloads):
    to_get = _ticker_to_get(base, tickers, date)
    if len(to_get) > 0:
        yfscraper.download_data(to_get, downloads, base)


def _get_stock(base, ticker):
    price = yfscraper.get_data(ticker, base)
    price["Index"] = price.index.values
    index = price[["Date", "Index"]]
    index = index.set_index("Date")
    index = index.to_dict()
    price = price[["Close"]]
    price = price.to_dict()
    return {"Index": index["Index"], "Price": price["Close"]}


def _get_change(base, ticker, step):
    stock = _get_stock(base, ticker)
    stock["Change"] = {}
    max_index = max(stock["Price"].keys())
    i = max_index
    while i >= step:
        stock["Change"][i] = math.log(stock["Price"][i] / stock["Price"][i - step])
        i -= 1
    return stock


def _add_market_days(changes):
    days = []
    for ticker in changes:
        for date in changes[ticker]["Index"]:
            if date not in days:
                days.append(date)
    days.sort()
    changes["_market_day"] = {}
    for i in range(0, len(days)):
        changes["_market_day"][i] = days[i]
    return changes


def get_changes(base, tickers, step, date, downloads):
    _update_prices(base, tickers, date, downloads)
    changes = {}
    for ticker in tickers:
        changes[ticker] = _get_change(base, ticker, step)
    changes = _add_market_days(changes)
    return changes
