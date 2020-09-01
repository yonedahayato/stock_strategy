from xgboost import XGBRegressor

from base_predicter import BasePredicter

class MyXGBRegressor(BasePredicter):
    """

    XGBRegressor の予測機

    """
    def __init__(self, datasets):
        """__init__ func

        特徴量の名称リストを作成
        モデルの設置(パラメータ)

        Args:
            dataset (Datasets): 使用するデータセット

        """
        super().__init__(datasets)

        self.feature_names = [f for f in datasets.training_data.columns if "feature" in f]
        self.model = XGBRegressor(max_depth=5, learning_rate=0.01, n_estimators=2000, colsample_bytree=0.1)

    def train(self, datasets):
        """train func

        training

        Args:
            dataset (Datasets): 使用するデータセット

        """
        self.model.fit(datasets.training_data[self.feature_names], \
                       datasets.training_data["target_kazutsugi"])

    def predict(self, datasets, save=False):
        """predict func

        predict

        Args:
            dataset (Datasets): 使用するデータセット
            save (bool, option): 予測結果を保存するかどうか

        Returns:
            DataFrame: 予測結果

        """
        self.predictions = model.predict(test_data[feature_names])
        if save:
            self.save()

        return self.predictions


def example():
    from datasets import Datasets
    datasets = Datasets()
    datasets.download()

    training_data = datasets.load()
    test_data = datasets.load(test=True)

    my_xgb_regressor = MyXGBRegressor(datasets)
    my_xgb_regressor.train(training_data)
    predictions = my_xgb_regressor.predict(test_data, save=True)

if __name__ == "__main__":
    example()
