class Stock_Storategy:
    def __init__(self, debug=False, back_test_return_date=0, method_name="method_name", multiprocess=False):
        self.msg_tmpl = "[Stock_Storategy:{}]: "

        self.debug = debug
        self.back_test_return_date = back_test_return_date
        self.method_name = method_name
        self.multiprocess = multiprocess

        self.result_codes = []

    def get_code_list(self):
        gcl = Get_Code_List()
        self.new_code_list = gcl.get_new_stock_code()
        self.new_code_list = list(self.new_code_list["コード"])
        if self.debug:
            self.new_code_list = self.new_code_list[:10]

        return self.new_code_list

    def get_stock_data(self, code):
        msg = self.msg_tmpl.format("get_stock_data") + "{}"

        dd = Data_Downloader()
        print(code)
        stock_data_df = dd.download(code)
        stock_data_df = stock_data_df.set_index("Date")
        if self.back_test_return_date != 0:
            stock_data_df = stock_data_df.iloc[:-self.back_test_return_date]

        if self.debug:
            print(msg.format(stock_data_df))

        return stock_data_df

    def select_code(self, code, stock_data_df):
        # example #
        # stock code number : i
        # stock data length : n
        # close value : C[i]
        # selected code list = argmax_{i} ( (C[n-1] - C[n-2]) / C[n-2] )

        if len(self.result_codes) == 0:
            self.result_codes.append(int(code))
            self.max_close_rate = (stock_data_df.iloc[-1]["Close"] - stock_data_df.iloc[-2]["Close"]) / stock_data_df.iloc[-2]["Close"]
        else:
            max_close_rate_tmp = (stock_data_df.iloc[-1]["Close"] - stock_data_df.iloc[-2]["Close"]) / stock_data_df.iloc[-2]["Close"]

            if max_close_rate_tmp > self.max_close_rate:
                self.max_rate_close = max_close_rate_tmp
                self.result_codes = [int(code)]

    def get_stock_data_index(self):
        code = self.new_code_list[0]
        stock_data_df = self.get_stock_data(code)
        return stock_data_df.index

    def save_result(self):
        sr = Save_Result()

        sr.add_info("result_code_list", self.result_codes)
        sr.add_info("method", self.method_name)

        stock_data_df_index = self.get_stock_data_index()
        sr.add_info("data_range_start", stock_data_df_index[0])
        sr.add_info("data_range_end", stock_data_df_index[-1])

        sr.save()

    def check_select_code(self):
        msg = self.msg_tmpl.format("check_select_code") + "{}"
        logger.info(msg.format(self.result_codes))

    def multiprocess_exect(self, code_cnt, code):
        msg = self.msg_tmpl.format("multiprocess_exect") + "{}"

        logger.info(msg.format("code {}, {} / {}".format(code, code_cnt+1, len(self.new_code_list))))

        try:
            stock_data_df = self.get_stock_data(code)
        except:
            err_msg = msg.format("fail to get stock histlical data.")
            logger.error(err_msg)
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            logger.info(msg.format("success to get stock histlical data."))

        try:
            self.select_code(code, stock_data_df)
        except:
            err_msg = msg.format("fail to select code.")
            logger.error(err_msg)
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            logger.info(msg.format("success to select code."))

        return self.result_codes

    def exect(self):
        msg = self.msg_tmpl.format("exect") + "{}"

        try:
            code_list = self.get_code_list()
        except:
            err_msg = msg.format("fail to get code list.")
            logger.error(err_msg)
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            logger.info(msg.format("success to get code list."))

        if not self.multiprocess:
            for code_cnt, code in enumerate(code_list):
                logger.info(msg.format("code {}, {} / {}".format(code, code_cnt+1, len(code_list))))

                try:
                    stock_data_df = self.get_stock_data(code)
                except:
                    err_msg = msg.format("fail to get stock histlical data.")
                    logger.error(err_msg)
                    logger.exception(err_msg)
                    raise Exception(err_msg)
                else:
                    logger.info(msg.format("success to get stock histlical data."))

                try:
                    self.select_code(code, stock_data_df)
                except:
                    err_msg = msg.format("fail to select code.")
                    logger.error(err_msg)
                    logger.exception(err_msg)
                    raise Exception(err_msg)
                else:
                    logger.info(msg.format("success to select code."))
        elif self.multiprocess:
            try:
                processed = Parallel(n_jobs=-1)([delayed(self.multiprocess_exect)(code_cnt, code) for code_cnt, code in enumerate(code_list)])
            except:
                err_msg = msg.format("fail to exect multiprocess.")
                logger.error(err_msg)
                logger.exception(err_msg)
                raise Exception(err_msg)
            else:
                logger.info(msg.format("success to ecect multiprocess."))

        try:
            self.check_select_code()
        except:
            err_msg = msg.format("fail to check select code.")
            logger.error(err_msg)
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            logger.info(msg.format("success to check select code."))

        try:
            self.save_result()
        except:
            err_msg = msg.format("fail to save result select code.")
            logger.error(err_msg)
            logger.exception(err_msg)
            raise Exception(err_msg)
        else:
            logger.info(msg.format("success to save result select code."))
