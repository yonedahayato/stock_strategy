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
    args
)

class TrendLine(StockStrategy):
    def __init__(self, debug=True, back_test_return_date=5, \
                method_name="trend_line", multiprocess=False):

        StockStrategy.__init__(self, debug=debug, back_test_return_date=back_test_return_date, \
                                method_name=method_name, multiprocess=multiprocess)


    def select_code(selfself, code, stock_data_df):
        self.result_codes.appends(code)

def main():
    back_test_return_date = args.back_test_return_date
    trend_line = TrendLine(debug=False, back_test_return_date=back_test_return_date,
                           method_name="trend_line", multiprocess=False)

    trend_line.execute()

if __name__ == "__main__":
    main()
