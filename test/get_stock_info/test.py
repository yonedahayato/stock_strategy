import os
import pandas as pd
import sys

abspath = os.path.dirname(os.path.abspath(__file__))
p_path = os.path.dirname(abspath)
sys.path.append(p_path)

from test_libs import (
    # 銘柄情報の取得
    GetCodeList,
    GetCodeListNikkei225,

    # データの取得
    GetStockData,
)

class TestGetCodeList(object):
    """TestGetCodeList class

    GetCodeList のテスト

    """
    def test_GetCodeList(self):
        """test_GetCodeList func

        GetCodeList と GetCodeListNikkei225 のテスト

        """
        get_colde_list = GetCodeList(verbose=True)
        data_df = get_colde_list.get_new_stock_code()
        print("東証１部リスト")
        print(data_df)

        gcl_nikkei_225 = GetCodeListNikkei225(verbose=True)
        data_df = gcl_nikkei_225.get_new_stock_code()
        print("日経２２５リスト")
        print(data_df)

class TestGetRowData(object):
    """TestGetRowData class

    データの取得のテスト

    """
    CODE = "4151"
    def test_get_stock_data(self):
        """test_get_stock_data func

        GetStockData のテスト

        """
        gsd = GetStockData(verbose=True)
        data_df = gsd.get_stock_data_investpy(self.CODE, \
                  "D", start=pd.Timestamp("20170101"), end=pd.Timestamp("20180731"))
        print(data_df)
