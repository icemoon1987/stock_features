#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################
#
# File Name:  main.py
#
# Function:   
#
# Usage:  
#
# Input:  
#
# Output:	
#
# Author: wenhai.pan
#
# Create Time:    2017-09-01 15:45:04
#
######################################################

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import time
import json
import shutil
import logging
import pandas as pd
from datetime import datetime, timedelta
from processor.feature_extractor import FeatureExtractor
from processor.signal_generator import SignalGenerator
from model.three_screen import ThreeScreen
import matplotlib.pyplot as plt

pd.set_option("display.width", 300)
pd.set_option("display.max_rows", None)

def init(conf_file):
    """
    Initilization process
    
    args:
        conf_file   configration file

    return: none
    """

    with open(conf_file, "r") as f:
        conf_obj = json.loads(f.read())

    # init directories
    log_dir = conf_obj["log_dir"]
    data_dir = conf_obj["data_dir"]
    result_dir = conf_obj["result_dir"]

    if conf_obj["clear_data_every_time"] and os.path.exists(data_dir):
        shutil.rmtree(data_dir)

    if conf_obj["clear_result_every_time"] and os.path.exists(result_dir):
        shutil.rmtree(result_dir)

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

    if not os.path.exists(result_dir):
        os.mkdir(result_dir)

    # init logging
    if conf_obj.get("debug_mode", False):
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(level=log_level, filename="%s/%s.%s" % (log_dir, "log", datetime.now().strftime("%Y%m%d")), filemode='a', format='%(asctime)s [%(levelname)s] [%(filename)s] [%(funcName)s] [%(lineno)d] %(message)s')

    return conf_obj


def print_help():
    print "USAGE: python %s CONF_FILE" % (__file__)
    return


def load_kline_data(data_dir, prefix):

    result = pd.DataFrame()

    kline_map = {}

    for file_name in os.listdir(data_dir):

        stock_id = file_name

        tmp = pd.read_csv(data_dir + "/" + file_name, parse_dates=["date"])

        rename_map = {}

        for column in tmp.columns:
            rename_map[column] = prefix + "_" + column

        tmp.rename(columns=rename_map, inplace=True)

        kline_map[stock_id] = tmp

    return kline_map


def main():

    if len(sys.argv) >= 2:
        date = datetime.strptime(sys.argv[1], "%Y%m%d")
    else:
        date = datetime.strptime(datetime.now().strftime("%Y%m%d"), "%Y%m%d")

    conf_file = "./conf/config.json"

    # Init
    conf_obj = init(conf_file)
    logging.info("init finish")

    merge_result_path = "%s/merge_result" % (conf_obj["result_dir"])
    merge_result = pd.read_csv( "%s/%s" % (merge_result_path, date.strftime("%Y%m%d")) )


    # Filter

    #filter_result = merge_result.where(merge_result["model_signal"] > 0).where(merge_result["stop_point"] < merge_result["stop_point_threshold"]).where(merge_result["profit_risk_ratio"] > 1.0).dropna()
    filter_result = merge_result.where(merge_result["model_signal"] > 0).dropna()
    #filter_result = merge_result.where(merge_result["model_signal"] == 3).dropna()
    #filter_result = filter_result.where(merge_result["stop_point"] < merge_result["stop_point_threshold"]).dropna()
    filter_result = filter_result.where(merge_result["profit_risk_ratio"] > 2.0).dropna()
    filter_result = filter_result.where(merge_result["profit_ratio"] > 0.05).dropna()

    filter_result = filter_result.sort_values(by = ["model_signal", "profit_risk_ratio"], ascending=False)

    #filter_result = filter_result.ix[:, ["day_date", "week_pulse_signal", "day_force_signal", "model_signal", "stop_point_threshold", "stop_point_predict", "stop_point", "day_close", "enter_point_predict", "enter_point", "target_point", "profit", "risk", "profit_risk_ratio", "profit_ratio", "stock_id"]]
    filter_result = filter_result.ix[:, ["day_date", "model_signal", "day_close", "enter_point", "stop_point", "target_point", "profit", "risk", "profit_risk_ratio", "profit_ratio", "stock_id"]]

    print filter_result

    filter_result_path = "%s/filter_result" % (conf_obj["result_dir"])

    if not os.path.exists(filter_result_path):
        logging.info("%s does not exist." % (filter_result_path))
        os.makedirs(filter_result_path)

    filter_result.to_csv("%s/%s" % (filter_result_path, date.strftime("%Y%m%d")), index=False)

    return


if __name__ == "__main__":
    main()

