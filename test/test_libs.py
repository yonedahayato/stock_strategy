import os
import sys

abspath = os.path.dirname(os.path.abspath(__file__))
p_path = os.path.dirname(abspath)
sys.path.append(p_path + "/check_reward")
sys.path.append(p_path + "/helper")

from result import Result

from log import (
    logger,
    logzero,
)

# log file
TEST_LOG_FILE = "./test.log"
logzero.logfile(TEST_LOG_FILE)
