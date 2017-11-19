import just_now
jst_now = just_now.jst_now
import pandas as pd
import sys
from datetime import datetime as dt
import datetime
import random

from get_stock_data import get_stock_data
from get_new_stock_code import get_new_stock_code

class move_average:
    def __init__(self, value_type, window=75):
        if value_type.lower() in ["open", "low", "high", "close"]:
            self.value_type = value_type
        else:
            print("value_type is invalid: '{}'".format(value_type))

        self.window = window

        self.rm_df = None
        self.rstd_df = None
        self.upper_bound_df = None
        self.lower_bound_df = None

        self.result_codes = []

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

    def buy_codes(self, random_choice=True):
        jst_now_str = jst_now.strftime('%Y-%m-%d')
        end_date = jst_now - datetime.timedelta(days=200)
        end_date_str = end_date.strftime('%Y-%m-%d')

        new_code_list = get_new_stock_code()
        new_code_list = list(new_code_list["コード"])

        flag_list_macr = []
        flag_list_dive_lower_bound = []
        flag_list_dive_move_average = []
        for i, code in enumerate(new_code_list):
            print("no. {}, code: {}".format(i, code))
            try:
                stock_data_df = get_stock_data(code, end_date_str, jst_now_str)
            except Exception as e:
                print("get stock data error, {}".format(e))

            bollinger_bands_df = self.bollinger_bands(stock_data_df)

            move_average_change_rate = (bollinger_bands_df.ix[-1, "rolling_mean"] - bollinger_bands_df.ix[-2, "rolling_mean"]) /\
                                        bollinger_bands_df.ix[-1, "rolling_mean"]
            flag_dive_move_average = (bollinger_bands_df.ix[-2, self.value_type] > bollinger_bands_df.ix[-2, "rolling_mean"]) and \
                                        (bollinger_bands_df.ix[-1, self.value_type] < bollinger_bands_df.ix[-1, "rolling_mean"])
            flag_dive_lower_bound = (bollinger_bands_df.ix[-2, self.value_type] > bollinger_bands_df.ix[-2, "lower_bound"]) and \
                                        (bollinger_bands_df.ix[-1, self.value_type] < bollinger_bands_df.ix[-1, "lower_bound"])

            print("move_average_change_rate > 0: {}, flag_dive_move_average: {}, flag_dive_lower_bound: {}".format(\
                    (move_average_change_rate > 0), flag_dive_move_average, flag_dive_lower_bound))

            flag_list_macr.append(move_average_change_rate > 0)
            flag_list_dive_move_average.append(flag_dive_move_average)
            flag_list_dive_lower_bound.append(flag_dive_lower_bound)

            if (move_average_change_rate > 0) and (flag_dive_lower_bound or flag_dive_move_average):
                self.result_codes.append(code)

        print("num_macr: {}, num_dive_move_average: {}, num_dive_lower_bound: {}".format(\
                sum(flag_list_macr), sum(flag_list_dive_move_average), sum(flag_list_dive_lower_bound)))

        if random_choice:
            buy_code = random.choice(self.result_codes)
            return buy_code

if __name__ == "__main__":
    window = 75
    code = 1332
    ma = move_average(value_type="Close", window=window)
    buy_code = ma.buy_codes()
    print(ma.result_codes)
    print(buy_code)
