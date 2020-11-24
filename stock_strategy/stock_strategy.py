import argparse
import copy
import datetime
from datetime import datetime as dt
import os
import pandas as pd
from statistics import mean
import sys
import time

abspath = os.path.dirname(os.path.abspath(__file__))
p_path = os.path.dirname(abspath)
sys.path.append(p_path + "/get_stock_info")
sys.path.append(p_path + "/get_stock_info/google_cloud_storage")
sys.path.append(p_path + "/get_stock_info/google_cloud_storage/google/cloud_storage")
sys.path.append(p_path + "/helper")
sys.path.append(abspath + "/helper")
sys.path.append(p_path + "/check_reward")
sys.path.append(p_path + "/draw_graph")
sys.path.append(p_path + "/draw_graph/helper")
sys.path.append(p_path + "/notification")

from data_downloader import Data_Downloader
from decide_drawing import PackageDrawing
from draw_graph import DrawGraph
from get_new_stock_code import GetCodeList, GetCodeListNikkei225
from get_stock_data import GetStockData
import log
logger = log.logger
import just_now
jst_now = just_now.jst_now
from push_line import push_line
from result import Result
from setting import (
    HISTRICAL_DATA_PATH,
    GOOGLE_REPORT_URL
)
from uploader import Uploader

DOWNLOAD_METHODES = ["LOCAL", "CLOUD", "API"]
CODE_LIST = ["1st_all", "1st_225"]

parser = argparse.ArgumentParser(description="stock_strategyの引数")
parser.add_argument("--back_test_return_date",
                    help = "どのくらいback test の使用するか(0の場合はback testには使用せず、全てのデータを使用)",
                    default=0,
                    type=int)


class StockStrategy(object):
    """StockStrategy class

    stock strategy のベースのクラス

    """

    debug_code_num = 10

    def __init__(self, debug=False, back_test_return_date=0,
                 method_name="method_name", multiprocess=False,
                 download_method="LOCAL", code_list = "1st_225"):

        """__init__ func

        パラメータの設置

        Args:
            debug(bool): デバッグモードかどうか
            back_test_return_date(int): バックテストに使うデータが直近何日までのデータか
            method_name(str): 手法の名前
            multiprocess(bool): 並列処理を行うかどうか
            download_method(str): 使用するデータをどのように取得するかどうか
            code_list(str): 使用するデータの種類

        """
        self.msg_tmpl = "[Stock_Storategy:{}]: "

        self.debug = debug
        self.back_test_return_date = back_test_return_date
        self.method_name = method_name
        self.multiprocess = multiprocess

        self.result_codes = []

        self.download_method = download_method
        self.code_list = code_list

    def get_code_list(self):
        """get_code_list func

        コードリストの取得

        Returns:
            list: コードリスト

        """
        if self.code_list == "1st_all":
            gettter = GetCodeList()

        elif self.code_list == "1st_225":
            getter = GetCodeListNikkei225()

        self.new_code_list = getter.get_new_stock_code()
        self.new_code_list = list(self.new_code_list["コード"])

        if self.debug:
            self.new_code_list = self.new_code_list[:self.debug_code_num]

        return self.new_code_list

    def get_stock_data(self, code):
        """get_stock_data func

        ヒストリカルデータの取得

        Args:
            code(str): コード番号

        Note:
            LOCALの場合:
                csv からファイルを読み取る

        """
        msg = self.msg_tmpl.format("get_stock_data") + "{}"

        if self.download_method == "CLOUD":
            dd = Data_Downloader()
            stock_data_df = dd.download(code)
            stock_data_df = stock_data_df.set_index("Date")
            if self.back_test_return_date != 0:
                stock_data_df = stock_data_df.iloc[:-self.back_test_return_date]

        elif self.download_method == "LOCAL":
            stock_data_df = pd.read_csv(HISTRICAL_DATA_PATH.format(code=code), index_col=0, parse_dates=[0])
            if self.back_test_return_date != 0:
                stock_data_df = stock_data_df.iloc[:-self.back_test_return_date]

        if self.debug:
            print(msg.format(stock_data_df))

        return stock_data_df

    def select_code(self, code, stock_data_df):
        """select_code func

        購買銘柄かどうかの判断

        Args:
            code(xxx): 対象銘柄コード
            stock_data_df(pandas.DataFrame): ヒストリカルデータ

        Note:
            # example #
            # stock code number : i
            # stock data length : n
            # close value : C[i]
            # selected code list = argmax_{i} ( (C[n-1] - C[n-2]) / C[n-2] )
        """

        if len(self.result_codes) == 0:
            self.result_codes.append(int(code))
            self.max_close_rate = (stock_data_df.iloc[-1]["Close"] - stock_data_df.iloc[-2]["Close"]) / stock_data_df.iloc[-2]["Close"]
        else:
            max_close_rate_tmp = (stock_data_df.iloc[-1]["Close"] - stock_data_df.iloc[-2]["Close"]) / stock_data_df.iloc[-2]["Close"]

            if max_close_rate_tmp > self.max_close_rate:
                self.max_rate_close = max_close_rate_tmp
                self.result_codes = [int(code)]

    def get_stock_data_index(self):
        """get_stock_data_index func

        使用したデータセットの期間を取得

        Returns:
            pandas.Series: 使用したデータの期間

        Note:
            get_code_list の実行が前提
            new_code_list が必要

        """
        code = self.new_code_list[0]
        stock_data_df = self.get_stock_data(code)
        return stock_data_df.index

    def save_result(self):
        """save_result func

        結果の保存

        Returns:
            Result: 結果情報

        Note:
            elapsed_times がなければエラー

        """
        to_GCS = not self.debug
        result = Result(to_GCS=to_GCS)

        result.add_info("result_code_list", self.result_codes)
        result.add_info("method", self.method_name)

        stock_data_df_index = self.get_stock_data_index()
        result.add_info("data_range_start_to_compute", stock_data_df_index[0])
        result.add_info("data_range_end_to_compute", stock_data_df_index[-1])
        result.add_info("back_test_return_date", self.back_test_return_date)

        result.add_info("elapsed_time_average", mean(self.elapsed_times))

        json_result = result.save()
        return json_result

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

    def draw_graph(self, to_GCS=True, remove=True):
        """draw_graph func

        購買決定した銘柄のヒストリカルデータをグラフ化
        その他、付随情報も記載

        Args:
            to_GCS(bool): GCSに送信するかどうか
            remove(bool): 作成した画像を削除するかどうか

        """
        for cnt, code in enumerate(self.result_codes):
            logger.info("draw graph {}".format(code))

            stock_data_df = self.get_stock_data(code)

            package_drawing = PackageDrawing(self, cnt, stock_data_df, code)

            draw_graph = DrawGraph(**package_drawing.__dict__)

            graph_image_path = draw_graph.draw()

            if self.debug:
                logger.info("debug mode なので、作成したグラフの保存、ラインへの通知を行いません")

            elif to_GCS:
                image_basename = os.path.basename(graph_image_path)
                uploader = Uploader(bucket_name="yoneda-stock-strategy")
                uploader.upload(local_path=graph_image_path,
                                gcp_path="result/image/{}".format(image_basename), public=True)

            else:
                push_line(str(code), image_path = graph_image_path)

            if remove:
                logger.info("作成したグラフを削除します")
                draw_graph.remove()
            else:
                logger.info("作成したグラフを削除せず、残します: {}".format(draw_graph.save_path))

    def execute(self):
        """execute func

        処理フロー
            1. コードリストの取得
            2. 銘柄ごとに処理
                a. ヒストリカルデータの取得
                b. 購入銘柄かどうかの判断
            3. 購入銘柄の結果リストを表示
            4. 購入銘柄の結果を保存
            5. グラフとして描画


        Returns:
            list[str]: 購買銘柄の結果リスト

        Note:
            - 2020/09/06 : 並列化(multiprocess)はできてなさそう

        """
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
            self.elapsed_times = []
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
                    start_time = time.time()
                    self.select_code(code, stock_data_df)
                    elapsed_time = time.time() - start_time
                    self.elapsed_times.append(elapsed_time)
                    logger.info("elapsed_time: {}".format(elapsed_time))
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
            if self.debug:
                logger.info("debug mode のため、結果を通知しません")
            else:
                push_line(GOOGLE_REPORT_URL)
        except:
            err_msg = msg.format("fail to save result select code.")
            logger.error(err_msg)
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            logger.info(msg.format("success to save result select code."))

        try:
            self.draw_graph(to_GCS=not self.debug)
        except:
            err_msg = msg.format("fail to draw graph.")
            logger.error(err_msg)
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            logger.info(msg.format("success to draw graph."))


        return self.result_codes
