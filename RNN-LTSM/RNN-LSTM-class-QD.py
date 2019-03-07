import numpy
import pandas
import matplotlib.pyplot as plt
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.layers import Embedding
from keras.layers import LSTM
from keras.wrappers.scikit_learn import KerasClassifier
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from keras.utils import np_utils
from sklearn.model_selection import KFold
from sklearn.metrics import confusion_matrix
import itertools

seed = 7
numpy.random.seed(seed)

dataframe = pandas.read_csv("RNN-ready-DT-MA30-NORM.csv", index_col=0)
print(dataframe.head)

X = dataframe.iloc[:,0:4].astype(float)
Y = dataframe.iloc[:,6]


encoder = LabelEncoder()
encoder.fit(Y)
encoded_Y = encoder.transform(Y)

encoded_Y = np_utils.to_categorical(encoded_Y)
print("encoded_Y=", encoded_Y)
# baseline model
max_feat = 1024
def create_baseline():
    # create model
    model = Sequential()
    model.add(Embedding(max_feat, output_dim=256))
    model.add(LSTM(128))
    model.add(Dropout(0.5))
    #model.add(Dense(4, input_dim=4, kernel_initializer='normal', activation='relu'))
    #model.add(Dense(4, kernel_initializer='normal', activation='relu'))
    #model.add(Dense(2, kernel_initializer='normal', activation='sigmoid'))

    #model.add(Dense(2, kernel_initializer='normal', activation='softmax'))
    model.add(Dense(2, activation='sigmoid'))

    # Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])  # for binayr classification
        #model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])  # for multi class
    return model


model=create_baseline();
history=model.fit(X, encoded_Y, batch_size=500, epochs=10, validation_split = 0.2, verbose=1)

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
