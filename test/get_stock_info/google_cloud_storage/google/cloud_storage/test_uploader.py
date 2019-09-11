from datetime import datetime
import os
import pytest
import sys

abspath = os.path.dirname(os.path.abspath(__file__))
p_path = os.path.dirname(abspath)
pp_path = os.path.dirname(p_path)
ppp_path = os.path.dirname(pp_path)
pppp_path = os.path.dirname(ppp_path)
sys.path.append(pppp_path)

from test_libs import (
    Uploader,
    logger,
    setting,
)

class TestUploader(object):
    def test_shuld_upload(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=setting.API_KEY_JSON_PATH

        uploader = Uploader(bucket_name="yoneda-tmp")
        now = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        uploader.upload(local_path="/Users/yonedahayato/github/stock_strategy/test/test.txt",
                        gcp_path="test_shuld_upload_{}.txt".format(now))
