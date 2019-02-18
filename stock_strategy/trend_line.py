from stock_strategy import (
    # library
    argparse,
    copy,
    datetime,
    dt,
    os,
    pd,
    sys,

    # my library
    StockStrategy,

    # variable
    args,
    logger
)
import itertools
import numpy as np

from helper.peak import PeakInfo
from helper.line import LineInfo


class TrendLine(StockStrategy):
    def __init__(self, debug=True, back_test_return_date=5, \
                method_name="trend_line", multiprocess=False):

        StockStrategy.__init__(self, debug=debug, back_test_return_date=back_test_return_date, \
                                method_name=method_name, multiprocess=multiprocess)

    def reset_info_each_brand(self):
        # for small peak
        self.rear_candle, self.middle_candle, self.fore_candle = [pd.Series([])] * 3
        self.small_peak_info = PeakInfo()

        # for large peak
        self.large_peak_info = PeakInfo()
        self.peak_indexes_in_small_peaks = []

        # for trend line
        self.lines_info = LineInfo(self.large_peak_info)
        self.trend_lines_info = LineInfo(self.large_peak_info)

    def set_candle(self, candle):
        if self.rear_candle.empty:
            self.rear_candle = copy.deepcopy(candle)
        elif self.middle_candle.empty:
            self.middle_candle = copy.deepcopy(self.rear_candle)
            self.rear_candle = copy.deepcopy(candle)
        else:
            self.fore_candle = copy.deepcopy(self.middle_candle)
            self.middle_candle = copy.deepcopy(self.rear_candle)
            self.rear_candle = copy.deepcopy(candle)

    def check_small_peak(self, fore_candle_index, for_buy=True):
        # for buy
        middle_candle_index = fore_candle_index - 1

        if self.fore_candle["High"] < self.middle_candle["High"] and \
           self.middle_candle["High"] > self.rear_candle["High"]:

            self.small_peak_info.append_info(index = middle_candle_index,\
                                             date = self.middle_candle.name, \
                                             price = self.middle_candle["High"])

        elif self.fore_candle["High"] == self.middle_candle["High"] and \
             self.middle_candle["High"] > self.rear_candle["High"]:

            back_past_cnt = 1
            while True:
                if fore_candle_index - back_past_cnt < 0:
                    break

                if self.data_df_tmp.iloc[fore_candle_index - back_past_cnt, :]["High"] < self.middle_candle["High"]:
                    self.small_peak_info.append_info(index = middle_candle_index,\
                                                     date = self.middle_candle.name, \
                                                     price = self.middle_candle["High"])
                    break

                elif self.data_df_tmp.iloc[fore_candle_index - back_past_cnt, :]["High"] == self.middle_candle["High"]:
                    pass
                elif self.data_df_tmp.iloc[fore_candle_index - back_past_cnt, :]["High"] > self.middle_candle["High"]:
                    break

                back_past_cnt += 1

        # TODO: for sell

    def check_large_peak(self, for_buy=True):
        for idx in range(1, self.small_peak_info.get_length() - 1):
            if self.small_peak_info.peak_prices[idx - 1] <= self.small_peak_info.peak_prices[idx] and \
               self.small_peak_info.peak_prices[idx] <= self.small_peak_info.peak_prices[idx + 1]:

                self.large_peak_info.append_info(**self.small_peak_info.get_info_from_id_as_dict(idx))
                self.peak_indexes_in_small_peaks.append(idx)

        # TODO: for sell

    def detect_small_peak(self, data_df):
        self.data_df_tmp = copy.deepcopy(data_df)

        for index, (date, candle) in enumerate(self.data_df_tmp.iterrows()):
            self.set_candle(candle)

            if self.fore_candle.empty:
                continue

            self.check_small_peak(index)

        del self.data_df_tmp

    def detect_large_peak(self):
        if self.small_peak_info.get_length() < 3:
            logger.info("[detect large peak]: No small peak, so I can not detect large peak")

        self.large_peak_info.append_info(**self.small_peak_info.get_info_from_id_as_dict(0))

        self.check_large_peak()

        self.large_peak_info.append_info(**self.small_peak_info.get_info_from_id_as_dict(-1))

    def detect_trend_line(self, stock_data_df):
        lines_tmp = list(itertools.combinations(self.peak_indexes_in_small_peaks, 2))

        self.lines_info.set_list_to_dict("start_index_in_peak", [line[0] for line in lines_tmp])
        self.lines_info.set_list_to_dict("end_index_in_peak", [line[1] for line in lines_tmp])

        self.lines_info.set_list_to_dict("start_index", \
                                   [self.small_peak_info.peak_indexes[line[0]] for line in lines_tmp])
        self.lines_info.set_list_to_dict("start_price", \
                                   [self.small_peak_info.peak_prices[line[0]] for line in lines_tmp])
        self.lines_info.set_list_to_dict("end_index", \
                                   [self.small_peak_info.peak_indexes[line[1]] for line in lines_tmp])
        self.lines_info.set_list_to_dict("end_price", \
                                   [self.small_peak_info.peak_prices[line[1]] for line in lines_tmp])

        if not self.lines_info.check_length():
            msg = "line のdata_dict内のリストの長さが同じでないのでエラーです"
            logger.error(msg)
            raise(Exception(msg))

        self.lines_info.make_data_frame()

        self.lines_info.compute_length_index_to_index()
        self.lines_info.compute_line_rate()
        self.lines_info.set_peak_lists_in_line()
        self.lines_info.set_candle_indexes_in_line_without_peak()
        self.lines_info.set_high_values_list(stock_data_df)
        self.lines_info.set_high_values_list_in_line()
        self.lines_info.set_high_values_list_in_peak()
        self.lines_info.set_line_values_list(stock_data_df)
        self.lines_info.set_line_values_list_in_peak()

        self.lines_info.check_diff_between_high_value_and_line()
        return
        self.lines_info.check_diff_between_high_value_and_line_in_peak()
        self.lines_info.count_peaks_used_in_line()
        self.lines_info.check_sumary_diff_between_high_value_and_line()
        self.lines_info.check_trend_line_rule()

        logger.debug(self.lines_info.data_df)

    def select_code(self, code, stock_data_df):
        self.reset_info_each_brand()

        self.detect_small_peak(stock_data_df)
        # self.small_peak_info.print()

        self.detect_large_peak()

        self.detect_trend_line(stock_data_df)
        sys.exit()

        self.result_codes.appends(code)




def main():
    back_test_return_date = args.back_test_return_date
    trend_line = TrendLine(debug=False, back_test_return_date=back_test_return_date,
                           method_name="trend_line", multiprocess=False)

    trend_line.execute()

if __name__ == "__main__":
    main()
