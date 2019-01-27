import csv
import datetime
import jsm
import numpy as np
import os
import os.path as path
import pandas as pd
from pandas.core import common as com
import quandl
import re
import sys

abs_dirname = os.path.dirname(os.path.abspath(__file__))
parent_dirname = path.dirname(abs_dirname)
helper_dirname = path.join(parent_dirname, "helper")
sys.path.append(helper_dirname)

import log

logger = log.logger

api_key = "c_MVftyir5vTKxyiuego"

class GetStockData:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def logging_error(self, err_msg=""):
        logger.error(err_msg)
        logger.exception(err_msg)
        raise Exception(err_msg)

    def logging_info(self, msg=None):
        logger.info(msg)
        if self.verbose:
            print(msg)

    def get_stock_data_jsm(self, code, freq='D', start=None, end=None, periods=None):
        """
        https://qiita.com/u1and0/items/f6dad2cc2ee730be321c
        get Japanese stock data using jsm
        Usage:
            `get_jstock(6502)`
            To get TOSHIBA daily from today back to 30days except holiday.

            `get_jstock(6502, 'W', start=pd.Timestamp('2016'), end=pd.Timestamp('2017'))`
            To get TOSHIBA weekly from 2016-01-01 to 2017-01-01.

            `get_jstock(6502, end=pd.Timestamp('20170201'), periods=50)`
            To get TOSHIBA daily from 2017-02-01 back to 50days except holiday.

            `get_jstock(6502, 'M', start='first', end='last')`
            To get TOSHIBA monthly from 2000-01-01 (the date of start recording) to today.

        """
        msg = "[Get_Stock_Data:get_stock_data_jsm]: {}"

        # Default args
        if com._count_not_none(start, end, periods) == 0:
            end = "last"
            periods = 30

        # Switch frequency Dayly, Weekly or Monthl
        freq_dict = {'D': jsm.DAILY, 'W': jsm.WEEKLY, 'M': jsm.MONTHLY}

        # 'first' means the start of recording date
        if start == "first":
            data = jsm.Quotes().get_historical_prices(
                code, range_type=freq_dict[freq], all=True
            )
            start = [i.date for i in data][-1]
        else:
            data = None # Temporaly defined

        # 'last' means lata weekday (or today)
        if end == "last":
            end = pd.datetime.today()

        # Return "start" and "end"
        try:
            start, end = (x.date() if hasattr(x, "date") \
                else x for x in self.set_span(start, end, periods, freq))
        except Exception as e:
            self.logging_error(msg.format("fail to set span, {}".format(e)))
        else:
            self.logging_info(msg.format("Get data from {} to {}".format(start, end)))

        data = jsm.Quotes().get_historical_prices(
            code, range_type = freq_dict[freq], start_date=start, end_date=end
        ) if not data else data

        try:
            data_df = self.convert_dataframe(data)
        except Exception as e:
            self.logging_error(msg.format("fail to convert to dataframe, {}".format(e)))
        else:
            self.logging_info(msg.format("success to convert to dataframe"))

        return data_df

    def set_span(self, start=None, end=None, periods=None, freq='D'):
        """ 引数のstart, end, periodsに対して
        startとendの時間を返す。

        * start, end, periods合わせて2つの引数が指定されていなければエラー
        * start, endが指定されていたらそのまま返す
        * start, periodsが指定されていたら、endを計算する
        * end, periodsが指定されていたら、startを計算する
        """
        if com._count_not_none(start, end, periods) != 2: # Like a pd.data_range Error
            self.logging_error("[Get_Stock_Data:set_span]: Must specify two of start, end, or periods")

        start = start if start else (pd.Period(end, freq) - periods).start_time
        end = end if end else (pd.Period(start, freq) + Periods).start_time

        return start, end

    def convert_dataframe(self, data):
        """Convert <jsm.pricebase.PriceData> to <pandas.DataFrame>"""
        date = [_.date for _ in data]
        open = [_.open for _ in data]
        high = [_.high for _ in data]
        low = [_.low for _ in data]
        close = [_.close for _ in data]
        adj_close = [_._adj_close for _ in data]
        volume = [_.volume for _ in data]

        data_dict = {"Open": open, "High": high, "Low": low, "Close": close, "Adj_Close": adj_close, "Vloume": volume}
        columns = *data_dict.keys(),

        data_df = pd.DataFrame(data_dict, index=date, columns=columns).sort_index()
        data_df.index.name = "Date"

        return data_df

if __name__ == "__main__":
    gsd = GetStockData(verbose=True)
    data_df = gsd.get_stock_data_jsm(1332, "D", start=pd.Timestamp("20170101"), end=pd.Timestamp("20180731"))
    print(data_df)
