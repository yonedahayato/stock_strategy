import numerapi
import os
import pandas as pd

class Datasets(object):
    def __init__(self, dir_="./dataset"):
        self.napi = numerapi.NumerAPI(verbosity="info")
        self.dir_ = dir_

        os.makedirs(dir_, exist_ok=True)

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

        print(data_path)
        self.row_data = pd.read_csv(data_path)

        return self.row_data

    def static(self):
        print("row: {}, colmun: {}".format(self.row_data.shape[0], self.row_data.shape[1]))

def main():
    datasets = Datasets()
    data_df = datasets.load()
    print(data_df.shape)


if __name__ == "__main__":
    main()
