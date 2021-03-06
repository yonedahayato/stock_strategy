from datetime import datetime as dt
import json
import os
import pandas as pd
import sys

save_result_path = os.path.dirname(os.path.abspath(__file__))
p_dirnam = os.path.dirname(save_result_path)

sys.path.append(p_dirnam+"/helper")
sys.path.append(p_dirnam+"/get_stock_info/google_cloud_storage/google/cloud_storage")

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
        now_str = dt.now().strftime("%Y-%m-%d-%H-%M-%S")
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
        # jsonをcsvに変換
        result_df = self.change_format_to_dataframe()

        # csv fileをlocalに保存
        csv_path = "{}/{}".format(self.save_path, file_name)
        csv_path = csv_path.replace(".json", ".csv")
        result_df.to_csv(csv_path, index=False)

        # json fileをlocalに保存
        json_path = "{}/{}".format(self.save_path, file_name)
        with open(json_path, "w") as file:
            json.dump(self.format, file, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))
            json_str = json.dumps(self.format, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ': '))

        self.json_path = json_path
        return json_str, json_path, csv_path

    def save_to_GCS(self, file_name, remove=False):
        # localにjson file と csv file を保存
        json_str, json_path, csv_path = self.save_to_local(file_name)

        # GCS upload準備
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = API_KEY_JSON_PATH
        uploader = Uploader(bucket_name="yoneda-stock-strategy")

        # json file をGCSに追加
        basename = os.path.basename(json_path)
        uploader.upload(local_path=json_path,
                        gcp_path="result/json/{}".format(basename))

        # csv file を GCSに追加
        basename = os.path.basename(csv_path)
        uploader.upload(local_path=csv_path,
                        gcp_path="result/csv/{}".format(basename), public=False)

        if remove:
            os.remove(json_path)
            os.remove(csv_path)

        return json_str

    def save(self):
        msg = "[Save_Result:save]: {}"
        try:
            file_name = "{}_{}.json".format(self.format["method"], self.format["creat_time"])
            if self.to_GCS:
                json_str = self.save_to_GCS(file_name)
            else:
                json_str, _, _ = self.save_to_local(file_name)
            return json_str

        except Exception as e:
            error_msg = "failt to save to json, format: {}, {}".format(self.format, e)
            logger.exception(msg.format(error_msg))
            raise Exception(e)

        else:
            sccess_msg = "success to save to json, format: {}".format(self.format)
            logger.info(sccess_msg)

    def change_format_to_dataframe(self):
        result_code_list = self.format["result_code_list"]
        record_length = len(result_code_list)
        result_df = {"result_code": result_code_list}
        for key, value in self.format.items():
            if key == "result_code_list":
                continue
            result_df[key] = [value] * record_length

        image_urls = [
            "https://storage.googleapis.com/yoneda-stock-strategy/result/image/{}_{}.png".format(
                self.format["method"], code)
            for code in result_code_list
        ]
        result_df["image_url"] = image_urls

        result_df = pd.DataFrame(result_df)
        columns = ["back_test_return_date", "creat_time", "data_range_end_to_compute",
                   "data_range_start_to_compute", "elapsed_time_average", "method",
                   "result_code", "image_url"]
        result_df = result_df[columns]
        return result_df

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
