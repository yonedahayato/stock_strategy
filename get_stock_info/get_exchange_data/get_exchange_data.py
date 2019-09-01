import os
from os import path
import pandas as pd
import pandas_datareader.data as web
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
    OANDA_API_KEY,
)

from get_exchange_data_from_oanda import get_exchange_data_from_oanda
from get_exchange_data_from_yahooF import get_exchange_data_from_yahoo


CURRENCY_FRED = {
	'ドル/円': 'DEXJPUS',
	'ユーロ/ドル': 'DEXUSEU',
	'ポンド/ドル': 'DEXUSUK',
    'ダウ平均': 'DJIA',
    'SP500': 'SP500',

    # 'NASDAQ',
    # 'SHA',
    }

CURRENCY_YAHOO = {
    "DAX指数": "GDAXI",
    "ハンセン指数": "HSI",
    "NASDAQ": "IXIC",
    "上海総合指数": "000001.SS",
}

SOURCES = {
    "fred": CURRENCY_FRED,
    "yahoo": CURRENCY_YAHOO,
}


def make_save_data_dir():
    save_dir = path.dirname(HISTRICAL_EXCHANGE_DATA_PATH)
    os.makedirs(save_dir, exist_ok=True)


def save_datas(currency, data):
    make_save_data_dir()

    for key, name in currency.items():
        data_for_save = data.loc[:, [key]]
        data_for_save.columns = ["Close"]
        save_data(name, data_for_save)

        logger.debug("key: {}, data:{}".format(key, data_for_save))


def save_data(name, data):
    data = data.fillna(method='bfill')
    data.to_csv(HISTRICAL_EXCHANGE_DATA_PATH.format(name=name))


def get_exchange_data_from_pandas(source, currency, start, end):
    logger.debug("source: {}".format(source))
    logger.debug("currency: {}".format(currency))

    data = web.DataReader(list(currency.values()), source, start, end)
    data.columns = list(currency.keys())

    return data


def get_exchange_data(start=None, end=None, sources=None):
    if start == None:
        start = HISTRICAL_DATA_RANGE_START
    if end == None:
        end = HISTRICAL_DATA_RANGE_END_NOW
    if sources == None:
        sources = SOURCES

    data_list = []
    for source, currency in sources.items():
        if source in ["fred"]:
            data = get_exchange_data_from_pandas(source, currency, start, end)
            save_datas(currency, data)

        elif source in ["yahoo"]:
            for name, symbol in currency.items():
                data = get_exchange_data_from_yahoo(symbol, start, end)
                save_data(symbol, data)

        else:
            logger.info("Source name is '{}'. But this is invalid.".format(source))


if __name__ == '__main__':
    get_exchange_data()
