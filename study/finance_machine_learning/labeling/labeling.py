"""labeling.py

    Section3

"""

import pandas as pd

def get_daily_vol(close, span0=100):
    """get_daily_vol func

    日次ボラティリティ推定

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
