"""strategic_risk.py

    Section15

"""
import numpy as np
import scipy.stats as st

def bin_hr(sl, pt, freq, t_sr):
    """bin_hr func

    スニペット 15.3
    インプライド Precision を計算する

    """
    pass

def bin_freq(sl, pt, p, t_sr):
    """bin_freq func

    スニペット 15.4
    ベットのインプライド頻度の計算

    """
    pass

def mix_gaussians(mu1, mu2, sigma1, sigma2, prob1, n_obs):
    """mix_gaussians func

    スニペット 15.5
    実務における戦略的リスクの計算

    """
    pass

def prob_failure():
    """prob_failure func

    スニペット 15.5
    実務における戦略的リスクの計算

    """
    pass

def main():
    """main func

    スニペット 15.5
    実務における戦略的リスクの計算

    """
        # 1: パラメータ
    mu1 = 0.05
    mu2 = -0.1
    sigma1 = 0.05
    sigma2 = 0.1
    prob1 = 0.75
    n_obs = 2600

    t_sr = 2.0
    freq = 260

        # 2: 混合ガウス分布からサンプルを生成
    ret = mix_gaussians(mu1, mu2, sigma1, sigma2, prob1, n_obs)

        # 3: 失敗確率の計算
    prob_f = prob_failure(ret, freq, t_sr)
    print("prob strategy will fail: {}".format(prob_f))

    return
