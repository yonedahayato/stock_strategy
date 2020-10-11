"""ensemble.py

    Section6

"""

# from scipy.misc import comb
from scipy.special import comb
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

class Ensemble(object):
    def __init__(self, fractional_difference):
        self.fractional_difference = fractional_difference

    def ensemble(self, avg_u):
        self.set_RF(avg_u)
        self.fit()

    def set_RF(self, avg_u):
        """set_RF func

        RF を設定する３つの方法
        スニペット 6.2

        """
        n_estimators = 1000
        self.clf0 = RandomForestClassifier(n_estimators=n_estimators, \
                                      class_weight="balanced_subsample", criterion="entropy")

        clf1 = DecisionTreeClassifier(criterion="entropy", max_features="auto", \
                                      class_weight="balanced")
        self.clf1 = BaggingClassifier(base_estimator=clf1, n_estimators=n_estimators, max_samples=avg_u)

        clf2 = RandomForestClassifier(n_estimators=1, criterion="entropy", bootstrap=False, \
                                      class_weight="balanced_subsample")
        self.clf2 = BaggingClassifier(base_estimator=clf2, n_estimators=n_estimators, max_samples=avg_u, \
                                 max_features=1.0)

        self.main_clf = clf2

    def fit(self):
        trns_x = self.fractional_difference.frac_diff_df
        cont = self.fractional_difference.bins_sampled

        fit0 = self.clf0.fit(X=trns_x, y=cont["bin"], sample_weight=cont["w"].values)
        fit1 = self.clf1.fit(X=trns_x, y=cont["bin"], sample_weight=cont["w"].values)
        fit2 = self.clf2.fit(X=trns_x, y=cont["bin"], sample_weight=cont["w"].values)

def bagging_accuracy():
    """bagging_accuracy func

    バギング分類の正解率
    スニペット 6.1

    Note:
        N: 訓練データセット数、推定器数（モデル）
        p: 予測を正しいラベルを付けられる確率（正解率）
        k: クラス数
        1-p_bagging: pは分類器単体の精度に対して、アンサンブルで多数決をとった場合の正解率

        この実行では、推定器を増やせば増やすほど、アンサンブルの精度が高くなるという検証
    """
    N, p, k = 100, 1.0/3, 3.0
    p_bagging = 0
    for i in range(0, int(N/k) + 1):
        p_bagging += comb(N, i) * p ** i * (1-p) ** (N-i)
        # print("\np, p_bagging", p, 1-p_bagging)
