from datetime import datetime
import os
import pandas as pd

abspath = os.path.dirname(os.path.abspath(__file__))
p_dirname = os.path.dirname(abspath)

NOW_STR_IN_SETTING = datetime.now().strftime("%Y%m%d")

# log
log_save_path = p_dirname + "/helper/log"

# stock data upload, download request url
# request_url = "http://127.0.0.1:8090"
request_url = "http://192.168.100.101:8090"

# tosho_1st_list_url
TOSHO_1ST_LIST_URL = "http://www.jpx.co.jp/markets/statistics-equities/misc/01.html"
NIKKEI_225_LIST_URL = "https://indexes.nikkei.co.jp/nkave/index/component?idx=nk225"

# range date to get stock data
HISTRICAL_DATA_RANGE_START = pd.Timestamp("20100101")
HISTRICAL_DATA_RANGE_END = pd.Timestamp("20190308")
HISTRICAL_DATA_RANGE_END_NOW = pd.Timestamp(NOW_STR_IN_SETTING)

# path save and get histrical data to local
HISTRICAL_DATA_PATH = p_dirname + "/get_stock_info/stock_data/{code}.csv"
HISTRICAL_EXCHANGE_DATA_PATH = p_dirname + "/get_stock_info/exchange_data/{name}.csv"

# path save result
RESULT_PATH = p_dirname + "/check_reward/result/selected_code"

# get stock data to local
THREAD_NUM = 2

# push line
LINE_NOTIFY_TOKEN = ""

# quandl API key
QUANDL_API_KEY = ""

# oanda API kye
OANDA_API_KEY = ""
