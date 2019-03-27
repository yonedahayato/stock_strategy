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

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress

from helper.peak import PeakInfo
from helper.line import LineInfo

class TrendLineUsingLinearRegression(StockStrategy):
    def __init__(self, debug=True, back_test_return_date=5, \
                method_name="trend_line_using_linear_regression", multiprocess=False,
                length_limited_between_end_and_latest=30):

        StockStrategy.__init__(self, debug=debug, back_test_return_date=back_test_return_date, \
                                method_name=method_name, multiprocess=multiprocess)

        # end peak と最後のローソクの距離をある数以下に制限する
        self.length_limited_between_end_and_latest = \
            length_limited_between_end_and_latest

        # 直近のローソクから何本目のローソクを使うかどうか
        self.length_historical_data = 250

        # for drawing to graph
        self.lines_for_draw_graph = []

        self.vertical_lines = []

        self.large_peak_infos = []
        self.flag_draw_large_peak = True
        # ====================

    def compute_trend_line(self, stock_data, high_or_low=None):
        if high_or_low==None:
            logger.error("high or low is None.")
        elif high_or_low not in ["High", "Low"]:
            logger.error("high or low is invalid")

        stock_data_output = stock_data.copy()
        stock_data_input = stock_data.copy()

        while len(stock_data_input) > 3:
            regression = linregress(
                x = stock_data_input["date_index"],
                y = stock_data_input[high_or_low]
            )
            if high_or_low == "High":
                stock_data_input = stock_data_input.loc[stock_data_input[high_or_low] > regression[0] * stock_data_input["date_index"] + regression[1]]
            elif high_or_low == "Low":
                stock_data_input = stock_data_input.loc[stock_data_input[high_or_low] < regression[0] * stock_data_input["date_index"] + regression[1]]

        regression = linregress(
            x = stock_data_input["date_index"],
            y = stock_data_input[high_or_low]
        )

        stock_data_output["{}_trend".format(high_or_low)] = regression[0] * stock_data_output["date_index"] + regression[1]

        return stock_data_output, regression, stock_data_input

    def select_code(self, code, stock_data_df):
        self.vertical_lines.append(len(stock_data_df) - self.length_limited_between_end_and_latest + 1)

        stock_data_df_with_trend = copy.deepcopy(stock_data_df)
        stock_data_df_with_trend["date_index"] = range(1, len(stock_data_df_with_trend)+1)

        stock_data_df_with_trend, regression, regression_point = self.compute_trend_line(stock_data_df_with_trend, "High")

        regression_end_point = regression_point["date_index"].iat[-1]-1
        logger.debug("regression_end_point: {}".format(regression_end_point))
        if regression[0] < 0 and
           (len(stock_data_df) - regression_end_point) < self.length_limited_between_end_and_latest:
           # 回帰直線の傾きが負
           # 回帰直線をもとめるために使った点で時系列的に最後の点が、直近のローソクから
           # ${length_limited_between_end_and_latest}以内にある

            self.lines_for_draw_graph.append([{"start_index": 0,
                                              "end_index": len(stock_data_df_with_trend)-1,
                                              "start_price": stock_data_df_with_trend["High_trend"].iloc[0],
                                              "end_price": stock_data_df_with_trend["High_trend"].iloc[len(stock_data_df_with_trend)-1]
                                              }])

            self.result_codes.append(code)

            self.large_peak_info = PeakInfo()
            for index, candle in regression_point.iterrows():
                self.large_peak_info.append_info(index = candle["date_index"]-1, date = index, price = candle["High"])
            self.large_peak_infos.append(self.large_peak_info)

def main():
    back_test_return_date = args.back_test_return_date
    lengthes_limited_between_end_and_latest = [30]

    for length_limited_between_end_and_latest in lengthes_limited_between_end_and_latest:
        trend_line = TrendLineUsingLinearRegression(debug=False,
                        back_test_return_date=back_test_return_date,
                        method_name="TrendLineUsingLinearRegression_length_limited={}".format(length_limited_between_end_and_latest),
                        multiprocess=False,
                        length_limited_between_end_and_latest = length_limited_between_end_and_latest)
        result = trend_line.execute()

if __name__ == "__main__":
    main()
