import os
import sys


abspath = os.path.dirname(os.path.abspath(__file__))
p_path = os.path.dirname(abspath)
sys.path.append(p_path + "/check_reward")
sys.path.append(p_path + "/get_stock_info/google_cloud_storage")
sys.path.append(p_path + "/get_stock_info/google_cloud_storage/google/cloud_storage")
sys.path.append(p_path + "/helper")
sys.path.append(p_path + "/stock_strategy")

from uploader import Uploader
from data_uploader import Data_Uploader
from data_downloader import Data_Downloader
from result import Result
import setting
from stock_strategy import StockStrategy

# log file
from log import (
    logger,
    logzero,
)
TEST_LOG_FILE = "./test.log"
logzero.logfile(TEST_LOG_FILE)
