from time import sleep
import os
import pandas as pd
import requests
import sys

abspath = os.path.dirname(os.path.abspath(__file__))
p_dirname = os.path.dirname(abspath)
gp_dirname = os.path.dirname(p_dirname)
helper_dir = gp_dirname + "/helper"

sys.path.append(abspath)
sys.path.append(p_dirname)
sys.path.append(helper_dir)

from data_uploader import Data_Uploader
from get_new_stock_code import GetCodeList
from get_stock_data import Get_Stock_Data
import log
import setting

logger = log.logger
download_request_url = setting.request_url

class Data_Downloader(Data_Uploader):
    def __init__(self):
        Data_Uploader.__init__(self)
        self.download_url = download_request_url

    def download(self, stock_code):
        file_path = "stock_data/stock_data_{}.csv".format(stock_code)
        self.request_downloader(file_path)
        file_path = "{}/{}".format(p_dirname, file_path)
        stock_data_df = self.read_csv_dataframe(file_path)
        self.remove_file(file_path)
        return stock_data_df

    def request_downloader(self, file_path):
        msg = "[Data_Downloader:request_downloader]: {}"
        file_path = file_path.split("/")
        file_path = "/".join(file_path[-2:])
        payload = {'file_path': file_path}
        request_cnt = 0
        while True:
            try:
                r = requests.post(self.request_url+"/download", data=payload)
            except requests.exceptions.ConnectionError:
                error_msg = msg.format("fail to conect to downloader.")
                logger.error(error_msg)
                logger.exception(error_msg)
                raise Exception(error_msg)
            except Exception as e:
                error_msg = msg.format("fail to request download, {}".format(e))
                logger.error(error_msg)
                logger.exception(error_msg)
                raise Exception(e)
            else:
                success_msg = msg.format("success to conect to downloader.")
                logger.info(success_msg)

            if str(r.status_code) == "200":
                success_msg = msg.format("success to request to downloader, message: {}".format(r.text))
                logger.info(success_msg)
                break
            elif request_cnt == 3:
                error_msg = msg.format("fail to request to downloader 3 times.")
                logger.error(error_msg)
                logger.exception(error_msg)
                raise Exception(error_msg)
            else:
                error_msg = msg.format("fail to request to downloader, request_cnt: {}".format(request_cnt))
                logger.error(error_msg)
                logger.exception(error_msg)
                request_cnt += 1
                sleep(5)

    def read_csv_dataframe(salf, file_path):
        stock_data_df = pd.read_csv(file_path)
        return stock_data_df

if __name__ == "__main__":
    dd = Data_Downloader()
    data_df = dd.download(1301)
    print(data_df)
