import itertools
import numpy as np
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
    DollarBar,
)

from labeling.labeling import (
    Labeling,
)

from sample_weighting.sample_weighting import (
    SampleWeighting,
)

from fractional_difference.fractional_difference import (
    plot_weights,
    frac_diff,
    frac_diff_FFD,
    FractionalDifference,
)

from ensemble.ensemble import (
    bagging_accuracy,
    Ensemble,
)

from cross_validation.cross_validation import (
    CrossValidation,
    cv_score,
)

from feature_importance.feature_importance import (
    get_test_data,
    feat_importance,
    FeatureImportance,
)

from back_test_of_artificial_data.back_test_of_artificial_data import main as back_test_of_artificial_data_main

from multiprocessing_vector.multiprocessing_vector import (
    lin_parts,
    nested_parts,
    mp_pandas_obj,
    process_jobs,
    process_jobs_single,
)

from .finance_machine_learning import FinanceMachineLearning

TEST_CODE = 1332

class TestOriginalData(object):
    """TestOriginalData class

    オリジナルのデータセットで検証

    """
    TEST_CODE = TEST_CODE

    def test_original_data(self):
        """test_original_data func

        あるテスト銘柄でのテスト

        """
        stock_strategy = StockStrategy()
        self.data_df = stock_strategy.get_stock_data(code = self.TEST_CODE)

        close_df = self.data_df["Close"]
        self.close_df = close_df
        save = False

        # section 3
        labeling = Labeling(code=self.TEST_CODE)
        self.bins, self.events = labeling.labeling(close_df, save=save)
        # self.bins, self.events = labeling.load()
        labeling.set_row_data(close_df)

        # section 4
        sample_weighting = SampleWeighting(labeling)
        self.bins_sampled = sample_weighting.sample_weighting(save=save)
        # self.bins_sampled = sample_weighting.load()

        # secion 5
        fractional_difference = FractionalDifference(sample_weighting)
        self.frac_diff_df, self.bins_sampled = \
            fractional_difference.fractional_difference(self.data_df, sample=True, save=save)

        # section 6
        avg_u = 10
        ensemble = Ensemble(fractional_difference)
        ensemble.ensemble(avg_u)

        # section 7
        cross_validation = CrossValidation(ensemble, fractional_difference)
        score = cross_validation.cross_validation()
        print("score", score)

        # section 8
        feature_importance = FeatureImportance(fractional_difference)
        feature_importance.feature_importance()

    def test_original_dataset(self):
        """test_original_dataset func

        複数のテスト銘柄でのテスト
        FinanceMachineLearning の実行の確認も含む

        """
        finance_machine_learning = FinanceMachineLearning(debug=True)
        finance_machine_learning.main()

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

    def test_dollar_bar(self):
        """

        DollarBar のテスト

        """
        print("\nDollarBar")
        dollar_bar = DollarBar()
        dollar_bar.make_dollar_bar()

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
        daily_vol_df = Labeling.get_daily_vol(close_df)
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
        daily_vol_df = Labeling.get_daily_vol(close_df, num_days=num_days)

        print("\nt_events\n", t_events)
        print("\ndaily_vol_df\n", daily_vol_df)
        print(daily_vol_df.index)
        print("\nclose\n", close_df)
        print(close_df.index)

        events = Labeling.get_events(close = close_df, t_events=t_events, ptsl=[0.1, 0.1], \
                            trgt=daily_vol_df, min_ret=0.03, num_threads=1, num_days=num_days,\
                            t1=True)
        print("events\n", events)
        bins = Labeling.get_bins(events, close_df)
        print("\nbins\n", bins)
        bins = Labeling.drop_labels(bins)
        print("\nbins after drop\n", bins)

    def test_labeling(self):
        """test_labeling func

        """
        labeling = Labeling(code=self.TEST_CODE)
        close_df = self.data_df["Close"]

        labeling.labeling(close_df, save=True)

class TestSampleWeighting(object):
    """TestSampleWeighting class

    sample_weighting のテスト

    Attributes:
        TEST_CODE(int): テストに使用する銘柄

    """

    TEST_CODE = TEST_CODE

    def setup_class(self):
        stock_strategy = StockStrategy()
        self.data_df = stock_strategy.get_stock_data(code = self.TEST_CODE)

        close_df = self.data_df["Close"]
        self.close_df = close_df

        labeling = Labeling(code=self.TEST_CODE)
        self.bins, self.events = labeling.labeling(close_df, save=True)

        self.sample_weighting = SampleWeighting(labeling)

    def test_mp_num_co_events_and_mp_sample_w(self):
        """test_mp_num_co_events

        mp_num_co_events, mp_sample_w のテスト
        スニペット 4.2 ラベルの平均性の推定

        mp_sample_wのテスト
        スニペット 4.10 絶対リターンの帰属による標本ウェイトの決定

        Note:
            ラベルの独自性を計算(mp_num_co_events)
            ラベルの平均独自性を計算(mp_sample_tw)

        """
        # スニペット 4.2 ラベルの平均性の推定
        num_co_events = mp_pandas_obj(func = SampleWeighting.mp_num_co_events,
                                      pd_obj = ("molecule", self.events.index),
                                      num_threads = 1,
                                      close_idx = self.close_df.index,
                                      t1 = self.events["t1"])
        print("\nnum_co_events\n", num_co_events)

        num_co_events = num_co_events.loc[~num_co_events.index.duplicated(keep="last")]
        num_co_events = num_co_events.reindex(self.close_df.index).fillna(0)

        self.bins["tw"] = mp_pandas_obj(SampleWeighting.mp_sample_tw, ("molecule", self.events.index), num_threads=1, \
                                        t1=self.events["t1"], num_co_events=num_co_events)

        print("\nbins after 4.2\n", self.bins)

        # スニペット 4.10 絶対リターンの帰属による標本ウェイトの決定
        self.bins["w"] = mp_pandas_obj(SampleWeighting.mp_sample_w, ("molecule", self.events.index), num_threads=1, \
                                       t1=self.events["t1"], num_co_events=num_co_events, close = self.close_df)
        self.bins["w"] *= self.bins.shape[0] / self.bins["w"].sum()

        print("\nbins after 4.10\n", self.bins)

    def test_bootstrap(self):
        """test_bootstrap func

        逐次ブートストラップの例
        スニペット 4.6

        Note:
            通常の抽出方法との比較
        """
        t1 = pd.Series([2, 3, 5], index=[0, 2, 4])  # 特徴量の観測値をそれぞれに対する t0, t1
        bar_ix = range(t1.max() + 1)                # バーのインデックス

        for time in range(3):
            print("=== {}回目の比較 ===".format(time + 1))
            ind_matrix = SampleWeighting.get_ind_matrix(bar_ix, t1)
            phi = np.random.choice(ind_matrix.columns, size=ind_matrix.shape[1])
            print("phi", phi)
            print("Standard uniqueness:", SampleWeighting.get_avg_uniqueness(ind_matrix[phi]).mean())

            phi = SampleWeighting.seq_bootstrap(ind_matrix)
            print("phi", phi)
            print("Sequential uniqueness:", SampleWeighting.get_avg_uniqueness(ind_matrix[phi]).mean())

    def test_bootstrap_mc(self):
        """ test_bootstrap_mc func

        aux_mc, get_rnd_t1 のテスト
        マルチスレッド化したモンテカルロ法
        スニペット 4.9

        """
        num_obs = 10
        num_bars = 100
        max_h = 5

        num_iters = 10
        num_threads = 1

        jobs = []
        for i in range(int(num_iters)):
            job = {"func": SampleWeighting.aux_mc, "num_obs": num_obs, "num_bars": num_bars, "max_h": max_h}
            jobs.append(job)

        if num_threads == 1:
            out = process_jobs_single(jobs)
        else:
            pass

        print(pd.DataFrame(out).describe())

    def test_sample_weighting(self):
        """test_sample_weighting func

        SampleWeighting のテスト

        """
        self.sample_weighting.sample_weighting()
        self.sample_weighting.sample_weighting()

class TestFractionalDifference(object):
    """TestFractionalDifference class

    fractional_difference のテスト
    section5

    """
    TEST_CODE = TEST_CODE
    D = 0.5

    def setup_class(self):
        stock_strategy = StockStrategy()
        self.data_df = stock_strategy.get_stock_data(code = self.TEST_CODE)

        close_df = self.data_df["Close"]
        self.close_df = close_df

        labeling = Labeling(code=self.TEST_CODE)
        # self.bins, self.events = labeling.labeling(close_df, save=True)
        self.bins, self.events = labeling.load()
        labeling.set_row_data(close_df)

        self.sample_weighting = SampleWeighting(labeling)
        # self.sample_weighting.sample_weighting(save=True)
        self.bins_sampled = self.sample_weighting.load()

    def test_plot_weights(self):
        """test_plot_weights func

        plot_weights のテスト

        """
        plot_weights(d_range=[0, 1], n_plots=11, size=6)

    def test_frac_diff(self):
        """test_frac_diff func

        frac_diff のテスト

        """
        frac_diff_df = frac_diff(self.data_df, self.D)
        print("frac_diff_df", frac_diff_df)

    def test_frac_diff_FFD(self):
        """test_frac_diff_FFD func

        frac_diff_FFD のテスト

        """
        frac_diff_FFD_df = frac_diff_FFD(self.data_df, self.D)
        print("frac_diff_FFD", frac_diff_FFD_df)

class TestEnsemble(object):
    """TestEnsemble class

    ensemble のテスト
    section6

    """
    TEST_CODE = TEST_CODE

    def setup_class(self):
        stock_strategy = StockStrategy()
        self.data_df = stock_strategy.get_stock_data(code = self.TEST_CODE)

        close_df = self.data_df["Close"]
        self.close_df = close_df

        labeling = Labeling(code=self.TEST_CODE)
        # self.bins, self.events = labeling.labeling(close_df, save=True)
        self.bins, self.events = labeling.load()
        labeling.set_row_data(close_df)

        self.sample_weighting = SampleWeighting(labeling)
        # self.sample_weighting.sample_weighting(save=True)
        self.bins_sampled = self.sample_weighting.load()

        self.fractional_difference = FractionalDifference(self.bins_sampled)
        self.frac_diff_df, self.bins_sampled = self.fractional_difference.fractional_difference(self.data_df, sample=True)

    def test_bagging_accuracy(self):
        """test_bagging_accuracy func

        bagging_accuracy のテスト

        """
        bagging_accuracy()

    def test_set_RF_and_fit(self):
        """test_set_RF func

        set_RF, fit のテスト

        """
        avg_u = 10
        ensemble = Ensemble()
        ensemble.set_RF(avg_u)
        ensemble.fit(trns_x = self.frac_diff_df, cont=self.bins_sampled)

class TestFeatureImportance(object):
    """TestFeatureImportance class

    feature_importance のテスト
    section 8

    """
    def test_get_test_data(self):
        """test_get_test_data

        get_test_data のテスト

        """
        get_test_data()

    def test_feat_importance(self):
        """test_feat_importance func

        feat_importance のテスト

        """
        trns_x, cont = get_test_data()
        feat_importance(trns_x, cont)

    def test_func(self, n_estimators=5, cv=10):
        """test_func func

        全要素の呼び出し
        スニペット 8.9

        Note:
            人工データにおける特徴量重要度関数のパフォーマンスを推定する
            ノイズ比率、すなわちノイズ特徴量 = n_features - (n_informative + n_redundant) である

        """
        trns_x, cont = get_test_data()
        args_feat_importance = {
            "min_w_leaf": [0.0], "scoring": ["accuracy"], "method": ["MDI", "MDA", "SFI"],
            "max_samples": [1.0]
        }
        jobs = (dict(zip(args_feat_importance, i) ) for i in itertools.product(*args_feat_importance.values()))
        out = []
        args_main = {
            "path_out": "./", "n_estimators": n_estimators, "tag": "test_func", "cv": cv
        }

        for job in jobs:
            job["sim_num"] = "{method}_{scoring}_{min_w_leaf}_{max_samples}".format(
                             method=job["method"], scoring=job["scoring"], min_w_leaf=job["min_w_leaf"], max_samples=job["max_samples"]
                             )
            print(job["sim_num"])
            args_main.update(job)
            imp, oob, oos = feat_importance(trns_x=trns_x, cont=cont, **args_main)

class TestBackTestOfArtificialData(object):
    def test_back_test_of_artificial_data(self):
        back_test_of_artificial_data_main()


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
