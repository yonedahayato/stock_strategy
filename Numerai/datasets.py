from glob import glob
import numerapi
import os
import pandas as pd
from mylogger import mylogger

def print_log(message):
    mylogger.info(message)

class Features(object):
    def __init__(self, cols):
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
    def __init__(self, dir_="./dataset"):
        self.napi = numerapi.NumerAPI(verbosity="info")
        self.dir_ = dir_

        os.makedirs(dir_, exist_ok=True)

    def print_log(self, message):
        print_log(message)

    def download(self):
        self.napi.download_current_dataset(unzip=True, dest_path=self.dir_)

    def load(self, test=False):
        files = os.listdir(path="{}/".format(self.dir_))
        dataset_names = [f for f in files if os.path.isdir(os.path.join(self.dir_, f))]
        sorted(dataset_names)
        base_path = os.path.join(self.dir_, "{}/numerai_{}_data.csv")
        if test:
            data_path = base_path.format(dataset_names[0], "tournament")
        else:
            data_path = base_path.format(dataset_names[0], "training")

        self.print_log(data_path)
        self.row_data = pd.read_csv(data_path)

        return self.row_data

    def static(self):
        self.print_log("row: {}, colmun: {}".format(self.row_data.shape[0], self.row_data.shape[1]))
        self.print_log(self.row_data.head())

        features = Features(self.row_data.columns)

def main():
    datasets = Datasets()
    data_df = datasets.load()
    print(data_df.shape)


if __name__ == "__main__":
    main()
