from datetime import datetime as dt
import json
import os
import sys

abspath = os.path.dirname(os.path.abspath(__file__))
p_dirnam = os.path.dirname(abspath)

sys.path.append(p_dirnam+"/helper")
import log

logger = log.logger

result_path = abspath + "/result/selected_code"

class Save_Result:
    def __init__(self, save_path=result_path):
        msg = "[Save_Result:__init__]: {}"
        self.save_path = save_path
        logger.info(msg.format("save_path: {}".format(save_path)))
        self.make_dir(self.save_path)

        self.make_format()

    def make_format(self):
        now_str = dt.now().strftime("%Y_%m_%d_%H_%M_%S")
        self.format = {"result_code_list": [],
                        "method": "",
                        "date": now_str,
                        "data_range_start": "",
                        "data_range_end": ""}

    def make_dir(self, dir_path):
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

    def print_format(self):
        msg = "[Save_Result:print_format]: {}"
        print(msg.format(self.format))

    def add_info(self, key, value):
        msg = "[Save_Result:add_info]: {}"
        if key not in list(self.format.keys()):
            raise Exception(msg.format("{} is invalid key.".format(key)))
        self.format[key] = value

    def save(self):
        msg = "[Save_Result:save]: {}"
        try:
            file_name = "{}_{}.json".format(self.format["method"], self.format["date"])
            file_path = "{}/{}".format(self.save_path, file_name)
            with open(file_path, "w") as file:
                json.dump(self.format, file)
        except Exception as e:
            error_msg = "failt to save to json, format: {}, {}".format(self.format, e)
            logger.error(msg.format(error_msg))
            logger.exception(error_msg)
            raise Exception(e)
        else:
            sccess_msg = "success to save to json, format: {}".format(self.format)
            logger.info(sccess_msg)

def main():
    sr = Save_Result()
    sr.print_format()

    sr.add_info("result_code_list", [1332, 2990])
    sr.add_info("method", "test")
    sr.add_info("data_range_start", "2018_01_01")
    sr.add_info("data_range_end", "2018_09_09")

    sr.print_format()
    sr.save()

if __name__ == "__main__":
    main()