"""feature_importance.py

    Section8

"""
import numpy as np
import os
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.metrics import log_loss, accuracy_score
import sys

ABSPATH = os.path.abspath(__file__)
BASEDIR = os.path.dirname(ABSPATH)
PARENTDIR = os.path.dirname(BASEDIR)

sys.path.append(PARENTDIR)

from cross_validation.cross_validation import (
    PurgedKFold,
    cv_score,
)

from multiprocessing_vector.multiprocessing_vector import (
    mp_pandas_obj,
)

def feat_imp_MDI(fit, feat_names):
    """feature_imo_MDI func

    MDI 特徴量重要性
    IS での平均不純度減少量に基づく特徴量重要度
    スニペット 8.3

    Args:
        fit(xxx): xxx
        feat_names(xxx): xxx

    Returns:
        pd.DataFrame: xxx

    """
    df0 = {i:tree.feature_importances_ for i, tree in enumerate(fit.estimators_)}
    df0 = pd.DataFrame.from_dict(df0, orient="index")
    df0.columns = feat_names
    df0 = df0.replace(0, np.nan) # max_features=1 のため

    imp = pd.concat({"mean": df0.mean(), "std": df0.std() * df0.shape[0] ** -0.5}, axis=1)
    imp /= imp["mean"].sum()

    return imp

def feat_imp_MDA(clf, X, y, cv, sample_weight, t1, pct_embargo, scoring="neg_log_loss"):
    """feat_imp_MDA func

    MDA による特徴量重要度測定
    アウトオブサンプルでのスコア低下に基づく特徴量重要度

    Args:
        clf(xxx): xxx
        X(xxx): xxx
        y(xxx): xxx
        cv(xxx): xxx
        sample_weight(xxx): xxx
        t1(xxx): xxx
        pct_embargo(xxx): xxx
        scoring(xxx): xxx

    """
    if scoring not in ["neg_log_loss", "accuracy"]:
        raise Exception("wrong scoring method")

    # パーズ付きCV
    cv_gen = PurgedKFold(n_splits=cv, t1=t1, pct_embargo=pct_embargo)

    scr0, scr1 = pd.Series(), pd.DataFrame(columns=X.columns)

    for i, (train, test) in enumerate(cv_gen.split(X=X)):
        X0, y0, w0 = X.iloc[train, :], y.iloc[train], sample_weight.iloc[train]
        X1, y1, w1 = X.iloc[test, :], y.iloc[test], sample_weight.iloc[test]

        fit = clf.fit(X=X0, y=y0, sample_weight=w0.values)

        if scoring == "neg_log_loss":
            prob = fit.predict_proba(X1)
            scr0.loc[i] = -log_loss(y1, prob, sample_weight=w1.values, labels=clf.classes_)
        else:
            pred = fit.predict(X1)
            scr0.loc[i] = accuracy_score(y1, pred, sample_weight=w1.values)

        for j in X.columns:
            X1_tmp = X1.copy(deep=True)
            np.random.shuffle(X1_tmp[j].values)

            if scoring == "neg_log_loss":
                prob = fit.predict_proba(X1_tmp)
                scr1.loc[i, j] = -log_loss(y1, prob, sample_weight=w1.values, labels=clf.classes_)

            else:
                prob = fit.predict(X1_tmp)
                scr1.loc[i, j] = accuracy_score(y1, pred, sample_weight=w1.values)

    imp = (-scr1).add(scr0, axis=0)

    if scoring == "neg_log_loss":
        imp = imp / -scr1
    else:
        imp = imp / (1.0 - scr1)

    imp = pd.concat({"mean": imp.mean(), "std": imp.std() * imp.shape[0] ** -0.5}, axis=1)

    return imp, scr0.mean()

def aux_feat_imp_SFI(feat_names, clf, trns_x, cont, scoring, cv_gen):
    """aux_feat_imp_SFI func

    SFI の実装
    スニペット 8.4

    """
    imp = pd.DataFrame(columns=["mean", "std"])

    for feat_name in feat_names:
        df0 = cv_score(clf, X=trns_x[[feat_name]], y=cont["bin"], sample_weight=cont["w"], \
                       scoring=scoring, cv_gen=cv_gen)
        imp.loc[feat_name, "mean"] = df0.mean()
        imp.loc[feat_name, "std"] = df0.std() * df0.shape[0] ** -0.5

    return imp

def get_test_data(n_features=40, n_informative=10, n_redundant=10, n_samples=500):
    """get_test_data func

    人工データセットの作成
    ランダムなデータセットを作成
    スニペット 8.7

    Args:
        n_features(int): すべての特徴量数
        n_informative(int): 有益な特徴量数
        n_redundant(int): 冗長な特徴量数
        n_samples(int): すべてのサンプル数

    Returns:
        pd.DataFrame: 特徴量データセット
        pd.DataFrame: ラベルデータセット
    """
    trns_x, cont = make_classification(n_samples=n_samples, n_features=n_features, \
                                       n_informative=n_informative, n_redundant=n_redundant, \
                                       random_state=0, shuffle=False)

    # datetime_index = pd.DatetimeIndex(freq=pd.tseries.offsets.BDay(), end=pd.datetime.today(), periods=n_samples)
    datetime_index = pd.date_range(freq=pd.tseries.offsets.BDay(), end=pd.datetime.today(), periods=n_samples)
    print("datetime_index: ", datetime_index)

    # set datetime index
    trns_x = pd.DataFrame(trns_x, index=datetime_index)
    cont = pd.Series(cont, index=datetime_index).to_frame("bin")

    # set columns
    n_noise = n_features - (n_informative + n_redundant)
    data_columns = ["I_" + str(i) for i in range(n_informative)] + \
                   ["R_" + str(i) for i in range(n_redundant)] + \
                   ["N_" + str(i) for i in range(n_noise)]
    trns_x.columns = data_columns

    cont["w"] = 1.0 / cont.shape[0]
    cont["t1"] = pd.Series(cont.index, index=cont.index)

    print("trns_x", trns_x.shape)
    print("cont", cont.shape)
    print("cont columns", cont.columns)

    return trns_x, cont

def feat_importance(trns_x, cont, n_estimators=5, cv=10, max_samples=1.0, num_threads=1,\
                    pct_embargo=0, scoring="accuracy", method="SFI", min_w_leaf=0.0,  **kargs):
    """feat_importance func

    任意の手法に対する特徴量重要度計算の呼び出し
    スニペット 8.8

    """

    if num_threads == 1:
        n_jobs = num_threads
    else:
        n_jobs = -1

    #1 classifier と cv を用意するマスキングを避けるために max_features=-1 とする
    clf = DecisionTreeClassifier(criterion="entropy", max_features=1, class_weight="balanced", \
                                 min_weight_fraction_leaf=min_w_leaf)
    clf = BaggingClassifier(base_estimator=clf, n_estimators=n_estimators, max_features=1.0, max_samples=max_samples, \
                            oob_score=True, n_jobs=n_jobs)

    fit = clf.fit(X=trns_x, y=cont["bin"], sample_weight=cont["w"].values)
    oob = fit.oob_score_

    print(method)
    if method == "MDI":
        imp = feat_imp_MDI(fit, feat_names=trns_x.columns)
        oos = cv_score(clf, X=trns_x, y=cont["bin"], cv=cv, sample_weight=cont["w"], t1=cont["t1"], \
                       pct_embargo=pct_embargo, scoring=scoring).mean()
    elif method == "MDA":
        imp, oos = feat_imp_MDA(clf, X=trns_x, y=cont["bin"], cv=cv, sample_weight=cont["w"], t1=cont["t1"], \
                       pct_embargo=pct_embargo, scoring=scoring)
    elif method == "SFI":
        cv_gen = PurgedKFold(n_splits=cv, t1=cont["t1"], pct_embargo=pct_embargo)
        oos = cv_score(clf, X=trns_x, y=cont["bin"], sample_weight=cont["w"], scoring=scoring, cv_gen=cv_gen).mean()

        clf.n_jobs = 1
        imp = mp_pandas_obj(aux_feat_imp_SFI, ("feat_names", trns_x.columns), num_threads, \
                            clf=clf, trns_x=trns_x, cont=cont, scoring=scoring, cv_gen=cv_gen)

    print("oos: ", oos)
    print("imp: ", imp)
    return imp, oob, oos

def plot_feat_importance(path_out, imp, ppb, oos, method, tag=0, sim_num=0, **kargs):
    """plot_feat_importance func

    特徴量重要度プロット関数
    スニペット 8.10

    """
    pass
