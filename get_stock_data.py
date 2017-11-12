import quandl
import datetime
import pandas as pd
import re
import sys
import csv

class Stock :
  def __init__(self, code):
    self.code_ = code

  def Get(self, start_date, end_date, api_key):
    year, month, day = start_date.split("-")
    start = datetime.date(int(year), int(month), int(day))
    year, month, day = end_date.split("-")
    end = datetime.date(int(year), int(month), int(day))

    quandl.ApiConfig.api_key = api_key
    data = quandl.get(self.code_, start_date = start, end_date = end)
    print(data.head())
    date, values = self.Shape(data)
    return (date, values)

  def Shape(self, data):
    return

class TseStock(Stock) :
  def __init__(self, code):
    self.code_ = code

  def Shape(self, data):
    date = data.index.strftime('%Y-%m-%d')
    values = data['Close']

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
      filename_code = re.sub(r'[\\|/|:|?|.|"|<|>|\|]', '-', str(code))
      f = open("code_" + filename_code + "_" + start_date + "_" + end_date + ".csv", 'w')
      writer = csv.writer(f, lineterminator='\n')
      for d, c in zip(date[::-1], values[::-1]):
        csv_row = [d,c]
        writer.writerow(csv_row)
      f.close()

if __name__ == "__main__":
    main()
