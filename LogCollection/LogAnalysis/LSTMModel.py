#!/usr/bin/env python
# -*- coding:utf-8 -*-
import os
from DataPrepare import DocLogs
from sklearn.model_selection import train_test_split
from sklearn import metrics

from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout, LSTM, Bidirectional
from keras.layers.convolutional import MaxPooling1D, Conv1D
from keras.callbacks import EarlyStopping
from keras.models import load_model
import pandas as pd
import functools
from keras import backend as K
import tensorflow as tf

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'


def as_keras_metric(method):
    @functools.wraps(method)
    def wrapper(self, args, **kwargs):
        """ Wrapper for turning tensorflow metrics into keras metrics """
        value, update_op = method(self, args, **kwargs)
        K.get_session().run(tf.local_variables_initializer())
        with tf.control_dependencies([update_op]):
            value = tf.identity(value)
        return value
    return wrapper


def MyLSTM():
    # how many words count?
    feature = 700
    # size of each word
    vec_size = 300
    # use ROC
    auc_roc = as_keras_metric(tf.metrics.auc)
    # model
    model = Sequential()
    # add conv1D layer
    model.add(Conv1D(filters=32, kernel_size=3, padding='same',
                     activation='relu', input_shape=(feature, vec_size)))
    model.add(Dropout(0.2))
    model.add(MaxPooling1D(pool_size=3))
    model.add(Dropout(0.2))
    # add conv1D layer
    model.add(Conv1D(filters=32, kernel_size=3,
                     padding='same', activation='relu'))
    model.add(Dropout(0.2))
    model.add(MaxPooling1D(pool_size=3))
    model.add(Dropout(0.2))
    # add conv1D layer
    model.add(Conv1D(filters=32, kernel_size=3,
                     padding='same', activation='relu'))
    model.add(Dropout(0.2))
    model.add(MaxPooling1D(pool_size=3))
    model.add(Dropout(0.2))
    # add conv1D layer
    model.add(Conv1D(filters=32, kernel_size=3,
                     padding='same', activation='relu'))
    model.add(Dropout(0.2))
    model.add(MaxPooling1D(pool_size=3))
    model.add(Dropout(0.2))
    # add LSTM layer
    model.add(LSTM(300, dropout=0.2, recurrent_dropout=0.2))
    # model.add(Dropout(0.2))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))
    model.compile(loss='binary_crossentropy',
                  optimizer='adam', metrics=[auc_roc])
    # model complete
    print model.summary()
    return model


def training_by_LSTM(dirname):
    print "training by LSTM + Doc2Vec"
    context = {}

    lstm = MyLSTM()
    data, label = DocLogs(dirname).GetDoc2VecModel()
    X_train, X_test, y_train, y_test = train_test_split(data, label, test_size=0.30)
    lstm.fit(X_train, y_train)

    predicted = lstm.predict(X_test)
    metrics_report = metrics.classification_report(y_test, predicted)
    metrics_score = metrics.accuracy_score(y_test, predicted)

    print "metrics socre:", metrics_score
    context['predicted'] = predicted
    context['metrics_score'] = metrics_score
    context['metrics_report'] = metrics_report
    return context
