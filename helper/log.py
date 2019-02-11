# import logging
import logzero
from logzero import logger
import os
from os import path
import sys

abspath = os.path.dirname(os.path.abspath(__file__))
sys.path.append(abspath)

import setting
log_save_path = setting.log_save_path

# ログの出力名を設定
# logger = logging.getLogger("stock_patterns")
# ログレベルの設定
logger.setLevel(10)

# ログのファイル出力先を設定
if not os.path.exists(log_save_path):
    os.mkdir(log_save_path)

log_file = log_save_path + "/stock_strategy.log"
if not os.path.exists(log_file):
    f = open(log_file, "a")
    f.close()

logzero.logfile(log_file)

# fh = logging.FileHandler(log_file)
# logger.addHandler(fh)

# ログのコンソール出力の設定
# sh = logging.StreamHandler()
# logger.addHandler(sh)

# ログの出力形式の設定
# formatter = logging.Formatter("%(asctime)s:%(lineno)d:%(levelname)s:%(message)s")
# fh.setFormatter(formatter)
# sh.setFormatter(formatter)
