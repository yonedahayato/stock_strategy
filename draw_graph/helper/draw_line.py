import numpy as np
import os
import sys

abspath_draw_line = os.path.dirname(os.path.abspath(__file__))
abspath_draw_graph = os.path.dirname(abspath_draw_line)
p_path = os.path.dirname(abspath_draw_graph)

sys.path.append(p_path + "/helper")

from log import logger

def draw_line(plt, fig, ax, lines):
    for cnt, line in enumerate(lines):
        indexes = np.array([int(line["start_index"]), int(line["end_index"])])
        prices = np.array([float(line["start_price"]), float(line["end_price"])])

        ax.plot(indexes, prices,
                linewidth=2, color="red", label="trend_lien_{}".format(cnt))

    return plt, fig, ax,


def draw_vertical_line(plt, fig, ax, vertical_lines):
    for vertical_id in vertical_lines:
        ax.axvline(x=vertical_id, linewidth=2, color="green", linestyle="dashed")

    return plt, fig, ax
