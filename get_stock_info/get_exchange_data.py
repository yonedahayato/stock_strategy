import datetime
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
    'SP500': 'SP500'

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

    data = web.DataReader(currency.values(), sources, start, end)
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
    get_exchange_data()
