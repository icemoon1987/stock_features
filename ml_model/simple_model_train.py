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
import shutil
import argparse
import pandas as pd
from datetime import datetime, timedelta
import tensorflow as tf
from tensorflow.keras import layers
from tensorflow.estimator import DNNLinearCombinedClassifier, RunConfig
from tensorflow.train import SessionRunHook


class MySessionHook(SessionRunHook):

    """get the runtime status of the model"""

    def __init__(self):
        """TODO: to be defined1. """
        SessionRunHook.__init__(self)

    def begin(self):
        print("begin")
        return

    def after_create_session(self, session, coord):
        print("after_create_session")
        return

    def before_run(self, run_context):
        #print('Before calling session.run().')
        return

    def after_run(self, run_context, run_values):
        #print('Done running one step. The value of my tensor: %s', run_values.results)
        return

    def end(self, session):
        print('Done with the session.')
        return


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
    parser.add_argument("--batch_size", help="batch size for training", type=int, default=10)
    parser.add_argument("--steps", help="step number for training", type=int, default=None)
    parser.add_argument("--epoch", help="epoch number for training", type=int, default=1)

    return parser.parse_args()


def load_data(data_path, label_col):

    df = pd.read_csv(data_path)
    data, label = df, df.pop(label_col)

    return (data, label)


def get_dataset(data, labels, columns, batch_size, epoch):

    dataset = tf.data.Dataset.from_tensor_slices(({k: data[k].values for k in columns}, labels))
    dataset = dataset.repeat(epoch).batch(batch_size)

    # Return the dataset.
    return dataset


def get_feature_columns():
    """get feature columns for wide and deep model
    :returns: TODO

    """

    features = {}
    features["day_open"] = tf.feature_column.numeric_column("day_open")
    features["day_close"] = tf.feature_column.numeric_column("day_close")
    features["day_high"] = tf.feature_column.numeric_column("day_high")
    features["day_low"] = tf.feature_column.numeric_column("day_low")
    features["day_volume"] = tf.feature_column.numeric_column("day_volume")
    features["day_close_ema_short"] = tf.feature_column.numeric_column("day_close_ema_short")
    features["day_close_ema_long"] = tf.feature_column.numeric_column("day_close_ema_long")
    features["quick_ema_x"] = tf.feature_column.numeric_column("quick_ema_x")
    features["slow_ema_x"] = tf.feature_column.numeric_column("slow_ema_x")
    features["day_macd"] = tf.feature_column.numeric_column("day_macd")
    features["day_macd_signal"] = tf.feature_column.numeric_column("day_macd_signal")
    features["day_macd_bar"] = tf.feature_column.numeric_column("day_macd_bar")
    features["day_pulse"] = tf.feature_column.categorical_column_with_vocabulary_list(key='day_pulse', vocabulary_list = ["r", "g", "b"])
    features["day_pulse_signal"] = tf.feature_column.categorical_column_with_identity(key='day_pulse_signal', num_buckets=9)
    features["day_force_raw"] = tf.feature_column.numeric_column("day_force_raw")
    features["day_force_ema"] = tf.feature_column.numeric_column("day_force_ema")
    features["day_force_signal"] = tf.feature_column.categorical_column_with_identity(key='day_force_signal', num_buckets=3)
    features["deviation_signal"] = tf.feature_column.numeric_column("deviation_signal")
    features["day_last_min"] = tf.feature_column.numeric_column("day_last_min")
    features["day_last_min_bar"] = tf.feature_column.numeric_column("day_last_min_bar")
    features["day_tr"] = tf.feature_column.numeric_column("day_tr")
    features["day_atr"] = tf.feature_column.numeric_column("day_atr")
    features["day_atr1_high"] = tf.feature_column.numeric_column("day_atr1_high")
    features["day_atr1_low"] = tf.feature_column.numeric_column("day_atr1_low")
    features["day_atr2_high"] = tf.feature_column.numeric_column("day_atr2_high")
    features["day_atr2_low"] = tf.feature_column.numeric_column("day_atr2_low")
    features["day_rise_rate"] = tf.feature_column.numeric_column("day_rise_rate")
    features["target_day_open"] = tf.feature_column.numeric_column("target_day_open")
    features["target_day_close"] = tf.feature_column.numeric_column("target_day_close")
    features["target_day_rise_rate"] = tf.feature_column.numeric_column("target_day_rise_rate")
    features["day_win_signal"] = tf.feature_column.categorical_column_with_identity(key='day_win_signal', num_buckets=2)
    features["day_win_percentage"] = tf.feature_column.numeric_column("day_win_percentage")
    #features["will_profit"] = 
    features["day_low_ema_gap"] = tf.feature_column.numeric_column("day_low_ema_gap")
    features["day_low_ema_gap_mean"] = tf.feature_column.numeric_column("day_low_ema_gap_mean")
    features["day_close_ema_predict"] = tf.feature_column.numeric_column("day_close_ema_predict")
    features["stop_point_threshold"] = tf.feature_column.numeric_column("stop_point_threshold")
    features["enter_point_predict"] = tf.feature_column.numeric_column("enter_point_predict")
    features["stop_point_predict"] = tf.feature_column.numeric_column("stop_point_predict")
    features["enter_point"] = tf.feature_column.numeric_column("enter_point")
    features["stop_point"] = tf.feature_column.numeric_column("stop_point")
    #features["week_date"] = 
    features["week_open"] = tf.feature_column.numeric_column("week_open")
    features["week_close"] = tf.feature_column.numeric_column("week_close")
    features["week_high"] = tf.feature_column.numeric_column("week_high")
    features["week_low"] = tf.feature_column.numeric_column("week_low")
    features["week_volume"] = tf.feature_column.numeric_column("week_volume")
    features["week_close_ema_short"] = tf.feature_column.numeric_column("week_close_ema_short")
    features["week_close_ema_long"] = tf.feature_column.numeric_column("week_close_ema_long")
    features["quick_ema_y"] = tf.feature_column.numeric_column("quick_ema_y")
    features["slow_ema_y"] = tf.feature_column.numeric_column("slow_ema_y")
    features["week_macd"] = tf.feature_column.numeric_column("week_macd")
    features["week_macd_signal"] = tf.feature_column.numeric_column("week_macd_signal")
    features["week_macd_bar"] = tf.feature_column.numeric_column("week_macd_bar")
    features["week_pulse"] = tf.feature_column.categorical_column_with_identity(key='week_pulse', num_buckets=3)
    features["week_pulse_signal"] = tf.feature_column.categorical_column_with_identity(key='week_pulse_signal', num_buckets=9)
    features["week_tr"] = tf.feature_column.numeric_column("week_tr")
    features["week_atr"] = tf.feature_column.numeric_column("week_atr")
    features["week_atr1_high"] = tf.feature_column.numeric_column("week_atr1_high")
    features["week_atr1_low"] = tf.feature_column.numeric_column("week_atr1_low")
    features["week_atr2_high"] = tf.feature_column.numeric_column("week_atr2_high")
    features["week_atr2_low"] = tf.feature_column.numeric_column("week_atr2_low")
    features["week_close_ema_short_predict"] = tf.feature_column.numeric_column("week_close_ema_short_predict")
    features["week_close_ema_long_predict"] = tf.feature_column.numeric_column("week_close_ema_long_predict")
    features["target_point"] = tf.feature_column.numeric_column("target_point")
    features["model_signal"] = tf.feature_column.categorical_column_with_identity(key='model_signal', num_buckets=10)
    features["profit"] = tf.feature_column.numeric_column("profit")
    features["risk"] = tf.feature_column.numeric_column("risk")
    features["profit_risk_ratio"] = tf.feature_column.numeric_column("profit_risk_ratio")
    features["profit_ratio"] = tf.feature_column.numeric_column("profit_ratio")
    #features["stock_id"] = 

    wide_col_names = []
    wide_col_names.append("day_pulse")
    wide_col_names.append("day_pulse_signal")
    wide_col_names.append("week_pulse")
    wide_col_names.append("week_pulse_signal")
    wide_col_names.append("day_force_signal")
    wide_col_names.append("day_win_signal")
    wide_col_names.append("model_signal")
    
    wide_feature_cols = []
    for col_name in wide_col_names:
        wide_feature_cols.append(features[col_name])

    deep_col_names = []
    #deep_col_names.append("day_pulse")
    #deep_col_names.append("day_pulse_signal")
    #deep_col_names.append("week_pulse")
    #deep_col_names.append("week_pulse_signal")
    #deep_col_names.append("day_force_signal")
    #deep_col_names.append("day_win_signal")
    #deep_col_names.append("model_signal")
    deep_col_names.append("deviation_signal")
    deep_col_names.append("day_open")
    deep_col_names.append("day_close")
    deep_col_names.append("day_high")
    deep_col_names.append("day_low")
    deep_col_names.append("day_volume")
    deep_col_names.append("day_win_percentage")
    deep_col_names.append("week_open")
    deep_col_names.append("week_close")
    deep_col_names.append("week_high")
    deep_col_names.append("week_low")
    deep_col_names.append("week_volume")

    deep_feature_cols = []
    for col_name in deep_col_names:
        deep_feature_cols.append(features[col_name])

    #deep_feature_cols.append(tf.feature_column.indicator_column(tf.feature_column.categorical_column_with_identity(key='day_pulse', num_buckets=3)))

    deep_feature_cols.append(tf.feature_column.indicator_column(features["day_pulse"]))

    cols = set()

    for col_name in deep_col_names:
        cols.add(col_name)

    for col_name in wide_col_names:
        cols.add(col_name)

    return cols, wide_feature_cols, deep_feature_cols


def main():

    args = parse_args()

    # Refresh model every time
    if os.path.exists(args.model_dir):
        shutil.rmtree(args.model_dir)

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

    cols, wide_feature_cols, deep_feature_cols = get_feature_columns()

    estimator = DNNLinearCombinedClassifier(
        linear_feature_columns = None,
        dnn_feature_columns = deep_feature_cols,
        dnn_hidden_units = [10, 10, 10],
        config = RunConfig(
            model_dir = args.model_dir,
            save_summary_steps = 100,
            log_step_count_steps = 100
            )
    )

    print "training..."
    estimator.train(
        input_fn = lambda: get_dataset(train_x, train_y, cols, args.batch_size, args.epoch),
        steps = args.steps,
        hooks = [MySessionHook()]
    )

    print "testing on training set..."
    metrics = estimator.evaluate(lambda: get_dataset(train_x, train_y, cols, args.batch_size, 1), steps = args.steps)

    print "test_on_training_set_metrics:"
    print metrics

    print "testing..."
    metrics = estimator.evaluate(lambda: get_dataset(test_x, test_y, cols, args.batch_size, 1), steps = args.steps)

    print "test__metrics:"
    print metrics

    return


if __name__ == "__main__":
    main()


