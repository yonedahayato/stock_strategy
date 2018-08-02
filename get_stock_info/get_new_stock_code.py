from html.parser import HTMLParser
from lxml import html
import numpy as np
import pandas as pd
import sys
import urllib
import urllib.request as request
import urllib.request

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

class Get_Code_List:
    def __init__(self, verbose=False):
        self.verbose = verbose

    def http_get(self):
        url = "http://www.jpx.co.jp/markets/statistics-equities/misc/01.html"
        with urllib.request.urlopen(url) as response:
            return response.read()

    def get_data_url(self, tag, attr, html):
        parser = Parser(tag, attr)
        parser.feed(str(html))
        for attr in parser.attrs:
            if "data_j.xls" in attr:
                return "http://www.jpx.co.jp" + attr

    def get_data_from_url(self, link):
        socket = urllib.request.urlopen(link)
        xls = pd.ExcelFile(socket)
        df_all = xls.parse(xls.sheet_names[0], header=0, index_col=None)
        data_1st_df = df_all.ix[df_all["市場・商品区分"]=="市場第一部（内国株）", :]

        if self.verbose:
            print("[Get_Code_list:get_data_from_url]: len(data_1st_df): {}".format(len(data_1st_df)))
        return data_1st_df

    def get_new_stock_code(self):
        link = self.get_data_url("a", "href", self.http_get())
        if self.verbose:
            print("[Get_Code_list:get_new_stock_code]: data url link: {}".format(link))

        data_df = self.get_data_from_url(link)
        return data_df

if __name__ == "__main__":
    gcl = Get_Code_List(verbose=True)
    data_df = gcl.get_new_stock_code()
    print(data_df)
