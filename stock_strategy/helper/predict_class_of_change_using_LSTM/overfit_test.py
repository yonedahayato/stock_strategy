import os
import sys

dirname = os.path.dirname

abspath = dirname(os.path.abspath(__file__))
project_path = dirname(dirname(abspath))

from predict_class_of_change_using_LSTM import *

if __name__ == "__main__":
    predict_class_of_change_using_lstm = PredictClassOfChangeUsingLSTM()
    predict_class_of_change_using_lstm.over_fit_test()
