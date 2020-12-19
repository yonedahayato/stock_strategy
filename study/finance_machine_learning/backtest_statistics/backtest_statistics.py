"""backtest_statistics.py

    Section14

"""

import numpy as np
import pandas as pd

def main(t_pos):
    """main func

    スニペット 14.1
    ターゲットポジションからベットのタイミングを導出

    Note:
        ベットはポジションが解消されるまでの間、または反転取引が行われるまでの間におこる
    """

    df0 = t_pos[t_pos == 0].index
    df1 = t_pos.shift(1)
    df1 = df1[df1 != 0].index
    bets = df0.intersecion(df1)

    df0 = t_pos.iloc[1:] * t_pos.iloc[:-1].values
    bets = bets.union(df0[df0 < 0].index).sort_values()

    if t_pos.index[-1] not in bets:
        bets.append(t_pos.index[-1:])

def get_holding_period(t_pos):
    """get_holding_period func

    スニペット 14.2
    保有期間推定の実装

    Note:
        平均エントリー時刻を求めるペアリングアルゴリズムを用いて平均保有期間（日数）を求める

    """
    hp = pd.DataFrame(columns=["dT", "w"])
    t_entry = 0.0

    p_diff = t_pos.t_diff()
    t_diff = (t_pos.index - t_pos.index[0]) / np.timedelta64(1, "D")

    for i in range(1, t_pos.shape[0]):
        if p_diff.iloc[i] * t_pos.iloc[i-1] >= 0:
                # 変化なしまたは増加
            if t_pos.iloc[i] != 0:
                t_entry = (t_entry * t_pos.iloc[i-1] + t_diff[i] * p_diff.iloc[i]) / t_pos.iloc[i]

        else:
                # 減少
            if t_pos.iloc[i] * t_pos.iloc[i-1] < 0:
                    # 反転
                hp.loc[t_pos.index[i], ["dT", "w"]] = (t_diff[i] - t_entry, abs(t_pos.iloc[i-1]))
                    # エントリー時刻のリセット
                t_entry = t_diff[i]
            else:
                hp.loc[t_pos.index[i], ["dT", "w"]] = (t_diff[i] - t_entry, abs(p_diff.iloc[i]))

    if hp["w"].sum() > 0:
        hp = (hp["dT"] * hp["w"]).sum() / hp["w"].sum()
    else:
        hp = np.nan

    return hp

def get_HHI(bet_ret):
    """get_hht func

    スニペット 14.3
    HHI 集中度導出アルゴリズム

    """
    if bet_ret.shape[0] <= 2:
        return np.nan

    wght = bet_ret / bet_ret.sum()
    hhi = (wght ** 2).sum()
    hhi = (hhi - bet_ret.shape[0] ** -1) / (1.0 - bet_ret.shape[0] ** -1)

    return hhi

def compute_DD_TuW(series, dollars=False):
    """compute_DD_TuW func

    スニペット 14.4
    DD と TuWの系列の導出

    Note:
        一連のドローダウンとそれらに関連する TuW を計算する

    """
    df0 = series.to_frame("pnl")
    df0["hwm"] = series.expanding().max()

    df1 = df0.group_by("hwm").min().reset_index()
    df1.columns = ["hwm", "min"]
        # HWM の時刻
    df1.index = df0["hwm"].drop_duplicates(keep="first").index
        # ドローダウンが後に続く HWM
    df1 = df1[df1["hwm"] > df1["min"]]

    if dollars:
        dd = df1["hwm"] - df1["min"]
    else:
        dd = 1 - df1["min"] / df1["hwm"]

    tuw = ((df1.index[1:] - df1.index[:-1]) / np.timedelta64(1, "Y")).values
        # 単位を年に換算
    tuw = pd.Series(tuw, index=df1.index[:-1])

    return dd, tuw
