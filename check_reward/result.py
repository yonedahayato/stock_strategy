from datetime import datetime as dt
import json
import os
import sys

save_result_path = os.path.dirname(os.path.abspath(__file__))
p_dirnam = os.path.dirname(save_result_path)

sys.path.append(p_dirnam+"/helper")
sys.path.append(p_dirnam+"/get_stock_data/google_cloud_storage/google/cloud_storage")

import log
logger = log.logger
from uploader import Uploader

from setting import (
    RESULT_PATH,
    API_KEY_JSON_PATH,
    )

class Result:
    def __init__(self, save_path=RESULT_PATH, to_GCS=True):
        msg = "[Save_Result:__init__]: {}"
        self.save_path = save_path
        self.to_GCS = to_GCS

        logger.info(msg.format("save_path: {}".format(save_path)))
        self.make_dir(self.save_path)

        self.make_format()

    def make_format(self):
        now_str = dt.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.format = {"result_code_list": [],
                        "method": "",
                        "creat_time": now_str,
                        "data_range_start_to_compute": "",
                        "data_range_end_to_compute": "",
                        "back_test_return_date": "",
                        "elapsed_time_average": 0}

    def make_dir(self, dir_path):
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

    def print_format(self):
        msg = "[Save_Result:print_format]: {}"
        print(msg.format(self.format))
        return msg.format(self.format)

    def add_info(self, key, value):
        msg = "[Save_Result:add_info]: {}"
        if key not in list(self.format.keys()):
            raise Exception(msg.format("{} is invalid key.".format(key)))
        self.format[key] = value

    def save_to_local(self, file_name):
        self.file_path = "{}/{}".format(self.save_path, file_name)
        with open(self.file_path, "w") as file:
            json.dump(self.format, file, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
            json_str = json.dumps(self.format, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
            return json_str

    def save_to_GCS(self, file_name, remove=False):
        json_str = self.save_to_local(file_name)

        basename = os.path.basename(file_name)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = API_KEY_JSON_PATH
        uploader = Uploader(bucket_name="yoneda-stock-strategy")
        uploader.upload(local_path=self.file_path,
                        gcp_path="result/json/{}".format(basename))
        if remove:
            os.remove(self.file_path)

        return json_str

    def save(self):
        msg = "[Save_Result:save]: {}"
        try:
            file_name = "{}_{}.json".format(self.format["method"], self.format["creat_time"])
            if self.to_GCS:
                json_str = self.save_to_GCS(file_name)
            else:
                json_str = self.save_to_local(file_name)
            return json_str

        except Exception as e:
            error_msg = "failt to save to json, format: {}, {}".format(self.format, e)
            logger.exception(msg.format(error_msg))
            raise Exception(e)

        else:
            sccess_msg = "success to save to json, format: {}".format(self.format)
            logger.info(sccess_msg)

def main():
    result = Result()
    result.print_format()

    result.add_info("result_code_list", [1332, 2990])
    result.add_info("method", "test")
    result.add_info("data_range_start", "2018_01_01")
    result.add_info("data_range_end", "2018_09_09")

    result.print_format()
    result.save()

if __name__ == "__main__":
    main()
