from datetime import datetime

class BasePredicter(object):
    """BasePredicter class

    予測機の共通の処理

    """
    def __init__(self, datasets):
        """__init__ func

        データの設置

        Args:
            datasets (Datasets): 使用するデータセット

        """
        self.predictions = None
        self.timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    def train(self):
        pass

    def predict(self):
        pass

    def save(self):
        """save func

        結果を保存する

        """
        file_name = "./predictions/{}_predictions.csv".format(self.timestamp)
        self.predictions.to_csv(file_name)

    def calculate_rank_correlation(self, datasets):
        """calculate_rank_correlation func

        Rank Correlation の計算

        """
        pass
