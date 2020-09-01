import copy
import gc
import math
import numpy as np
import os
import pandas as pd
from sklearn.metrics import confusion_matrix
import sys

from keras.backend.tensorflow_backend import clear_session
from keras.backend.tensorflow_backend import get_session
from keras.callbacks import EarlyStopping

abspath = os.path.dirname(os.path.abspath(__file__))
project_path = os.path.dirname(os.path.dirname(abspath))
sys.path.append(abspath + "/helper/predict_class_of_change_using_LSTM")

from stock_strategy import (
    args,
    # my library
    StockStrategy,
    logger
)

from setting import (
    HISTRICAL_EXCHANGE_DATA_PATH,
    HISTRICAL_DATA_PATH,
)

from model import create_model
from set_dataset import set_dataset

pd.options.display.max_rows = None
np.set_printoptions(threshold=10000)

class PredictClassOfChangeUsingLSTM(StockStrategy):
    def __init__(self, debug=False, back_test_return_date=5, \
                method_name="predict_class_of_change_using_lstm", multiprocess=False):
        StockStrategy.__init__(self, debug=debug, back_test_return_date=back_test_return_date, \
                                method_name=method_name, multiprocess=multiprocess)

        self.training_days = 40
        self.batch_size = 10
        self.epochs = 50
        self.hidden_neurons = 432
        self.patience = 10
        self.over_fit_test_flag = False

        # === threshold ===
        self.threshold = 0.01
        self.category_threshold = [-10, -self.threshold, 0, self.threshold, 10]
        self.f_value_threshold = 0.65
        self.precision_threshold = 0.60
        # =================

    def select_code(self, code, stock_data_df_original):
        logger.debug("==== {} ====".format(code))

        stock_data_df = copy.deepcopy(stock_data_df_original)
        close_values, open_values, high_values, low_values, stock_data_df = set_dataset(stock_data_df)

        y_data = self.compute_rate_of_decline(close_values)
        y_data = pd.cut(y_data, self.category_threshold, labels=False)

        y_data, stock_data_df = self.compute_log_and_diff(y_data, stock_data_df)

        y_data_df = pd.DataFrame(y_data, columns=["y"])
        logger.debug(y_data_df.groupby("y").size())

        x = np.array(stock_data_df)
        just_target = np.array([x[-self.training_days:]])
        x = x[:-self.training_days]
        y_data = y_data[:-self.training_days]
        X, Y = self.create_train_data(x, y_data, self.training_days)

        # データを学習用と検証用に分割
        split_pos = int(len(X) * 0.8)
        train_x = X[:split_pos]
        train_y = Y[:split_pos]
        test_x = X[split_pos:]
        test_y = Y[split_pos:]

        dimension = len(X[0][0])
        model = create_model(dimension, self.hidden_neurons, self.training_days)

        es = EarlyStopping(patience=self.patience, verbose=1)
        history = model.fit(train_x, train_y, batch_size=self.batch_size,
                            epochs=self.epochs, verbose=1, validation_split=0.2, callbacks=[es])

        self.print_train_history(history)

        preds = model.predict(test_x)
        logger.debug("preds: {}".format(preds))
        self.print_predict_result(preds, test_y)

        just_pred = model.predict(just_target)
        just_pred_index = np.argmax(just_pred[0])
        logger.info("just pred: {}".format(just_pred))
        logger.info("just pred argmax: {}".format(just_pred_index))
        if self.f_value > self.f_value_threshold and\
           self.precision > self.precision_threshold and\
           just_pred_index in [2, 3]:
            self.result_codes.append(code)

        sess = get_session()
        clear_session()
        sess.close()
        del model, stock_data_df, close_values, open_values, high_values, low_values
        gc.collect()

    def create_train_data(self, x_data, y_data, samples):

        _x = []
        _y = []
        length = len(x_data)

        for i in np.arange(0, length - samples):
            s = i + samples # samplesサンプル間の変化を素性にする
            _x.append(x_data[i:s])

            __y = [0, 0, 0, 0]
            __y[int(y_data[s][0])] = 1
            _y.append(__y)

            if self.over_fit_test_flag:
                _x = _x * (length - samples)
                _y = _y * (length - samples)
                return np.array(_x), np.array(_y)

        # 上げ下げの結果と教師データのセットを返す
        return np.array(_x), np.array(_y)

    def print_train_history(self, history):
        logger.info("Epoch, Loss, Val loss, Acc, Val Acc")
        for i in range(len(history.history['loss'])):
            loss = history.history['loss'][i]
            val_loss = history.history['val_loss'][i]
            acc = history.history['categorical_accuracy'][i]
            val_acc = history.history['val_categorical_accuracy'][i]
            logger.info("%d,%f,%f,%f,%f" % (i, loss, val_loss, acc, val_acc))

    def print_predict_result(self, preds, test_y):
        tp = 0
        fp = 0
        tn = 0
        fn = 0
        predicts = []
        trues = []
        for i in range(len(preds)):
            predict = np.argmax(preds[i])
            test    = np.argmax(test_y[i])
            positive = True if predict == 2 or predict == 3 else False
            true     = True if test == 2 or test == 3 else False
            if true and positive:
                tp += 1
            if not true and positive:
                fp += 1
            if true and not positive:
                tn += 1
            if not true and not positive:
                fn += 1

            predicts.append(predict)
            trues.append(test)

        logger.info("TP = %d, FP = %d, TN = %d, FN = %d" % (tp, fp, tn, fn))
        self.precision = tp / (tp + fp + 0.00000001)
        self.recall = tp / (tp + fn + 0.0000001)
        self.f_value = 2 * self.recall * self.precision / (self.recall + self.precision + 0.0000001)
        logger.info("Precision = %f, Recall = %f, F = %f" % (self.precision, self.recall, self.f_value))

        matrix = confusion_matrix(trues, predicts, labels=[0, 1, 2, 3])
        matrix = pd.DataFrame(matrix,
                              columns=["pred_{}".format(i) for i in range(4)],
                              index=["true_{}".format(i) for i in range(4)])
        logger.info("Matrix: \n{}".format(matrix))

    @staticmethod
    def compute_rate_of_decline(data_df):
        rate_of_decline = data_df.pct_change()
        rate_of_decline.iloc[0, :] = 0
        return rate_of_decline

    @staticmethod
    def compute_log_and_diff(y_data, stock_data_df):
        stock_data_df = stock_data_df.applymap(lambda x: math.log10(x))
        stock_data_df = stock_data_df.diff()
        stock_data_df = stock_data_df.dropna(how='any')
        y_data = y_data[1:]
        return y_data, stock_data_df

    def over_fit_test(self):
        self.over_fit_test_flag = True
        self.execute()


if __name__ == '__main__':
    back_test_return_date = args.back_test_return_date
    predict_class_of_change_using_lstm = PredictClassOfChangeUsingLSTM(back_test_return_date=back_test_return_date)
    predict_class_of_change_using_lstm.execute()
