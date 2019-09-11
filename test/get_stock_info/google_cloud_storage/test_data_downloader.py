import os
import pytest
import sys

abspath = os.path.dirname(os.path.abspath(__file__))
p_path = os.path.dirname(abspath)
pp_path = os.path.dirname(p_path)
sys.path.append(pp_path)

from test_libs import (
    Data_Downloader,
    logger,
)

class TestDataDownloader(object):
    def test_shuld_download(self):
        pass
