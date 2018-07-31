import urllib.request as request
import urllib
from lxml import html
import numpy as np
import pandas as pd
import sys
from html.parser import HTMLParser

def http_get():
    url = "http://www.jpx.co.jp/markets/statistics-equities/misc/01.html"
    import urllib.request
    with urllib.request.urlopen(url) as response:
        return response.read()

class Parser(HTMLParser):
    def __init__(self, tag, attr):
        super(Parser, self).__init__()
        self.tag = tag
        self.attr = attr
        self.attrs = []

    def handle_starttag(self, tag, attrs):
        if tag == self.tag:
            for attr in attrs:
                if attr[0] == self.attr:
                    self.attrs.append(attr[1])

def get_data_url(tag, attr, html):
    parser = Parser(tag, attr)
    parser.feed(str(html))
    for attr in parser.attrs:
        if "data_j.xls" in attr:
            return "http://www.jpx.co.jp" + attr

def get_data_from_url(link):
    socket = urllib.request.urlopen(link)
    xls = pd.ExcelFile(socket)
    df_all = xls.parse(xls.sheet_names[0], header=0, index_col=None)
    data_1st_df = df_all.ix[df_all["市場・商品区分"]=="市場第一部（内国株）", :]
    print("len(data_1st_df): {}".format(len(data_1st_df)))
    return data_1st_df

def get_new_stock_code():
    link = get_data_url("a", "href", http_get())
    print("data url link: {}".format(link))
    data_df = get_data_from_url(link)
    return data_df

if __name__ == "__main__":
    data_df = get_new_stock_code()
    print(data_df)
