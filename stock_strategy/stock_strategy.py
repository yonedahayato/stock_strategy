import argparse
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
sys.path.append(p_path + "/draw_graph")
sys.path.append(p_path + "/notification")

from data_downloader import Data_Downloader
from get_new_stock_code import GetCodeList, GetCodeListNikkei225
from get_stock_data import GetStockData
import log
import just_now
from save_result import Save_Result
from setting import HISTRICAL_DATA_PATH
from draw_graph import DrawGraph
from push_line import push_line

jst_now = just_now.jst_now

logger = log.logger

DOWNLOAD_METHODES = ["LOCAL", "CLOUD", "API"]
CODE_LIST = ["1st_all", "1st_225"]

parser = argparse.ArgumentParser(description="stock_strategyの引数")
parser.add_argument("--back_test_return_date",
                    help = "どのくらいback test の使用するか(0の場合はback testには使用せず、全てのデータを使用)",
                    default=0,
                    type=int)

args = parser.parse_args()

class StockStrategy:
    def __init__(self, debug=False, back_test_return_date=args.back_test_return_date,
                 method_name="method_name", multiprocess=False,
                 download_method="LOCAL", code_list = "1st_225"):
        self.msg_tmpl = "[Stock_Storategy:{}]: "

        self.debug = debug
        self.back_test_return_date = back_test_return_date
        self.method_name = method_name
        self.multiprocess = multiprocess

        self.result_codes = []

        self.download_method = download_method
        self.code_list = code_list

    def get_code_list(self):
        if self.code_list == "1st_all":
            gettter = GetCodeList()

        elif self.code_list == "1st_225":
            getter = GetCodeListNikkei225()

        self.new_code_list = getter.get_new_stock_code()
        self.new_code_list = list(self.new_code_list["コード"])

        if self.debug:
            self.new_code_list = self.new_code_list[:10]

        return self.new_code_list

    def get_stock_data(self, code):
        msg = self.msg_tmpl.format("get_stock_data") + "{}"

        if self.download_method == "CLOUD":
            dd = Data_Downloader()
            stock_data_df = dd.download(code)
            stock_data_df = stock_data_df.set_index("Date")
            if self.back_test_return_date != 0:
                stock_data_df = stock_data_df.iloc[:-self.back_test_return_date]

        elif self.download_method == "LOCAL":
            stock_data_df = pd.read_csv(HISTRICAL_DATA_PATH.format(code=code), index_col=0)
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
        sr.add_info("data_range_start_to_compute", stock_data_df_index[0])
        sr.add_info("data_range_end_to_compute", stock_data_df_index[-1])
        sr.add_info("back_test_return_date", self.back_test_return_date)

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

    def draw_graph(self):
        for code in self.result_codes:
            logger.info("draw graph {}".format(code))
            stock_data_df = self.get_stock_data(code)
            draw_graph = DrawGraph(stock_data_df, code, self.method_name)
            graph_image_path = draw_graph.draw()
            push_line(str(code), image_path = graph_image_path)
            draw_graph.remove()
            return

    def execute(self):
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
                    continue
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
            json_result = self.save_result()
        except:
            err_msg = msg.format("fail to save result select code.")
            logger.error(err_msg)
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            logger.info(msg.format("success to save result select code."))

        try:
            self.draw_graph()
        except:
            err_msg = msg.format("fail to draw graph.")
            logger.error(err_msg)
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            logger.info(msg.format("success to draw graph."))


        return self.result_codes
