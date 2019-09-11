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
    def test_shuld_execute_stock_strategy(self):
        stock_strategy = StockStrategy(debug=True, back_test_return_date=5,
                                       method_name="method_is_test")
        stock_strategy.execute()
