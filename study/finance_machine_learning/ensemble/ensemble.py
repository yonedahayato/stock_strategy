"""ensemble.py

    Section6

"""

# from scipy.misc import comb
from scipy.special import comb
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

def bagging_accuracy():
    """bagging_accuracy func

    バギング分類の正解率
    スニペット 6.1
    """
    N, p, k = 100, 1.0/3, 3.0
    p_tmp = 0
    for i in range(0, int(N/k) + 1):
        p_tmp += comb(N, i) * p ** i * (1-p) ** (N-i)
        print("\np, p_tmp", p, p_tmp)

def set_RF(avg_u):
    """set_RF func

    RF を設定する３つの方法
    スニペット 6.2

    """
    n_estimators = 1000
    clf0 = RandomForestClassifier(n_estimators=n_estimators, \
                                  class_weight="balanced_subsample", criterion="entropy")

    clf1 = DecisionTreeClassifier(criterion="entropy", max_features="auto", \
                                  class_weight="balanced_subsample")
    clf1 = BaggingClassifier(base_estimator=clf1, n_estimators=n_estimators, max_samples=avg_u)

    clf2 = RandomForestClassifier(n_estimators=1, criterion="entropy", bootstrap=False, \
                                  class_weight="balanced_subsample")
    clf2 = BaggingClassifier(base_estimator=clf2, n_estimators=n_estimators, max_samples=avg_u, \
                             max_features=1.0)
