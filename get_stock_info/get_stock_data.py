import csv
import datetime
import jsm
import numpy as np
import os
import pandas as pd
from pandas.core import common as com
import quandl
import re
import sys

abs_dirname = os.path.dirname(os.path.abspath(__file__))
parent_dirname = abs_dirname.split("/")
parent_dirname = "/".join(parent_dirname[:-1])
sys.path.append(parent_dirname + "/helper")

import log

logger = log.logger

api_key = "c_MVftyir5vTKxyiuego"

class Stock :
    def __init__(self, code):
        self.code_ = code

    def Get(self, start_date, end_date, api_key, shape_value="Close"):
        year, month, day = start_date.split("-")
        start = datetime.date(int(year), int(month), int(day))
        year, month, day = end_date.split("-")
        end = datetime.date(int(year), int(month), int(day))

        quandl.ApiConfig.api_key = api_key
        quandl.ApiConfig.api_version = '2015-04-09'
        data = quandl.get(self.code_, start_date = start, end_date = end)
        # data = quandl.get('NSE/OIL', start_date = start, end_date = end)
        print(data.head())

        date, values = self.Shape(data, shape_value)
        return (date, values)

    def Shape(self, data):
        return

class TseStock(Stock) :
    def __init__(self, code):
        self.code_ = code

    def Shape(self, data, shape_value):
        date = data.index.strftime('%Y-%m-%d')
        if shape_value == "All":
            return (date, data)

        values = data[shape_value]

        return (date, values)

def main():
    args = sys.argv
    codelist_file = str(args[1])
    start_date = str(args[2])
    end_date = str(args[3])
    api_key = "c_MVftyir5vTKxyiuego"

    print("get stocks")
    print("codelist file = " + codelist_file)
    print("date  = " + start_date + " to " + end_date)
    print("api_key  = " + api_key)

    code_list = pd.read_csv(codelist_file)
    print(code_list)

    for key, codes in code_list.iteritems():
        for code in codes:
            if str(key) == "TSE":
                print("TSE " + str(code))
                stock = TseStock(code)

            date, values = stock.Get(start_date, end_date, api_key)
            #print(date)
            #print(values)

            filename_code = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '-', str(code))
            f = open("code_" + filename_code + "_" + start_date + "_" + end_date + ".csv", 'w')
            writer = csv.writer(f, lineterminator='\n')

        for d, c in zip(date[::-1], values[::-1]):
            csv_row = [d,c]
            writer.writerow(csv_row)
        f.close()

def get_stock_data(code, start, end):
    code = "TSE/"+str(code)
    print("code: {}".format(code))
    print("start: {}, end: {}".format(start, end))

    stock = TseStock(code)
    shape_value = "All"
    date, values = stock.Get(start, end, api_key, shape_value)
    return values

class Get_Stock_Data:
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
    #main()
    # stock_df = get_stock_data(1332, "2017-12-12", "2018-07-31")
    # print(stock_df)
    gsd = Get_Stock_Data(verbose=True)
    data_df = gsd.get_stock_data_jsm(1606, "D", start=pd.Timestamp("20170101"), end=pd.Timestamp("20180731"))
    print(data_df)
