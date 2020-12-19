import copy
from decimal import Decimal, ROUND_HALF_UP
import matplotlib
import numpy as np
import os
import pandas as pd
import sys

matplotlib.use('Agg')
# import matplotlib.pyplot as plt
from mpl_finance import candlestick2_ohlc, volume_overlay

abspath_draw_graph = os.path.dirname(os.path.abspath(__file__))
p_path = os.path.dirname(abspath_draw_graph)
sys.path.append(p_path + "/helper")
sys.path.append(p_path + "/stock_strategy")
sys.path.append(abspath_draw_graph + "/helper")

from log import logger
from draw_line import draw_line, draw_vertical_line
from draw_peak import draw_peak

IMAGE_SAVE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/graphs"


class DrawGraph:
    def __init__(self, data_df, code, method_name, window=None, lines=[],
                 small_peak_info=None, large_peak_info=None, vertical_lines=[]):
        self.data_df = data_df
        self.code = code
        self.method_name = method_name

        # self.graph_length = 100
        self.graph_length = 0
        self.window = window
        self.lines = lines
        self.small_peak_info = small_peak_info
        self.large_peak_info = large_peak_info
        self.vertical_lines = vertical_lines

    def draw(self):
        import matplotlib.pyplot as plt
        plt, fig, ax = self.draw_chlcv(plt)

        if self.window != None:
            plt, fig, ax = self.draw_move_average_line(plt, fig, ax)

        if self.lines != []:
            plt, fig, ax = draw_line(plt, fig, ax, self.lines)

        if self.small_peak_info != None:
            plt, fig, ax = draw_peak(plt, fig, ax, self.small_peak_info, "small")

        if self.large_peak_info != None:
            plt, fig, ax = draw_peak(plt, fig, ax, self.large_peak_info, "large")

        if self.vertical_lines != []:
            plt, fig, ax = draw_vertical_line(plt, fig, ax, self.vertical_lines)


        ax.legend(fontsize=12)
        plt.title("{}_{}".format(self.method_name, self.code))

        save_path = self.save(plt)
        plt.close(fig)
        return save_path

    def draw_chlcv(self, plt):
        """draw_chlcv func

        Open, High, Low, Close, Volume の値を取り出し描画する

        Args:
            plt(module): 描画するためのモジュール

        Returns:
            module:                                 描画した情報
            matplotlib.figure.Figure:               描画した情報
            matplotlib.axes._subplots.AxesSubplot   描画した情報
        """
        data_df = copy.deepcopy(self.data_df)
        data_df = data_df.iloc[-self.graph_length:]
        data_df.columns = ["Open", "High", "Low", "Close", "Adj_Close", "Volume"]
        data_df = data_df[["Open", "High", "Low", "Close", "Volume"]]

        fig = plt.figure(figsize=(18, 9))
        fig.subplots_adjust(left=0.045, bottom=0.075, right=0.95, top=0.95, wspace=0.15, hspace=0.15)
        ax = plt.subplot(1, 1, 1)

        candlestick2_ohlc(ax, data_df["Open"], data_df["High"], data_df["Low"], data_df["Close"],
                          width=0.9, colorup="grey", colordown="black")

        place = ax.get_xticks()
        place[-2] = place[-2] - 1.0
        ax.set_xticks(place)

        labels_length = len(ax.get_xticks())

        def cal_index(x):
            """cal_index func

            新たなindexを計算

            Args:
                x(int): もともとのindex

            Returns:
                float: 新たなindex

            """
            return x / (labels_length-1) * len(data_df)

        def my_round(f):
            """my_round func

            四捨五入関数

            Args:
                f(float): 四捨五入計算後の入力

            Returns:
                int: 四捨五入計算後の出力

            """
            return int(Decimal(str(f)).quantize(Decimal('0'), rounding=ROUND_HALF_UP))

        def get_date_index(i):
            """get_date_index

            index として使用する日付を取得

            Args:
                i(int); index

            Returns:
                str: 日付のindex

            """
            return data_df.index[i]

        new_labels = [data_df.index[0]] + \
                     [get_date_index(my_round(cal_index(x))) for x in range(1, labels_length - 1)] + \
                     [data_df.index[-1]]
        ax.set_xticklabels(new_labels, rotation=30)

        ax.set_xlim([-1, data_df.shape[0]+1])
        ax.set_ylabel("Price")

        # 出来高を描写する範囲を指定
        bottom, top = ax.get_ylim()
        ax.set_ylim(bottom - (top - bottom) / 4, top)

        # 出来高のチャートをプロット
        ax2 = ax.twinx()
        volume_overlay(ax2, data_df["Open"], data_df["Close"], data_df["Volume"], width=1, colorup="g", colordown="g")
        ax2.set_xlim([0, data_df.shape[0]])

        # 出来高チャートは下側25%に収める
        ax2.set_ylim([0, float(data_df["Volume"].max()) * 4])
        ax2.set_ylabel("Volume")

        return plt, fig, ax

    def draw_move_average_line(self, plt, fig, ax):
        from move_average import MoveAverage
        data_df = copy.deepcopy(self.data_df)

        move_average_for_compute = MoveAverage(window=self.window)
        move_average_df = move_average_for_compute.get_move_average(data_df)
        move_average_df = move_average_df.iloc[-self.graph_length:]

        index = data_df.index[-self.graph_length:]

        ax.plot(index, move_average_df["rolling_mean"], label="move_average_{}".format(self.window))
        return plt, fig, ax

    def save(self, plt):
        self.save_path = "{}/{}_{}.png".format(IMAGE_SAVE_PATH, self.method_name, self.code)
        plt.savefig(self.save_path)

        return self.save_path

    def remove(self):
        os.remove(self.save_path)
