"""back_test_of_artificial_data.py

    Section13

"""

import numpy as np
from random import gauss
from itertools import product

def main():
    """main func

    最適取引ルールの決定のためのPython コード
    スニペット 13.1

    Note:
        確率過程のパラメータ(forecasts(予測), half_life(半減期、tau))のデカルト積を生成

    """
        # rule_profit_taking
        # rule_stop_loss
    r_pt = r_sl_m = np.linspace(0, 10, 21)

    forecasts = [10, 5, 0, -5, -10]
    half_lifes = [5, 10, 25, 50, 100]
    n_iter = 10
    for count, (forecast, half_life) in enumerate(product(forecasts, half_lifes)):
        print("count: {}".format(count))
        coeffs = {"forecast": forecast, "hl": half_life, "sigma": 1}
        output = batch(coeffs, n_iter=n_iter, max_hp=100, r_pt=r_pt, r_sl_m=r_sl_m)

    return output

def batch(coeffs, n_iter=1e5, max_hp=100, r_pt=np.linspace(0.5, 10, 20), \
          r_sl_m=np.linspace(0.5, 10, 20), seed=0):
    """batch func

    最適取引ルールの決定のためのPython コード
    スニペット 13.2

    Args:
        coeffs(dict): xxx
        n_iter(int): イテレーションの回数
        max_hp(int): 最大保有期間(max holding period)
        r_pt(numpy.array): xxx
        r_sl_m(numpy.array): xxx
        seed(xxx): 価格の初期値

    Note:
        一対のパラメータ(forecast, half_life) を入力として、
        20 x 20 メッシュの各取引ルール(利益確定と損切りの閾値)に対応するシャープレシオを計算

    """
    phi = 2 ** (-1.0 / coeffs["hl"])
    output1 = []

    for pt, sl in product(r_pt, r_sl_m):
            # 取引ルールの作成 comb
            # 20 x 20 のノード
        output2 = []

        for iter in range(int(n_iter)):
                # パスのイテレーション
                    # price(価格), holding period(保有期間)の初期化
            p = seed
            hp = 0

            while True:
                    # price(価格)の推定
                    # holding period(保有期間)のインクリメント
                p = (1 - phi) * coeffs["forecast"] + phi * p + coeffs["sigma"] * gauss(0, 1)
                cp = p - seed
                hp += 1

                if cp > pt or cp < -sl or hp > max_hp:
                        # ポジションの解消の条件が成立したら終了
                    output2.append(cp)
                    break

        mean = np.mean(output2)
        std = np.std(output2)
        sharpe_ratio = mean / std
        output1.append((pt, sl, mean, std, sharpe_ratio))
    return output1
