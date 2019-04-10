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


def get_data_from_oanda():
    start = datetime.datetime(year=2018,month=5,day=1)
    start = start.strftime("%Y-%m-%dT%H:%M:00.000000Z")
    api = API(environment="practice",
              access_token="0b92552de1941a6f0bd5b237474035a9-6a85bd3a1ab348b29cda485348a1937f")

    request = oandapy.InstrumentsCandles(instrument = "USD_JPY",
                   params = { "alignmentTimezone": "Japan", "from": start, "count": 150, "granularity": "D" })

    api.request(request)
    logger.debug("candles: {}".format(request.response['candles']))

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
