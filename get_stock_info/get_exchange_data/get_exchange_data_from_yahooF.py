from bs4 import BeautifulSoup
import copy
import datetime
import dateutil.parser
import requests
from os import path
import pandas as pd
import sys

abs_dirname = path.dirname(path.abspath(__file__))
home_dirname = path.dirname(path.dirname(abs_dirname))
helper_dirname = path.join(home_dirname, "helper")
sys.path.append(helper_dirname)

from log import logger

from setting import (
    HISTRICAL_DATA_RANGE_START,
    HISTRICAL_DATA_RANGE_END,
    HISTRICAL_DATA_RANGE_END_NOW,

    HISTRICAL_EXCHANGE_DATA_PATH,
)
class Url:
    def __init__(self, symbol):
        logger.info("symbol: {}".format(symbol))
        if symbol in ["000001.SS"]:
            self.url = "https://finance.yahoo.com/quote/{symbol}/history".format(symbol=symbol)
        else:
            self.url = "https://finance.yahoo.com/quote/%5E{symbol}/history".format(symbol=symbol)
        self.url = self.url + "?period1={}&period2={}&interval=1d&filter=history&frequency=1d"

    def make(self, start_unix, end_unix):
        url = self.url.format(start_unix, end_unix)
        logger.info("url: {}".format(url))
        return url


def transform_to_unix_from_timestamp(timestamp):
    date = timestamp.date()
    return date.strftime("%s")


def request(url):
    response = requests.get(url)
    content = response.content

    return content


def convert_html_to_dataframe(content):
    data_list = []
    soup = BeautifulSoup(content,"html.parser")

    tables = soup.findAll("table", {"data-test": "historical-prices"})
    logger.info("tablse length: {}".format(len(tables)))

    table = tables[0]
    rows = table.findAll('tr')

    for count_row, row in enumerate(rows):
        row_text = row.get_text()
        if row_text == "*Close price adjusted for splits.**Adjusted close price adjusted for both dividends and splits.":
            continue

        items_list = []
        if len(row.findAll("th")) != 0:
            items = row.findAll("th")
            items = [item.get_text().replace("*", "").replace("*", "").replace(" ", "_") for item in items]
            header = copy.deepcopy(items)
            continue

        items = row.findAll("td")
        items = [item.get_text().replace(",", "") for item in items]
        data_list.append(items)

    hist_data_df = pd.DataFrame(data_list, columns=header)
    return hist_data_df


def convert_data_to_unix_from_string(date_str="Oct 12 2018"):
    date = dateutil.parser.parse(date_str)
    return date.strftime("%s")


def get_exchange_data_from_yahoo(symbol, start, end):
    start_unix = transform_to_unix_from_timestamp(start)
    end_unix = transform_to_unix_from_timestamp(end)
    logger.debug("start_unix: {}".format(start_unix))
    logger.debug("end_unix: {}".format(end_unix))

    url = Url(symbol)

    hist_data_sum = []
    retry = True
    while retry:
        content = request(url.make(start_unix, end_unix))

        hist_data_df = convert_html_to_dataframe(content)
        if len(hist_data_df) == 0:
            logger.info("hits data is empty")
            break
        else:
            hist_data_sum.append(hist_data_df)

        last_date = hist_data_df["Date"].iat[-1]
        last_date_unix = convert_data_to_unix_from_string(last_date)

        if str(end_unix) != str(last_date_unix):
            next_date = dateutil.parser.parse(last_date) - datetime.timedelta(days=1)
            next_date_unix = next_date.strftime("%s")
            end_unix = next_date_unix
            logger.info("retry")
        else:
            logger.info("finish to retry")
            break

    hist_data = pd.concat(hist_data_sum, axis=0)
    hist_data = hist_data.reset_index(drop=True)

    # convert date format
    replace_function = lambda x: dateutil.parser.parse(x).strftime("%Y-%m-%d")
    hist_data["Date"] = hist_data["Date"].map(replace_function)

    # reverse sort
    hist_data = hist_data.iloc[::-1]

    # replace no data
    for column_name, item in hist_data.iteritems():
        hist_data[column_name] = hist_data[column_name].replace("-", method="bfill")

    hist_data = hist_data.set_index("Date")

    return hist_data


if __name__ == "__main__":
    symbol = "GDAXI"
    start = HISTRICAL_DATA_RANGE_START
    end = HISTRICAL_DATA_RANGE_END
    get_exchange_data_from_yahoo(symbol, start, end)
