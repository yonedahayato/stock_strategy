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

from labeling.labeling import (
    Labeling,
)

from sample_weighting.sample_weighting import (
    SampleWeighting,
)

from fractional_difference.fractional_difference import (
    FractionalDifference,
    FractionalDifferenceDatasets,
)

from ensemble.ensemble import (
    Ensemble,
)

from cross_validation.cross_validation import (
    CrossValidation,
)

from helper.log import logger

from backtest.my_backtests import (
    MyBacktests,
    BacktestStrategy,
)

class FinanceMachineLearning(StockStrategy):
    """FinanceMachineLearning class

    この書籍の処理を取りまとめる

    """
    debug_code_num = 30

    def __init__(self, method_name="fincance_machine_learning", **kargs):
        super().__init__(method_name=method_name, **kargs)
        self.code_list = self.get_code_list()
        self.code_num = len(self.code_list)

    def get_stock_data(self, code):
        """get_stock_data func

        データの取得処理

        Args:
            code(int): 銘柄番号、シンボル

        Note:
            親クラスの関数をラップした
            debug の時の処理をこの関数で定義

        """
        data_df = super().get_stock_data(code=code)
        if self.debug:
            test_data_num = 500
            data_df = data_df.iloc[:test_data_num, :]
        close_df = data_df["Close"]

        return data_df, close_df

    def curate_dataset(self, save=True):
        """curate_dataset func

        データセットに関する処理

        Args:
            save(bool): 計算した結果を保存するかどうか

        """
        self.codes_curated = []
        for cnt, code in enumerate(self.code_list):
            if cnt > self.debug_code_num and self.debug:
                break

            logger.info("=== {} ===".format(code))

            # データの読み込みと設置
            try:
                data_df, close_df = self.get_stock_data(code)
            except Exception as e:
                logger.error("データの読み込みに失敗")
                logger.exception(e)
                continue
            else:
                logger.info("データの読み込みに成功")

            try:
                self.labeling = Labeling(code=code)
                bins, events = self.labeling.labeling(close_df, min_pct=0.05, save=save)
            except Exception as e:
                logger.error("ラベリングに失敗")
                logger.exception(e)
                continue
            else:
                logger.info("ラベリングに成功")

            try:
                self.sample_weighting = SampleWeighting(self.labeling)
                bins_sampled = self.sample_weighting.sample_weighting(save=save)
            except Exception as e:
                logger.error("サンプリングに失敗")
                logger.exception(e)
                continue
            else:
                logger.info("サンプリングに成功")

            self.codes_curated.append(code)

        logger.info("{} / {} 件、ラベリングとサンプリング完了".format(\
                    len(self.codes_curated), self.code_num))

    def analyze_feature(self, save=True):
        """analyze_feature func

        特徴量に関する処理をまとめる

        Args:
            save(bool): 計算した結果を保存するかどうか
            load(bool): この処理よりも前の処理の情報を取得するかどうか

        """
        self.codes_analyzed = []
        for code in self.codes_curated:
            logger.info("=== {} ===".format(code))

            try:
                self.load_data(code=code, data_name="weighted")
            except Exception as e:
                logger.error("ロード処理に失敗")
                logger.exception(e)
                continue
            else:
                logger.info("ロード処理に成功")

            try:
                self.fractional_difference = FractionalDifference(self.sample_weighting)
                frac_diff_df, bins_sampled = \
                    self.fractional_difference.fractional_difference(self.data_df, sample=True, save=save)
            except Exception as e:
                logger.error("分数次差分の計算に失敗")
                logger.exception(e)
                continue
            else:
                logger.info("分数次差分の計算に成功")

            self.codes_analyzed.append(code)

        logger.info("{} / {} 件、特徴量算出の計算完了".format(\
                    len(self.codes_analyzed), self.code_num))

    def train(self, cv=True):
        """train func

        学習に関する処理をまとめる

        Args:
            cv(bool): cross validation を使用するかどうか

        """
        fractional_difference_datasets = FractionalDifferenceDatasets()

        for code in self.codes_analyzed:
            logger.info("=== {} ===".format(code))
            try:
                self.load_data(code=code, data_name="feature_extracted")
                fractional_difference_datasets.append(self.fractional_difference)
            except Exception as e:
                logger.error("ロード処理に失敗")
                logger.exception(e)
                continue
            else:
                logger.info("ロード処理に成功")

        frac_diff_concated_df, bins_sampled_concated_df = fractional_difference_datasets.concat()

        if cv:
            logger.info("CV を使用")
            ensemble = Ensemble(fractional_difference_datasets = fractional_difference_datasets)
            cross_validation = CrossValidation(ensemble, fractional_difference_datasets = fractional_difference_datasets)

            score, ensemble = cross_validation.cross_validation()
            logger.info("cv のスコア: {}".format(score))

        else:
            logger.info("CV を不使用")
            avg_u = 10
            ensemble = Ensemble(fractional_difference_datasets = fractional_difference_datasets)
            ensemble.ensemble(avg_u)

        self.ensemble = ensemble

    def load_data(self, data_name, code):
        """load_data func

        中間ファイルの読み込みの処理をまとめる

        Note:
            ロード処理の順番は
                1. labeled
                2. weighted
                3. feature extracted

        """
        data_names = ["raw_data", "labeled", "weighted", "feature_extracted"]

        if data_name in data_names:
            try:
                self.data_df, close_df = self.get_stock_data(code)
            except Exception as e:
                logger.error("データの読み込みに失敗")
                logger.exception(e)
                raise
            else:
                logger.info("データの読み込みに成功")
                data_names.pop(0)

        if data_name in data_names:
            try:
                self.labeling = Labeling(code=code)
                bins, events = self.labeling.load()
            except FileNotFoundError as e:
                logger.error("ラベリング済みファイルが見つかりません")
                logger.exception(e)
                raise
            except Exception as e:
                logger.error("ラベリングのロードに失敗")
                logger.exception(e)
                raise
            else:
                logger.info("ラベリングのロードに成功")
                data_names.pop(0)

        if data_name in data_names:
            try:
                self.sample_weighting = SampleWeighting(self.labeling)
                bins_sampled = self.sample_weighting.load()
            except FileNotFoundError as e:
                logger.error("標本重み付け済みファイルが見つかりません")
                logger.exception(e)
                raise
            except Exception as e:
                logger.error("標本重み付けのロードに失敗")
                logger.exception(e)
                raise
            else:
                logger.info("標本重み付けのロードに成功")
                data_names.pop(0)

        if data_name in data_names:
            try:
                self.fractional_difference = FractionalDifference(self.sample_weighting)
                frac_diff_df, bins_sampled = self.fractional_difference.load()

            except FileNotFoundError as e:
                logger.error("特徴量抽出済みファイルが見つかりません")
                logger.exception(e)
                raise
            except Exception as e:
                logger.error("特徴量のロードに失敗")
                logger.exception(e)
                raise
            else:
                logger.info("特徴量抽出のロードに成功")
                data_names.pop(0)

        return

    def predict(self, data):
        """predict my_func

        推定に関する処理をまとめる

        """
        pred = self.ensemble.main_clf.predict(data)
        return pred

    def make_backtest(self, frac_diff_df):
        """make backtest

        backtest用の strategy class を作成する

        Returns:
            MyBacktestStrategy

        """
        def predict_backtest(data):
            return self.predict(data)

        ensemble = self.ensemble

        class MyBacktestStrategy(BacktestStrategy):
            """MyBacktestStrategy class

            backtest に使用する Strategy class

            """
            price_delta = .004

            def init(self):
                self.ensemble = ensemble
                self.predicts = []
                self.frac_diff_df = frac_diff_df

            def next(self):
                try:
                    frac_diff_df = self.analyze_feature()
                    if frac_diff_df.empty:
                        return
                except KeyError:
                    return
                except Exception as e:
                    logger.error("特徴量の取得に失敗")
                    logger.exception(e)
                    return
                # else:
                #     logger.info("特徴量抽出に成功")

                # pred = predict_backtest(self.data.df.iloc[[-1], :])
                pred = predict_backtest(frac_diff_df)
                pred = pred[0]
                self.predicts.append(pred)

                upper, lower = self.data.Close[-1] * (1 + np.r_[1, -1]*self.price_delta)

                if pred == 1.0 and not self.position.is_long:
                    # logger.debug("buy")
                    self.buy(tp=upper, sl=lower)
                elif pred == -1.0 and not self.position.is_short:
                    # logger.debug("sell")
                    self.sell(tp=lower, sl=upper)

            def analyze_feature(self, get_only=True):
                """analyze_feature func

                生データから特徴量の抽出する処理
                差分の計算など、時系列ごとの処理をしていると時間がかかってしまう処理などは、
                全時系列で処理する手段をとる

                Args:
                    get_only(bool):
                        計算はせず、すでに計算されたデータから
                        最前の時系列データを取得して返すかどうか

                """
                if get_only:
                    current_time = self.data.index[-1]
                    frac_diff_df = self.frac_diff_df.loc[[current_time], :]

                else:
                    fractional_difference = FractionalDifference(sample_weighting = None)
                    frac_diff_df, bins_sampled = \
                        fractional_difference.fractional_difference(self.data.df, sample=False, save=False)
                    frac_diff_df = frac_diff_df.iloc[[-1], :]

                return frac_diff_df

        return MyBacktestStrategy

    def backtest(self):
        """backtest func

        バックテストに関する処理をまとめる

        """

        results = {}
        for code in self.codes_analyzed:
            logger.info("=== {} ===".format(code))
            my_backtests = MyBacktests()

            try:
                self.load_data(code=code, data_name="feature_extracted")
            except Exception as e:
                logger.error("ロード処理に失敗")
                logger.exception(e)
                continue
            else:
                logger.info("ロード処理に成功")

            try:
                self.fractional_difference = FractionalDifference(sample_weighting = None)
                frac_diff_df, bins_sampled = \
                    self.fractional_difference.fractional_difference(self.data_df, sample=False, save=False)
            except Exception as e:
                logger.error("特徴量抽出に失敗")
                logger.exception(e)
            else:
                logger.info("特徴量抽出に成功")

            MyBacktestStrategy = self.make_backtest(frac_diff_df)

            try:
                my_backtests.execute(self.data_df, MyBacktestStrategy)
            except Exception as e:
                logger.error("バックテストに失敗")
                logger.exception(e)
                continue
            else:
                logger.info("バックテストに成功")
                results[code] = my_backtests

        for code, result in results.items():
            logger.info("=== {} ===".format(code))

            logger.debug("=== stats ===")
            logger.debug(result.stats)
            logger.debug("=== equity_curve ===")
            with pd.option_context('display.max_rows', 501):
                logger.debug(result.stats["_equity_curve"])
            logger.debug("=== trades ===")
            logger.debug("\n{}".format(result.stats["_trades"]))
            logger.debug("=== predicts ===")
            logger.debug("\n{}".format(result.stats._strategy.predicts))

    def main(self):
        logger.info("curate_dataset")
        self.curate_dataset(save=False)

        self.codes_curated = self.code_list
        logger.info("analyze_feature")
        self.analyze_feature()

        self.codes_analyzed = self.code_list
        logger.info("training")
        self.train(cv=True)
        self.backtest()
