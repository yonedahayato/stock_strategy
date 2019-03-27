import copy

class PackageDrawing(object):
    # DrawGraph class のinitするときの引数として使用する
    def __init__(self, attributes, cnt, stock_data_df, code):

        self.data_df = stock_data_df
        self.code = code

        attributes_dict = attributes.__dict__
        self.reset_attribute()

        self.method_name = attributes.method_name

        # 以下の変数がStockStrategy class に含まれて入れば、それぞれの処理が行われる
        if "window" in attributes_dict.keys():
            # 平均移動線を描画
            self.window = copy.deepcopy(attributes.window)

        if "lines_for_draw_graph" in attributes_dict.keys():
            # 直線を描画
            self.lines = copy.deepcopy(attributes.lines_for_draw_graph[cnt])

        if "small_peak_info" in attributes_dict.keys() and \
            attributes_dict.get("flag_draw_small_peak", False):
            # small peak を円で描画
            self.small_peak_info = copy.deepcopy(attributes.small_peak_infos[cnt])

        if "large_peak_info" in attributes_dict.keys() and \
            attributes_dict.get("flag_draw_large_peak", False):
            # large peak を円で描画
            self.large_peak_info = copy.deepcopy(attributes.large_peak_infos[cnt])

        if "vertical_lines" in attributes_dict.keys():
            # 縦線を描画
            self.vertical_lines = copy.deepcopy(attributes.vertical_lines)

    def reset_attribute(self):
        self.window = None
        self.lines = []
        self.small_peak_info = None
        self.large_peak_info = None
        self.method_name = ""
        self.vertical_lines = []

    def output_as_dict(self):
        pass

if __name__ == "__main__":
    class Attributes(object):
        def __init__(self):
            self.method_name = "method_name"
    attributes = Attributes()
    package = PackageDrawing(attributes=attributes, cnt="cnt",
                            stock_data_df="stock_data_df", code="code")

    print(package.__dict__)
