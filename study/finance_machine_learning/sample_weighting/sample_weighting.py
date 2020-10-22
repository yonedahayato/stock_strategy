"""sample_weighting.py

    Section4

"""

import numpy as np
import os
import pandas as pd
import sys

ABSPATH = os.path.abspath(__file__)
BASEDIR = os.path.dirname(ABSPATH)
PARENTDIR = os.path.dirname(BASEDIR)
PPARENTDIR = os.path.dirname(PARENTDIR)
PPPARENTDIR = os.path.dirname(PPARENTDIR)

sys.path.append(PARENTDIR)
sys.path.append(PPPARENTDIR)

from multiprocessing_vector.multiprocessing_vector import (
    mp_pandas_obj,
    process_jobs_single,
)

from helper.log import logger

from utils import (
    FilePath
)

file_path = FilePath()

delta = 0.001

class SampleWeighting(object):
    """SampleWeighting class

    標本の重み付けの処理をまとめる

    """
    def __init__(self, labeling):
        self.labeling = labeling
        self.bins, self.events = self.labeling.get_labels()

        self.num_threads = 1
        self.code = labeling.code

        self.bins_save_filename = file_path.get_path(code=self.code, file_type="labels_sampled")

    def sample_weighting(self, check_mc=False, save=False):
        """sample_weighting func

        標本の重み付けの処理

        Args:
            check_mc(bool): モンテカルロ法で逐次ブートストラップ法の有用性を確認するかどうか

        """

        # スニペット 4.1
        # スニペット 4.2 ラベルの平均性の推定
        num_co_events = mp_pandas_obj(func = self.mp_num_co_events,
                                      pd_obj = ("molecule", self.events.index),
                                      num_threads = self.num_threads,
                                      close_idx = self.labeling.close_df.index,
                                      t1 = self.events["t1"])

        num_co_events = num_co_events.loc[~num_co_events.index.duplicated(keep="last")]
        num_co_events = num_co_events.reindex(self.labeling.close_df.index).fillna(0)

        self.bins["tw"] = mp_pandas_obj(self.mp_sample_tw, ("molecule", self.events.index), num_threads=self.num_threads, \
                                        t1=self.events["t1"], num_co_events=num_co_events)

        # スニペット 4.10 絶対リターンの帰属による標本ウェイトの決定
        self.bins["w"] = mp_pandas_obj(self.mp_sample_w, ("molecule", self.events.index), num_threads=self.num_threads, \
                                       t1=self.events["t1"], num_co_events=num_co_events, close = self.labeling.close_df)
        self.bins["w"] *= self.bins.shape[0] / self.bins["w"].sum()

        # スニペット 4.11 時間減衰ファクターの実装
        self.bins["tw"] = get_time_decay(self.bins["tw"], c_if_last_w=0.5)

        # bar_ix = self.get_bar_ix()
        bar_ix = self.labeling.close_df.index
        if check_mc:
            # スニペット 4.8 標準的ブートストラップと逐次ブートストラップによる独自性
            num_iters = 2
            jobs = []
            for i in range(int(num_iters)):
                job = {"func": SampleWeighting.aux_mc, "t1": self.events["t1"], "bar_ix": bar_ix}
                jobs.append(job)

            if self.num_threads == 1:
                out = process_jobs_single(jobs)

            out_df = pd.DataFrame(out)
            print("out_df", out_df)
            print("out_df describe", out_df.describe())

        # スニペット 4.3
        # スニペット 4.4
        ind_matrix = SampleWeighting.get_ind_matrix(bar_ix, self.events["t1"])
        phi = SampleWeighting.seq_bootstrap(ind_matrix)

        phi = list(set(sorted(phi)))
        self.bins_sampled = self.bins.iloc[phi, :]
        logger.info("サンプル前 -> サンプル後: {} -> {}".format(len(self.bins), len(self.bins_sampled)))

        if save:
            print("結果を保存します")
            self.bins_sampled.to_csv(self.bins_save_filename)

    def load(self, csv_path=None):
        """load func

        csv からラベルを読み込む

        """
        self.bins_sampled = pd.read_csv(self.bins_save_filename, index_col=0)
        self.bins_sampled.index = pd.to_datetime(self.bins_sampled.index)

        return self.bins_sampled


    def get_bar_ix(self):
        """get_bar_ix func

        インディケータの計算に必要なbar のインデックスを取得する

        Returns:
            list(int)

        Note:
            self.labeling.close_df と self.events["t1"] を使用
            self.events["t1"] の日付を含む self.labeling.close_df のインデックスを取得する

            2020/10/08 : 必要な bar_ix は数値のインデックスではなく、日付のインデックスだったので
                        この関数は使用しないが、一応残す

        """
        close_df_tmp = self.labeling.close_df.copy(deep=True)
        close_df_tmp = close_df_tmp.reset_index()

        t1 = self.events["t1"].values
        close_df_tmp = close_df_tmp.query("Date in @t1")
        return close_df_tmp.index

    @staticmethod
    def mp_num_co_events(close_idx, t1, molecule):
        """mp_num_co_events func

        バーごとの同時発生的な事象の数を計算する
        スニペット 4.1

        Args:
            close_idx(xxx): xxx
            t1(xxx): xxx
            molecule(list):
                molecule[0]: ウェイトが計算される最初の日付
                molecule[-1]: ウェイトが計算される最後の日付

        Note:
            t1[molecule.nax()] の前に始まる事象はすべて計算に影響する
            おそらくコールバック関数(引数にmolecule があるから)

        """
        # 1: 期間 [ molecule[0], molecule[-1] ]に及ぶ事象を見つける
        # クローズしていない事象は他のウェイトに影響しなければならない
        t1 = t1.fillna(close_idx[-1])

        # 時点 molecule[0] またはその後に終わる事象
        t1 = t1[t1 >= molecule[0]]

        # 時点t1 [molecule].max() またはその前に始まる事象
        t1 = t1.loc[:t1[molecule].max()]

        # 2: バーに及ぶ事象を数える
        iloc = close_idx.searchsorted(np.array(
            [t1.index[0], t1.max()]
        ))
        count = pd.Series(0, index=close_idx[iloc[0]:iloc[1] + 1])
        for t_in, t_out in t1.iteritems():
            count.loc[t_in:t_out] += 1

        return count.loc[molecule[0]:t1[molecule].max()]

    @staticmethod
    def mp_sample_tw(t1, num_co_events, molecule):
        """mp_sample_tw func

        ラベルの平均独自性の推定
        事象の存在期間にわたる平均独自性を導出する
        スニペット 4.2

        Args:
            t1(xxx): xxx
            mp_num_co_events(xxx): xxx
            molecule(xxx): xxx
        """

        wght = pd.Series(index=molecule)
        for t_in, t_out in t1.loc[wght.index].iteritems():
            wght.loc[t_in] = (1.0 / num_co_events.loc[t_in:t_out]).mean()

        return wght

    @staticmethod
    def mp_sample_w(t1, num_co_events, close, molecule):
        """mp_sample_w

        絶対リターンの帰属による標本ウェイトの決定
        リターンの大きさによる標本サイズを調整する
        加法的にするために対数リターンで計算
        スニペット 4.10

        Args:
            t1(xxx): xxx
            num_co_events(xxx): xxx
            close(xxx): xxx
            molecule(xxx): xxx

        Returns:
            xxx: xxx
        """
        ret = np.log(close).diff()
        wght = pd.Series(index=molecule)
        for t_in, t_out in t1.loc[wght.index].iteritems():
            wght.loc[t_in] = (ret.loc[t_in:t_out] / num_co_events.loc[t_in:t_out]).sum()

        return wght.abs()

    @staticmethod
    def get_ind_matrix(bar_ix, t1):
        """get_ind_matrix func

        インディケータ行列の構築
        スニペット 4.3

        Args:
            bar_ix(Series): xxx
            t1(xxx): xxx

        Returns:
            pandas.DataFrame: インディケータ行列
        """

        ind_matrix = pd.DataFrame(0, index=bar_ix, columns=range(t1.shape[0]))
        for i, (t0, t1) in enumerate(t1.iteritems()):
            ind_matrix.loc[t0:t1, i] = 1.0

        return ind_matrix

    @staticmethod
    def get_avg_uniqueness(ind_matrix):
        """get_avg_uniqueness func

        平均独立性の計算
        インディケータ行列から平均独自性を計算する
        スニペット 4.4

        Args:
            ind_matrix(pandas.DataFrame): インディケータ行列

        Returns:
            pandas.Series: 平均独自性
        """

        c = ind_matrix.sum(axis=1)      # 同時発生性
        c += delta
        u = ind_matrix.div(c, axis=0)   # 独自性

        # 平均独自性
        avg_u = u[u >= 0.0].mean()

        return avg_u

    @staticmethod
    def seq_bootstrap(ind_matrix, s_length=None):
        """set_bootstrap func

        逐次ブートストラップからの抽出
        逐次ブートストラップを通じてサンプルを生成する
        スニペット 4.5

        Args:
            ind_matrix(pandas.DataFrame): インディケータ行列
            s_length(xxx): xxx
        """

        if s_length is None:
            s_length = ind_matrix.shape[1]

        phi = []
        while len(phi) < s_length:
            avg_u = pd.Series()
            for i in ind_matrix:
                ind_matrix_tmp = ind_matrix[phi + [i]] # ind_matrix を縮める
                avg_u.loc[i] = SampleWeighting.get_avg_uniqueness(ind_matrix_tmp).iloc[-1]

            prob = avg_u / avg_u.sum() # 抽出確率

            if prob.isnull().any():
                print(avg_u)
                raise Exception("prob の計算ができません")

            phi += [np.random.choice(ind_matrix.columns, p=prob)]

        return phi

    @staticmethod
    def get_rnd_t1(num_obs, num_bars, max_h):
        """get_rnd_t1 func

        ランダムな t1 系列を生成
        スニペット 4.7

        Args:
            num_obs(int): 観測値の数
            num_bars(int): バーの数
            max_h(int): xxx

        Returns:
            pandas.Series: t1
        """
        t1 = pd.Series()
        for i in range(num_obs):
            ix = np.random.randint(0, num_bars)
            val = ix + np.random.randint(1, max_h)
            t1.loc[ix] = val

        return t1.sort_index()

    @staticmethod
    def aux_mc(num_obs=None, num_bars=None, max_h=None, t1=pd.DataFrame(), bar_ix=None):
        """aux_mc func

        標準的ブートストラップと逐次ブートストラップによる独自性
        並列にして補助関数
        スニペット 4.8

        Args:
            num_obs(int): 観測値の数
            num_bars(int): バーの数
            max_h(int): xxx
            t1(pd.DataFrame): t1
            bar_ix(list): bar_ix

        Returns:
            dict: xxx

        """
        if t1.empty:
            t1 = SampleWeighting.get_rnd_t1(num_obs, num_bars, max_h)
            bar_ix = range(t1.max() + 1)

        ind_matrix = SampleWeighting.get_ind_matrix(bar_ix, t1)

        phi = np.random.choice(ind_matrix.columns, size=ind_matrix.shape[1])
        std_u = SampleWeighting.get_avg_uniqueness(ind_matrix[phi]).mean()

        phi = SampleWeighting.seq_bootstrap(ind_matrix)
        seq_u = SampleWeighting.get_avg_uniqueness(ind_matrix[phi]).mean()

        return {"std_u": std_u, "seq_u": seq_u}

def get_time_decay(tw, c_if_last_w=1.0):
    """get_time_decay func

    時間減衰ファクター
    スニペット 4.11

    Args:
        tw(xxx): 観測された独自性
        c_if_last_w(float): xxx
    Note:
        観測された独自性(tw)に区分線形な減衰を適用する
        最も新しい観測値のウェイト =1
        最も古い観測値のウェイト =c_if_last_w
    """
    c_if_w = tw.sort_index().cumsum()
    if c_if_last_w >= 0:
        slope = (1.0 - c_if_last_w) / c_if_w.iloc[-1]
    else:
        slope = 1.0 / ((c_if_last_w + 1) * c_if_w.iloc[-1])

    const = 1.0 - slope * c_if_w.iloc[-1]
    c_if_w = const + slope * c_if_w
    c_if_w[c_if_w < 0] = 0
    print("const, slope: ", const, slope)

    return c_if_w
