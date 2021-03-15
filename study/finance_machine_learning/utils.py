import os
import sys

ABSPATH = os.path.abspath(__file__)
BASEDIR = os.path.dirname(ABSPATH)
PARENTDIR = os.path.dirname(BASEDIR)
PPARENTDIR = os.path.dirname(PARENTDIR)

sys.path.append(PPARENTDIR)

from helper.log import logger

class FilePath(object):
    """FilePath class

    ファイルのパスの設定と操作

    Attributes:
        base_dir(str): base dir
        file_name_dict(dict): ファイル名のリスト

    """
    base_dir = os.path.join(PPARENTDIR, "get_stock_info", "stock_data")
    file_name_dict = {
        "name":             "{code}_file_name.{ext}",               # 詳細
        "histcal_row":      "{code}.{ext}",                         # ヒストリカルデータ
        "labels_bins":      "{code}_labels_bins.{ext}",             # ラベリング済みデータ (section3)
        "labels_events":    "{code}_labels_events.{ext}",           # ラベリング済みデータ (section3)
        "labels_sampled":   "{code}_labels_bins_sampled.{ext}",     # 標本の重み付け済みデータ (section4)
        "frac_diff_data":   "{code}_frac_diff.{ext}",               # 分数次差分の計算済みデータ (section5)
    }

    def set_base_dir(self, base_dir):
        """set_base_dir func

        base_dir の設置

        """
        self.base_dir = base_dir

    def get_path(self, code, file_type, base_dir=None, ext="csv"):
        """get_path func

        file path の取得

        """
        if base_dir is None:
            base_dir = self.base_dir

        if file_type not in self.file_name_dict.keys():
            raise Exception("file type が異常です")

        file_name = self.file_name_dict[file_type].format(code=code, ext=ext)
        file_path = os.path.join(base_dir, file_name)

        return file_path

class ProcessingBase(object):
    """ProcessingBase class

    各処理の共通処理まとめ

    """
    file_path = FilePath()
    logger = logger
