from stock_strategy import (
    # library
    argparse,
    copy,
    datetime,
    dt,
    os,
    pd,
    sys,

    # my library
    StockStrategy,

    # variable
    args,
    logger
)

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress

from helper.peak import PeakInfo
from helper.line import LineInfo

class TrendLineUsingLinearRegression(StockStrategy):
    def __init__(self, debug=True, back_test_return_date=5, \
                method_name="trend_line_using_linear_regression", multiprocess=False):
        StockStrategy.__init__(self, debug=debug, back_test_return_date=back_test_return_date, \
                                method_name=method_name, multiprocess=multiprocess)

    def select_code(self, code, stock_data_df):
        pass

def main():
    # back_test_return_date = args.back_test_return_date
    back_test_return_date = 5

    trend_line = TrendLine(debug=False, back_test_return_date=back_test_return_date,
                           method_name="TrendLineUsingLinearRegression",
                           multiprocess=False)
    # result = trend_line.execute()

if __name__ == "__main__":
    main()
