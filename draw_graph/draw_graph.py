import copy
import matplotlib
import numpy as np
import os
import pandas as pd
import sys

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_finance import candlestick2_ohlc, volume_overlay

abspath_draw_graph = os.path.dirname(os.path.abspath(__file__))
p_path = os.path.dirname(abspath_draw_graph)
sys.path.append(p_path + "/helper")
sys.path.append(p_path + "/stock_strategy")

from log import logger

IMAGE_SAVE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/graphs"


class DrawGraph:
    def __init__(self, data_df, code, method_name, window=None):
        self.data_df = data_df
        self.code = code
        self.method_name = method_name

        self.graph_length = 100
        self.window = window

    def draw(self):
        plt, fig, ax = self.draw_chlcv()

        if self.window != None:
            plt, fig, ax = self.draw_move_average_line(plt, fig, ax)

        ax.legend(fontsize=12)

        save_path = self.save(plt)
        plt.close(fig)
        return save_path


    def draw_chlcv(self):
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

        labels = [(data_df.index[int(x)] if x < data_df.shape[0] else x) for x in ax.get_xticks()]+[data_df.index[-1]]
        ax.set_xticklabels(labels, rotation=30)

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
