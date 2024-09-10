import yfscraper
import numpy
import pandas
import tqdm
import json
import os


def _compute_LC(df, desc):
    for step in list(desc.keys()):
        df["Close_step"] = df["Close"].shift(periods=-step)
        df["LC" + str(step)] = numpy.log(df["Close"] / df["Close_step"])
    return df


def _compute_vol(df, desc):
    for step in list(desc.keys()):
        for size in desc[step]["vol"]:
            df["LC" + str(step) + "VOL" + str(size)] = 0.0
            for i in df.index:
                df.at[i, "LC" + str(step) + "VOL" + str(size)] = numpy.std(
                    df[(df.index >= i) & (df.index < i + size)]["LC" + str(step)]
                )
    return df


def _compute_percs(df, highs):
    for size in highs:
        df["PERC" + str(size)] = 0.0
        for i in df.index:
            low = numpy.min(df[(df.index >= i) & (df.index < i + size)]["Low"])
            high = numpy.max(df[(df.index >= i) & (df.index < i + size)]["High"])
            if high == low:
                df.at[i, "PERC" + str(size)] = 0.5
            else:
                P = df.at[i, "Close"]
                df.at[i, "PERC" + str(size)] = (P - low) / (high - low)
    return df


FEATURE_KEYWORD = ["VOL", "PERC"]


def get(base, ticker, desc, highs):
    df = yfscraper.v2.get_data(ticker, base)
    df = _compute_LC(df, desc)
    df = _compute_vol(df, desc)
    df = _compute_percs(df, highs)
    df = df.dropna()
    COLS = (
        ["LC" + str(step) for step in list(desc.keys())]
        + [
            "LC" + str(step) + "VOL" + str(size)
            for step in list(desc.keys())
            for size in desc[step]["vol"]
        ]
        + ["PERC" + str(size) for size in highs]
    )
    df = df[["Date"] + COLS]
    df = df.set_index("Date")
    return df


def to_parquet(df, folder, ticker):
    path = folder + ticker + ".parquet"
    df.to_parquet(path)


def from_parquet(folder, ticker):
    path = folder + ticker + ".parquet"
    df = pandas.read_parquet(path)
    return df


def get_metadata(parq_folder):
    data = []
    path = parq_folder + "_metadata.json"
    if os.path.exists(path):
        with open(path, "r") as file:
            data = json.load(file)
    return data


def write_metadata(data, parq_folder):
    with open(parq_folder + "_metadata.json", "w") as file:
        json.dump(data, file)


def compute_base(base, desc, highs, parq_folder):
    price_data = yfscraper.v2.get_metadata(base)
    parq_data = get_metadata(parq_folder)
    for ticker in tqdm.tqdm(price_data):
        if ticker not in parq_data:
            df = get(base, ticker, desc, highs)
            to_parquet(df, parq_folder, ticker)
            parq_data.append(ticker)
            write_metadata(parq_data, parq_folder)
