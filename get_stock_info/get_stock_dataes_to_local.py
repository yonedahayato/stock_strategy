import gc
import os
from os import path
import pandas as pd
import sys
import threading

abs_dirname = os.path.dirname(os.path.abspath(__file__))
parent_dirname = path.dirname(abs_dirname)
helper_dirname = path.join(parent_dirname, "helper")
sys.path.append(helper_dirname)
sys.path.append(abs_dirname)

from get_new_stock_code import GetCodeListNikkei225
from get_stock_data import GetStockData
import log
from setting import HISTRICAL_DATA_PATH

logger = log.logger

def request(code_list, result):
    for code in code_list:
        try:
            get_stock_data = GetStockData(verbose=True)
            data_df = get_stock_data.get_stock_data_jsm(code, "D", start=pd.Timestamp("20170101"), end=pd.Timestamp("20180731"))
            data_df.to_csv("{}/{}.csv".format(HISTRICAL_DATA_PATH, code))
        except Exception as e:
            logger.error("[{}]: ヒストリカルデータの取得に失敗しました。{}".format(code, e))
        else:
            logger.info("[{}]: ヒストリカルデータを取得しました。".format(code))
            result.append(code)

        get_stock_data = None
        data_df = None
        gc.collect()


def split_list(l, n):
    """
    リストをサブリストに分割する
    :param l: リスト
    :param n: サブリストの要素数
    :return:
    """
    for idx in range(0, len(l), n):
        yield l[idx:idx + n]


def GetStockDataesToLocal():
    gcl_nikkei_225 = GetCodeListNikkei225(verbose=True)
    code_list_df = gcl_nikkei_225.get_new_stock_code()
    code_list = code_list_df["コード"].values.tolist()
    code_list = code_list[:10]

    thread_num = 2
    code_lists = list(split_list(code_list, int(len(code_list)/thread_num) + 1))

    thread_list = []
    result = []
    for thread_id in range(thread_num):
        thread = threading.Thread(target=request, args=([code_lists[thread_id], result]), name = "thread_{}".format(thread_id))
        thread_list.append(thread)

    for thread in thread_list:
        while True:
            try:
                thread.start()
            except Exception as e:
                logger.exception("threadの処理の開始を失敗しました、再度行います, {}".format(e))
                continue
            else:
                break

    for thread in thread_list:
        while True:
            try:
                print("xxx")
                thread.join()
                print("aaa")
            except Exception as e:
                logger.exception("thredの処理の終了を失敗しました、再度行います, {}".format(e))
                continue
            else:
                break

    print(result)

if __name__ == "__main__":
    GetStockDataesToLocal()
