from logzero import logger
import os
import pandas as pd
import sys

abspath = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(os.path.dirname(os.path.dirname(abspath)))
sys.path.append(project_path + "/helper")

from setting import (
    HISTRICAL_EXCHANGE_DATA_PATH,
    HISTRICAL_DATA_PATH,
)

def set_dataset(stock_data_df):

    # get option data
    option_data_list = []
    for name in ["DEXJPUS", "SP500", "DJIA", "000001.SS", "DEXUSEU", "DEXUSUK", "DJIA", "GDAXI", "HSI", "IXIC"]:
        option_data = read_exchange_data(name)
        option_data = option_data.loc[:, ["Close"]]
        option_data.columns = ["Close_{}".format(name)]
        option_data_list.append(option_data)

    nikei225_data = read_nikei225_data()
    TOPIX_data = read_TOPIX_data()

    nikei225_data = nikei225_data[["Open", "Close", "High", "Low"]]
    nikei225_data.columns = ["Open_nikei225", "Close_nikei225", "High_nikei225", "Low_nikei225"]

    TOPIX_data = TOPIX_data[["Open", "Close", "High", "Low"]]
    TOPIX_data.columns = ["Open_TOPIX", "Close_TOPIX", "High_TOPIX", "Low_TOPIX"]

    stock_data_df = pd.concat([stock_data_df[["Open", "Close", "High", "Low"]],
                               nikei225_data, TOPIX_data] + option_data_list, axis=1)
    stock_data_df = stock_data_df.dropna(how='any')

    close_values = stock_data_df[["Close"]]
    open_values = stock_data_df[["Open"]]
    high_values = stock_data_df[["High"]]
    low_values = stock_data_df[["Low"]]

    return close_values, open_values, high_values, low_values, stock_data_df


def read_exchange_data(name):
    return pd.read_csv(HISTRICAL_EXCHANGE_DATA_PATH.format(name=name), index_col=0)


def read_nikei225_data():
    return pd.read_csv(HISTRICAL_DATA_PATH.format(code="998407"), index_col=0)


def read_TOPIX_data():
    return pd.read_csv(HISTRICAL_DATA_PATH.format(code="998405"), index_col=0)


if __name__ == "__main__":
    abspath = os.path.dirname(os.path.abspath(__file__))
    project_path = os.path.dirname(os.path.dirname(os.path.dirname(abspath)))
    sys.path.append(project_path + "/get_stock_info")

    from get_stock_data import GetStockData
    gsd = GetStockData(verbose=True)
    data_df = gsd.get_stock_data_jsm(1332, "D", start=pd.Timestamp("20170101"), end=pd.Timestamp("20180731"))

    close_values, open_values, high_values, low_values, stock_data_df = set_dataset(data_df)
    logger.debug(close_values)
