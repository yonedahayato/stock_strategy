"""fractional_difference.py

    Section5

"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

class FractionlDifference(object):
    """FractionlDifference class

    分数次差分の処理をまとめる

    """
    def fractional_difference(self, data_df, FFD=True, save=False):
        """
        分数次差分の処理を実行する

        Args:
            data_df(pandas.DataFrame): 入力
            FFD(bool): FFDを使用するかどうか
            save(bool): 結果を保存するかどうか

        Returns:
            pandas.DataFrame:結果

        """
        d = 0.5

        if FFD:
            print("固定幅ウインドウ分数次差分(FFD)を利用します")
            frac_diff_df = frac_diff_FFD(data_df, d)
        else:
            print("標準的な分数次差分（拡大ウインドウ）を利用します")
            frac_diff_df = frac_diff(data_df, d)

        print("frac_diff_df", frac_diff_df)

        return frac_diff_df



def get_weights(d, size):
    """get_weights func

    ウェイト関数
    スニペット 5.1

    Args:
        d(int): 指数
        size(int): xxx

    Returns:
        np.array: ウェイト
    """
    w = [1.0]
    for k in range(1, size):
        w_tmp = -w[-1] / k * (d - k + 1)
        w.append(w_tmp)

    w = np.array(w[::-1]).reshape(-1, 1)
    return w

def plot_weights(d_range, n_plots, size):
    """plot_weights func

    スニペット 5.1

    Args:
        d_range(int): xxx
        n_plots(int): xxx
        size(int): xxx

    """
    w = pd.DataFrame()
    for d in np.linspace(d_range[0], d_range[1], n_plots):
        w_tmp = get_weights(d, size=size)
        w_tmp = pd.DataFrame(w_tmp, index=range(w_tmp.shape[0])[::-1], columns=[d])
        w = w.join(w_tmp, how="outer")

    ax = w.plot()
    ax.legend(loc="upper left")
    plt.savefig("plot_weights.png")

def frac_diff(series, d, thres=0.01):
    """frac_diff fun

    標準的な分数次差分（拡大ウインドウ）
    スニペット 5.2

    Args:
        series(pandas.DataFrame): xxx
        d(int): xxx
        thres(float): 閾値

    Returns:
        xxx: xxx

    Note:
        NaNを処理しながら、ウインドウ幅を拡大していく
        注意1 : thres = 1 のとき、スキップされるデータはない
        注意2 : d は [0, 1]の範囲でなく任意の正値でよい
    """
    # 1: 最長の系列に対してウェイトを計算する
    w = get_weights(d, series.shape[0])

    # 2: ウェイト損失閾値に基づいてスキップする最初の計算結果を決める
    w_tmp = np.cumsum(abs(w))
    w_tmp /= w_tmp[-1]
    skip = w_tmp[w_tmp > thres].shape[0]

    # 3: 値にウェイトを適用する
    df = {}
    for name in series.columns:
        print("columns name: {}".format(name))
        series_f = series[[name]].fillna(method="ffill").dropna()
        df_tmp = pd.Series()

        for iloc in range(skip, series_f.shape[0]):
            loc = series_f.index[iloc]

            # NA を排除
            if not np.isfinite(series.loc[loc, name]):
                continue

            df_tmp[loc] = np.dot(w[-(iloc + 1):, :].T, series_f.loc[:loc])[0, 0]

        df[name] = df_tmp.copy(deep=True)

    df = pd.concat(df, axis=1)

    return df

def get_weights_FFD(d, thres):
    """

    固定幅ウインドウ分数次差分という新しい方法
    スニペット 5.3

    Args:
        d(int): xxx
        thres(float): 閾値
        size(int): xxx

    Returns:
        xxx: xxx
    """
    w, k = [1.0], 1
    while True:
        w_tmp = - w[-1] / k * (d - k + 1)

        if abs(w_tmp) < thres:
            break

        w.append(w_tmp)
        k += 1

    return np.array(w[::-1]).reshape(-1, 1)

def frac_diff_FFD(series, d, thres=1e-4):
    """frac_diff fun

    固定幅ウインドウ分数次差分という新しい方法
    スニペット 5.3

    Args:
        series(pandas.DataFrame): xxx
        d(int): xxx
        thres(float): 閾値

    """
    w = get_weights_FFD(d, thres)
    print("w shape", w.shape)
    width = len(w) - 1
    df = {}

    for name in series.columns:
        print("columns name: {}".format(name))
        series_f = series[[name]].fillna(method="ffill").dropna()
        df_tmp = pd.Series()

        print("width, series_f.shape[0]", width, series_f.shape[0])

        for iloc1 in range(width, series_f.shape[0]):
            loc0 = series_f.index[iloc1 - width]
            loc1 = series_f.index[iloc1]

            # NA を排除
            if not np.isfinite(series.loc[loc1, name]):
                print("continue")
                continue

            df_tmp[loc1] = np.dot(w.T, series_f.loc[loc0:loc1])[0, 0]

        df[name] = df_tmp.copy(deep=True)

    df = pd.concat(df, axis=1)

    return df

def plot_min_FFD():
    """plot_min_FFD func

    ADF検定をパスする最小のDの探索
    スニペット 5.4
    """
    pass
