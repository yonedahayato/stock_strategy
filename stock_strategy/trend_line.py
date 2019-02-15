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

class PeakInfo():
    def __init__(self):
        self.peak_indexes = []
        self.peak_dates = []
        self.peak_prices = []

    def append_info(self, index, date, price):
        self.peak_indexes.append(index)
        self.peak_dates.append(date)
        self.peak_prices.append(price)

    def print(self):
        logger.debug("indexes: {}".format(self.peak_indexes))
        logger.debug("dates: {}".format(self.peak_dates))
        logger.debug("prices: {}".format(self.peak_prices))


class TrendLine(StockStrategy):
    def __init__(self, debug=True, back_test_return_date=5, \
                method_name="trend_line", multiprocess=False):

        StockStrategy.__init__(self, debug=debug, back_test_return_date=back_test_return_date, \
                                method_name=method_name, multiprocess=multiprocess)

    def reset_info_each_brand(self):
        # detect small peak
        self.rear_candle, self.middle_candle, self.fore_candle = [pd.Series([])] * 3
        self.small_peak_info = PeakInfo()

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

    def check_peak(self, fore_candle_index, for_buy=True):
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

    def detect_small_peak(self, data_df):
        self.data_df_tmp = copy.deepcopy(data_df)

        for index, (date, candle) in enumerate(self.data_df_tmp.iterrows()):
            self.set_candle(candle)

            if self.fore_candle.empty:
                continue

            self.check_peak(index)

        del self.data_df_tmp

    def detect_large_peak(self):
        pass

    def detect_trend_line(self):
        pass

    def select_code(self, code, stock_data_df):
        self.reset_info_each_brand()

        self.detect_small_peak(stock_data_df)
        self.small_peak_info.print()

        sys.exit()

        self.detect_large_peak()

        self.detect_trend_line()

        self.result_codes.appends(code)




def main():
    back_test_return_date = args.back_test_return_date
    trend_line = TrendLine(debug=False, back_test_return_date=back_test_return_date,
                           method_name="trend_line", multiprocess=False)

    trend_line.execute()

if __name__ == "__main__":
    main()
