import numpy
import pandas
import matplotlib.pyplot as plt
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.layers import Embedding, Dense, Dropout, BatchNormalization
from keras.layers import LSTM, CuDNNLSTM
from keras.optimizers import Adam
from keras.preprocessing.sequence import TimeseriesGenerator
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.model_selection import StratifiedKFold, KFold
from sklearn.preprocessing import LabelEncoder, StandardScaler, MinMaxScaler
from sklearn.pipeline import Pipeline
from keras.utils import np_utils
from sklearn.metrics import confusion_matrix
import itertools

seed = 7
numpy.random.seed(seed)

full_data = pandas.read_csv("../../Data/Next24.csv")
full_data = full_data.loc[:, ~full_data.columns.str.contains('^Unnamed')]
full_data = full_data.drop(columns=['time'])
full_data.columns = full_data.columns.str.replace('.','_')

X = full_data.drop(columns=['Next_24', 'Labs'])
y = full_data['Next_24']
print(X.head)

# One hot encoding
encoder = LabelEncoder()
encoder.fit(y)
encoded_y = encoder.transform(y)
encoded_y = np_utils.to_categorical(encoded_y)
print("encoded_y=", encoded_y)

# Train test split
X_train = X.iloc[:250000]
X_test = X.iloc[250000:]
y_train = encoded_y[:250000]
y_test = encoded_y[250000:]
print(X_train.shape, X_test.shape,
        y_train.shape, y_test.shape)

# Normalize
scaler = StandardScaler()
# scaler = MinMaxScaler(feature_range=(0,1))
scaler.fit(X_train)
X_train = scaler.transform(X_train)
X_test = scaler.transform(X_test)

# Define sequence generator
SEQ_LEN = 720

train_gen = TimeseriesGenerator(X_train, y_train,
        length=SEQ_LEN, batch_size=1)
test_gen = TimeseriesGenerator(X_test, y_test,
        length=SEQ_LEN, batch_size=1)

x_, y_ = train_gen[0]
print(x_.shape, y_.shape, y_[0].shape, y_[0])

# baseline model
max_feat = 1024
def create_baseline():
    model = Sequential()
    model.add(LSTM(128, input_shape=(SEQ_LEN,5),
        return_sequences=True))
    model.add(Dropout(0.2))
    model.add(BatchNormalization())

    model.add(LSTM(128, return_sequences=True))
    model.add(Dropout(0.1))
    model.add(BatchNormalization())

    model.add(LSTM(128))
    model.add(Dropout(0.2))
    model.add(BatchNormalization())

    model.add(Dense(32, activation='relu'))
    model.add(Dropout(0.2))

    model.add(Dense(2, activation='softmax'))

    # Compile model
    opt = Adam(lr=0.001, decay=1e-6)
    model.compile(loss='binary_crossentropy',
            optimizer=opt, metrics=['accuracy'])

    return model


model = create_baseline()
print(model.summary())

history=model.fit_generator(train_gen, epochs=10,
        verbose=2)

print(history.history.keys())
# list all data in history
print(history.history.keys())
# summarize history for accuracy
plt.plot(history.history['acc'])
plt.plot(history.history['val_acc'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()
# summarize history for loss
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper left')
plt.show()


pre_cls=model.predict_classes(X)
cm1 = confusion_matrix(encoder.transform(Y),pre_cls)
print('Confusion Matrix : \n')
print(cm1)


score, acc = model.evaluate(X,encoded_Y)
print('Test score:', score)
print('Test accuracy:', acc)
