import asyncio
import gc
import os
from os import path
import pandas as pd
import sys
import threading
import time

abs_dirname = os.path.dirname(os.path.abspath(__file__))
parent_dirname = path.dirname(abs_dirname)
helper_dirname = path.join(parent_dirname, "helper")
sys.path.append(helper_dirname)
sys.path.append(abs_dirname)

from get_new_stock_code import GetCodeListNikkei225
from get_stock_data import GetStockData
import log
from setting import *

logger = log.logger

get_stock_data = GetStockData(verbose=True)

def req(code):
    try:
        data_df = get_stock_data.get_stock_data_jsm(code, "D",
                    start=HISTRICAL_DATA_RANGE_START, end=HISTRICAL_DATA_RANGE_END_NOW)
        data_df.to_csv(HISTRICAL_DATA_PATH.format(code=code))

    except Exception as e:
        logger.error("[{}]: ヒストリカルデータの取得に失敗しました。{}".format(code, e))
    else:
        logger.info("[{}]: ヒストリカルデータを取得しました。".format(code))


async def run(loop, code_list):
    async def run_req(code):
        return await loop.run_in_executor(None, req, code)

    tasks = [run_req(code) for code in code_list]
    return await asyncio.gather(*tasks, return_exceptions=True)


def GetStockDataesToLocal():
    """GetStockDataesToLocal func

    Note:
        処理フロー
            1. 銘柄リストを取得
            2. 銘柄ごとにデータを取得

    """
    os.makedirs(os.path.dirname(HISTRICAL_DATA_PATH), exist_ok=True)

    gcl_nikkei_225 = GetCodeListNikkei225(verbose=True)
    code_list_df = gcl_nikkei_225.get_new_stock_code()
    code_list = code_list_df["コード"].values.tolist()

    code_list_option = {"日経平均": 998407, "TOPIX": 998405}
    code_list += list(code_list_option.values())

    code_list_tmp = []

    for cnt, code in enumerate(code_list):
        logger.debug("code; {}, {} / {}".format(code, cnt, len(code_list)))
        code_list_tmp.append(code)

        if cnt % THREAD_NUM == (THREAD_NUM - 1) or cnt == len(code_list)-1:
        # バッチごとに実行
        # 最後のバッチ
            try:
                st = time.time()
                loop = asyncio.get_event_loop()
                loop.run_until_complete(run(loop, code_list_tmp))
                logger.info("処理時間: {}".format(time.time() - st))
            except Exception as e:
                logger.exception("非同期処理が失敗しました。: {}".format(e))
            else:
                logger.info("非同期処理終了しました。")
            code_list_tmp = []



if __name__ == "__main__":
    GetStockDataesToLocal()
