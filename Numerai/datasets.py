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
        files = os.listdir(path="{}/".format(self.dir_))
        dataset_names = [f for f in files if os.path.isdir(os.path.join(self.dir_, f))]
        sorted(dataset_names)
        base_path = os.path.join(self.dir_, "{}/numerai_{}_data.csv")
        if test:
            data_path = base_path.format(dataset_names[0], "tournament")
        else:
            data_path = base_path.format(dataset_names[0], "training")

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

def main():
    datasets = Datasets()
    data_df = datasets.load()
    print(data_df.shape)


if __name__ == "__main__":
    main()
