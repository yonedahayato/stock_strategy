import copy
import pandas as pd

class LineInfo():
    def __init__(self, peak_info):
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

        self.peak_info = peak_info

    def append_info(self, start_index, start_index_in_peak, start_price,
                    end_index, end_index_in_peak, end_price):
        self.start_indexes.append(start_index)
        self.start_indexes_in_peak.append(start_index_in_peak)
        self.start_prices.append(start_price)
        self.end_indexes.append(end_index)
        self.end_indexes_in_peak.append(end_index_in_peak)
        self.end_prices.append(end_price)

    def set_list_to_dict(self, key, data_list):
        data_list_tmp = self.data_dict[key]
        data_list_tmp.clear()
        data_list.extend(data_list)

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

    def set_peak_lists_in_line(self):
        peak_index = copy.deepcopy(self.peak_info.peak_indexes)
        self.peak_lists_in_line = \
            [peak_index[self.start_indexes_in_peak[line_id]+1:self.end_indexes_in_peak[line_id]]\
            for line_id in self.data_df.index]

    def set_candle_indexes_in_line_without_peak(self):
        peak_info = copy.deepcopy(self.peak_info)
        self.candle_indexes_in_line_without_peak = \
            [list(
                set(range(self.data_df.iloc[line_id, :]["start_index"] + 1, self.data_df.iloc[line_id, :]["end_index"])) - \
                set(self.peak_lists_between_start_and_end)
            )\
            for line_id in self.data_df.index]

    def set_high_values_list(self, histlical_data_df):
        histlical_data_df_tmp = copy.deepcopy(histlical_data_df)
        self.high_values = histlical_data_df["High"].values

    def set_high_values_list_in_line(self):
        peak_info = copy.deepcopy(self.peak_info)
        high_values = copy.deepcopy(self.high_values)

        self.high_values_list_in_line = [
            np.transpose(
                high_values[peak_info.start_indexes[line_id]+1 : high_values[peak_info.end_indexes[line_id]]]
            )
            for lind_id in self.data_df.index]

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
                self.start_prices[line_id] +\
                self.data_df.iloc[line_id, :]["line_rate"] * \
                (time - self.start_indexes[line_id])
                for time in range(self.start_indexes[line_id] + 1,
                                  self.end_indexes[line_id])\
                ]\
            )
        for line_id in self.data_df.index]

    def set_line_values_list_in_peak(self):
        self.line_values_list_in_peak = [
            np.array([
                self.start_prices[line_id] + \
                self.data_df[line_id:, :]["line_rate"] *
                (time - self.start_indexes[line_id])
                for time in self.peak_lists_in_line[line_id]]
            )
        for line_id in self.data_df.index]

    def check_diff_between_high_value_and_line(self):
        self.list_checked_diff_between_high_value_and_line = \
            [
                (
                    (
                        self.high_values_list_in_line[line_id] - \
                        self.line_values_list[line_id] \
                     ) \
                < 0.5).all()
            for line_id in self.data_df.index]

    def check_diff_between_high_value_and_line_in_peak(sekf):
        self.list_checked_diff_between_high_value_and_line_in_peak = \
            [
                (
                    np.absolute(
                        self.high_values_list_in_peak[line_id] - \
                        self.line_values_list_in_peak[line_id] \
                        ) \
                    < 0.5).sum()
            for line_id in self.data_df.index]

    def count_peaks_used_in_line(self):
        pass
