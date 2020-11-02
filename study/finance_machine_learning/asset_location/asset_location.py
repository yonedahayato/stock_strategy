"""asset_location.py

    Section16

"""

def get_quasi_diag(link):
    """get_quasi_diag func

    スニペット 16.2 準対角化

    """
    pass

def get_rec_bipart(cov, sort_ix):
    """get_rec_bipart func

    スニペット 16.3 再帰的二分

    """
    pass

class AssetLocation(object):
    """AssetLocation class

    スニペット 16.4 HRP アルゴリズムの実装（全体）

    """
    def get_IVP(self, cov, **largs):
        """get_IVP func

        逆分散ポートフォリオの計算

        """
        pass

    def get_cluster_var(self, cov, cltems):
        """get_cluster_var func

        クラスター単位の分散の計算

        """
        pass

    def get_quasi_diag(self, link):
        """get_quasi_diag

        クラスターされた要素を距離でソートする

        """
        pass

    def get_rec_bipart(self, cov, sort_ix):
        """get_rec_bipart func

        HRP 配分の計算

        """
        pass

    def corre_idist(self, corr):
        """corre_idist func

        相関ベースの距離行列

        """
        pass

    def plot_corr_matrix(self, path, corr, labels=None):
        """plot_corr_matrix func

        相関係数行列のヒートマップを描画

        """
        pass

    def generate_data(self, n_obs, size0, size1, sigma1):
        """generate_data func

        相関のある変数の時系列を作成する

        """
        pass

    def main(self, plot=False):
        """main func

        """
            #1 Generate correlatetd data
        x, cols = self.generate_data()

        if plot
            #2 compute and plot correl matrix
            self.plot_corr_matrix()

            #3 cluster
        self.corre_idist()
        self.get_quasi_diag()
        if plot:
            self.plot_corr_matrix()

            #4 Capital allocation
        hrp = self.get_rec_bipart()

class AssetLocationMC(AssetLocation):
    """AssetLocationMC class

    スニペット 16.5 HRPのモンテカルロ実験におけるアウトオブサンプルでのパフォーマンス

    """
    def generate_data(self, n_obs, s_lemgth, size0, size1, mu0, sigma1, sigma1F):
        """generate_data func

        関数のある変数の時系列を作成

        """
        pass

    def get_HRP(self, cov, corr):
        """get_HRP func

        階層ポートフォリオの構築

        """
        pass

    def get_CLA(self, cov, **kargs):
        """get_CLA func

        CLA 最小ポートフォリオの計算

        """
        pass

    def hrp_MC(self):
        """hrp_MC func

        HRPにおえkるモンテカルロ実験

        """
        pass
