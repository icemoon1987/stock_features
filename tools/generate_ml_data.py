#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""  TODO: module description

Usage:  

Input:  

Output:  

Author: wenhai.pan

Create Time:    2019-04-08 20:39:43

"""

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import time
import shutil
import argparse
import progressbar
import pandas as pd
from datetime import datetime, timedelta
import tensorflow as tf


pd.set_option("display.width", 300)
pd.set_option("display.max_rows", None)

def parse_args():
    """parse command line args

    :returns: argparse object

    """

    parser = argparse.ArgumentParser(description="generate data for Machine Learning models")
    parser.add_argument("--date", help="target date of the data", type=str, default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--train_day", help="number of days of training data", type=int, default=1000)
    parser.add_argument("--test_day", help="number of days of test data", type=int, default=30)
    parser.add_argument("--src", help="source data path", type=str, default="./result/single_result")
    parser.add_argument("--dst", help="result data path", type=str, default="./result/ml_data")
    parser.add_argument("--stock", help="stock id for generating data", type=str, default="all")

    return parser.parse_args()

def _bytes_feature(value):
    """Returns a bytes_list from a string / byte."""
    if isinstance(value, type(tf.constant(0))):
        value = value.numpy() # BytesList won't unpack a string from an EagerTensor.
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def _float_feature(value):
    """Returns a float_list from a float / double."""
    return tf.train.Feature(float_list=tf.train.FloatList(value=[value]))

def _int64_feature(value):
    """Returns an int64_list from a bool / enum / int / uint."""
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))


def load_single_result(result_dir, stock_id):

    result = pd.DataFrame()

    result_map = {}

    if stock_id == "all":
        file_list = os.listdir(result_dir)
    else:
        file_list = [stock_id]


    for file_name in file_list:
        stock_id = file_name
        tmp = pd.read_csv(result_dir + "/" + file_name, parse_dates=["day_date"])

        result_map[stock_id] = tmp

    return result_map 


def create_tf_example(data):

    feature = {
        "day_date": _bytes_feature(data["day_date"].strftime("%Y%m%d")),
        "day_open": _float_feature(data["day_open"]),
        "day_close": _float_feature(data["day_close"]),
        "day_high": _float_feature(data["day_high"]),
        "day_low": _float_feature(data["day_low"]),
        "day_volume": _float_feature(data["day_volume"]),
        "day_close_ema_short": _float_feature(data["day_close_ema_short"]),
        "day_close_ema_long": _float_feature(data["day_close_ema_long"]),
        "quick_ema_x": _float_feature(data["quick_ema_x"]),
        "slow_ema_x": _float_feature(data["slow_ema_x"]),
        "day_macd": _float_feature(data["day_macd"]),
        "day_macd_signal": _float_feature(data["day_macd_signal"]),
        "day_macd_bar": _float_feature(data["day_macd_bar"]),
        "day_pulse": _bytes_feature(data["day_pulse"]),
        "day_pulse_signal": _int64_feature(int(data["day_pulse_signal"])),
        "day_force_raw": _float_feature(data["day_force_raw"]),
        "day_force_ema": _float_feature(data["day_force_ema"]),
        "day_force_signal": _int64_feature(int(data["day_force_signal"])),
        "deviation_signal": _int64_feature(int(data["deviation_signal"])),
        "day_last_min": _float_feature(data["day_last_min"]),
        "day_last_min_bar": _float_feature(data["day_last_min_bar"]),
        "day_tr": _float_feature(data["day_tr"]),
        "day_atr": _float_feature(data["day_atr"]),
        "day_atr1_high": _float_feature(data["day_atr1_high"]),
        "day_atr1_low": _float_feature(data["day_atr1_low"]),
        "day_atr2_high": _float_feature(data["day_atr2_high"]),
        "day_atr2_low": _float_feature(data["day_atr2_low"]),
        "day_rise_rate": _float_feature(data["day_rise_rate"]),
        "target_day_open": _float_feature(data["target_day_open"]),
        "target_day_close": _float_feature(data["target_day_close"]),
        "target_day_rise_rate": _float_feature(data["target_day_rise_rate"]),
        "day_win_signal": _int64_feature(int(data["day_win_signal"])),
        "day_win_percentage": _float_feature(data["day_win_percentage"]),
        "will_profit": _int64_feature(int(data["will_profit"])),
        "day_low_ema_gap": _float_feature(data["day_low_ema_gap"]),
        "day_low_ema_gap_mean": _float_feature(data["day_low_ema_gap_mean"]),
        "day_close_ema_predict": _float_feature(data["day_close_ema_predict"]),
        "stop_point_threshold": _float_feature(data["stop_point_threshold"]),
        "enter_point_predict": _float_feature(data["enter_point_predict"]),
        "stop_point_predict": _float_feature(data["stop_point_predict"]),
        "enter_point": _float_feature(data["enter_point"]),
        "stop_point": _float_feature(data["stop_point"]),
        "week_date": _bytes_feature(data["week_date"]),
        "week_open": _float_feature(data["week_open"]),
        "week_close": _float_feature(data["week_close"]),
        "week_high": _float_feature(data["week_high"]),
        "week_low": _float_feature(data["week_low"]),
        "week_volume": _float_feature(data["week_volume"]),
        "week_close_ema_short": _float_feature(data["week_close_ema_short"]),
        "week_close_ema_long": _float_feature(data["week_close_ema_long"]),
        "quick_ema_y": _float_feature(data["quick_ema_y"]),
        "slow_ema_y": _float_feature(data["slow_ema_y"]),
        "week_macd": _float_feature(data["week_macd"]),
        "week_macd_signal": _float_feature(data["week_macd_signal"]),
        "week_macd_bar": _float_feature(data["week_macd_bar"]),
        "week_pulse": _bytes_feature(data["week_pulse"]),
        "week_pulse_signal": _int64_feature(int(data["week_pulse_signal"])),
        "week_tr": _float_feature(data["week_tr"]),
        "week_atr": _float_feature(data["week_atr"]),
        "week_atr1_high": _float_feature(data["week_atr1_high"]),
        "week_atr1_low": _float_feature(data["week_atr1_low"]),
        "week_atr2_high": _float_feature(data["week_atr2_high"]),
        "week_atr2_low": _float_feature(data["week_atr2_low"]),
        "week_close_ema_short_predict": _float_feature(data["week_close_ema_short_predict"]),
        "week_close_ema_long_predict": _float_feature(data["week_close_ema_long_predict"]),
        "target_point": _float_feature(data["target_point"]),
        "model_signal": _int64_feature(int(data["model_signal"])),
        "profit": _float_feature(data["profit"]),
        "risk": _float_feature(data["risk"]),
        "profit_risk_ratio": _float_feature(data["profit_risk_ratio"]),
        "profit_ratio": _float_feature(data["profit_ratio"]),
        "stock_id": _bytes_feature(data["stock_id"])
    }

    tf_example = tf.train.Example(features = tf.train.Features(feature = feature))

    return tf_example


def store_tf_records(data_df, file_path):

    keys = []
    for item in data_df:
        keys.append(item)

    with tf.python_io.TFRecordWriter(file_path) as writer:
        for item in data_df.values:
            data = dict(zip(keys, item))
            example = create_tf_example(data)

            writer.write(example.SerializeToString())

    return


def main():

    args = parse_args()

    single_result_path = "%s/%s" % (args.src, args.date)
    single_result = load_single_result(single_result_path, args.stock)

    test_df_list = []
    train_df_list = []
    all_df_list = []

    print "merging, total num: %d" % (len(single_result))
    pbar = progressbar.ProgressBar(max_value=len(single_result))

    i = 0
    for stock_id in single_result:
        pbar.update(i)
    	i += 1

        test_df = single_result[stock_id][0 - args.test_day :].copy()
        train_df = single_result[stock_id][0 - args.test_day - args.train_day : 0 - args.test_day].copy()

        if test_df.shape[0] == 0 or train_df.shape[1] == 0:
            continue

        test_df["stock_id"] = "stock_" + stock_id
        train_df["stock_id"] = "stock_" + stock_id
        single_result[stock_id]["stock_id"] = "stock_" + stock_id

        test_df_list.append(test_df)
        train_df_list.append(train_df)
        all_df_list.append(single_result[stock_id])

    result_path = "%s/%s/%s" % ( args.dst, args.date, args.stock )

    if os.path.exists(result_path):
        shutil.rmtree(result_path)

    if not os.path.exists(result_path):
        os.makedirs(result_path)

    merge_test_df = pd.concat(test_df_list)
    merge_train_df = pd.concat(train_df_list)
    merge_all_df = pd.concat(all_df_list)

    # sort data by day_date, will split the data in future use, so need to sort here.
    merge_all_df.sort_values("day_date", inplace=True)

    merge_test_df.to_csv("%s/%s" % (result_path, "test.csv"), index=False)
    merge_train_df.to_csv("%s/%s" % (result_path, "train.csv"), index=False)
    merge_all_df.to_csv("%s/%s" % (result_path, "all.csv"), index=False)

    print "storing tf records files..."
    #store_tf_records(merge_test_df, "%s/%s" % (result_path, "test.tfrecord"))
    #store_tf_records(merge_train_df, "%s/%s" % (result_path, "train.tfrecord"))

    #print "merge_test_df:"
    #print merge_test_df[0:10]

    #print "merge_train_df:"
    #print merge_train_df[0:10]

    return


if __name__ == "__main__":
    main()


