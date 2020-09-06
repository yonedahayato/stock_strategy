import os
import pytest
import sys

abspath = os.path.dirname(os.path.abspath(__file__))
p_path = os.path.dirname(abspath)

sys.path.append(p_path)

from test_libs import (
    logger,
    setting,
    StockStrategy,
)

class TestStockStrategy(object):
    """TestStockStrategy class

    stock strategy script のテスト

    Attributes:
        TEST_CODE(str): テストするコード番号

    """
    TEST_CODE = "1332"

    def setup_method(self):
        print("\nsetup now ...\n")
        self.stock_strategy = StockStrategy(debug=True, back_test_return_date=5,
                                            method_name="method_is_test")

    def test_get_code_list(self):
        """test_get_code_list func

        code list の取得のテスト

        """
        code_list = self.stock_strategy.get_code_list()

    def test_get_stock_data(self):
        """test_get_stock_data func

        ヒストリカルデータの取得のテスト

        """
        stock_data_df = self.stock_strategy.get_stock_data(self.TEST_CODE)

    def test_select_code(self):
        """test_select_code func

        購買する銘柄かどうかを判断するテスト

        """
        stock_data_df = self.stock_strategy.get_stock_data(self.TEST_CODE)
        self.stock_strategy.select_code(self.TEST_CODE, stock_data_df)

    def test_save_result(self):
        """test_save_result func

        結果の保存のテスト

        """
        code_list = self.stock_strategy.get_code_list()
        self.stock_strategy.result_codes = ["1332"]
        self.stock_strategy.elapsed_times = [10]
        json_result = self.stock_strategy.save_result()

    def test_draw_graph(self):
        """test_draw_graph func

        グラフの描画のテスト

        """
        self.stock_strategy.result_codes = ["1332"]

        # グラフ内容を確認したい場合はremove=Trueに
        self.stock_strategy.draw_graph(remove=True)

    def test_execute_stock_strategy(self):
        """test_execute_stock_strategy func

        stock_strategy の実行のテスト

        """
        stock_strategy = StockStrategy(debug=True, back_test_return_date=5,
                                       method_name="method_is_test")
        stock_strategy.execute()
