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
sys.path.append(abspath + "/get_stock_info")
sys.path.append(abspath + "/get_stock_info/google_cloud_storage")
sys.path.append(abspath + "/helper")
sys.path.append(abspath + "/check_reward")

from data_downloader import Data_Downloader
from get_new_stock_code import Get_Code_List
from get_stock_data import get_stock_data, Get_Stock_Data
from helper import log
import just_now
from save_result import Save_Result

jst_now = just_now.jst_now

logger = log.logger

class Stock_Storategy:
    def __init__(self, debug=False, back_test_return_date=0, method_name="method_name", multiprocess=False):
        self.msg_tmpl = "[Stock_Storategy:{}]: "

        self.debug = debug
        self.back_test_return_date = back_test_return_date
        self.method_name = method_name
        self.multiprocess = multiprocess

        self.result_codes = []

    def get_code_list(self):
        gcl = Get_Code_List()
        self.new_code_list = gcl.get_new_stock_code()
        self.new_code_list = list(self.new_code_list["コード"])
        if self.debug:
            self.new_code_list = self.new_code_list[:10]

        return self.new_code_list

    def get_stock_data(self, code):
        msg = self.msg_tmpl.format("get_stock_data") + "{}"

        dd = Data_Downloader()
        print(code)
        stock_data_df = dd.download(code)
        stock_data_df = stock_data_df.set_index("Date")
        if self.back_test_return_date != 0:
            stock_data_df = stock_data_df.iloc[:-self.back_test_return_date]

        if self.debug:
            print(msg.format(stock_data_df))

        return stock_data_df

    def select_code(self, code, stock_data_df):
        # example #
        # stock code number : i
        # stock data length : n
        # close value : C[i]
        # selected code list = argmax_{i} ( (C[n-1] - C[n-2]) / C[n-2] )

        if len(self.result_codes) == 0:
            self.result_codes.append(int(code))
            self.max_close_rate = (stock_data_df.iloc[-1]["Close"] - stock_data_df.iloc[-2]["Close"]) / stock_data_df.iloc[-2]["Close"]
        else:
            max_close_rate_tmp = (stock_data_df.iloc[-1]["Close"] - stock_data_df.iloc[-2]["Close"]) / stock_data_df.iloc[-2]["Close"]

            if max_close_rate_tmp > self.max_close_rate:
                self.max_rate_close = max_close_rate_tmp
                self.result_codes = [int(code)]

    def get_stock_data_index(self):
        code = self.new_code_list[0]
        stock_data_df = self.get_stock_data(code)
        return stock_data_df.index

    def save_result(self):
        sr = Save_Result()

        sr.add_info("result_code_list", self.result_codes)
        sr.add_info("method", self.method_name)

        stock_data_df_index = self.get_stock_data_index()
        sr.add_info("data_range_start", stock_data_df_index[0])
        sr.add_info("data_range_end", stock_data_df_index[-1])

        sr.save()

    def check_select_code(self):
        msg = self.msg_tmpl.format("check_select_code") + "{}"
        logger.info(msg.format(self.result_codes))

    def multiprocess_exect(self, code_cnt, code):
        msg = self.msg_tmpl.format("multiprocess_exect") + "{}"

        logger.info(msg.format("code {}, {} / {}".format(code, code_cnt+1, len(self.new_code_list))))

        try:
            stock_data_df = self.get_stock_data(code)
        except:
            err_msg = msg.format("fail to get stock histlical data.")
            logger.error(err_msg)
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            logger.info(msg.format("success to get stock histlical data."))

        try:
            self.select_code(code, stock_data_df)
        except:
            err_msg = msg.format("fail to select code.")
            logger.error(err_msg)
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            logger.info(msg.format("success to select code."))

        return self.result_codes

    def exect(self):
        msg = self.msg_tmpl.format("exect") + "{}"

        try:
            code_list = self.get_code_list()
        except:
            err_msg = msg.format("fail to get code list.")
            logger.error(err_msg)
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            logger.info(msg.format("success to get code list."))

        if not self.multiprocess:
            for code_cnt, code in enumerate(code_list):
                logger.info(msg.format("code {}, {} / {}".format(code, code_cnt+1, len(code_list))))

                try:
                    stock_data_df = self.get_stock_data(code)
                except:
                    err_msg = msg.format("fail to get stock histlical data.")
                    logger.error(err_msg)
                    logger.exception(err_msg)
                    raise Exception(err_msg)
                else:
                    logger.info(msg.format("success to get stock histlical data."))

                try:
                    self.select_code(code, stock_data_df)
                except:
                    err_msg = msg.format("fail to select code.")
                    logger.error(err_msg)
                    logger.exception(err_msg)
                    raise Exception(err_msg)
                else:
                    logger.info(msg.format("success to select code."))
        elif self.multiprocess:
            try:
                processed = Parallel(n_jobs=-1)([delayed(self.multiprocess_exect)(code_cnt, code) for code_cnt, code in enumerate(code_list)])
            except:
                err_msg = msg.format("fail to exect multiprocess.")
                logger.error(err_msg)
                logger.exception(err_msg)
                raise Exception(err_msg)
            else:
                logger.info(msg.format("success to ecect multiprocess."))

        try:
            self.check_select_code()
        except:
            err_msg = msg.format("fail to check select code.")
            logger.error(err_msg)
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            logger.info(msg.format("success to check select code."))

        try:
            self.save_result()
        except:
            err_msg = msg.format("fail to save result select code.")
            logger.error(err_msg)
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            logger.info(msg.format("success to save result select code."))


class Move_Average(Stock_Storategy):
    def __init__(self, debug=True, back_test_return_date=5, \
                method_name="move_average", multiprocess=False, window=75):

        Stock_Storategy.__init__(self, debug=debug, back_test_return_date=back_test_return_date, \
                                method_name=method_name, multiprocess=multiprocess)

        self.window = window

    def shape_stock_data(self, stock_data_df, value="Close"):
        shape = stock_data_df.shape
        if shape[1] != 1:
            stock_data_df = stock_data_df[[value]]

        return stock_data_df

    def get_move_average(self, stock_data_df):
        stock_data_df = self.shape_stock_data(stock_data_df)

        rm_df = stock_data_df.rolling(window=self.window, center=False).mean()
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

        sign_rising_MA_term = 20 # 10
        move_average_diff_df = move_average_diff_df.iloc[-sign_rising_MA_term:]>0
        sign_rising_MA = move_average_diff_df.all().values[0]

        if self.debug:
            print("sign_rising_MA: {}".format(sign_rising_MA))

        stock_data_low_df = self.shape_stock_data(stock_data_df, value="Low")
        diff_Low_MoveAverage = stock_data_low_df - move_average_df

        sign_rising_Low_term = 20 # 10
        diff_Low_MoveAverage = diff_Low_MoveAverage.iloc[-sign_rising_Low_term:] > 0

        sign_rising_Low = False
        for cnt in range(sign_rising_Low_term-1):
            if (diff_Low_MoveAverage.iloc[cnt].values[0] == False) and \
                (diff_Low_MoveAverage.iloc[cnt+1].values[0] == True):
                sign_rising_Low = True
                break

        if self.debug:
            print("sign_rising_Low: {}".format(sign_rising_Low))

        # if sign_rising_MA and sign_rising_Low:
        #     self.result_codes.append(code)
        self.result_codes.append(code)
        self.result_codes.reverse()
        if len(self.result_codes) > 5:
            self.result_codes = self.result_codes[:5]

def main():
    # ss = Stock_Storategy(debug=True, back_test_return_date=5)
    # ss.exect()

    ma = Move_Average(debug=True, back_test_return_date=5, method_name="MAMAM", multiprocess=False, window=75)
    ma.exect()

if __name__ == "__main__":
    main()
