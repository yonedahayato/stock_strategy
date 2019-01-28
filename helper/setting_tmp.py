import os
abspath = os.path.dirname(os.path.abspath(__file__))
p_dirname = os.path.dirname(abspath)


# log
log_save_path = p_dirname + "/helper/log"

# stock data upload, download request url
# request_url = "http://127.0.0.1:8090"
request_url = "http://192.168.100.101:8090"

# tosho_1st_list_url
TOSHO_1ST_LIST_URL = "http://www.jpx.co.jp/markets/statistics-equities/misc/01.html"
NIKKEI_225_LIST_URL = "https://indexes.nikkei.co.jp/nkave/index/component?idx=nk225"

# path save and get histrical data to local
HISTRICAL_DATA_PATH = p_dirname + "/get_stock_info/stock_data/{code}.csv"

# path save result
RESULT_PATH = p_dirname + "/check_reward/result/selected_code"

# get stock data to local
THREAD_NUM = 2
