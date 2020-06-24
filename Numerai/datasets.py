import numerapi
import os
import pandas as pd

class Datasets(object):
    def __init__(self, dir_="./datasets"):
        self.napi = numerapi.NumerAPI(verbosity="info")
        self.dir_ = dir_

        os.makedirs(dir_, exist_ok=True)

    def download(self):
        self.napi.download_current_dataset(unzip=True, dest_path=self.dir_)

    def load(self, test=False):
        base_path = os.path.join(self.dir_, "numerai_dataset_217/numerai_{}_data.csv")
        if test:
            data_path = base_path.format("tournament")
        else:
            data_path = base_path.format("training")

        print(data_path)
        self.row_data = pd.read_csv(data_path)

        return self.row_data

def main():
    datasets = Datasets()
    data_df = datasets.load()
    print(data_df.shape)


if __name__ == "__main__":
    main()
