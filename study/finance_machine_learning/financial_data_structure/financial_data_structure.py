"""financial_data_structure.py

    Section2

"""

import pandas as pd

def get_t_events(g_raw, h):
    """get_t_events func

    対称CUSUMフィルタ

    Args:
        g_raw(xxx): フィルタ処理さたる原時系列
        h(xxx): 閾値

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
