import logzero
from logzero import logger
import os

class LogSetting(object):
    def __init__(self,
                 logfile_path = os.path.dirname(os.path.abspath(__file__)),
                 logfile_name = "sample.log",
                 disableStderrLogger=False,
                 maxBytes = 10e10,
                 backupCount = 10):
        self.logfile_path = logfile_path
        self.logfile_name = logfile_name
        self.disableStderrLogger = disableStderrLogger # 標準出力を切る場合はTrue
        self.maxBytes = maxBytes
        self.backupCount = backupCount

        self.formatter = None

    def set_format(self, log_format='%(color)s[%(module)s.%(funcName)s:%(lineno)3d]%(end_color)s %(message)s', asctime="%Y/%m/%d %H:%M:%S"):
        self.formatter = logzero.LogFormatter(fmt=log_format, datefmt=asctime)
        logzero.setup_default_logger(formatter=self.formatter)

    def create(self):
        logfile = os.path.join(self.logfile_path, self.logfile_name)
        logzero.logfile(logfile,
                        formatter = self.formatter,
                        disableStderrLogger=self.disableStderrLogger,
                        maxBytes=self.maxBytes,
                        backupCount=self.backupCount)
        return logger

log_setting = LogSetting()
# log_setting.set_format()
mylogger = log_setting.create()
