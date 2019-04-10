#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""  TODO: module description

Usage:  

Input:  

Output:  

Author: wenhai.pan

Create Time:    2019-04-08 19:28:39

"""

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import time
import argparse
import pandas as pd
from datetime import datetime, timedelta
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.estimator import DNNLinearCombinedClassifier


def parse_args():
    """parse command line args

    :returns: argparse object

    """

    parser = argparse.ArgumentParser(description="train the model")
    parser.add_argument("--date", help="target date of the data", type=str, default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--data_dir", help="data directory", type=str, default="./result/ml_data")
    parser.add_argument("--model_dir", help="model directory", type=str, default="./result/model")
    parser.add_argument("--train", help="data for training", type=str, default=None)
    parser.add_argument("--test", help="data for testing", type=str, default=None)
    parser.add_argument("--stock", help="select one stock id for training", type=str, default="all")
    parser.add_argument("--batch_size", help="batch size for training", type=int, default=100)
    parser.add_argument("--steps", help="step number for training", type=int, default=10000)

    return parser.parse_args()


def load_data(data_path, label_col):

    df = pd.read_csv(data_path)
    data, label = df, df.pop(label_col)

    return (data, label)


def get_dataset(data, labels, columns, batch_size):

    #dataset = tf.data.Dataset.from_tensor_slices((pd.DataFrame({k: data[k].values for k in columns}), labels))
    dataset = tf.data.Dataset.from_tensor_slices(({k: data[k].values for k in columns}, labels))
    #dataset = tf.data.Dataset.from_tensor_slices((dict(data), labels))

    # Shuffle, repeat, and batch the examples.
    #dataset = dataset.shuffle(1000).repeat().batch(batch_size)
    dataset = dataset.batch(batch_size)

    # Return the dataset.
    return dataset


def main():

    print(tf.__version__)
    print(tf.keras.__version__)

    args = parse_args()

    if not os.path.exists(args.model_dir):
        os.makedirs(args.model_dir)

    if args.train != None:
        train_data_path = args.train
    else:
        train_data_path = "%s/%s/%s/%s" % (args.data_dir, args.date, args.stock, "train.csv")

    if args.test != None:
        test_data_path = args.test
    else:
        test_data_path = "%s/%s/%s/%s" % (args.data_dir, args.date, args.stock, "test.csv")

    train_x, train_y = load_data(train_data_path, "will_profit")
    test_x, test_y = load_data(test_data_path, "will_profit")

    #print train_x
    #print train_y
    #print test_x
    #print test_y

    cols = []
    cols.append("day_open")
    cols.append("day_close")

    wide_feature_cols = []

    deep_feature_cols = []
    deep_feature_cols.append(tf.feature_column.numeric_column("day_open"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_close"))

    train_dataset = get_dataset(train_x, train_y, cols, args.batch_size)
    test_dataset = get_dataset(test_x, test_y, cols, args.batch_size)

    estimator = DNNLinearCombinedClassifier(
        linear_feature_columns = None,
        dnn_feature_columns = deep_feature_cols,
        dnn_hidden_units = [5, 5],
        model_dir = args.model_dir)

    print train_dataset
    print test_dataset

    estimator.train(input_fn = lambda: get_dataset(train_x, train_y, cols, args.batch_size), steps = args.steps)
    #metrics = estimator.evaluate(input_fn = test_dataset, steps = args.steps)

    #estimator.train(input_fn = train_dataset, steps = args.steps)
    #metrics = estimator.evaluate(input_fn = test_dataset, steps = args.steps)

    print metrics

    return


if __name__ == "__main__":
    main()


