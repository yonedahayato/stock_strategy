from html.parser import HTMLParser
from lxml import html
import numpy as np
import os.path as path
import pandas as pd
import re
import sys
import urllib
import urllib.request as request
import urllib.request

abs_dirname = path.dirname(path.abspath(__file__))
parent_dirname = path.dirname(abs_dirname)
helper_dirname = path.join(parent_dirname, "helper")
sys.path.append(helper_dirname)

from setting import TOSHO_1ST_LIST_URL, NIKKEI_225_LIST_URL

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

class GetCodeList:
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.url = TOSHO_1ST_LIST_URL

    def get_response(self):
        with urllib.request.urlopen(self.url) as response:
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
            print("[Get_Code_List:get_data_from_url]: len(data_1st_df): {}".format(len(data_1st_df)))
        return data_1st_df

    def get_new_stock_code(self):
        link = self.get_data_url("a", "href", self.get_response())
        if self.verbose:
            print("[Get_Code_List:get_new_stock_code]: data url link: {}".format(link))

        data_df = self.get_data_from_url(link)
        return data_df

class GetCodeListNikkei225(GetCodeList):
    def __init__(self, verbose=False, nikkei_225=False):
        self.verbose = verbose
        self.url = NIKKEI_225_LIST_URL

    def get_new_stock_code(self):
        response = self.get_response()
        code_list = self.parse_html(response)
        code_list_df = pd.DataFrame.from_dict({"コード": code_list})

        return code_list_df

    def parse_html(self, response):
        response = response.decode("utf-8")

        pattern = r'<div class="col-xs-3 col-sm-1_5">([0-9]+)<\/div>'

        repattern = re.compile(pattern)
        search_obj = repattern.findall(response)

        return search_obj

if __name__ == "__main__":
    get_colde_list = GetCodeList(verbose=True)
    data_df = get_colde_list.get_new_stock_code()
    print("東証１部リスト")
    print(data_df)

    gcl_nikkei_225 = GetCodeListNikkei225(verbose=True)
    data_df = gcl_nikkei_225.get_new_stock_code()
    print("日経２２５リスト")
    print(data_df)
