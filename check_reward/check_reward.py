from glob import glob
import json
import os
import pandas as pd
import sys

abspath_check_reward = os.path.dirname(os.path.abspath(__file__))
p_dirname = os.path.dirname(abspath_check_reward)
sys.path.append(p_dirname+"/stock_strategy")

from save_result import Save_Result, save_result_path, logger
from check_list import *

result_path = save_result_path + "/result/reward"
SELECTED_CODE_RESULT_PATH = save_result_path + "/result/selected_code"

class Check_Reward(Save_Result):
    def __init__(self, save_path=result_path):
        Save_Result.__init__(self, save_path = save_path)

        # self.selected_code_json_file = "move_average_2018_08_14_08_55_08.json"
        self.selected_code_json_files = []
        for method_name in CHECK_LIST:
            files_tmp = glob("{}/{}*".format(SELECTED_CODE_RESULT_PATH, method_name))
            files_tmp.sort()
            self.selected_code_json_files.append(files_tmp[-1])

        logger.info("selected_code_json_files: {}".format(self.selected_code_json_files))
        self.date_index = []

    def make_format(self):
        logger.info("[Check_Reward:make_format]: not need to make format.")

    def read_json_result(self, json_file_path):
        # json_file_path = "{}/{}".format(save_result.result_path, self.selected_code_json_file)
        with open(json_file_path) as j_file:
            selected_code_dic = json.load(j_file)
            self.method = selected_code_dic["method"]
            self.data_range_start_to_compute = selected_code_dic["data_range_start_to_compute"]
            self.data_range_end_to_compute = selected_code_dic["data_range_end_to_compute"]
            self.back_test_return_date = selected_code_dic["back_test_return_date"]

            # self.data_range_start = selected_code_dic["data_range_start"]
            # self.data_range_end = selected_code_dic["data_range_end"]
            self.stock_list = selected_code_dic["result_code_list"]
            self.creat_time = selected_code_dic["creat_time"]

        return self.stock_list

    def get_stock_data(self, code):
        dd = Data_Downloader()
        stock_data_df = dd.download(code)
        stock_data_df = stock_data_df.set_index("Date")

        return stock_data_df

    def compute_reward(self, stock_data_df):
        close = stock_data_df.loc[self.data_range_end]["Close"]
        reward = stock_data_df.loc[self.data_range_end:].iloc[1:]["Close"]

        if len(self.date_index) == 0:
            self.date_index = list(reward.index)

        reward = (reward - close) / close

        reward_list = list(reward)
        return reward_list

    def check_reward(self):
        msg = "[Check_Reward:check_reward]: {}"

        for json_file_path in self.selected_code_json_files:
            logger.debug(msg.format("json_file_path: {}".format(json_file_path)))

            stock_list = self.read_json_result(json_file_path)
            logger.debug("stock_list: {}".format(stock_list))
            if stock_list == []:
                logger.info(msg.format("stock list to check is empty."))
                return

            return
            self.reward_result_dic = {}
            for code in stock_list:
                msg_tmp = msg.format("code: {}".format(code))
                logger.info(msg_tmp)
                stock_data_df = self.get_stock_data(code)

                reward_list = self.compute_reward(stock_data_df)
                self.reward_result_dic[str(code)] = reward_list

            self.save_reward_result()

    def save_reward_result(self):
        self.format = {"code_json_file": self.selected_code_json_file,
                        "method": self.method,
                        "data_range_start": self.data_range_start,
                        "data_range_end": self.data_range_end,
                        "stock_list": self.stock_list,
                        "reward_results": self.reward_result_dic,
                        "date": self.date
                        }
        self.save() # json save

        summary_df = pd.DataFrame(self.reward_result_dic).T

        summary_df = pd.concat([summary_df, summary_df.mean(axis=1)], axis=1)

        summary_mean = summary_df.mean(axis=0).to_frame().T
        summary_mean.index = ["mean"]

        summary_df = pd.concat([summary_df, summary_mean], axis=0)
        summary_df.columns = self.date_index + ["mean"]

        print(summary_df)

def main():
    cr = Check_Reward()
    cr.check_reward()

if __name__ == "__main__":
    main()
