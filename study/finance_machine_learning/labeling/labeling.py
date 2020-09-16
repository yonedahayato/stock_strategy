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

from multiprocessing_vector.multiprocessing_vector import (
    mp_pandas_obj,
)


def get_daily_vol(close, span0=100):
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
    one_day = pd.Timedelta(days=1)

    datetime_index = close.index
    datetime_index_before_one_day = datetime_index - one_day

    searchsorted_index = close.index.searchsorted(datetime_index_before_one_day)
    searchsorted_index = searchsorted_index[searchsorted_index > 0]

    datetime_index_resize = datetime_index[len(datetime_index) - len(searchsorted_index):]
    datetime_index_before = pd.Series(datetime_index[searchsorted_index-1], index=datetime_index_resize)
    return_df = close.loc[datetime_index_resize] / close.loc[datetime_index_before.values].values - 1
    return_ewm_std_df = return_df.ewm(span=span0).std()

    return return_ewm_std_df


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


def get_events(close, t_events, ptsl, trgt, min_ret, num_threads, t1=False, side=None):
    """get_events func

    最初のバリアに触れる時間を見つける関数
    スニペット 3.2
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
    trgt = trgt.loc[t_events]
    trgt = trgt[trgt > min_ret] # min_ret

    # 2: t1(最大保有期間)の定義
    if t1 is False:
        t1 = pd.Series(pd.NaT, index = t_events)

    # 3: イベントオブジェクトを作成し、t1にストップロスを適用
    if side is None:
        # side = pd.Seeries(1.0, index=trgt.index)
        new_side, new_ptsl = pd.Series(1.0, index=trgt.index), [ptsl[0], ptsl[0]]
    else:
        new_side, new_ptsl = side.loc[trgt.index], ptsl[:2]

    events = {"t1": t1, "trgt": trgt, "side": new_side}
    events = pd.concat(events, axis=1).dropna(subset = ["trgt"])

    df0 = mp_pandas_obj(func=apply_ptsl_on_t1, pd_obj = ("moleculte", events.index), num_threads = num_threads, \
                        close = close, events = events, ptsl = new_ptsl)

    # pd.min は nan を無視する
    events["t1"] = df0.dropna(how = "all").min(axis=1)
    if side is None:
        events = events.drop("side", axis=1)

    return events

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


def drop_labels(events, min_pct=0.05):
    """drop_labels func

    出現回数が少ないラベルの削除

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
