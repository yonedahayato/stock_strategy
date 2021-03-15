"""bet_size_determination.py

    Section10

"""

import pandas as pd
from scipy.stats import norm

from multiprocessing_vector.multiprocessing_vector import (
    mp_pandas_obj,
)

def get_signal(events, step_size, prob, pred, num_classes, num_threads, **kargs):
    """get_signal func

    確率からベットサイズへ
    スニペット 10.1
    予測からシグナルを得る

    """
    if prob.shape[0] == 0:
        return pd.Series()

    # 1: 多項分布（一対他メソッド （OvR））からシグナルを生成する
        # OvR の t値
    signal0 = (prob - 1.0 / num_classes) / (prob * (1.0 - prob)) ** 0.5
        # シグナル = サイド x サイズ
    signal0 = pred * (2 * norm.cdf(signal0) - 1)

    if "size" in envents:
        # メタラベリング
        signal0 *= events.loc[signal0.index, "side"]

    # 2: 同時にオープンであるシグナルの平均を計算する
    df0 = signal0.to_frame("signal").join(events[["t1"]], how="left")
    df0 = avg_active_signals(df0, num_threads)
    signal1 = discrete_signal()

    return signal1

def avg_active_signals(signals, num_threads):
    """avg_active_signals func

    またアクティブなベットを平均化する
    スニペット 10.2
    アクティブなシグナルの平均を計算する

    """
    # 1: シグナルが変わった時点（シグナルの開始、もしくは終了時点）
    t_pnts = set(signals["t1"].dropna().values)
    t_pnts = t_pnts.union(signals.index.values)
    t_pnts = list(t_pnts)
    t_pnts.sort()

    out = mp_pandas_obj(mp_avg_active_signals, ("molecule", t_pnts), num_threads, signals=signals)

    return out

def mp_avg_active_signals(signals, num_threads):
    """mp_avg_active_signals func

    またアクティブなベットを平均化する
    スニペット 10.2

    Note:
        時刻loc で、まだアクティブなシグナルを平均化する
        以下の場合にシグナルはアクティブである
            a: loc 以前にシグナルがでている、かつ
            b: loc はシグナルの終了時刻より前、もしくは終了時刻がまだわからない(NaT)

    """
    out = xxx
    for loc in moleculte:
        df0 = (signals.index.values <= loc) & (loc < signals["t1"]) | pd.isnull(signals["t1"])
        act = signals[df0].index

        if len(act) > 0:
            out[loc] = signals.loc[act, "signal"].mean()
        else:
            out[loc] = 0

    return out

def discrete_signal(signal0, step_size):
    """discrete_signal func

    過剰なトレードを防ぐためのサイズ離散化
    スニペット 10.3

    """
    # 離散化
    signal1 = (signal0 / step_size).round() * step_size

    # 上限
    signal1[sinal1 > 1] = 1

    # 下限
    signal1[sinal1 < -1] = -1

    return signal1

# 動的なポジションサイズと指数
# スニペット 10.4
def bet_size(w, x):
    return x * (w + x**2) ** -0.5

def get_t_pos(w, f, mp, max_pos):
    return int(bet_size(w, f - mp) * max_pos)

def inv_price(f, w, m):
    return f - m * (w / (1 - m ** 2)) **0.5

def limit_price(t_pos, pos, f, w, max_pos):
    sgn = (1 if t_pos >= pos else -1)
    ip = 0

    for j in range(abs(pos + sgn), abs(t_pos + 1)):
        ip += inv_price(f, w, j / float(max_pos))

    ip /= t_pos - pos

    return ip

def get_w(x, m):
    return x ** 2 * (m ** (-2) - 1)
