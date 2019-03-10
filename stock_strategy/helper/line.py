import copy
import numpy as np
import pandas as pd
pd.options.display.max_rows = None
pd.options.display.max_columns = None

from stock_strategy import logger

class LineInfo():
    def __init__(self, peak_info, value_accept_between_high_value_and_line):
        self.reset_indexes()

        self.peak_info = peak_info

        # start peak と end peak の間の長さが何本以上あればよいのか
        self.candle_num_start_to_end = 10

        # ラインの班員全てにおいて、高値とライン上の値の差がどれくらいの範囲内なはっていればよいか
        #  オリジナルは0.5
        self.value_accept_between_high_value_and_line = value_accept_between_high_value_and_line

        # ピークにおいて、高値とライン上の値の差がどれくらいの範囲内なはっていればよいか
        # オリジナルは0.5
        self.value_accept_between_high_value_and_line_in_peak = value_accept_between_high_value_and_line

    def reset_indexes(self):
        self.start_indexes = []
        self.start_indexes_in_peak = []
        self.start_prices = []
        self.end_indexes = []
        self.end_indexes_in_peak = []
        self.end_prices = []

        self.data_dict = {"start_index": self.start_indexes,
                          "start_index_in_peak": self.start_indexes_in_peak,
                          "start_price": self.start_prices,
                          "end_index": self.end_indexes,
                          "end_index_in_peak": self.end_indexes_in_peak,
                          "end_price": self.end_prices}

    def set_list_to_dict(self, key, data_list):
        data_list_tmp = self.data_dict[key]
        data_list_tmp.clear()
        data_list_tmp.extend(data_list)

    # 全ての辞書のkeyのlistの長さが同じかどうかを確認する
    def check_length(self):
        length = 0
        for cnt, data_list in enumerate(self.data_dict.values()):
            if cnt == 0:
                length = len(data_list)
            else:
                if length != len(data_list):
                    return False

        return True

    def make_data_frame(self):
        self.data_df = pd.DataFrame(self.data_dict)
        self.reset_indexes()

        self.data_df = self.data_df.astype(
             {"start_index": "uint32",
              "start_index_in_peak": "uint32",
              "start_price": "float64",
              "end_index": "uint32",
              "end_index_in_peak": "uint32",
              "end_price": "float64"}
              )

        return copy.deepcopy(self.data_df)

    def compute_length_index_to_index(self):
        self.data_df["length_index_to_index"] = \
            self.data_df["end_index"] - self.data_df["start_index"]

        self.data_df["length_index_to_index_in_peak"] = \
            self.data_df["end_index_in_peak"] - self.data_df["start_index_in_peak"]

    def compute_line_rate(self):
        data_df = copy.deepcopy(self.data_df)
        self.data_df["line_rate"] = (data_df["end_price"] - data_df["start_price"]) / \
                                    (data_df["end_index"] - data_df["start_index"])

    def check_line_rate(self):
        self.data_df = self.data_df.query("line_rate <= 0")
        self.data_df = self.data_df.reset_index(drop=True)

    def set_peak_lists_in_line(self):
        peak_index = copy.deepcopy(self.peak_info.peak_indexes)
        self.peak_lists_in_line = \
            [peak_index[peak_index.index(self.data_df["start_index"].iat[line_id])+1 : \
                        peak_index.index(self.data_df["end_index"].iat[line_id])] \
            for line_id in self.data_df.index]

    def set_candle_indexes_in_line_without_peak(self):
        peak_info = copy.deepcopy(self.peak_info)

        self.candle_indexes_in_line_without_peak = \
            [list(
                set(range(self.data_df["start_index"].iat[line_id] + 1, self.data_df["end_index"].iat[line_id])) - \
                set(self.peak_lists_in_line[line_id]) \
            )\
            for line_id in self.data_df.index]

    def set_high_values_list(self, histlical_data_df):
        histlical_data_df_tmp = copy.deepcopy(histlical_data_df)
        self.high_values = histlical_data_df["High"].values

    def set_high_values_list_in_line(self):
        high_values = copy.deepcopy(self.high_values)

        self.high_values_list_in_line = [
            np.transpose(
                high_values[self.data_df["start_index"].iat[line_id]+1 :
                            self.data_df["end_index"].iat[line_id]]
            )
            for line_id in self.data_df.index]

    def set_high_values_list_in_peak(self):
        high_values = copy.deepcopy(self.high_values)
        peak_info = copy.deepcopy(self.peak_info)

        self.high_values_list_in_peak = [
            high_values[self.peak_lists_in_line[line_id]]
        for line_id in self.data_df.index]

    def set_line_values_list(self, histlical_data_df):
        peak_info = copy.deepcopy(self.peak_info)
        self.line_values_list = [
            np.array([
                self.data_df["start_price"].iat[line_id] +\
                self.data_df.iloc[line_id, :]["line_rate"] * \
                (time - self.data_df["start_index"].iat[line_id])
                for time in range(self.data_df["start_index"].iat[line_id] + 1,
                                  self.data_df["end_index"].iat[line_id])\
                ]\
            )
        for line_id in self.data_df.index]

    def set_line_values_list_in_peak(self):
        self.line_values_list_in_peak = [
            np.array([
                self.data_df["start_price"].iat[line_id] + \
                self.data_df["line_rate"].iat[line_id] *
                (time - self.data_df["start_index"].iat[line_id])
                for time in self.peak_lists_in_line[line_id]]
            )
        for line_id in self.data_df.index]

    def check_diff_between_high_value_and_line(self):
        self.list_checked_diff_between_high_value_and_line = \
            [
                (
                    (self.high_values_list_in_line[line_id] - \
                     self.line_values_list[line_id]) \
                < self.value_accept_between_high_value_and_line).all()
            for line_id in self.data_df.index]

    def check_diff_between_high_value_and_line_in_peak(self):
        self.list_checked_diff_between_high_value_and_line_in_peak = \
            [
                (
                    np.absolute(
                        self.high_values_list_in_peak[line_id] - \
                        self.line_values_list_in_peak[line_id] \
                        ) \
                    < self.value_accept_between_high_value_and_line_in_peak)
            for line_id in self.data_df.index]

        self.counts_checked_diff_between_high_value_and_line_in_peak = \
            [checked.sum() for checked in self.list_checked_diff_between_high_value_and_line_in_peak]

    def check_sumary_diff_between_high_value_and_line(self):
        # high value が line value を上回っていない
        # （peak にて） high value と line value の値が 0.5以下となる peak が 1以上存在する
        list_checked_summary_diff = \
            [
                self.list_checked_diff_between_high_value_and_line[line_id] and \
                (self.counts_checked_diff_between_high_value_and_line_in_peak[line_id] >= 1)
            for line_id in self.data_df.index]

        if not self.data_df.empty:
            self.data_df = self.data_df[
                pd.Series(list_checked_summary_diff)
            ].reset_index(drop=True)
        else:
            logger.info("ckeck するデータが空です。")

    def check_trend_line_rule(self):
        # 通常ルール1（突き抜ける）、ピーク３〜４
        trend_line_rule_1 = \
            [   True
                if ((self.counts_checked_diff_between_high_value_and_line_in_peak[line_id] == 1) |
                    (self.counts_checked_diff_between_high_value_and_line_in_peak[line_id] == 2)) &
                   self.data_df["length_index_to_index"].iat[line_id] + 1 >= self.candle_num_start_to_end
                else False
            for line_id in self.data_df.index]

        # 直近ルール（突き抜けなくてもいい）
        trend_line_rule_1_immediate = \
            [   True
                if (self.counts_checked_diff_between_high_value_and_line_in_peak[line_id] == 1) |
                   (self.counts_checked_diff_between_high_value_and_line_in_peak[line_id] == 2)
                else False
            for line_id in self.data_df.index]

        # 通常ルール2（突き抜ける）、ピーク５以上
        trend_line_rule_2 = \
            [   True
                if (self.counts_checked_diff_between_high_value_and_line_in_peak[line_id] > 2)
                else False
            for line_id in self.data_df.index]

        checked_rules = pd.DataFrame({"trend_line_rule_1": trend_line_rule_1,
                                      "trend_line_rule_1_immediate": trend_line_rule_1_immediate,
                                      "trend_line_rule_2": trend_line_rule_2})

        self.data_df = pd.concat([self.data_df, checked_rules], axis=1)
        self.data_df = self.data_df[checked_rules.any(axis=1)]
        self.data_df = self.data_df.reset_index(drop=True)
