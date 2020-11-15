try:
    from backtesting import Strategy
    from backtesting import Backtest
except:
    print("backtesting import 失敗")

BacktestStrategy = Strategy

class MyBacktests(object):
    """MyBacktests class

    backtest 全般の処理
    使用するライブラリは処理ごとに変わる可能性あり

    """
    def execute(self, data_df, strategy, cash = 100000, commission = 0.001):
        """execute func

        バックテストを実行する
        backtesting ライブラリを使用

        Args:
            data_df(xxx): xxx
            strategy(xxx): xxx
            cash(int): 予算 (10万円)
            commission(float): 手数料 (0.1%)

        """
        self.bt = Backtest(data_df, strategy, cash=cash, commission=commission)
        self.stats = self.bt.run()

    def get_return(self):
        """get_return func

        バックテストの結果からリターンを計算する
        backtesting ライブラリを使用

        Args:
            data_df(xxx): xxx
            strategy(xxx): xxx
            cash(int): 予算 (10万円)
            commission(float): 手数料 (0.1%)

        """

        equity_curve = self.stats['_equity_curve']
        equity = equity_curve["Equity"]
        return_df = equity.diff()

        return return_df

    def get_TWRR(self):
        """get_TWRR func

        時間加重収益率(TWRR : Time-Weighted Rate of Return) を計算

        """
        market_value = []
        returns = []

        for i in range(len(market_value) - 1):
            return_ = (market_value[i+1] - market_value[i]) / market_value[i]
            returns.append(return_)

        TWRR = 1
        for i, return_ in enumerate(returns):
            TWRR *= (1 + return_)
            TWRR -= 1

        return TWRR
