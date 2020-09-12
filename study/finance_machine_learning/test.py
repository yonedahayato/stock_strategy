import os
import sys

ABSPATH = os.path.abspath(__file__)
BASEDIR = os.path.dirname(ABSPATH)
PARENTDIR = os.path.dirname(BASEDIR)
PPARENTDIR = os.path.dirname(PARENTDIR)

sys.path.append(PPARENTDIR)

from stock_strategy.stock_strategy import StockStrategy

from labeling.labeling import get_daily_vol

class TestLabeling(object):
    """TestLabeling class

    labeling のテスト

    Attributes:
        TEST_CODE(int): テストに使用する銘柄

    """

    TEST_CODE = 1332
    def setup_method(self):
        stock_strategy = StockStrategy()
        self.data_df = stock_strategy.get_stock_data(code = self.TEST_CODE)

    def test_get_daily_vol(self):
        close_df = self.data_df["Close"]
        daily_vol_df = get_daily_vol(close_df)
        print("daily_vol_df", daily_vol_df)
