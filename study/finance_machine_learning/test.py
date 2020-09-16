import os
import pandas as pd
import sys

ABSPATH = os.path.abspath(__file__)
BASEDIR = os.path.dirname(ABSPATH)
PARENTDIR = os.path.dirname(BASEDIR)
PPARENTDIR = os.path.dirname(PARENTDIR)

sys.path.append(PPARENTDIR)

from stock_strategy.stock_strategy import StockStrategy

from financial_data_structure.financial_data_structure import (
    get_t_events,
)

from labeling.labeling import (
    get_daily_vol,
    get_events,
    get_bins,
    drop_labels,
)

from sample_weighting.sample_weighting import (
    mp_num_co_events,
    mp_sample_tw,
)

from multiprocessing_vector.multiprocessing_vector import (
    lin_parts,
    nested_parts,
    mp_pandas_obj,
)

class TestLabeling(object):
    """TestLabeling class

    labeling のテスト

    Attributes:
        TEST_CODE(int): テストに使用する銘柄

    """

    TEST_CODE = 1332
    def setup_method(self):
        """setup_method

        テストデータを取得

        """
        stock_strategy = StockStrategy()
        self.data_df = stock_strategy.get_stock_data(code = self.TEST_CODE)

    def test_get_daily_vol(self):
        """test_get_daily_vol func

        get_daily_vol のテスト

        """
        close_df = self.data_df["Close"]
        daily_vol_df = get_daily_vol(close_df)
        print("daily_vol_df", daily_vol_df)

    def test_get_events(self):
        """test_get_events func

        get_events のテスト

        """
        close_df = self.data_df["Close"]
        t_events = get_t_events(close_df, h=10)
        print("t_events", t_events)
        events = get_events(close = close_df, t_events=t_events, ptsl=[0.1, 0.1], trgt=close_df, min_ret=100, num_threads=1)
        print("events", events)

    def test_get_bins(self):
        """test_get_bins

        get_bins のテスト

        """
        close_df = self.data_df["Close"]
        t_events = get_t_events(close_df, h=10)
        events = get_events(close = close_df, t_events=t_events, ptsl=[0.1, 0.1], trgt=close_df, min_ret=100, num_threads=1)
        bins = get_bins(events, close_df)
        print("bins", bins)

    def test_drop_labels(self):
        """test_drop_labels func

        drop_labels のテスト

        """
        close_df = self.data_df["Close"]
        t_events = get_t_events(close_df, h=10)
        events = get_events(close = close_df, t_events=t_events, ptsl=[0.1, 0.1], trgt=close_df, min_ret=100, num_threads=1)
        bins = get_bins(events, close_df)

        events = drop_labels(bins)

class TestSampleWeighting(object):
    """TestSampleWeighting class

    sample_weighting のテスト

    """
    def test_mp_num_co_events(self):
        """test_mp_num_co_events

        mp_num_co_events のテスト

        """
        raise Exception("これから書きます")

def my_func(molecule):
    return molecule

class TestMultiprocess(object):
    """Multiprocess class

    multiprocessing のテスト

    """
    def test_lin_parts(self):
        """test_lin_parts func

        lin_parts のテスト

        """
        parts = lin_parts(num_atoms=10, num_threads=4)
        print(parts)

    def test_nested_parts(self):
        """test_nested_parts func

        nested_parts のテスト

        """

        parts = nested_parts(num_atoms=10, num_threads=4)
        print(parts)

    def test_mp_pandas_obj_single(self):
        """test_mp_pandas_obj_single func

        mp_pandas_obj のテスト
        シングルスレッド

        """

        def func(molecule):
            return molecule
        print(type(func))
        mp_pandas_obj(func = func, pd_obj = ("molecule", pd.Series([0, 1, 2, 3])), num_threads=1)

    def test_mp_pandas_obj_multi(self):
        """test_mp_pandas_obj_multi func

        mp_pandas_obj のテスト
        マルチスレッド

        """
        mp_pandas_obj(func = my_func, pd_obj = ("molecule", pd.Series([0, 1, 2, 3])), num_threads=24)
