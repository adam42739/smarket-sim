from smarketsim.v2 import datasets
from smarketsim.v2 import mfeature
from sklearn.decomposition import PCA


DSET_N = 1000
DSET_PACKET = 100

PCA_KEEP = 2


class Model:
    def __init__(self):
        return

    def _perform_PCA(self):
        self.pca = PCA(n_components=PCA_KEEP)
        cols = []
        for col in self.dset.df.columns:
            for keyword in mfeature.FEATURE_KEYWORD:
                if keyword in col:
                    cols.append(col)
                    break
        self.pca.fit(self.dset.df[cols])

    def _config_dset(self, parq, train_before):
        self.dset = datasets.Dataset()
        self.dset.load_from_parq(parq)
        self.dset.split(train_before)
        self.dset.rng_sample_pop(DSET_N, DSET_PACKET, True)

    def fit_base(self, base, desc, highs, parq, train_before, mlog_dim):
        mfeature.compute_base(base, desc, highs, parq)
        self.fit_parq(parq, train_before, mlog_dim)

    def _config_mlog(self, mlog_dim):
        return

    def fit_parq(self, parq, train_before, mlog_dim):
        self._config_dset(parq, train_before)
        self._perform_PCA()
        self._config_mlog(mlog_dim)
