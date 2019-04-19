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

    cols = []
    #cols.append("day_date")
    cols.append("day_open")
    cols.append("day_close")
    cols.append("day_high")
    cols.append("day_low")
    cols.append("day_volume")
    cols.append("day_close_ema_short")
    cols.append("day_close_ema_long")
    cols.append("quick_ema_x")
    cols.append("slow_ema_x")
    cols.append("day_macd")
    cols.append("day_macd_signal")
    cols.append("day_macd_bar")
    cols.append("day_pulse")
    cols.append("day_pulse_signal")
    cols.append("day_force_raw")
    cols.append("day_force_ema")
    cols.append("day_force_signal")
    cols.append("deviation_signal")
    cols.append("day_last_min")
    cols.append("day_last_min_bar")
    cols.append("day_tr")
    cols.append("day_atr")
    cols.append("day_atr1_high")
    cols.append("day_atr1_low")
    cols.append("day_atr2_high")
    cols.append("day_atr2_low")
    cols.append("day_rise_rate")
    cols.append("target_day_open")
    cols.append("target_day_close")
    cols.append("target_day_rise_rate")
    cols.append("day_win_signal")
    cols.append("day_win_percentage")
    #cols.append("will_profit")
    cols.append("day_low_ema_gap")
    cols.append("day_low_ema_gap_mean")
    cols.append("day_close_ema_predict")
    cols.append("stop_point_threshold")
    cols.append("enter_point_predict")
    cols.append("stop_point_predict")
    cols.append("enter_point")
    cols.append("stop_point")
    #cols.append("week_date")
    cols.append("week_open")
    cols.append("week_close")
    cols.append("week_high")
    cols.append("week_low")
    cols.append("week_volume")
    cols.append("week_close_ema_short")
    cols.append("week_close_ema_long")
    cols.append("quick_ema_y")
    cols.append("slow_ema_y")
    cols.append("week_macd")
    cols.append("week_macd_signal")
    cols.append("week_macd_bar")
    cols.append("week_pulse")
    cols.append("week_pulse_signal")
    cols.append("week_tr")
    cols.append("week_atr")
    cols.append("week_atr1_high")
    cols.append("week_atr1_low")
    cols.append("week_atr2_high")
    cols.append("week_atr2_low")
    cols.append("week_close_ema_short_predict")
    cols.append("week_close_ema_long_predict")
    cols.append("target_point")
    cols.append("model_signal")
    cols.append("profit")
    cols.append("risk")
    cols.append("profit_risk_ratio")
    cols.append("profit_ratio")
    #cols.append("stock_id")

    wide_feature_cols = []
    wide_feature_cols.append(tf.feature_column.categorical_column_with_identity(key='day_pulse', num_buckets=3))
    wide_feature_cols.append(tf.feature_column.categorical_column_with_identity(key='day_pulse_signal', num_buckets=9))
    wide_feature_cols.append(tf.feature_column.categorical_column_with_identity(key='week_pulse', num_buckets=3))
    wide_feature_cols.append(tf.feature_column.categorical_column_with_identity(key='week_pulse_signal', num_buckets=9))
    wide_feature_cols.append(tf.feature_column.categorical_column_with_identity(key='day_force_signal', num_buckets=3))
    wide_feature_cols.append(tf.feature_column.categorical_column_with_identity(key='day_win_signal', num_buckets=2))
    wide_feature_cols.append(tf.feature_column.categorical_column_with_identity(key='model_signal', num_buckets=10))

    deep_feature_cols = []
    deep_feature_cols.append(tf.feature_column.numeric_column("day_open"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_close"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_high"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_low"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_volume"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_close_ema_short"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_close_ema_long"))
    deep_feature_cols.append(tf.feature_column.numeric_column("quick_ema_x"))
    deep_feature_cols.append(tf.feature_column.numeric_column("slow_ema_x"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_macd"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_macd_signal"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_macd_bar"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_force_raw"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_force_signal"))
    deep_feature_cols.append(tf.feature_column.numeric_column("deviation_signal"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_last_min"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_last_min_bar"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_tr"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_atr"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_atr1_high"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_atr1_low"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_atr2_high"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_atr2_low"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_rise_rate"))
    deep_feature_cols.append(tf.feature_column.numeric_column("target_day_open"))
    deep_feature_cols.append(tf.feature_column.numeric_column("target_day_close"))
    deep_feature_cols.append(tf.feature_column.numeric_column("target_day_rise_rate"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_win_percentage"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_low_ema_gap"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_low_ema_gap_mean"))
    deep_feature_cols.append(tf.feature_column.numeric_column("day_close_ema_predict"))
    deep_feature_cols.append(tf.feature_column.numeric_column("stop_point_threshold"))
    deep_feature_cols.append(tf.feature_column.numeric_column("enter_point_predict"))
    deep_feature_cols.append(tf.feature_column.numeric_column("stop_point_predict"))
    deep_feature_cols.append(tf.feature_column.numeric_column("enter_point"))
    deep_feature_cols.append(tf.feature_column.numeric_column("stop_point"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_open"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_close"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_high"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_low"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_volume"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_close_ema_short"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_close_ema_long"))
    deep_feature_cols.append(tf.feature_column.numeric_column("quick_ema_y"))
    deep_feature_cols.append(tf.feature_column.numeric_column("slow_ema_y"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_macd"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_macd_signal"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_macd_bar"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_tr"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_atr"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_atr1_high"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_atr1_low"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_atr2_high"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_atr2_low"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_close_ema_short_predict"))
    deep_feature_cols.append(tf.feature_column.numeric_column("week_close_ema_long_predict"))
    deep_feature_cols.append(tf.feature_column.numeric_column("target_point"))
    deep_feature_cols.append(tf.feature_column.numeric_column("profit"))
    deep_feature_cols.append(tf.feature_column.numeric_column("risk"))
    deep_feature_cols.append(tf.feature_column.numeric_column("profit_risk_ratio"))
    deep_feature_cols.append(tf.feature_column.numeric_column("profit_ratio"))

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


