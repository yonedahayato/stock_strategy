"""labeling.py

    Section3

"""

import numpy as np
import os
import pandas as pd
import sys

ABSPATH = os.path.abspath(__file__)
BASEDIR = os.path.dirname(ABSPATH)
PARENTDIR = os.path.dirname(BASEDIR)

sys.path.append(PARENTDIR)

from financial_data_structure.financial_data_structure import (
    get_t_events,
)
from multiprocessing_vector.multiprocessing_vector import (
    mp_pandas_obj,
)

class Labeling(object):
    """Labeling class

    ラベリング処理を取りまとめる

    """
    def __init__(self, code):
        self.code = code
        self.bins = pd.DataFrame()
        self.events = pd.DataFrame()

        self.bins_save_filename = "{}_labels_bins.csv".format(self.code)
        self.events_save_filename = "{}_labels_events.csv".format(self.code)

    @staticmethod
    def get_daily_vol(close, span0=100, num_days=1):
        """get_daily_vol func

        日次ボラティリティ推定
        スニペット 3.1

        Args:
            close(pandas.core.series.Series): 株価終値データ
            span0(int): 指数平滑移動平均の計算に使用するパラメータ

        Note:
            2日前の値と比較して変換率を計算
            2日前祝日 / 休日のでデータがない場合は直近の日付を使用
                例:
                    2016-01-06   2016-01-04     <- 2日前と比較
                    2016-01-07   2016-01-05     <- 2日前と比較
                    2016-01-08   2016-01-06     <- 2日前と比較
                    2016-01-12   2016-01-08     <- 2日前が祝日 / 休日なので直近の日付と比較
                    2016-01-13   2016-01-08     <- 2日前が祝日 / 休日なので直近の日付と比較
                    2016-01-14   2016-01-12     <- 2日前と比較
                    2016-01-15   2016-01-13     <- 2日前と比較
            変化率をリターンとする
            アウトプットは変化率の指数平滑移動平均の標準偏差

        """
        # 日次ボラティリティ、close (株価系列)に従いインデックス再作成)
        one_day = pd.Timedelta(days=num_days)

        datetime_index = close.index
        datetime_index_before_one_day = datetime_index - one_day

        searchsorted_index = close.index.searchsorted(datetime_index_before_one_day)
        searchsorted_index = searchsorted_index[searchsorted_index > 0]

        datetime_index_resize = datetime_index[len(datetime_index) - len(searchsorted_index):]
        datetime_index_before = pd.Series(datetime_index[searchsorted_index-1], index=datetime_index_resize)
        return_df = close.loc[datetime_index_resize] / close.loc[datetime_index_before.values].values - 1
        return_ewm_std_df = return_df.ewm(span=span0).std()

        return return_ewm_std_df

    @staticmethod
    def apply_ptsl_on_t1(close, events, ptsl, moleculte):
        """applyptsl_on_t1 func

        トリプルバリア方式の適用
        スニペット 3.2

        Args:
            close(pandas.core.series.Series): 株価終値データ
            events(DataFrame): 次の情報を含むDataFrame
                t1(xxx): 垂直バリアのタイムスタンプ。値がnp.nanの場合、垂直バリアはない
                trgt(xxx): 水平バリアの幅の単位
            ptsl(list): 2つの非負float値のリスト
                [0]: 上部バリアの幅を設定するためにtrgtに乗算する係数、0の場合、上部バリアはない
                [1]: 下部バリアの幅を設定するためにtrgtに乗算する係数、0の場合、下部バリアはない
            moleculte(list): シングルスレットによって処理されるイベントインデックスのサブセットを含むリスト

        Note:
            おそらくコールバック関数 (molecule が引数であるので)

        """

        # t1 (イベント終了)前に行われた場合は、ストップロス / 利食いを実施
        events_tmp = events.loc[moleculte]
        out = events_tmp[["t1"]].copy(deep=True)

        # profit taking
        if ptsl[0] > 0:
            pt = ptsl[0] * events_tmp["trgt"]
        else:
            pt = pd.Series(index=events.index) # NaNs

        # stop loss
        if ptsl[1] > 0:
            sl = -ptsl[1] * events_tmp["trgt"]
        else:
            sl = pd.Series(index=events.index) # NaNs

        for loc, t1 in events_tmp["t1"].fillna(close.index[-1]).iteritems():
            df0 = close[loc:t1] # 価格経路
            df0 = (df0 / close[loc] -1 ) * events_tmp.at[loc, "side"] # リターン

            # ストップロスの最短タイミング
            out.loc[loc, "sl"] = df0[df0 < sl[loc]].index.min()
            # 利食いの最短タミング
            out.loc[loc, "pt"] = df0[df0 > pt[loc]].index.min()

        return out

    @staticmethod
    def get_events(close, t_events, ptsl, trgt, min_ret, num_threads, t1=False, side=None, num_days=10):
        """get_events func

        最初のバリアに触れる時間を見つける関数
        スニペット 3.2
        スニペット 3.4
        スニペット 3.6

        Args:
            close(pandas.core.series.Series): 株価終値データ
            t_events(xxx): すべてのトリプルバイアを生成するタイムスタンプを含む pandasのタイムインデックス
            ptsl(list): 2つの非負float値のリスト
                [0]: 上部バリアの幅を設定するためにtrgtに乗算する係数、0の場合、上部バリアはない
                [1]: 下部バリアの幅を設定するためにtrgtに乗算する係数、0の場合、下部バリアはない
            t1(bool): 垂直バリアのタイムスタンプの pandas Series、垂直バリアを無効にしたい場合はFalse
            trgt(xxx): 絶対リターンで表現されたターゲットのpandas Series
            min_ret(xxx): トリプルバリアの検索を実行するために必要な最小目標リターン
            num_threads(int): 関数によって同時に使用されているスレッド数

        Returns:
            DataFrame: 結果、events
                t1: 最初のバリアに触れたときのタイムスタンプ
                trgt: 水平バリアを生成するために使用されたターゲット

        """
        # 1: ターゲットの定義
        try:
            trgt = trgt.loc[t_events]
        except:
            trgt = trgt.loc[t_events[1:]]
        trgt = trgt[trgt > min_ret] # min_ret

        # 2: t1(最大保有期間)の定義
        if t1 is False:
            t1 = pd.Series(pd.NaT, index = t_events)
        else:
            # スニペット 3.4
            t1 = close.index.searchsorted(t_events + pd.Timedelta(days = num_days))
            t1 = t1[t1 < close.shape[0]]
            t1 = pd.Series(close.index[t1], index = t_events[:t1.shape[0]]) # 終了時にNaNs

        # 3: イベントオブジェクトを作成し、t1にストップロスを適用
        if side is None:
            # side = pd.Seeries(1.0, index=trgt.index)
            new_side, new_ptsl = pd.Series(1.0, index=trgt.index), [ptsl[0], ptsl[0]]
        else:
            new_side, new_ptsl = side.loc[trgt.index], ptsl[:2]

        events = {"t1": t1, "trgt": trgt, "side": new_side}
        events = pd.concat(events, axis=1).dropna(subset = ["trgt"])

        df0 = mp_pandas_obj(func=Labeling.apply_ptsl_on_t1, pd_obj = ("moleculte", events.index), num_threads = num_threads, \
                            close = close, events = events, ptsl = new_ptsl)

        # pd.min は nan を無視する
        events["t1"] = df0.dropna(how = "all").min(axis=1)
        if side is None:
            events = events.drop("side", axis=1)

        return events

    @staticmethod
    def get_bins(events, close):
        """get_bins func

        観測値にラベルをつける
        スニペット 3.5
        スニペット 3.7

        Args:
            events(DataFrame): 結果、events
                index: イベント開始時間
                t1:
                    最初のバリアに触れたときのタイムスタンプ
                    イベント終了時間
                trgt:
                    水平バリアを生成するために使用されたターゲット
                    イベントのターゲット
                side(option):
                    ポジションサイド

            close(pandas.core.series.Series): 株価終値データ

        Returns:
            DataFrame: 結果、out
                ret: 最初にバリアに接触した時点で実現したリターン
                bin: ラベル {0 , 1}のどれか

        Note:
            イベント結果を計算する(もしあれば、ロングかショートかの情報を含む)
            ケース1 (side が eventsに含まれていない場合):
                bin は (-1, 1) のいずれか <- 価格変動によるラベル
            ケース2 (side が eventsに含まれている場合):
                bin は (0, 1) のいずれか <- pnl（メタラベリング）によるラベル

        """
        # 1: イベント発生時の価格
        events_tmp = events.dropna(subset=["t1"])
        px = events_tmp.index.union(events_tmp["t1"].values).drop_duplicates()
        px = close.reindex(px, method="bfill")

        # 2: out オブジェクトを生成
        out = pd.DataFrame(index=events_tmp.index)
        out["ret"] = px.loc[events_tmp["t1"].values].values / px.loc[events_tmp.index] - 1
        out["bin"] = np.sign(out["ret"])

        # 3: メタラベリング
        if "side" in events_tmp:
            out["ret"] *= events_tmp["side"]
            out["bin"] = np.sign(out["ret"])

            out.loc[out["ret"] <= 0, "bin"] = 0

        return out

    @staticmethod
    def drop_labels(events, min_pct=0.05):
        """drop_labels func

        出現回数が少ないラベルの削除
        スニペット 8.3

        Args:
            events(xxx): xxx
            min_pct(float): xxx

        """
        # ウェイトを適用し、不十分なレベルを削除する例
        while True:
            df0 = events["bin"].value_counts(normalize=True)
            if df0.min() > min_pct or df0.shape[0] < 3:
                break
            print("dropped label", df0.argmin(), df0.min())
            events = events[events["bin"] != df0.argmin()]
        return events

    def labeling(self, close_df, num_days=5, save=False):
        """labeling func

        ラベリングの処理を実行する

        Args:
            close_df(pandas.DataFrame): 価格情報
            num_days(int): xxx

        Note:
            1. 変化分が大きいシグナルを検出(t_events, get_t_events)、CUSUMサンプリング
            2. 変化率を計算(daily_vol_df, get_daily_vol)
            3. トリプルバリア法により、ラベルづけ可能なシグナルを検出(events, get_events)
            4. ラベルを決定(get_bin)
            5. 重複ラベルを削除(drop_labels)

        """
        print("\nclose_df len: ", len(close_df))
        t_events = get_t_events(close_df, h=30)
        daily_vol_df = self.get_daily_vol(close_df, num_days=num_days)
        print("t_events len: ", len(t_events))

        events = self.get_events(close = close_df, t_events=t_events, ptsl=[0.1, 0.1], \
                                 trgt=daily_vol_df, min_ret=0.03, num_threads=1, num_days=num_days,\
                                 t1=True)
        print("events len: ", len(events))
        bins = self.get_bins(events, close_df)
        bins = self.drop_labels(bins)

        if save:
            print("label file を保存します。")
            bins.to_csv(self.bins_save_filename)
            events.to_csv(self.events_save_filename)

        self.close_df = close_df
        self.bins = bins
        self.events = events

        return bins, events

    def load(self, csv_path=None):
        """load func

        csv からラベルを読み込む

        """

        self.bins = pd.read_csv(self.bins_save_filename, index_col=0)
        self.events = pd.read_csv(self.events_save_filename, index_col=0)

        self.bins.index = pd.to_datetime(self.bins.index)
        self.events.index = pd.to_datetime(self.events.index)
        self.events['t1'] = pd.to_datetime(self.events['t1'])

        return self.bins, self.events

    def get_labels(self):
        """get_labels func

        作成したラベルを取得する

        Returns:
            pandas.DataFrame: bins
            pandas.DataFrame: events

        Raises:
            Exception: ラベルが作成できていない場合

        """
        if self.bins.empty or self.events.empty:
            raise Exception("ラベリングができてないため、取得できません")
        return self.bins, self.events

    def set_row_data(self, close_df):
        self.close_df = close_df
