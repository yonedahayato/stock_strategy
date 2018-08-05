from datetime import datetime
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

from get_new_stock_code import Get_Code_List
from get_stock_data import Get_Stock_Data
import log
import setting

logger = log.logger

upload_request_url = setting.request_url

class Data_Uploader:
    def __init__(self):
        msg = "[Data_Uploader:__init__]: {}"

        self.save_dir = p_dirname + "/stock_data"
        self.logging_info(msg.format("save dir: {}".format(self.save_dir)))

        if not os.path.exists(self.save_dir):
            os.mkdir(self.save_dir)

        self.request_url = upload_request_url

    def logging_info(self, msg):
        logger.info(msg)

    def logging_error(self, msg):
        logger.exception(msg)
        logger.error(msg)

    def upload(self):
        msg = "[Data_Uploader:upload]: {}"
        try:
            stock_list = self.get_stock_list()
        except Exception as e:
            err_msg = msg.format("fail to get stock list, {}".format(e))
            self.logging_error(err_msg)
            raise Exception(err_msg)
        else:
            sccs_msg = msg.format("success to get stock list")
            self.logging_info(sccs_msg)

        for stock_code in stock_list:
            try:
                stock_data_df = self.get_stock_data(stock_code)
                save_file_path = self.save_stock_data(stock_data_df, stock_code)
                self.request_uploader(save_file_path)
                self.remove_file(save_file_path)
            except Exception as e:
                err_msg = msg.format("fail to get stock data, code: {}, {}".format(stock_code, e))
                self.logging_error(err_msg)
                raise Exception(err_msg)
            else:
                sccs_msg = msg.format("success to get stock data, code: {}".format(stock_code))
                self.logging_info(sccs_msg)

    def get_stock_list(self):
        self.gcl = Get_Code_List(verbose=False)
        code_df = self.gcl.get_new_stock_code()
        self.stock_list = list(code_df["コード"])

        return self.stock_list

    def get_stock_data(self, code):
        gsd = Get_Stock_Data(verbose=True)
        data_df = gsd.get_stock_data_jsm(code, "D", end=pd.Timestamp.today(), periods=120)
        return data_df

    def save_stock_data(self, data_df, stock_code):
        msg = "[Data_Uploader:save_stock_data]: {}"
        save_file_path = self.save_dir + "/stock_data_{}.csv".format(stock_code)
        data_df.to_csv(save_file_path)

        self.logging_info(msg.format("save file path: {}".format(save_file_path)))
        return save_file_path

    def request_uploader(self, save_file_path):
        save_file_path = save_file_path.split("/")
        save_file_path = "/".join(save_file_path[-2:])
        payload = {'file_path': save_file_path}
        r = requests.post(self.request_url+"/upload", data=payload)
        print(r.text)

    def remove_file(self, save_file_path):
        os.remove(save_file_path)
        return

if __name__ == "__main__":
    du = Data_Uploader()
    du.upload()
