import yfscraper
import numpy
import pandas


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
