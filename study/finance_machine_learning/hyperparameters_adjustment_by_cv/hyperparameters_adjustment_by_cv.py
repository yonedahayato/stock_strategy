"""hyperparameters_adjustment_by_cv.py

    Section9

"""

from sklearn.model_selection import (
    GridSearchCV,
    RandomizedSearchCV,
)
from sklearn.pipeline import Pipeline
from scipy.stats import rv_continuous

ABSPATH = os.path.abspath(__file__)
BASEDIR = os.path.dirname(ABSPATH)
PARENTDIR = os.path.dirname(BASEDIR)

sys.path.append(PARENTDIR)

from cross_validation.cross_validation import (
    PurgedKFold,
)

def clf_hyper_fit(feat, lbl, t1, pipe_clf, paramd_grid, cv=3, rand_search_iter=0, \
                  bagging=[0, None, 1.0], n_jobs=-1, pct_embargo=0, **fit_params):
    """clf_hyper_fit func

    パージさらた k-分割交差検証法によるグリッドサーチ
    スニペット 9.1
    スニペット 9.3

    Args:
        feat(xxx): 特徴量、入力データ、X
        lbl(xxx): ラベル情報、y
        t1
        pipe_clf(xxx): モデル、推定器
        paramd_grid
        cv3,
        bagging(list)
            [0](int)
            [1](float)
            [2](float)
        n_jobs=-1
        pct_embargo=0
        **fit_params

    """
    # f1 はメタラベリングのため
    if set(lbl.values) == {0, 1}:
        scoring = "f1"
    else:
        # すべての事例について対象
        scoring = "neg_log_loss"

    # 1: 教師データもついてハイパーパラメータをサーチ
        # パージ
    inner_cv = PurgedKFold(n_splits=cv, t1=t1, pct_embargo=pct_embargo)

    if rand_search_iter == 0:
        gs = GridSearchCV(estimator=pipe_clf, param_grid=param_grid, scoring=scoring, \
                          cv=inner_cv, n_jobs=n_jobs, iid=False)
    else:
        # スニペット 9.3
        gs = RandomizedSearchCV(estimator=pipe_clf, param_distributions=paramd_grid, \
                                scoring=scoring, cv=inner_cv, n_jobs=n_jobs, iid=False, n_iter=rand_search_iter)

        # パイプライン
    gs = gs.fit(feat, lbi, **fit_params).best_estimator_

    # 2: データ全体に検証モデルをフィッティングする
    if bagging[1] > 0:
        gs = BaggingClassifier(base_estimator=MyPipeline(gs.steps), \
                               n_estimators=int(bagging[0]), max_samples=float(bagging[1]), \
                               max_features=float(bagging[2]), n_jobs=n_jobs)
        gs = gs.fit(feat, lbl, \
                    sample_weight=fit_params[gs.base_estimator.steps[-1][0] + "__sample_weight"])
        gs = Pipeline([("bag", gs)])

    return gs

class MyPipeline(Pipeline):
    """MyPipeline class

    Pipelineクラスの強化
    スニペット 9.2

    """
    def fit(self, X, y, sample_weight=None, **fit_params):
        """fit func

        xxx

        """
        if sample_weight is not None:
            fit_params[self.steps[-1][0] + "__sample_weight"] = sample_weight

        return super(MyPipeline, self).fit(X, y, **fit_params)

class LogUniformGen(rv_continuous):
    """LogUniformGen class

    スニペット 9.4

    """
    def _cdf(self, x):
        return np.log(x / self.a) / np.log(self.b / self.a)

def log_uniform(a=1, b=np.exp(1)):
    """log_uniform func

    スニペット 9.4

    """
    return log_uniform_gen(a=a, b=b, name="log_uniform")
