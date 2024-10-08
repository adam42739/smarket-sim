from . import datasets
from sklearn.decomposition import PCA
from sklearn.neighbors import NearestNeighbors
from . import metalog
import numpy
import pickle
from numpy.random import multivariate_normal
from scipy.stats import norm
import json
from sklearn.preprocessing import normalize


DSET_N = 1000
DSET_PACKET = 100

PCA_KEEP = 2

KNN_NEIGHBOORS = 50

MLOG_PREC_COUNT = 10

MLOG_DIM = 5


class MetaModel:
    def __init__(self):
        return

    def _perform_PCA(self, X_cols):
        self.X_cols = X_cols
        self.X = self.dset.df[X_cols]
        self.pca = PCA(n_components=PCA_KEEP)
        norm_res = normalize(self.X.values, axis=0, return_norm=True)
        self.norm = norm_res[1]
        self.pca_Xtran = self.pca.fit_transform(norm_res[0])

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

    def _config_mlog(self, y_col):
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
                self.mlogs[i][j] = metalog.Metalog(MLOG_DIM)
                self.mlogs[i][j].fit(array)

    def clean_fitting_data(self):
        del self.X
        del self.dset
        del self.knn
        del self.pca_Xtran

    def fit_parq(self, parq, X_cols, y_col, train_before):
        self._config_dset(parq, train_before)
        self._perform_PCA(X_cols)
        self._config_mlog(y_col)

    def _get_perc_index(self, val, iter):
        index = 0
        while index < MLOG_PREC_COUNT:
            if val < self.mlog_percs[iter][index]:
                return index
            index += 1
        return index - 1

    def predict(self, series):
        s_tran = self.pca.transform([series[self.X_cols] / self.norm])[0]
        i = self._get_perc_index(s_tran[0], 0)
        j = self._get_perc_index(s_tran[1], 1)
        mlog = self.mlogs[i][j]
        return mlog


class Model:
    def __init__(self):
        return

    def write_model(self, folder, name):
        metadata = {}
        for y_col in self.models:
            self.models[y_col]["metamodel"].clean_fitting_data()
            with open(folder + name + "-" + y_col + "-metamodel.bin", "wb") as file:
                pickle.dump(self.models[y_col]["metamodel"], file)
            with open(folder + name + "-" + y_col + "-calgn.bin", "wb") as file:
                pickle.dump(self.models[y_col]["calgn"], file)
            metadata[y_col] = self.models[y_col]["corr_size"]
        with open(folder + name + "-metadata.json", "w") as file:
            json.dump(metadata, file)
        with open(folder + name + "-indexes.json", "w") as file:
            json.dump(self.indexes, file)

    def read_model(self, folder, name):
        with open(folder + name + "-indexes.json", "r") as file:
            self.indexes = json.load(file)
        metadata = {}
        with open(folder + name + "-metadata.json", "r") as file:
            metadata = json.load(file)
        self.models = {}
        for y_col in metadata:
            self.models[y_col] = {}
            with open(folder + name + "-" + y_col + "-metamodel.bin", "rb") as file:
                self.models[y_col]["metamodel"] = pickle.load(file)
            with open(folder + name + "-" + y_col + "-calgn.bin", "rb") as file:
                self.models[y_col]["calgn"] = pickle.load(file)
            self.models[y_col]["corr_size"] = metadata[y_col]

    def fit_parq(
        self,
        parq,
        desc,
        tickers,
        date,
    ):
        self.indexes = {tickers[i]: i for i in range(0, len(tickers))}
        self.models = {}
        for y_col in desc:
            metamodel = MetaModel()
            metamodel.fit_parq(parq, desc[y_col]["X_cols"], y_col, date)
            calgn = datasets.ChangeAlign()
            calgn.create(parq, tickers, date, desc[y_col]["LC"])
            self.models[y_col] = {
                "metamodel": metamodel,
                "calgn": calgn,
                "corr_size": desc[y_col]["corr_size"],
            }

    def predict(self, data_series):
        res = {}
        for y_col in self.models:
            corr = self.models[y_col]["calgn"].compute_corr(
                self.models[y_col]["corr_size"]
            )
            mlogs = {}
            for ticker in data_series:
                series = data_series[ticker]
                mlog = self.models[y_col]["metamodel"].predict(series)
                mlogs[ticker] = mlog
            res[y_col] = {"corr": corr, "mlogs": mlogs}
        return res

    def sample(self, data_series):
        res = self.predict(data_series)
        samp = {}
        for y_col in res:
            norm_Z = multivariate_normal(
                numpy.zeros(len(data_series)), res[y_col]["corr"]
            )
            norm_P = norm.cdf(norm_Z)
            changes = {}
            for ticker in data_series:
                mlog = res[y_col]["mlogs"][ticker]
                index = self.indexes[ticker]
                changes[ticker] = mlog.quantile(norm_P[index])
            samp[y_col] = changes
        return samp
