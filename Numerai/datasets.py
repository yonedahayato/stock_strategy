from glob import glob
import numerapi
import os
import pandas as pd
from mylogger import mylogger

def print_log(message):
    """print_log func

    メッセージを表示させる
    ログに残す

    Args:
        message (str): メッセージ
    """
    mylogger.info(message)

class Features(object):
    """ Features class

    データの特徴量を整理する
    また、表示する
    """
    def __init__(self, cols):
        """__init__ func

        パラメータの設置
        特徴量のカウント

        Args:
            cols (list[str]): 特徴量のリスト
        """
        self.cols = cols
        self.counts = {
                      "wisdom": 0,
                      "intelligence": 0,
                      "charisma": 0,
                      "strength": 0,
                      "dexterity": 0,
                      "constitution": 0,
                  }

        self.count()

    def count(self):
        """count func

        各項目の特徴量のカウントを行う

        """
        for col in self.cols:
            if "feature" not in col:
                print_log(col)
            else:
                if "wisdom" in col:
                    if self.counts["wisdom"] == 0:
                        print_log(col)
                    self.counts["wisdom"] += 1
                elif "intelligence" in col:
                    if self.counts["intelligence"] == 0:
                        print_log(col)
                    self.counts["intelligence"] += 1
                elif "charisma" in col:
                    if self.counts["charisma"] == 0:
                        print_log(col)
                    self.counts["charisma"] += 1
                elif "strength" in col:
                    if self.counts["strength"] == 0:
                        print_log(col)
                    self.counts["strength"] +=1
                elif "dexterity" in col:
                    if self.counts["dexterity"] == 0:
                        print_log(col)
                    self.counts["dexterity"] += 1
                elif "constitution" in col:
                    if self.counts["constitution"] == 0:
                        print_log(col)
                    self.counts["constitution"] += 1
                else:
                    print_log(col)

        print_log(self.counts)

class PathManager(object):
    """PathManager class

    パス、ディレクトリ、ファイルの名称決定処理

    Attributes:
        test_name_tag (str): テストデータの名称
        training_name_tag (str): トレーニングデータの名称
    """
    test_name_tag = "tournament"
    training_name_tag = "training"

    def __init__(self, main_dir):
        self.main_dir = main_dir

    def make_path(self, test):
        """make_path func

        データセットのパスを作成

        Args:
            test (bool): テストデータかどうか

        Returns:
            str: データセットのパス

        """
        files = os.listdir(path="{}/".format(self.main_dir))
        dataset_names = [f for f in files if os.path.isdir(os.path.join(self.main_dir, f))]
        sorted(dataset_names)
        base_path = os.path.join(self.main_dir, "{}/numerai_{}_data.csv")
        if test:
            data_path = base_path.format(dataset_names[0], self.test_name_tag)
        else:
            data_path = base_path.format(dataset_names[0], self.training_name_tag)

        return data_path

    def make_sample_dir(self):
        """make_sample_dir func

        サンプルデータのディレクトリの作成

        Returns:
            str: サンプルデータのディレクトリ
        """
        self.sample_dir = os.path.join(self.dir_, "samples")
        os.path.makedirs(save_dir, exist_ok=True)

        return self.sample_dir

    def make_sample_path(self, test):
        """make_sample_dir func

        サンプルデータのディレクトリの作成

        Args:
            test (bool): テストデータかどうか

        Returns:
            str: サンプルデータのディレクトリ
            str: サンプルデータのファイルパス
        """
        sample_dir = self.make_sample_dir()
        if test:
            file_name = "sample_{}.csv".format(file_nameself.test_name_tag)
        else:
            file_name = "sample_{}.csv".format(file_nameself.training_name_tag)

        self.sample_path = os.path.join(sample_dir, file_name)
        return sample_dir, self.sample_path

class Datasets(object):
    """Datasets class

    データセットに関する処理をまとめる

    """
    def __init__(self, dir_="./dataset"):
        """__init__ func

        APIの準備
        パラメータの設置
        ディレクトリの作成

        Args:
            dir_ (str): データセットを保存するパス
        """
        self.napi = numerapi.NumerAPI(verbosity="info")
        self.dir_ = dir_
        self.path_manager = PathManager(dir_)

        os.makedirs(dir_, exist_ok=True)

    def print_log(self, message):
        print_log(message)

    def download(self):
        """download func

        numerapi を使ってデータをdownloadする

        """
        self.napi.download_current_dataset(unzip=True, dest_path=self.dir_)

    def load(self, test=False):
        """load func

        CSVデータをロードする

        Args:
            test (bool): テストデータかどうか

        Return:
            pandas.core.frame.DataFrame: 読み込んだデータ
        """

        data_path = self.path_manager.make_path(test)
        self.print_log(data_path)

        if test:
            self.test_data = pd.read_csv(data_path)
            return self.test_data
        else:
            self.training_data = pd.read_csv(data_path)
            return self.training_data

    def static(self):
        """static func

        データの統計情報を表示する

        """
        self.print_log("row: {}, colmun: {}".format(self.training_data.shape[0], self.training_data.shape[1]))
        self.print_log(self.training_data.head())

        self.features = Features(self.training_data.columns)

        # 平均の計算
        mean_df = self.training_data.mean()
        mean_df.plot(legend=False, kind='hist', title="各列の平均のヒストグラム")

    def make_sample(self, test=False, sample_num=100):
        """make_sample func

        サンプルデータを作成する

        Args:
            test (bool): テストデータかどうか
            sample_num (int): データの何行目までをサンプルデータとするか

        Return:
            pandas.core.frame.DataFrame: 作成したサンプルデータ
        """
        try:
            if test:
                sample_data = self.training_data[:sample_num]
            else:
                sample_data = self.test_data[:sample_num]
        except NameError:
            self.print_log("データがないので、load します。")
        else:
            self.print_log("サンプルデータ作成成功")

        save_dir, save_path = self.path_manager.make_sample_path(test=test)
        sample_data.to_csv(save_path)

        return sample_data

def main():
    datasets = Datasets()
    data_df = datasets.load()
    print(data_df.shape)


if __name__ == "__main__":
    main()
