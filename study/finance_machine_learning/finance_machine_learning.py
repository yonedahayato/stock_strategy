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

from helper.log import logger

class FinanceMachineLearning(StockStrategy):
    """FinanceMachineLearning class

    この書籍の処理を取りまとめる

    """
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
            if cnt > 10 and self.debug:
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
            pass
        else:
            avg_u = 10
            ensemble = Ensemble(fractional_difference_datasets = fractional_difference_datasets)
            ensemble.ensemble(avg_u)

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


    def predict(self):
        """predict my_func

        推定に関する処理をまとめる

        """
        pass

    def main(self):
        # logger.info("curate_dataset")
        # self.curate_dataset()

        # self.codes_curated = self.code_list
        # logger.info("analyze_feature")
        # self.analyze_feature()

        self.codes_analyzed = self.code_list
        logger.info("training")
        self.train(cv=False)
