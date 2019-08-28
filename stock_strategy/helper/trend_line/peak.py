import os
import sys

abspath_peak = os.path.dirname(os.path.abspath(__file__))
abspath_helper = os.path.dirname(abspath_peak)
abspath_draw_graph = os.path.dirname(abspath_helper)
abspath_project = os.path.dirname(abspath_draw_graph)

sys.path.append(abspath_project + "/helper")

import log
logger = log.logger

class PeakInfo():
    def __init__(self):
        self.peak_indexes = []
        self.peak_dates = []
        self.peak_prices = []

    def append_info(self, index, date, price):
        self.peak_indexes.append(index)
        self.peak_dates.append(date)
        self.peak_prices.append(price)

    def print(self):
        logger.debug("indexes: {}".format(self.peak_indexes))
        logger.debug("dates: {}".format(self.peak_dates))
        logger.debug("prices: {}".format(self.peak_prices))

    def get_length(self):
        return len(self.peak_indexes)

    def get_info_from_id_as_dict(self, idx):
        return {"index": self.peak_indexes[idx],
                "date": self.peak_dates[idx],
                "price": self.peak_prices[idx]}
