"""financial_data_structure.py

    Section2

"""
import datetime
import numpy as np
from mlfinlab.data_structures import standard_data_structures
import os
import pandas as pd
import requests
import urllib.request
from urllib import request

BITCOIN_DATA_URL = "https://s3-eu-west-1.amazonaws.com/public.bitmex.com/data/trade/{}.csv.gz"
TIMESTAMP_FORMAT = "%Y%m%d%H%M%S%f"
TIMESTAMP_KEY_NAME = "Time"

def download_sample_data(sample_date = "20181127"):
    """get_sample_data func

    サンプルデータの取得

    Args:
        sample_date(str): 取得するデータの日付
    Note:
        40M程度のデータを取得
        10秒程度

    """
    url = BITCOIN_DATA_URL.format(sample_date)
    urllib.request.urlretrieve(url,"./sample_{}.csv.gz".format(sample_date))

def read_csvs(csvs):
    """read_csv func

    複数のサンプルデータを取得

    Notes:
        'timestamp', 'symbol', 'side', 'size', 'price', 'tickDirection',
        'trdMatchID', 'grossValue', 'homeNotional', 'foreignNotional'

    """
    output_df = None
    for csv_path in csvs:
        print("reading,,,{}".format(csv_path))
        if output_df is None:
            output_df = pd.read_csv(csv_path)

        else:
            tmp_df = pd.read_csv(csv_path)
            output_df = output_df.append(tmp_df)

    return output_df

def compute_vwap(data_df):
    """compute_vwap func

    volume weighted average price の計算

    """
    q = data_df["foreignNotional"]
    p = data_df["price"]

    vwap = np.sum(p * q) / np.sum(q)
    data_df["vwap"] = vwap

    return data_df

def reset_data(data_df, symbol=None):
    """reset_data func

    データの調整

    Note:
        symbol の取得
        timestamp の調整

    """
    if symbol is not None:
        data_df = data_df[data_df.symbol == symbol]

    rewrite_date = lambda t: datetime.datetime.strptime(t[:-3], "%Y-%m-%dD%H:%M:%S.%f")
    data_df[TIMESTAMP_KEY_NAME] = data_df.timestamp.map(rewrite_date)

    data_df.set_index(TIMESTAMP_KEY_NAME)

    return data_df

DICT_IO = {"Instrument": "FUT_CUR_GEN_TICKER",
           "Open": "PX_OPEN",
           "Close": "PX_LASR"}

def roll_gaps(data_df, dictio = DICT_IO, match_end=True):
    """roll gaps func

    スニペット 2.2

    """
    # 前限月の終値と後限月の始値のロールギャップの計算
    roll_dates = data_df[dictio["Instrument"]].drop_duplicates(keep="first").index
    gaps = data_df[dictio["Close"]] * 0
    iloc = list(data_df.index)

    # ロールする前日のインデックス
    iloc = [iloc.index(i) - 1 for i in roll_dates]
    gaps.loc[roll_dates[1:]] = data_df[dictio["Open"]].loc[roll_dattes[1:]] - \
                               data_df[dictio["Close"]].iloc[iloc[1:]].valuues

    gaps = gaps.cumsum()
    if match_end:
        gaps -= gaps.iloc[-1]

    return gaps

def get_rolled_series(data_df):
    """get_rolled_series func

    価格系列からギャップ系列を差し引く
    スニペット 2.2

    Args:
        path_in(str): 有効な文字列パス
        key(xxx): xxx

    Returns:
        Series

    """
    gaps = roll_gaps(data_df)
    for fid in ["Close", "VWAP"]:
        series[fid] -= gaps

    return series

def get_t_events(g_raw, h):
    """get_t_events func

    対称CUSUMフィルタ
    スニペット 2.4

    Args:
        g_raw(Series): フィルタ処理される原時系列
        h(float): 閾値

    Note:
        前日との差分を計算(diff)
        差分ごとに以下の計算処理実行
            s_pos, s_neg の計算
            閾値との比較をして、該当した場合日付を保存(t_events.append)

    """
    t_events, s_pos, s_neg = [], 0, 0
    diff = g_raw.diff()

    for i in diff.index[1:]:
        s_pos, s_neg = max(0, s_pos + diff.loc[i]), min(0, s_neg + diff.loc[i])

        if s_neg < -h:
            s_neg = 0
            t_events.append(i)
        elif s_pos > h:
            s_pos = 0
            t_events.append(i)
    return pd.DatetimeIndex(t_events)

class DollarBar(object):
    """DollarBar class

    ドルバーを作成するサンプルコード

    Note:
        参考 : https://kabukimining.hateblo.jp/entry/FinanceDollarBar

    """
    date = "20200401"
    symbol="XBTUSD"
    baseurl = 'https://s3-eu-west-1.amazonaws.com/public.bitmex.com/data/trade/'
    filepath = './dollar_{}.csv.gz'.format(date)
    threshold = 4000000

    def download_dataset(self):
        """download func

        データのダウンロード

        Note:
            ['timestamp', 'symbol', 'side', 'size', 'price', 'tickDirection',
             'trdMatchID', 'grossValue', 'homeNotional', 'foreignNotional']

        """
        if not os.path.exists(self.filepath):
            request.urlretrieve(self.baseurl + '{}.csv.gz'.format(self.date), self.filepath)

    def make_candles(self, df, symbol):
        """make_candles func

        Args:
            symbol(str): 銘柄名
        Note:
            参考: https://note.com/nagi7692/n/ne674d117d1b6?magazine_key=m0b2a506bf904
        """

        df = df.query('symbol == "{}"'.format(symbol))

        df.drop(["symbol", "side", 'tickDirection', 'trdMatchID', 'grossValue', 'homeNotional', 'foreignNotional'], axis=1, inplace=True)
        df = df.sort_index()
        df['timestamp'] = pd.to_datetime(df['timestamp'], format="%Y-%m-%dD%H:%M:%S.%f")
        df = df.rename(columns={'timestamp': 'date_time', "size": "volume"})
        df = df[["date_time", "price", "volume"]]

        return df

    def make_dollar_bar(self):
        """make_dollar_bar func

        Note:
            参考 : https://kabukimining.hateblo.jp/entry/FinanceDollarBar

        """
        self.download_dataset()
        row_data_df = pd.read_csv(self.filepath)
        print("data_df shape", row_data_df.shape)
        print("data_df columns", row_data_df.columns)
        print("data_df index", row_data_df.index)

        data_df = self.make_candles(row_data_df, self.symbol)

        print("data_df head\n", data_df.head())

        # dollar = standard_data_structures.get_dollar_bars(data_df, \
        #          threshold=self.threshold, batch_size=1000000, verbose=True, \
        #          to_csv=True, output_path=file_title)
        dollar = standard_data_structures.get_dollar_bars(data_df, \
                 threshold=self.threshold, batch_size=1000000, verbose=True,)
        print("dollar", dollar.shape)
        print("dollar head\n", dollar.head())
