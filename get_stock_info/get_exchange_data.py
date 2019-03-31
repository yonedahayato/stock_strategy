import datetime
import os
from os import path
import pandas
import pandas_datareader.data as web
import sys

abs_dirname = path.dirname(path.abspath(__file__))
parent_dirname = path.dirname(abs_dirname)
helper_dirname = path.join(parent_dirname, "helper")
sys.path.append(helper_dirname)

from setting import (
    HISTRICAL_DATA_RANGE_START,
    HISTRICAL_DATA_RANGE_END,
    HISTRICAL_DATA_RANGE_END_NOW,

    HISTRICAL_EXCHANGE_DATA_PATH,
)

CURRENCY = {
	'ドル/円': 'DEXJPUS',
	'ユーロ/ドル': 'DEXUSEU',
	'ポンド/ドル': 'DEXUSUK',
    }

def make_save_data_dir():
    save_dir = path.dirname(HISTRICAL_EXCHANGE_DATA_PATH)
    os.makedirs(save_dir, exist_ok=True)

def get_exchange_data(start=None, end=None, currency=None):
    if start == None:
        start = HISTRICAL_DATA_RANGE_START
    if end == None:
        end = HISTRICAL_DATA_RANGE_END_NOW
    if currency == None:
        currency = CURRENCY

    data = web.DataReader(currency.values(), 'fred', start, end)
    data.columns = list(currency.keys())

    make_save_data_dir()

    for key, name in currency.items():
        data_for_save = data.loc[:, [key]]
        data_for_save.columns = ["Close"]
        data_for_save = data_for_save.fillna(method='bfill')
        data_for_save.to_csv(HISTRICAL_EXCHANGE_DATA_PATH.format(name=name))

if __name__ == '__main__':
    get_exchange_data()
