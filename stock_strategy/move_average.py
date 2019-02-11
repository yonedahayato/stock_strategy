import copy
import datetime
from datetime import datetime as dt
from joblib import Parallel, delayed
import jsm
import os
import pandas as pd
import random
import sys
import traceback

abspath = os.path.dirname(os.path.abspath(__file__))
p_path = os.path.dirname(abspath)
sys.path.append(p_path + "/get_stock_info")
sys.path.append(p_path + "/get_stock_info/google_cloud_storage")
sys.path.append(p_path + "/helper")
sys.path.append(p_path + "/check_reward")
sys.path.append(p_path + "/stock_strategy")

from data_downloader import Data_Downloader
from get_new_stock_code import GetCodeList
from get_stock_data import GetStockData
import log
import just_now
from save_result import Save_Result
from setting import HISTRICAL_DATA_PATH
from stock_strategy import StockStrategy, args

jst_now = just_now.jst_now

logger = log.logger


class MoveAverage(StockStrategy):
    def __init__(self, debug=True, back_test_return_date=5, \
                method_name="move_average", multiprocess=False, window=75):

        StockStrategy.__init__(self, debug=debug, back_test_return_date=back_test_return_date, \
                                method_name=method_name, multiprocess=multiprocess)

        self.window = window

    def shape_stock_data(self, stock_data_df, value="Close"):
        shape = stock_data_df.shape
        if shape[1] != 1:
            stock_data_df = stock_data_df[[value]]

        return stock_data_df

    def get_move_average(self, stock_data_df, window=None):
        stock_data_df = self.shape_stock_data(stock_data_df)

        if window == None:
            window = copy.deepcopy(self.window)

        rm_df = stock_data_df.rolling(window=window, center=False).mean()
        rm_df.columns = ["rolling_mean"]

        return rm_df

    def select_code(self, code, stock_data_df):
        move_average_df = self.get_move_average(stock_data_df)
        move_average_diff_df = move_average_df.diff(periods=1)

        sign_rising_MA_term = 3 # 10
        move_average_diff_df = move_average_diff_df.iloc[-sign_rising_MA_term:]>0
        sign_rising_MA = move_average_diff_df.all().values[0]

        if sign_rising_MA:
            self.result_codes.append(code)

def main():
    back_test_return_date = args.back_test_return_date
    move_average_window_75 = MoveAverage(debug=False, back_test_return_date=back_test_return_date,
                        method_name="MAMAM_window=75", multiprocess=False, window=75)
    move_average_window_50 = MoveAverage(debug=False, back_test_return_date=back_test_return_date,
                        method_name="MAMAM_window=50", multiprocess=False, window=50)
    move_average_window_25 = MoveAverage(debug=False, back_test_return_date=back_test_return_date,
                        method_name="MAMAM_window=25", multiprocess=False, window=25)
    move_average_window_10 = MoveAverage(debug=False, back_test_return_date=back_test_return_date,
                        method_name="MAMAM_window=10", multiprocess=False, window=10)

    move_average_window_75.execute()
    move_average_window_50.execute()
    move_average_window_25.execute()
    move_average_window_10.execute()

if __name__ == "__main__":
    main()
