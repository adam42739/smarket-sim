from smarketsim.v2 import mfeature


class Dataset:
    def __init__(self):
        return

    def load_from_base(self, base, desc, highs, parq):
        mfeature.compute_base(base, desc, highs, parq)
        self.load_from_parq(parq)

    def load_from_parq(self, parq):
        self.tickers = mfeature.get_metadata(parq)

    def split(self, date):
        self.split_date = date
