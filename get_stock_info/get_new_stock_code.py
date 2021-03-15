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
    """GetCodeList class

    銘柄リストを取得する

    """
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.url = TOSHO_1ST_LIST_URL

    def get_response(self):
        """get_response func

        url にアクセスし、html 情報を取得する

        Returns:
            str: html 情報

        """
        print("url: ", self.url)
        with urllib.request.urlopen(self.url) as response:
            return response.read()

    def get_data_url(self, tag, attr, html):
        """get_data_url func

        html から銘柄リストが記載された excel file の url を取得する

        Args:
            tag(str): xxx
            attr(str): xxx
            html(xxx): 銘柄リストが記載された excel file の url情報が記載された html

        Returns:
            str: excel file の url

        """
        parser = Parser(tag, attr)
        parser.feed(str(html))
        for attr in parser.attrs:
            if "data_j.xls" in attr:
                return "http://www.jpx.co.jp" + attr

    def get_data_from_url(self, link):
        """get_data_from_url func

        銘柄一覧が記載された excel の url から情報を取得する

        Args:
            link(str): 銘柄一覧が記載された excel の url

        Returns:
            pd.DataFrame: 銘柄一覧の情報

        """
        try:
            socket = urllib.request.urlopen(link)
            xls = pd.ExcelFile(socket)
            df_all = xls.parse(xls.sheet_names[0], header=0, index_col=None)
        except:
            print("use pandas read_excel")
            df_all = pd.read_excel(link, header=0, index_col=None)

        try:
            data_1st_df = df_all.ix[df_all["市場・商品区分"]=="市場第一部（内国株）", :]
        except:
            print("ix の使用を避けました")
            data_1st_df = df_all.loc[df_all["市場・商品区分"]=="市場第一部（内国株）", :]

        if self.verbose:
            print("[Get_Code_List:get_data_from_url]: len(data_1st_df): {}".format(len(data_1st_df)))
        return data_1st_df

    def get_new_stock_code(self):
        """get_new_stock_code func

        銘柄一覧の情報を取得する

        Returns:
            pandas.DataFrame: 銘柄一覧の情報

        Note:
            1. 日本取引所グループ(JPX)のurl (link) からhtml 情報を取得
            2. html をパースして、銘柄一覧 excel の url を取得
            3. 銘柄一覧 excel の url から情報を取得

        """
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
