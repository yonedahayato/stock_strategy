import copy
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM
from keras.optimizers import Adam
from keras.callbacks import EarlyStopping
import math
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

from stock_strategy import (
    # library
    sys,

    # my library
    StockStrategy,
    logger
)

from setting import (
    HISTRICAL_EXCHANGE_DATA_PATH,
    HISTRICAL_DATA_PATH,
)

pd.options.display.max_rows = None

class PredictClassOfChangeUsingLSTM(StockStrategy):
    def __init__(self, debug=False, back_test_return_date=5, \
                method_name="predict_class_of_change_using_lstm", multiprocess=False):
        StockStrategy.__init__(self, debug=debug, back_test_return_date=back_test_return_date, \
                                method_name=method_name, multiprocess=multiprocess)

        self.threshold = 0.01
        self.category_threshold = [-100.0, -self.threshold, 0.0, self.threshold, 100.0]
        self.training_days = 5
        self.batch_size = 10
        self.epochs = 2000
        self.hidden_neurons = 432
        self.patience = 10

    def select_code(self, code, stock_data_df_original):
        logger.debug(code)

        stock_data_df = copy.deepcopy(stock_data_df_original)
        close_values, open_values, high_values, low_values, stock_data_df = self.set_dataset(stock_data_df)

        y_data = self.compute_rate_of_decline(close_values)
        y_data = pd.cut(y_data, self.category_threshold, labels=False)
        y_data, stock_data_df = self.compute_log_and_diff(y_data, stock_data_df)
        X, Y = self.create_train_data(np.array(stock_data_df), y_data, self.training_days)

        # データを学習用と検証用に分割
        split_pos = int(len(X) * 0.8)
        train_x = X[:split_pos]
        train_y = Y[:split_pos]
        test_x = X[split_pos:]
        test_y = Y[split_pos:]

        dimension = len(X[0][0])
        model = self.create_model(dimension)

        es = EarlyStopping(patience=self.patience, verbose=1)
        history = model.fit(train_x, train_y, batch_size=self.batch_size,
                            epochs=self.epochs, verbose=1, validation_split=0.2, callbacks=[es])

        self.print_train_history(history)

        preds = model.predict(test_x)
        self.print_predict_result(preds, test_y)
        sys.exit()

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

        # 上げ下げの結果と教師データのセットを返す
        return np.array(_x), np.array(_y)

    def create_model(self, dimension):
        model = Sequential()
        model.add(LSTM(self.hidden_neurons,
                       activation='tanh',
                       recurrent_activation='hard_sigmoid',
                       use_bias=True,
                       kernel_initializer='random_uniform',
                       bias_initializer='zeros',
                       dropout=0.5,
                       recurrent_dropout=0.5,
                       return_sequences=False,
                       batch_input_shape=(None, self.training_days, dimension)))
        model.add(Dropout(0.5))
        model.add(Dense(4,
                        kernel_initializer='random_uniform',
                        bias_initializer='zeros'))
        model.add(Activation("softmax"))
        model.compile(loss="categorical_crossentropy",
                      optimizer="RMSprop", metrics=['categorical_accuracy'])
        return model

    def print_train_history(self, history):
        print("Epoch, Loss, Val loss, Acc, Val Acc")
        for i in range(len(history.history['loss'])):
            loss = history.history['loss'][i]
            val_loss = history.history['val_loss'][i]
            acc = history.history['categorical_accuracy'][i]
            val_acc = history.history['val_categorical_accuracy'][i]
            print("%d,%f,%f,%f,%f" % (i, loss, val_loss, acc, val_acc))

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
        precision = tp / (tp + fp + 0.00000001)
        recall = tp / (tp + fn + 0.0000001)
        f_value = 2 * recall * precision / (recall + precision + 0.0000001)
        logger.info("Precision = %f, Recall = %f, F = %f" % (precision, recall, f_value))

        matrix = confusion_matrix(trues, predicts, labels=[0, 1, 2, 3])
        matrix = pd.DataFrame(matrix,
                              columns=["pred_{}".format(i) for i in range(4)],
                              index=["true_{}".format(i) for i in range(4)])
        logger.info("Matrix: \n{}".format(matrix))

    def set_dataset(self, stock_data_df):
        close_values = stock_data_df[["Close"]]
        open_values = stock_data_df[["Open"]]
        high_values = stock_data_df[["High"]]
        low_values = stock_data_df[["Low"]]
        # stock_data_df["diff_Open_Close"] = open_values["Open"] - close_values["Close"]
        # stock_data_df["diff_rate_Opne_Close"] = stock_data_df["diff_Open_Close"] / close_values["Close"]

        # get option data
        option_data_list = []
        for name in ["DEXJPUS", "SP500", "DJIA"]:
            option_data = self.read_exchange_data(name)
            option_data.columns = ["Close_{}".format(name)]

        nikei225_data = self.read_nikei225_data()
        TOPIX_data = self.read_TOPIX_data()

        nikei225_data = nikei225_data[["Open", "Close", "High", "Low"]]
        nikei225_data.columns = ["Open_nikei225", "Close_nikei225", "High_nikei225", "Low_nikei225"]
        # nikei225_data["diff_Open_Close_nikei225"] = nikei225_data["Open_nikei225"] - nikei225_data["Close_nikei225"]
        # nikei225_data["diff_rate_Opne_Close_nikei225"] = nikei225_data["diff_Open_Close_nikei225"] / nikei225_data["Close_nikei225"]

        TOPIX_data = TOPIX_data[["Open", "Close", "High", "Low"]]
        TOPIX_data.columns = ["Open_TOPIX", "Close_TOPIX", "High_TOPIX", "Low_TOPIX"]
        # TOPIX_data["diff_Open_Close_TOPIX"] = TOPIX_data["Open_TOPIX"] - TOPIX_data["Close_TOPIX"]
        # TOPIX_data["diff_rate_Opne_Close_TOPIX"] = TOPIX_data["diff_Open_Close_TOPIX"] / TOPIX_data["Close_TOPIX"]
        # ==============

        stock_data_df = pd.concat([stock_data_df[["Open", "Close", "High", "Low"]],
                                   nikei225_data, TOPIX_data] + option_data_list, axis=1)
        stock_data_df = stock_data_df.dropna(how='any')

        return close_values, open_values, high_values, low_values, stock_data_df

    @staticmethod
    def compute_rate_of_decline(data_df):
        rate_of_decline = data_df.pct_change()
        rate_of_decline.iloc[0, :] = 0
        return rate_of_decline

    @staticmethod
    def read_exchange_data(name):
        return pd.read_csv(HISTRICAL_EXCHANGE_DATA_PATH.format(name=name), index_col=0)

    @staticmethod
    def read_nikei225_data():
        return pd.read_csv(HISTRICAL_DATA_PATH.format(code="998407"), index_col=0)

    @staticmethod
    def read_TOPIX_data():
        return pd.read_csv(HISTRICAL_DATA_PATH.format(code="998405"), index_col=0)

    @staticmethod
    def compute_log_and_diff(y_data, stock_data_df):
        stock_data_df = stock_data_df.applymap(lambda x: math.log10(x))
        stock_data_df = stock_data_df.diff()
        stock_data_df = stock_data_df.dropna(how='any')
        y_data = y_data[1:]
        return y_data, stock_data_df


if __name__ == '__main__':

    predict_class_of_change_using_lstm = PredictClassOfChangeUsingLSTM()
    predict_class_of_change_using_lstm.execute()