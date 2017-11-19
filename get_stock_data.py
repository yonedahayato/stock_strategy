import quandl
import datetime
import pandas as pd
import re
import sys
import csv
api_key = "c_MVftyir5vTKxyiuego"

class Stock :
    def __init__(self, code):
        self.code_ = code

    def Get(self, start_date, end_date, api_key, shape_value="Close"):
        year, month, day = start_date.split("-")
        start = datetime.date(int(year), int(month), int(day))
        year, month, day = end_date.split("-")
        end = datetime.date(int(year), int(month), int(day))

        quandl.ApiConfig.api_key = api_key
        data = quandl.get(self.code_, start_date = start, end_date = end)
        print(data.head())

        date, values = self.Shape(data, shape_value)
        return (date, values)

    def Shape(self, data):
        return

class TseStock(Stock) :
    def __init__(self, code):
        self.code_ = code

    def Shape(self, data, shape_value):
        date = data.index.strftime('%Y-%m-%d')
        if shape_value == "All":
            return (date, data)

        values = data[shape_value]

        return (date, values)

def main():
    args = sys.argv
    codelist_file = str(args[1])
    start_date = str(args[2])
    end_date = str(args[3])
    api_key = "c_MVftyir5vTKxyiuego"

    print("get stocks")
    print("codelist file = " + codelist_file)
    print("date  = " + start_date + " to " + end_date)
    print("api_key  = " + api_key)

    code_list = pd.read_csv(codelist_file)
    print(code_list)

    for key, codes in code_list.iteritems():
        for code in codes:
            if str(key) == "TSE":
                print("TSE " + str(code))
                stock = TseStock(code)

            date, values = stock.Get(start_date, end_date, api_key)
            #print(date)
            #print(values)

            filename_code = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '-', str(code))
            f = open("code_" + filename_code + "_" + start_date + "_" + end_date + ".csv", 'w')
            writer = csv.writer(f, lineterminator='\n')

        for d, c in zip(date[::-1], values[::-1]):
            csv_row = [d,c]
            writer.writerow(csv_row)
        f.close()

def get_stock_data(code, start, end):
    code = "TSE/"+str(code)
    print("code: {}".format(code))
    print("start: {}, end: {}".format(start, end))

    stock = TseStock(code)
    shape_value = "All"
    date, values = stock.Get(start, end, api_key, shape_value)
    return values


if __name__ == "__main__":
    #main()
    stock_df = get_stock_data(1332, "2017-11-01", "2017-11-17")
    print(stock_df)
