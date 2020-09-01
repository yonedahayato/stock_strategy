import os
import pytest
import sys

abspath = os.path.dirname(os.path.abspath(__file__))
p_path = os.path.dirname(abspath)
sys.path.append(p_path)

from test_libs import (
    Result,
    logger,
)

def check_exist_file_in_GCS():
    pass

class TestResult(object):

    def test_shuld_make_result_to_local(self):
        result = Result(to_GCS=False)
        logger.info(result.print_format())

        result.add_info("result_code_list", [1332, 2990])
        result.add_info("method", "test")
        result.add_info("data_range_start_to_compute", "2018_01_01")
        result.add_info("data_range_end_to_compute", "2018_09_09")

        logger.info(result.print_format())
        logger.info(result.save())

        if os.path.exists(result.json_path):
            assert True
        else:
            raise Exception("result file が保存されていません。")

    def test_shuld_not_make_result(self):
        with pytest.raises(BaseException):
            result = Result()
            result.print_format()

            result.add_info("invalid_key", "example_value")

    def test_shuld_save_GCS(self):
        result = Result(to_GCS=True)

        result.add_info("back_test_return_date", 0)
        result.add_info("result_code_list", [1332, 2990])
        result.add_info("method", "test_shuld_save_GCP")
        result.add_info("data_range_start_to_compute", "2018_01_01")
        result.add_info("data_range_end_to_compute", "2018_09_09")

        result.save()
