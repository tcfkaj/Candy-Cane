import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np
import os

from tensorflow.python.keras.models import Sequential
from tensorflow.python.keras.layers import Input, Dense, GRU, Embedding
from tensorflow.python.keras.optimizers import RMSprop
from tensorflow.python.keras.callbacks import EarlyStopping, ModelCheckpoint, TensorBoard, ReduceLROnPlateau

print(tf.__version__,tf.keras.__version__,pd.__version__)

###############################
######## Preprocessing ########
###############################

## Load Data
CC = pd.read_csv('after_data_prep.csv', index_col=0)
print(CC.head())

print(CC.shape)

## Define Target
target_name = 'Vol.Day'

## Shift target
shift_days = 1
shift_steps = shift_days*1440

CC_targets = CC[[target_name]].shift(-shift_steps)

print(CC_targets.head())
print(CC_targets.tail())
print(CC_targets.shape)

## Drop target and time
CC = CC.drop([target_name, 'time'], axis=1)
print(CC.head())

## Define x,y as numpy arrays
print('x_data:')
x_data = CC.values[0:-shift_steps]
print(type(x_data))
print(x_data.shape)

y_data = CC_targets.values[:-shift_steps]
print('y_data:')
print(type(y_data))
print(y_data.shape)
print(y_data[0:10])

## Train-test split
num_data = len(x_data)
print(num_data)
train_split= 0.9
num_train = int(train_split*num_data)
print(num_train)

x_train = x_data[0:num_train]
x_test = x_data[num_train:]
print(len(x_train)+len(x_test))

y_train = y_data[0:num_train]
y_test = y_data[num_train:]
print(len(y_train)+len(y_test))

## Number of input/ output signals
num_x_signals = x_data.shape[1]
num_y_signals = y_data.shape[1]
print(num_x_signals, num_y_signals)

## Define generator for creating random batches of training data
def batch_generator(batch_size, seq_length):

    # Infinite loop.
    while True:
        # Allocate a new array for batch of input signals.
        x_shape = (batch_size, seq_length, num_x_signals)
        x_batch = np.zeros(shape=x_shape, dtype=np.float16)

        # Allocate a new array for batch of output signals.
        y_shape = (batch_size, seq_length, num_y_signals)
        y_batch = np.zeros(shape=y_shape, dtype=np.float16)

        # Fill batch with random sequences of data
        for i in range(batch_size):
            # Get a random start index.
            # Points to somehwere in training data.
            idx = np.random.randint(num_train - seq_length)

            # Copy sequences of training data starting at this index.
            x_batch[i] = x_train[idx:idx+seq_length]
            y_batch[i] = y_train[idx:idx+seq_length]

        yield (x_batch, y_batch)

batch_size = 256
seq_length = 1440*20


## Lets test this generator
generator = batch_generator(batch_size = batch_size,
                            seq_length=seq_length)

x_batch, y_batch = next(generator)

## Create validation set
validation_data = (np.expand_dims(x_test, axis=0),
                    np.expand_dims(y_test, axis=0))

################################
######### Creating RNN #########
################################

model = Sequential()

model.add(GRU(units=512,
                return_sequences=True,
                input_shape=(None,num_x_signals,)))

model.add(Dense(num_y_signals, activation='sigmoid'))

## This may need to be tweaked
if False:
    from tensorflow.python.keras.initializers import RandomUniform

    init = RandomUniform(minval=-0.05, maxval=0.05)
    model.add(Dense(num_y_signals,
                    activation='linear',
                    kernel_initializer=init))

## Define loss function
warmup_steps = 50

def loss_mse_warmup(y_true, y_pred):
    """
    Calculate the Mean Squared Error between y_true and y_pred,
    but ignore the beginning "warmup" part of the sequences.

    y_true is the desired output.
    y_pred is the model's output.
    """

    # The shape of both input tensors are:
    # [batch_size, sequence_length,num_y_signals].

    # Ignore the "warmup" parts of the sequences
    # by taking slices of the tensors.
    y_true_slice = y_true[:, warmup_steps:, :]
    y_pred_slice = y_pred[:, warmup_steps:, :]

    loss = tf.losses.mean_squared_error(labels=y_true_slice,
                                        predictions=y_pred_slice)

    loss_mean = tf.reduce_mean(loss)

    return loss_mean


## Compile Model

optimizer = RMSprop(lr=1e-3)

model.compile(loss=loss_mse_warmup, optimizer=optimizer)

print(model.summary())

## Callback functions

## path_checkpoint = '23_checkpoint.keras'
## callback_checkpoint = ModelCheckpoint(filepath=path_checkpoint,
##                                         monitor='val_loss',
##                                         verbose=1,
##                                         save_weights_only=True,
##                                         save_best_only=True)
##
## callback_early_stopping = EarlyStopping(monitor='val_loss',
##                                         patience=5, verbose=1)
##
## callback_tensorboard = Tensorboard(log_dir='./23_logs/',
##                                     histogram_freq=0,
##                                     write_graph=False)
##
## callback_reduce_lr = ReduceLROnPlateau(monitor='val_loss',
##                                         factor=0.1,
##                                         min_lr=1e-4,
##                                         patience=0,
##                                         verbose=1)
##
## callbacks = [callback_early_stopping
