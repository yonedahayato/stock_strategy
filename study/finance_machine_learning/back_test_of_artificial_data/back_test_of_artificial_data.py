"""back_test_of_artificial_data.py

    Section13

"""

import numpy as np
from rnadom import gauss
from itertools import product

def main():
    """main func

    最適取引ルールの決定のためのPython コード
    スニペット 13.1

    """
    r_pt = r_sl_m = np.linespace(0, 10, 21)
    count = 0
    list1 = [10, 5, 0, -5, -10]
    list2 = [5, 10, 25, 50, 100]
    for prod_tmp in product(list1, list2):
        count += 1
        coeffs = {"forecast": prod_tmp[0], "hl": prod_tmp, "sigma": 1}
        output = batch(coeffs, n_iter=1e5, max_hp=100, r_pt=r_pt, r_sl_m=r_sl_m)

    return output

def batch(coeffs, n_iter=1e5, max_hp=100, r_pt=np.linspace(5, 10, 20), \
          r_sl_m=np.linspace(5, 10, 20), seed=0):
    """batch func

    最適取引ルールの決定のためのPython コード
    スニペット 13.2

    """
    phi = 2 ** (-1.0 / coeffs["hl"])
    output1 = []

    for comb in product(r_pt, r_sl_m):
        output2 = []

        for iter in range(int(n_iter)):
            p = seed
            hp = 0
            count = 0

            while True:
                p = (1 - phi) * coeffs["forecast"] + phi * p + coeffs["sigma"] * gauss(0, 1)
                cp = p - seed
                hp += 1

                if cp > comb[0] or cp < -comb[1] or hp > max_hp:
                    output2.append(cp)
                    break

        mean = np.mean(output2)
        std = np.std(output2)
        output1.append((comb[0], comb[1], mean, std, mean / std))
    return ouput1
