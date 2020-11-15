"""cross_validation.py

    Section7

"""

import numpy as np
import os
import pandas as pd
from sklearn.metrics import log_loss, accuracy_score
from sklearn.model_selection import KFold
import sys

ABSPATH = os.path.abspath(__file__)
BASEDIR = os.path.dirname(ABSPATH)
PARENTDIR = os.path.dirname(BASEDIR)

sys.path.append(PARENTDIR)

from utils import (
    ProcessingBase,
)

BaseKFold = KFold

class CrossValidation(ProcessingBase):
    """

    Cross Validation の処理についてまとめる

    """
    def __init__(self, ensemble, fractional_difference=None, fractional_difference_datasets=None):
        """__init__ func

        引数を格納する

        Note:
            fractional_difference object または、fractional_difference_datasets class
            のどちらかを引数として取得できれば、処理を行うことができる
            どちらも入力された場合は、fractional_difference_datasets に対して実行する

        """
        self.ensemble = ensemble
        self.fractional_difference = fractional_difference
        self.fractional_difference_datasets = fractional_difference_datasets

    def cross_validation(self, purged=False):
        """cross_validation func

        Cross Validation の処理を実行する

        Args:
            purged(bool): パージを適用したCVを行うかどうか

        """
        if self.fractional_difference_datasets is None:
            trns_x = self.fractional_difference.frac_diff_df
            cont = self.fractional_difference.bins_sampled
            t1 = self.fractional_difference.events["t1"]

        else:
            trns_x = self.fractional_difference_datasets.frac_diff_concated_df
            cont = self.fractional_difference_datasets.bins_sampled_concated_df
            t1 = self.fractional_difference_datasets.events_concated_df["t1"]

        self.logger.info("cont.describe(): {}".format(cont.describe()))
        hist, bin_edges = np.histogram(cont["bin"])
        self.logger.info("hist: {}".format(hist))
        self.logger.info("bin_edges: {}".format(bin_edges))

        if self.ensemble.main_clf is None:
            avg_u = 10
            self.ensemble.set_RF(avg_u)

        if purged:
            pass
        else:
            self.logger.warn("パージを行わないCVを行います。")
            cv = 2
            cv_gen = KFold(n_splits=cv, shuffle=False, random_state=None)

        score = cv_score(clf=self.ensemble.main_clf, X=trns_x, y=cont["bin"], sample_weight=cont["w"], t1=t1, \
                         cv_gen=cv_gen)
        return score, self.ensemble

def get_train_times(t1, test_times):
    """get_train_times func

    訓練データセットの観測データのパージング
    スニペット 7.1
    test_times を所与として、訓練データの時点を探す

    Args:
        t1(Series): xxx
            - t1.index: xxx
            - t1.value: xxx
        test_times(Series): xxx

    """
    trn = t1.copy(deep=True)
    for i, j in test_times.iteritems():
        # テストデータセットのなかで開始する訓練データ
        df0 = trn[(i <= trn.index) & (trn.index <= j)].index

        # テストデータセットのなかで終了する訓練データ
        df1 = trn[(i <= trn) & (trn <= j)].index

        # テストデータセットを覆う訓練データ
        df2 = trn[(trn.index <= i) & (j <= trn)].index

        trn = trn.drop(df0.union(df1).union(df2))

    return trn

def get_embargo_times(times, pct_embargo):
    """get_embargo_times func

    訓練データのエンバーゴ
    スニペット 7.2

    Args:
        times(xxx): xxx
        pct_embargo(xxx): xxx

    Note:
        各データのエンバーゴ時点を取得(step)

    """
    step = xx

    if step == 0:
        mbrg = pd.Series(times, index=times)
    else:
        mbrg = pd.Series(times[step:], index=times[:-step])
        mbrg = mbrg.append(pd.Series(times[-1], index=times[-step:]))

    return mbrg

class PurgedKFold(BaseKFold):
    """purged_k_fold func

    観測データが重複するときの交差検証クラス
    スニペット 7.3

    Note:
        区間にまたがるラベルに対して、機能するようにKFoldクラスを拡張する
        訓練データのうちテストラベル区間と重複する観測値がパージされる
        テストデータセットは連続的(shuffle=False)で、間に訓練データがないとする

    """
    def __init__(self, n_splits=3, t1=None, pct_embargo=0.1):
        """__init__ func

        t1 の型確認
        変数の設置

        Args:
            n_splits(int): 分割する数
            t1(xxx): xxx
            pct_embargo(float): xxx

        """
        if not isinstance(t1, pd.Series):
            raise ValueError("Label Through Dates must be a pd.Series")

        super().__init__(n_splits, shuffle=False, random_state=None)

        self.t1 = t1
        self.pct_embargo = pct_embargo

    def split(self, X, y=None, groups=None):
        """split func

        Args:
            X(xxx): xxx
            y(xxx): xxx
            groups(xxx): xxx

        Yield:
            xxx: xxx
            xxx: xxx

        """
        if (X.index == self.t1.index).sum() != len(self.t1):
            raise ValueError("X and ThruDateValues must have the same index")

        indices = np.arange(X.shape[0])
        mbrg = int(X.shape[0] * self.pct_embargo)
        test_starts = [(i[0], i[-1] + 1) for i in np.array_split(np.arange(X.shape[0]), self.n_splits)]

        for i, j in test_starts:
            t0 = self.t1.index[i] # テストデータセットの始まり
            test_indices = indices[i:j]
            max_t1_idx = self.t1.index.searchsorted(self.t1[test_indices].max())

            train_indices = self.t1.index.searchsorted(self.t1[self.t1 <= t0].index)
            train_indices = np.concatenate((train_indices, indices[max_t1_idx + mbrg:]))

            yield train_indices, test_indices

def cv_score(clf, X, y, sample_weight, scoring="neg_log_loss", t1=None, cv=3, cv_gen=None, pct_embargo=0.1):
    """cv_score func

    PurgedKFold クラスの使用
    スニペット 7.4

    Note:
        label の値は {-1, 0, 1}のどれか
        しかし、0のデータ数が少なく、学習データに含まれていない場合があり、
        その場合は、テストデータで初めて出てきた0に対し、loss の計算ができなくエラーが出る場合がある
        学習データとテストデータでの逆のケースもでもエラーが生じる

        対策
            データセット数を増やす

    """
    if scoring not in ["neg_log_loss", "accuracy"]:
        raise Exception("wrong scoring method")

    if cv_gen is None:
        # パージ
        cv_gen = PurgedKFold(n_splits=cv, t1=t1, pct_embargo=pct_embargo)

    score = []
    for train, test in cv_gen.split(X=X):
        fit = clf.fit(X=X.iloc[train, :], y=y.iloc[train], sample_weight=sample_weight.iloc[train].values)

        if scoring == "neg_log_loss":
            prob = fit.predict_proba(X.iloc[test, :])
            score_tmp = -log_loss(y.iloc[test], prob, sample_weight=sample_weight.iloc[test].values)
        else:
            pred = fit.predict(X.iloc[test, :])
            score_tmp = accuracy_score(y.iloc[test], pred, sample_weight=sample_weight.iloc[test].values)

        score.append(score_tmp)

    return np.array(score)
