from smarketsim.v2 import datasets
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from smarketsim.v2 import metalog
import numpy


DSET_N = 1000
DSET_PACKET = 100

PCA_KEEP = 2

KNN_NEIGHBOORS = 50

MLOG_PREC_COUNT = 10


class Model:
    def __init__(self):
        return

    def _perform_PCA(self, X_cols):
        self.X_cols = X_cols
        self.X = self.dset.df[X_cols]
        self.pca = PCA(n_components=PCA_KEEP)
        self.pca_Xtran = self.pca.fit_transform(self.X.values)

    def _config_dset(self, parq, train_before):
        self.dset = datasets.Dataset()
        self.dset.load_from_parq(parq)
        self.dset.split(train_before)
        self.dset.rng_sample_pop(DSET_N, DSET_PACKET, True)

    def _perc(self, i):
        return numpy.percentile(
            self.pca_Xtran, 100 * (i + 0.5) / MLOG_PREC_COUNT, axis=0
        )

    def _compute_percs(self, iter):
        self.mlog_percs[iter] = []
        for i in range(0, MLOG_PREC_COUNT):
            self.mlog_percs[iter].append(self._perc(i)[iter])

    def _config_mlog(self, y_col, mlog_dim):
        self.knn = NearestNeighbors(n_neighbors=KNN_NEIGHBOORS)
        self.knn.fit(self.pca_Xtran)
        self.mlog_percs = {}
        self._compute_percs(0)
        self._compute_percs(1)
        self.mlogs = {}
        for i in range(0, MLOG_PREC_COUNT):
            self.mlogs[i] = {}
            for j in range(0, MLOG_PREC_COUNT):
                indexes = self.knn.kneighbors(
                    [[self.mlog_percs[0][i], self.mlog_percs[1][j]]],
                    return_distance=False,
                )
                indexes = indexes[0]
                array = []
                for index in indexes:
                    array.append(self.dset.df.at[index, y_col])
                self.mlogs[i][j] = metalog.Metalog(mlog_dim)
                self.mlogs[i][j].fit(array)

    def fit_parq(self, parq, X_cols, y_col, train_before, mlog_dim):
        self._config_dset(parq, train_before)
        self._perform_PCA(X_cols)
        self._config_mlog(y_col, mlog_dim)

    def _get_perc_index(self, val, iter):
        index = 0
        while index < MLOG_PREC_COUNT:
            if val < self.mlog_percs[iter][index]:
                break
            index += 1
        return index

    def predict(self, series):
        s_tran = self.pca.transform([series[self.X_cols]])[0]
        i = self._get_perc_index(s_tran[0], 0)
        j = self._get_perc_index(s_tran[1], 1)
        mlog = self.mlogs[i][j]
        return mlog
