"""sample_weighting.py

    Section4

"""

import numpy as np
import pandas as pd

def mp_num_co_events(closeldx, t1, molecule):
    """mp_num_co_events func

    バーごとの同時発生的な事象の数を計算する

    Args:
        closeldx(xxx): xxx
        t1(xxx): xxx
        molecule(list):
            molecule[0]: ウェイトが計算される最初の日付
            molecule[-1]: ウェイトが計算される最後の日付

    Note:
        t1[molecule.nax()] の前に始まる事象はすべて計算に影響する

    """
    # 1: 期間 [ molecule[0], molecule[-1] ]に及ぶ事象を見つける
    # クローズしていない事象は他のウェイトに影響しなければならない
    t1 = tf.fillna(closeldx[-1])

    # 時点 molecule[0] またはその後に終わる事象
    t1 = t1[t >= molecule[0]]

    # 時点t1 [molecule].max() またはその前に始まる事象
    t1 = t1.loc[:t1[molecule].max()]

    # 2: バーに及ぶ事象を数える
    iloc = closeldx.searchsorted(np.array(
        [t1.index[0], t1.max()]
    ))
    count = pd.Series(0, index=closeldx[iloc[0]:iloc[1] + 1])
    for tin, t_out in t1.iteritems():
        count.loc[tin:t_out] += 1

    return count.loc[molecule[0]:t1[molecule].max()]
