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

pd.set_option("display.width", 300)
pd.set_option("display.max_rows", None)

def parse_args():
    """parse command line args

    :returns: argparse object

    """

    parser = argparse.ArgumentParser(description="generate data for Machine Learning models")
    parser.add_argument("--date", help="target date of the data", type=str, default=datetime.now().strftime("%Y%m%d"))
    parser.add_argument("--train_day", help="number of days of training data", type=int, default=1000)
    parser.add_argument("--test_day", help="number of days of test data", type=int, default=7)
    parser.add_argument("--src", help="source data path", type=str, default="./result/single_result")
    parser.add_argument("--dst", help="result data path", type=str, default="./result/ml_data")
    parser.add_argument("--stock", help="stock id for generating data", type=str, default="all")

    return parser.parse_args()


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


def main():

    args = parse_args()

    single_result_path = "%s/%s" % (args.src, args.date)
    single_result = load_single_result(single_result_path, args.stock)

    test_df_list = []
    train_df_list = []

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

        test_df["stock_id"] = stock_id
        train_df["stock_id"] = stock_id

        test_df_list.append(test_df)
        train_df_list.append(train_df)

    result_path = "%s/%s/%s" % ( args.dst, args.date, args.stock )

    if os.path.exists(result_path):
        shutil.rmtree(result_path)

    if not os.path.exists(result_path):
        os.makedirs(result_path)

    merge_test_df = pd.concat(test_df_list)
    merge_train_df = pd.concat(train_df_list)

    merge_test_df.to_csv("%s/%s" % (result_path, "test.csv"), index=False)
    merge_train_df.to_csv("%s/%s" % (result_path, "train.csv"), index=False)

    #print "merge_test_df:"
    #print merge_test_df[0:10]

    #print "merge_train_df:"
    #print merge_train_df[0:10]

    return


if __name__ == "__main__":
    main()


