#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time    : 2021/3/25 1:22 PM
# @Author  : Zhihu Yang
# @File    : testddmc.py
import warnings

warnings.filterwarnings("ignore")

import multiprocessing

import pandas as pd
import numpy as np
import jieba
import yaml
from gensim.corpora import Dictionary
from gensim.models import Word2Vec
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dropout, Dense, Activation
from tensorflow.keras.models import model_from_yaml
from tensorflow.keras.preprocessing import sequence
from sklearn.model_selection import train_test_split

vocab_dim = 200
n_exposures = 10
window_size = 7
cpu_count = multiprocessing.cpu_count()
n_iterations = 1
max_len = 10
input_length = 200
batch_size = 32
n_epoch = 20


# 加载文件
def loadfile():
    neg = pd.read_excel('../data/neg.xls', sheet_name=0, header=None)
    pos = pd.read_excel('../data/pos.xls', sheet_name=0, header=None)

    combined = np.concatenate((pos[0], neg[0]))
    y = np.concatenate((np.ones(len(pos), dtype=int), np.zeros(len(neg), dtype=int)))

    return combined, y


# 对句子进行分词，并取掉换行
def tokenizer(text):
    '''Simple Parser converting each document to lower-case, then
        removing the breaks for new lines and finally splitting on the
        whitespace
    '''
    text = [jieba.lcut(document.replace('\n', '')) for document in text]
    return text


# 创建词语字典，并返回每个词语的索引，词向量，以及每个句子所对应的词语索引
def word2vec_train(combined):
    model = Word2Vec(size=vocab_dim,
                     min_count=n_exposures,
                     window=window_size,
                     workers=cpu_count,
                     iter=n_iterations)
    model.build_vocab(combined)
    model.train(combined, total_examples=model.corpus_count, epochs=model.iter)
    model.save('../lstm_data/Word2vec_model.pkl')
    index_dict, word_vectors, combined = create_dictionaries(model=model, combined=combined)
    return index_dict, word_vectors, combined


# 创建词语字典，并返回每个词语的索引，词向量，以及每个句子所对应的词语索引
def create_dictionaries(model=None,
                        combined=None):
    maxlen = 200
    ''' Function does are number of Jobs:
            1- Creates a word to index mapping
            2- Creates a word to vector mapping
            3- Transforms the Training and Testing Dictionaries
    '''
    if (combined is not None) and model is not None:
        gensim_dict = Dictionary()
        gensim_dict.doc2bow(model.wv.vocab.keys(), allow_update=True)
        w2indx = {v: k + 1 for k, v in gensim_dict.items()}  # 所有词频数超过10的词语的索引
        w2vec = {word: model[word] for word in w2indx.keys()}  # 所有词频数超过10的词语的词向量

        def parse_dataset(combined):
            '''
            Words become integers
            '''
            data = []
            for sentence in combined:
                new_txt = []
                for word in sentence:
                    try:
                        new_txt.append(w2indx[word])
                    except:
                        new_txt.append(0)
                data.append(new_txt)
            return data

        combined = parse_dataset(combined)
        combined = sequence.pad_sequences(combined, maxlen=maxlen)
        return w2indx, w2vec, combined
    else:
        print('No data provide')


def get_data(index_dict, word_vectors, combined, y):
    n_symbols = len(index_dict) + 1  # 所有单词的索引数，词频小于10的词语索引为0，所以加1

    embedding_weights = np.zeros((n_symbols, vocab_dim))  # 索引为0的词语，词向量全为0

    for word, index in index_dict.items():  # 从索引为1的词语开始，对每个词语对应其词向量
        embedding_weights[index, :] = word_vectors[word]
    x_train, x_test, y_train, y_test = train_test_split(combined, y, test_size=0.2)
    print(x_train, x_test, y_train, y_test)
    return n_symbols, embedding_weights, x_train, y_train, x_test, y_test


# 定义网络结构
def train_lstm(n_symbols, embedding_weights, x_train, y_train, x_test, y_test):
    print('Defining a simple Keras Model')
    model = Sequential()  # or Graph or whatever
    model.add(Embedding(output_dim=vocab_dim,
                        input_dim=n_symbols,
                        mask_zero=True,
                        weights=[embedding_weights],
                        input_length=input_length))
    model.add(LSTM(activation="sigmoid", units=64, recurrent_activation="hard_sigmoid", return_sequences=True))
    model.add(LSTM(activation="sigmoid", units=32, recurrent_activation="hard_sigmoid"))

    model.add(Dropout(0.5))
    model.add(Dense(1))
    model.add(Activation('sigmoid'))

    print('Compiling the Model...')
    model.compile(loss='binary_crossentropy',
                  optimizer='adam', metrics=['accuracy'])
    print("Train...")

    model.fit(x_train, y_train, batch_size=batch_size, epochs=n_epoch, verbose=1, validation_data=(x_test, y_test))

    print("Evaluate...")

    score = model.evaluate(x_test, y_test,
                           batch_size=batch_size)
    yaml_string = model.to_yaml()
    with open('../lstm_data/lstm.yml', 'w') as outfile:
        outfile.write(yaml.dump(yaml_string, default_flow_style=True))
    model.save_weights('../lstm_data/lstm.h5')
    print('Test score:', score)


# 训练模型，并保存
def train():
    print('Loading Data...')
    combined, y = loadfile()
    print(len(combined), len(y))
    print('Tokenising...')
    combined = tokenizer(combined)
    print('Training a Word2vec model...')
    index_dict, word_vectors, combined = word2vec_train(combined)
    print('Setting up Arrays for Keras Embedding Layer...')
    n_symbols, embedding_weights, x_train, y_train, x_test, y_test = get_data(index_dict, word_vectors, combined, y)
    print(x_train.shape, y_train.shape)
    train_lstm(n_symbols, embedding_weights, x_train, y_train, x_test, y_test)


def input_transform(string):
    words = jieba.lcut(string)
    words = np.array(words).reshape(1, -1)
    model = Word2Vec.load('../lstm_data/Word2vec_model.pkl')
    _, _, combined = create_dictionaries(model, words)
    return combined


# 执行结果
def lstm_predict(string):
    # print('loading model......')
    with open('../lstm_data/lstm.yml', 'r') as f:
        yaml_string = yaml.load(f)
    model = model_from_yaml(yaml_string)

    # print('loading weights......')
    model.load_weights('../lstm_data/lstm.h5')
    model.compile(loss='binary_crossentropy',
                  optimizer='adam', metrics=['accuracy'])
    data = input_transform(string)
    data.reshape(1, -1)

    # print data
    result = model.predict_classes(data)
    if result[0][0] == 1:
        print(string, ' positive')
        return string, 1
    else:
        print(string, ' negative')
        return string, 0


if __name__ == '__main__':
    train()
    string = '电池充完了电连手机都打不开.简直烂的要命.真是金玉其外,败絮其中!连5号电池都不如'
    lstm_predict(string)
