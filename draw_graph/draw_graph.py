import copy
import matplotlib
import numpy as np
import os
import pandas as pd
import sys

matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_finance import candlestick2_ohlc, volume_overlay

IMAGE_SAVE_PATH = os.path.dirname(os.path.abspath(__file__)) + "/images"


class DrawGraph:
    def __init__(self, data_df, code):
        self.data_df = data_df
        self.code = code

    def draw(self):
        data_df = copy.deepcopy(self.data_df)
        data_df = data_df[["Open", "High", "Low", "Close", "Vloume"]]

        fig = plt.figure(figsize=(18, 9))
        fig.subplots_adjust(left=0.045, bottom=0.075, right=0.95, top=0.95, wspace=0.15, hspace=0.15)
        ax = plt.subplot(1, 1, 1)

        candlestick2_ohlc(ax, data_df["Open"], data_df["High"], data_df["Low"], data_df["Close"], width=0.9, colorup="white", colordown="black")

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

        plt.savefig(IMAGE_SAVE_PATH)
