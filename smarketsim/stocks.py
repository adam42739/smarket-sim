import yfscraper
import math
import pandas
import datetime


def _ticker_to_get(base, tickers, date):
    metadata = yfscraper.v2.get_metadata(base)
    to_get = []
    for ticker in tickers:
        if ticker not in metadata:
            to_get.append(ticker)
        elif metadata[ticker]["end_date"] < date:
            to_get.append(ticker)
    return to_get


def _update_prices(base, tickers, date):
    to_get = _ticker_to_get(base, tickers, date)
    if len(to_get) > 0:
        yfscraper.v2.download_data(to_get, base, datetime.datetime.today())


def _get_price(base, ticker):
    metadata = yfscraper.v2.get_metadata(base)
    if ticker in metadata:
        price = yfscraper.v2.get_data(ticker, base)
        price = price[["Date", "Close"]]
        return price
    else:
        return pandas.DataFrame()


def _get_change(base, ticker, step, df_dict):
    df_dict[ticker] = {}
    price = _get_price(base, ticker)
    if not price.empty:
        max_index = price.index.values.max()
        i = max_index
        while i >= step:
            df_dict[ticker][price.at[i, "Date"]] = math.log(
                price.at[i, "Close"] / price.at[i - step, "Close"]
            )
            i -= 1
        return df_dict
    else:
        return None


def get_changes(base, tickers, step, date):
    tickers = yfscraper.v2.yahoo_format(tickers)
    _update_prices(base, tickers, date)
    df_dict = {}
    for ticker in tickers:
        df_dict = _get_change(base, ticker, step, df_dict)
        if df_dict == None:
            return None
    return pandas.DataFrame(df_dict)
