import os
import pandas as pd
import pytest
import sys

ABSPATH = os.path.abspath(__file__)
BASEDIR = os.path.dirname(ABSPATH)
PARENTDIR = os.path.dirname(BASEDIR)
PPARENTDIR = os.path.dirname(PARENTDIR)

sys.path.append(PPARENTDIR)

from stock_strategy.stock_strategy import StockStrategy

from financial_data_structure.financial_data_structure import (
    download_sample_data,
    read_csvs,
    reset_data,
    get_rolled_series,
    get_t_events,
    BITCOIN_DATA_URL,
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

TEST_CODE = 1332

class TestFinancialDataStructure(object):
    """TestFinancialDataStructure

    financial_data_structure のテスト

    """
    SAMPLE_DATES = ["20181127", "20181128", "20181129"]
    SAMPLE_SYMBOL = "XBTUSD"
    TEST_CODE = TEST_CODE

    def setup_class(self):
        """setup class func

        class 単位での前処理
        主にデータのロード

        """

        stock_strategy = StockStrategy()
        self.data_df = stock_strategy.get_stock_data(code = self.TEST_CODE)

    @pytest.mark.skip(reason='毎回データセットをダウンロードすると時間かかるので使用するときのみ実行する')
    def test_download_sample_data(self):
        """test_download_sample_data func

        download_sample_data のテスト

        """
        print("test_download_sample_data")
        for sample_date in self.SAMPLE_DATES:
            download_sample_data(sample_date)

    @pytest.mark.skip(reason="毎回データ読み込むと時間かかるので一度だけ実行確認できればよい")
    def test_read_samples(self):
        """test_read_samples func

        read_samples のテスト

        """
        csvs = ["./sample_{}.csv.gz".format(sample_date) for sample_date in self.SAMPLE_DATES]
        samples_df = read_csvs(csvs)
        print(samples_df)

    def test_get_t_events(self):
        t_events = get_t_events(self.data_df["Close"], 30)
        print("\nt_events\n", t_events)

class TestLabeling(object):
    """TestLabeling class

    labeling のテスト

    Attributes:
        TEST_CODE(int): テストに使用する銘柄

    """

    TEST_CODE = TEST_CODE

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
        print("\ndaily_vol_df\n", daily_vol_df)

    def test_get_events_and_get_bins_and_drop_labels(self):
        """test_get_events func

        get_events, get_bins, drop_labels のテスト

        Note:
            get_t_events, t_events:
                前日との変化分を計算
                閾値以上の変化をしている日付を取得
            daily_vol_df, get_daily_vol:
                変化率を計算
            get_events, events:
                最初にバリアに接触する時間の取得
            bins, get_bins:
                サイズとサイドのラベル付け

        """
        close_df = self.data_df["Close"]
        num_days = 5

        t_events = get_t_events(close_df, h=30)
        daily_vol_df = get_daily_vol(close_df, num_days=num_days)

        print("\nt_events\n", t_events)
        print("\ndaily_vol_df\n", daily_vol_df)
        print(daily_vol_df.index)
        print("\nclose\n", close_df)
        print(close_df.index)

        events = get_events(close = close_df, t_events=t_events, ptsl=[0.1, 0.1], \
                            trgt=daily_vol_df, min_ret=0.03, num_threads=1, num_days=num_days,\
                            t1=True)
        print("events\n", events)
        bins = get_bins(events, close_df)
        print("\nbins\n", bins)
        bins = drop_labels(bins)
        print("\nbins after drop\n", bins)

class TestSampleWeighting(object):
    """TestSampleWeighting class

    sample_weighting のテスト

    Attributes:
        TEST_CODE(int): テストに使用する銘柄

    """

    TEST_CODE = TEST_CODE

    def setup_method(self):
        stock_strategy = StockStrategy()
        self.data_df = stock_strategy.get_stock_data(code = self.TEST_CODE)

        self.close_df = self.data_df["Close"]
        t_events = get_t_events(self.close_df, h=10)
        self.events = get_events(close = self.close_df, t_events=t_events, ptsl=[0.1, 0.1], trgt=self.close_df, min_ret=100, num_threads=1)

    def test_mp_num_co_events(self):
        """test_mp_num_co_events

        mp_num_co_events のテスト

        """
        num_co_events = mp_pandas_obj(func = mp_num_co_events,
                                      pd_obj = ("molecule", self.events.index),
                                      num_threads = 1,
                                      close_idx = self.close_df,
                                      t1 = self.events["t1"])

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
