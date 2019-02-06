import copy
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
from stock_strategy import StockStrategy

result_path = save_result_path + "/result/reward"
SELECTED_CODE_RESULT_PATH = save_result_path + "/result/selected_code"

COMPUTE_REWARD_METHOD = ["using_all_of_data_for_backtest_with_mean", "using_all_of_data_for_backtest"]

class Check_Reward(Save_Result):
    def __init__(self, save_path=result_path, download_method="LOCAL",
                 compute_reward_methodes=["using_all_of_data_for_backtest_with_mean", "using_all_of_data_for_backtest"]):
        Save_Result.__init__(self, save_path = save_path)

        self.compute_reward_methodes = compute_reward_methodes
        self.stock_strategy = StockStrategy(download_method=download_method)

        # self.selected_code_json_file = "move_average_2018_08_14_08_55_08.json"
        self.selected_code_json_files = []
        for method_name in CHECK_LIST:
            files_tmp = glob("{}/{}*".format(SELECTED_CODE_RESULT_PATH, method_name))
            files_tmp.sort()
            self.selected_code_json_files.append(files_tmp[-1])

        logger.info("selected_code_json_files: {}".format(self.selected_code_json_files))
        self.make_new_format()


    def make_new_format(self):
        self.date_indexes_for_backtest = []

        self.reward_results = []
        self.result_format = {
                                "code": [],
                                "reward_rates": [],
                                "reward_rate_mean": 0
                            }
        self.date_indexes = []
        self.reward_rate_mean_in_method = []

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

            self.stock_list = selected_code_dic["result_code_list"]
            self.creat_time = selected_code_dic["creat_time"]

        return self.stock_list

    def get_stock_data(self, code):
        stock_data_df = self.stock_strategy.get_stock_data(code)
        return stock_data_df

    def compute_reward(self, stock_data_df):
        # close_value = stock_data_df.loc[self.data_range_end]["Close"]
        # reward = stock_data_df.loc[self.data_range_end:].iloc[1:]["Close"]

        result_format_tmp = copy.deepcopy(self.result_format)

        close_value_bought = stock_data_df.loc[self.data_range_end_to_compute]["Close"]
        close_values_for_backtest = stock_data_df.loc[self.data_range_end_to_compute:].iloc[1:]["Close"]

        if len(self.date_indexes) == 0:
            self.date_indexes_for_backtest = list(close_values_for_backtest.index)

        reward_rates = (close_values_for_backtest - close_value_bought) / close_value_bought

        if "using_all_of_data_for_backtest_with_mean" in self.compute_reward_methodes:
            result_format_tmp["reward_rate_mean"] = reward_rates.mean()


        if "using_all_of_data_for_backtest" in self.compute_reward_methodes:
            result_format_tmp["reward_rates"] = list(reward_rates)

        return result_format_tmp

    def check_reward(self):
        msg = "[Check_Reward:check_reward]: {}"

        for json_file_path in self.selected_code_json_files:
            logger.debug(msg.format("json_file_path: {}".format(json_file_path)))

            stock_list = self.read_json_result(json_file_path)
            logger.debug("stock_list: {}".format(stock_list))
            if stock_list == []:
                logger.info(msg.format("stock list to check is empty."))
                return

            for code in stock_list:
                msg_tmp = msg.format("code: {}".format(code))
                logger.info(msg_tmp)
                stock_data_df = self.get_stock_data(code)

                reward_result = self.compute_reward(stock_data_df)
                reward_result["code"] = str(code)
                self.reward_results.append(reward_result)

            self.reward_rate_mean_in_method.append(reward_result["reward_rate_mean"])
            self.save_reward_result(json_file_path)
            self.make_new_format()

    def save_reward_result(self, json_file_path):

        count_winner = sum([ reward_rate > 0 for raward_rate in self.reward_rate_mean_in_method])
        self.format = {"code_json_file": json_file_path,
                        "method": self.method,
                        "data_range_start": self.data_range_start_to_compute,
                        "data_range_end": self.data_range_end_to_compute,
                        "stock_list": self.stock_list,
                        "reward_results": self.reward_results,
                        "creat_time": self.creat_time,
                        "reward_rate_mean_in_method": self.reward_rate_mean_in_method.mean(),
                        "count_winner_brand": "{} / {}".format(count_winner, len(self.stock_list))
                        }
        self.save() # json save


def main():
    cr = Check_Reward(download_method="LOCAL", compute_reward_methodes=["using_all_of_data_for_backtest_with_mean", "using_all_of_data_for_backtest"])
    cr.check_reward()

if __name__ == "__main__":
    main()
