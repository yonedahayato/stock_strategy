import copy
import datetime
import oandapy
from oandapyV20 import API
import oandapyV20.endpoints.instruments as oandapy
import os
from os import path
import pandas as pd
import pandas_datareader.data as web
import sys

abs_dirname = path.dirname(path.abspath(__file__))
parent_dirname = path.dirname(abs_dirname)
helper_dirname = path.join(parent_dirname, "helper")
sys.path.append(helper_dirname)

from log import logger

from setting import (
    HISTRICAL_DATA_RANGE_START,
    HISTRICAL_DATA_RANGE_END,
    HISTRICAL_DATA_RANGE_END_NOW,

    HISTRICAL_EXCHANGE_DATA_PATH,
    OANDA_API_KEY,
)

CURRENCY_FRED = {
	'ドル/円': 'DEXJPUS',
	'ユーロ/ドル': 'DEXUSEU',
	'ポンド/ドル': 'DEXUSUK',
    'ダウ平均': 'DJIA',
    # 'DAX指数',
    # ハンセン指数,
    'SP500': 'SP500',
    # 'NASDAQ',
    # 'SHA',
    }

SOURCES = {
    "fred": CURRENCY_FRED,
}

def make_save_data_dir():
    save_dir = path.dirname(HISTRICAL_EXCHANGE_DATA_PATH)
    os.makedirs(save_dir, exist_ok=True)


def get_data(sources, currency, start, end):
    logger.debug("source: {}".format(sources))
    logger.debug("currency: {}".format(currency))

    for source in sources.keys():
        if source in ["fred"]:
            data = web.DataReader(list(currency.values()), source, start, end)
            data.columns = list(currency.keys())
        elif sources:
            get_data_from_oanda()

    return data


def get_data_from_oanda(instrument="USD_JPY"):
    start = datetime.datetime(year=HISTRICAL_DATA_RANGE_START.year,
                              month=HISTRICAL_DATA_RANGE_START.month,
                              day=HISTRICAL_DATA_RANGE_START.day)
    start = start.strftime("%Y-%m-%dT%H:%M:00.000000Z")
    end = datetime.datetime(year=HISTRICAL_DATA_RANGE_END_NOW.year,
                            month=HISTRICAL_DATA_RANGE_END_NOW.month,
                            day=HISTRICAL_DATA_RANGE_END_NOW.day)
    end = end.strftime("%Y-%m-%d")

    api = API(environment="practice",
              access_token=OANDA_API_KEY)

    request = oandapy.InstrumentsCandles(instrument = instrument,
                   params = { "alignmentTimezone": "Japan", "from": start,
                              "count": 5000, "granularity": "D" })

    api.request(request)
    candles = request.response['candles']
    candle = candles[0]

    def change_keys_name(original_dict, key_name_dict):
        new_dict = copy.deepcopy(original_dict)
        for old_key_name, new_key_name in key_name_dict.items():
            new_dict[new_key_name] = new_dict.pop(old_key_name)

        return new_dict

    key_name_dict = {"c": "Close", "o": "Open", "h": "High", "l": "Low"}
    histrical_data = pd.DataFrame.from_dict([change_keys_name(row["mid"], key_name_dict) for row in candles])
    histrical_data["DATE"] = [row["time"].split("T")[0] for row in candles]
    histrical_data = histrical_data.set_index("DATE")
    histrical_data = histrical_data.query("DATE<='{}'".format(end))

    logger.debug("histrical_data length: {}".format(len(histrical_data)))
    logger.debug("histrical_data head: {}".format(histrical_data.head()))
    logger.debug("histrical_data tail: {}".format(histrical_data.tail()))

    return histrical_data

def get_exchange_data(start=None, end=None, sources=None):
    if start == None:
        start = HISTRICAL_DATA_RANGE_START
    if end == None:
        end = HISTRICAL_DATA_RANGE_END_NOW
    if sources == None:
        sources = SOURCES

    data_list = []
    for source, currency in sources.items():
        data_list.append(get_data(source, currency, start, end))

    data = pd.concat(data_list, axis=0)

    make_save_data_dir()
    for source, currency in sources.items():
        for key, name in currency.items():
            data_for_save = data.loc[:, [key]]
            data_for_save.columns = ["Close"]
            data_for_save = data_for_save.fillna(method='bfill')
            data_for_save.to_csv(HISTRICAL_EXCHANGE_DATA_PATH.format(name=name))

if __name__ == '__main__':
    # get_exchange_data()
    get_data_from_oanda()
