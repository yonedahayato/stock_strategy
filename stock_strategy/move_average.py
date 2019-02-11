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
        # ＊買い
        # １、７５日移動平均線が上向いている
        # ２、７５日移動平均線の下にあった株価（安値）が上に抜ける
        #
        # ＊売り
        # １、７５日移動平均線を下に抜ける

        move_average_df = self.get_move_average(stock_data_df)
        move_average_diff_df = move_average_df.diff(periods=1)

        sign_rising_MA_term = 100 # 10
        move_average_diff_df = move_average_diff_df.iloc[-sign_rising_MA_term:]>0
        sign_rising_MA = move_average_diff_df.all().values[0]

        if self.debug:
            print("sign_rising_MA: {}".format(sign_rising_MA))

        stock_data_low_df = self.shape_stock_data(stock_data_df, value="Low")
        diff_Low_MoveAverage = stock_data_low_df - move_average_df

        sign_rising_Low_term = 100 # 10
        diff_Low_MoveAverage = diff_Low_MoveAverage.iloc[-sign_rising_Low_term:] > 0

        sign_rising_Low = False
        for cnt in range(sign_rising_Low_term-1):
            if (diff_Low_MoveAverage.iloc[cnt].values[0] == False) and \
                (diff_Low_MoveAverage.iloc[cnt+1].values[0] == True):
                sign_rising_Low = True
                break

        if self.debug:
            print("sign_rising_Low: {}".format(sign_rising_Low))

        if sign_rising_MA and sign_rising_Low:
            self.result_codes.append(code)
        # self.result_codes.append(code)
        # self.result_codes.reverse()
        # if len(self.result_codes) > 5:
        #     self.result_codes = self.result_codes[:5]

def main():
    # ss = Stock_Storategy(debug=True, back_test_return_date=5)
    # ss.exect()

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
