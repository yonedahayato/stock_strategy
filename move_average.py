import datetime
from datetime import datetime as dt
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

class move_average:
    def __init__(self, value_type, window=75, verbose=False, debug=False, back_test_return_date=0):
        if value_type.lower() in ["open", "low", "high", "close"]:
            self.value_type = value_type
        else:
            error_msg = "[move_average:__init__]: value_type is invalid: '{}'".format(value_type)
            logger.error(error_msg)
            logger.exception(error_msg)
            raise Exception(error_msg)

        self.window = window

        self.rm_df = None
        self.rstd_df = None
        self.upper_bound_df = None
        self.lower_bound_df = None

        self.result_codes = []

        self.verbose = verbose
        self.debug = debug

        self.back_test_return_date = back_test_return_date

    def logging_info(self, msg):
        logger.info(msg)
        if self.verbose:
            print(msg)

    def shape(self, stock_data_df):
        shape = stock_data_df.shape
        if shape[1] != 1:
            stock_data_df = stock_data_df.ix[:, [self.value_type]]

        return stock_data_df

    def move_average(self, stock_data_df):
        stock_data_df = self.shape(stock_data_df)
        #rm_df = pd.rolling_mean(stock_data_df, window=self.window) # feature warning
        rm_df = stock_data_df.rolling(window=self.window, center=False).mean()
        rm_df.columns = ["rolling_mean"]
        self.rm_df = rm_df

        return rm_df

    def bollinger_bands(self, stock_data_df):
        msg = "[move_average:bollinger_bands]: {}"
        if len(stock_data_df) <= self.window:
            raise Exception(msg.format("stock data < window"))

        stock_data_df = self.shape(stock_data_df)
        self.rm_df = self.move_average(stock_data_df)
        #self.rstd_df = pd.rolling_std(stock_data_df, window=self.window) # featre warning
        self.rstd_df = stock_data_df.rolling(window=self.window, center=False).std()
        self.rstd_df.columns = ["rolling_std"]

        self.upper_bound_df = pd.DataFrame(self.rm_df["rolling_mean"] + self.rstd_df["rolling_std"] * 2)
        self.lower_bound_df = pd.DataFrame(self.rm_df["rolling_mean"] - self.rstd_df["rolling_std"] * 2)
        self.upper_bound_df.columns = ["upper_bound"]
        self.lower_bound_df.columns = ["lower_bound"]

        self.bollinger_bands_df = pd.concat([self.rm_df, self.rstd_df, \
                                        self.upper_bound_df, self.lower_bound_df, stock_data_df], axis=1)
        return self.bollinger_bands_df

    def get_buy_codes(self, random_choice=True):
        msg = "[move_average:get_buy_codes]: {}"

        jst_now_str = jst_now.strftime('%Y-%m-%d')
        end_date = jst_now - datetime.timedelta(days=200)
        end_date_str = end_date.strftime('%Y-%m-%d')

        gcl = Get_Code_List()
        new_code_list = gcl.get_new_stock_code()
        new_code_list = list(new_code_list["コード"])
        if self.debug:
            new_code_list = new_code_list[:5]

        flag_list_macr = []
        flag_list_dive_lower_bound = []
        flag_list_dive_move_average = []
        for i, code in enumerate(new_code_list):
            self.logging_info(msg.format("no. {}/{}, code: {}".format(i, len(new_code_list),code)))

            try:
                # stock_data_df = get_stock_data(code, end_date_str, jst_now_str)

                # gsd = Get_Stock_Data()
                # stock_data_df = gsd.get_stock_data_jsm(code, 'D', start=pd.Timestamp(end_date_str), end=pd.Timestamp(jst_now_str))

                dd = Data_Downloader()
                stock_data_df = dd.download(code)
                stock_data_df = stock_data_df.set_index("Date")
                if self.back_test_return_date != 0:
                    stock_data_df = stock_data_df.iloc[:-self.back_test_return_date]

            except jsm.exceptions.CCODENotFoundException:
                continue
            except Exception as e:
                error_msg = msg.format("get stock data error, code: {},\
                    end_data_str: {}, jst_now_str: {}, result_codes: {}, {}".format(\
                    code, end_date_str, jst_now_str, self.result_codes, e))
                logger.error(error_msg)
                logger.exception(error_msg)
                raise Exception(error_msg)

            try:
                bollinger_bands_df = self.bollinger_bands(stock_data_df)
            except Exception as e:
                error_msg = msg.format("fail to compute bollinger bands, result_codes:{}, {}".format(self.result_codes, e))
                logger.error(error_msg)
                logger.exception(error_msg)
            else:
                sccess_msg = "success to compute bollinger bands"
                logger.info(sccess_msg)

            # 移動平均線の変化率
            move_average_change_rate = (bollinger_bands_df.ix[-1, "rolling_mean"] - bollinger_bands_df.ix[-2, "rolling_mean"]) /\
                                        bollinger_bands_df.ix[-1, "rolling_mean"]
            # 株価(t-1) > 移動平均(t-1) and 株価(t) < 移動平均(t)
            flag_dive_move_average = (bollinger_bands_df.ix[-2, self.value_type] > bollinger_bands_df.ix[-2, "rolling_mean"]) and \
                                        (bollinger_bands_df.ix[-1, self.value_type] < bollinger_bands_df.ix[-1, "rolling_mean"])
            # 株価(t-1) > 下限ボリンジャーバンド(t-1) and 株価(t) < 下限ボリンジャーバンド(t)
            flag_dive_lower_bound = (bollinger_bands_df.ix[-2, self.value_type] > bollinger_bands_df.ix[-2, "lower_bound"]) and \
                                        (bollinger_bands_df.ix[-1, self.value_type] < bollinger_bands_df.ix[-1, "lower_bound"])

            flag_list_macr.append(move_average_change_rate > 0)
            flag_list_dive_move_average.append(flag_dive_move_average)
            flag_list_dive_lower_bound.append(flag_dive_lower_bound)

            if (move_average_change_rate > 0) and (flag_dive_lower_bound or flag_dive_move_average):
                self.result_codes.append(int(code))

        self.logging_info(msg.format("num_macr: {}, num_dive_move_average: {}, num_dive_lower_bound: {}".format(\
                sum(flag_list_macr), sum(flag_list_dive_move_average), sum(flag_list_dive_lower_bound))))

        sr = Save_Result()

        sr.add_info("result_code_list", self.result_codes)
        sr.add_info("method", "move_average")
        stock_data_df_index = stock_data_df.index
        sr.add_info("data_range_start", stock_data_df_index[0])
        sr.add_info("data_range_end", stock_data_df_index[-1])

        sr.save()

        if random_choice:
            if len(self.result_codes) == 0:
                self.logging_info(msg.format("result_codes is empty"))
                return []
            buy_code = random.choice(self.result_codes)
            return buy_code

if __name__ == "__main__":
    window = 75
    code = 1332
    ma = move_average(value_type="Close", window=window, verbose=True, debug=False, back_test_return_date=5)
    buy_code = ma.get_buy_codes()
    print(ma.result_codes)
    print(buy_code)
