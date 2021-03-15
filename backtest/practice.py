import pytest

import datetime
import numpy as np
import os
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
import sys

ABSPATH = os.path.abspath(__file__)
BASEDIR = os.path.dirname(ABSPATH)
PARENTDIR = os.path.dirname(BASEDIR)

sys.path.append(PARENTDIR)

from stock_strategy.stock_strategy import StockStrategy

TEST_CODE = 1332

try:
    from backtesting import Strategy
    from backtesting import Backtest
    from backtesting.test import EURUSD, SMA
except:
    print("backtesting import 失敗")

class MyStrategy(Strategy):
    """MyStrategy class

    テスト用の戦略クラス

    """
    def init(self):
        """init func

        これは一体なんなのか
        初期化するようなのだが

        """
        pass

    def next(self):
        """next func

        sell or buy を実行するメソッド?

        """
        if self.data.Close[-1]> self.data.Open[-1]:
            self.buy()
        else:
            self.sell()

class MLTrainOnceStrategy(Strategy):
    price_delta = .004  # 0.4%
    N_TRAIN = 400

    def init(self):
        # Init our model, a kNN classifier
        self.clf = KNeighborsClassifier(7)

        # Train the classifier in advance on the first N_TRAIN examples
        df = self.data.df.iloc[:self.N_TRAIN]
        X, y = BacktestingTutorialWithML.get_clean_Xy(df)
        self.clf.fit(X, y)

        # Plot y for inspection
        self.I(BacktestingTutorialWithML.get_y, self.data.df, name='y_true')

        # Prepare empty, all-NaN forecast indicator
        self.forecasts = self.I(lambda: np.repeat(np.nan, len(self.data)), name='forecast')

    def next(self):
        # Skip the training, in-sample data
        if len(self.data) < self.N_TRAIN:
            return

        # Proceed only with out-of-sample data. Prepare some variables
        high, low, close = self.data.High, self.data.Low, self.data.Close
        current_time = self.data.index[-1]

        # Forecast the next movement
        X = BacktestingTutorialWithML.get_X(self.data.df.iloc[-1:])
        forecast = self.clf.predict(X)[0]

        # Update the plotted "forecast" indicator
        self.forecasts[-1] = forecast

        # If our forecast is upwards and we don't already hold a long position
        # place a long order for 20% of available account equity. Vice versa for short.
        # Also set target take-profit and stop-loss prices to be one price_delta
        # away from the current closing price.
        upper, lower = close[-1] * (1 + np.r_[1, -1]*self.price_delta)

        if forecast == 1 and not self.position.is_long:
            self.buy(size=.2, tp=upper, sl=lower)
        elif forecast == -1 and not self.position.is_short:
            self.sell(size=.2, tp=lower, sl=upper)

        # Additionally, set aggressive stop-loss on trades that have been open
        # for more than two days
        for trade in self.trades:
            if current_time - trade.entry_time > pd.Timedelta('2 days'):
                if trade.is_long:
                    trade.sl = max(trade.sl, low)
                else:
                    trade.sl = min(trade.sl, high)

class BacktestingTutorialWithML(object):
    """BacktestingTutorialWithML class

    backtesting tutorial の trading_with_Machine_Learning で使用する関数
    https://kernc.github.io/backtesting.py/doc/examples/Trading%20with%20Machine%20Learning.html

    """

    @staticmethod
    def BBANDS(data, n_lookback, n_std):
        """BBANDS func

        Bollinger bands indicator

        """
        hlc3 = (data.High + data.Low + data.Close) / 3
        mean, std = hlc3.rolling(n_lookback).mean(), hlc3.rolling(n_lookback).std()
        upper = mean + n_std*std
        lower = mean - n_std*std
        return upper, lower

    @staticmethod
    def get_X(data):
        """Return model design matrix X"""
        return data.filter(like='X').values

    @staticmethod
    def get_y(data):
        """Return dependent variable y"""
        y = data.Close.pct_change(48).shift(-48)  # Returns after roughly two days
        y[y.between(-.004, .004)] = 0             # Devalue returns smaller than 0.4%
        y[y > 0] = 1
        y[y < 0] = -1
        return y

    @staticmethod
    def get_clean_Xy(df):
        """Return (X, y) cleaned of NaN values"""
        X = BacktestingTutorialWithML.get_X(df)
        y = BacktestingTutorialWithML.get_y(df).values
        isnan = np.isnan(y)
        X = X[~isnan]
        y = y[~isnan]
        return X, y


class TestBacktestingPy(object):
    """TestBacktestingPy class

    pip install backtesting
    backtesting の練習

    """

    TEST_CODE = TEST_CODE

    def setup_class(self):
        """setup class func

        class 単位での前処理
        主にデータのロード

        """
        stock_strategy = StockStrategy()
        self.data_df = stock_strategy.get_stock_data(code = self.TEST_CODE)

    def test_backtesting_py(self):
        """test_backtesting_py func

        backtesting.py の起動確認

        記事
            https://nehori.com/nikki/2020/01/28/15315/
        公式
            https://kernc.github.io/backtesting.py/doc/examples/Quick%20Start%20User%20Guide.html

        """
        from backtesting import Strategy
        from backtesting import Backtest

        cash = 100000 # 予算 (10万円)
        commission = 0.001 # 手数料 (0.1%)
        bt = Backtest(self.data_df, MyStrategy, cash=cash, commission=commission)
        stats = bt.run()
        print("\nbacktest.py")
        print("stats: \n{}".format(stats))

        # print("class: {}".format(type(stats)))
        # <class 'backtesting.backtesting.Backtest._Stats'>

        print("equity: \n{}".format(stats['_equity_curve'].iloc[:10]))
        print("trades: \n{}".format(stats['_trades']))

        attrs = []
        for attr in dir(stats):
            if "__" in attr:
                continue
            if "_" not in attr:
                continue
            if "_" != attr[0]:
                continue

            attrs.append(attr)

        print(attrs)

    def test_get_return(self):
        """test_get_return func

        return を取得するテスト

        """
        cash = 100000 # 予算 (10万円)
        commission = 0.001 # 手数料 (0.1%)
        print("len data: {}".format(len(self.data_df)))
        bt = Backtest(self.data_df, MyStrategy, cash=cash, commission=commission)
        stats = bt.run()
        equity_curve = stats['_equity_curve']
        print("\nequity_curve: {}".format(equity_curve))

        equity = equity_curve["Equity"]
        print("quity: {}".format(equity))

        return_df = equity.diff()
        print("return: {}".format(return_df))

    def test_trading_with_Machine_Learning(self):
        test_funcs = BacktestingTutorialWithML

        data = EURUSD.copy()

        close = data.Close.values
        sma10 = SMA(data.Close, 10)
        sma20 = SMA(data.Close, 20)
        sma50 = SMA(data.Close, 50)
        sma100 = SMA(data.Close, 100)
        upper, lower = test_funcs.BBANDS(data, 20, 2)

        # Design matrix / independent features:

        # Price-derived features
        data['X_SMA10'] = (close - sma10) / close
        data['X_SMA20'] = (close - sma20) / close
        data['X_SMA50'] = (close - sma50) / close
        data['X_SMA100'] = (close - sma100) / close

        data['X_DELTA_SMA10'] = (sma10 - sma20) / close
        data['X_DELTA_SMA20'] = (sma20 - sma50) / close
        data['X_DELTA_SMA50'] = (sma50 - sma100) / close

        # Indicator features
        data['X_MOM'] = data.Close.pct_change(periods=2)
        data['X_BB_upper'] = (upper - close) / close
        data['X_BB_lower'] = (lower - close) / close
        data['X_BB_width'] = (upper - lower) / close
        data['X_Sentiment'] = ~data.index.to_series().between('2017-09-27', '2017-12-14')

        # Some datetime features for good measure
        data['X_day'] = data.index.dayofweek
        data['X_hour'] = data.index.hour

        data = data.dropna().astype(float)

        X, y = test_funcs.get_clean_Xy(data)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.5, random_state=0)

        clf = KNeighborsClassifier(7)  # Model the output based on 7 "nearest" examples
        clf.fit(X_train, y_train)

        y_pred = clf.predict(X_test)

        _ = pd.DataFrame({'y_true': y_test, 'y_pred': y_pred}).plot(figsize=(15, 2), alpha=.7)
        print('Classification accuracy: ', np.mean(y_test == y_pred))

        bt = Backtest(data, MLTrainOnceStrategy, commission=.0002, margin=.05)
        bt.run()
