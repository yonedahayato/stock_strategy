from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.layers.recurrent import LSTM

from logzero import logger

def create_model(dimension, hidden_neurons, training_days):
    model = Sequential()
    model.add(LSTM(hidden_neurons,
                   activation='tanh',
                   recurrent_activation='hard_sigmoid',
                   use_bias=True,
                   kernel_initializer='random_uniform',
                   bias_initializer='zeros',
                   dropout=0.5,
                   recurrent_dropout=0.5,
                   return_sequences=False,
                   batch_input_shape=(None, training_days, dimension)))
    model.add(Dropout(0.5))
    model.add(Dense(4,
                    kernel_initializer='random_uniform',
                    bias_initializer='zeros'))
    model.add(Activation("softmax"))
    model.compile(loss="categorical_crossentropy",
                  optimizer="RMSprop", metrics=['categorical_accuracy'])
    return model

if __name__ == "__main__":
    dimension = 10
    hidden_neurons = 432
    training_days = 5
    model = create_model(dimension, hidden_neurons, training_days)
    logger.debug(model)
