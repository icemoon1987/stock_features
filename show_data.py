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


def df_to_js(df, variable_name):

    result = "%s = [\n" % (variable_name)

    for item in list(df.values):
        result += "[%s],\n" % (",".join(["\""+str(a)+"\"" for a in item]))

    result += "];\n"

    return result


def main():

    if len(sys.argv) >= 3:
        stock_id = sys.argv[1]
        date = datetime.strptime(sys.argv[2], "%Y%m%d")
    else:
        stock_id = sys.argv[1]
        date = datetime.strptime(datetime.now().strftime("%Y%m%d"), "%Y%m%d")

    conf_file = "./conf/config.json"

    # Init
    conf_obj = init(conf_file)
    logging.info("init finish")

    single_result_path = "%s/single_result/%s" % (conf_obj["result_dir"], date.strftime("%Y%m%d"))
    single_result = pd.read_csv("%s/%s" % (single_result_path, stock_id))

    print single_result.columns

    #print single_result.ix[:, ["day_date", "model_signal", "day_close", "day_low_ema_gap_mean", "day_close_ema_predict", "enter_point", "stop_point", "target_point", "profit", "risk", "profit_risk_ratio", "profit_ratio", "week_close_ema_short", "week_close_ema_long"]]
    print single_result.ix[:, ["day_date", "week_pulse", "day_force_ema", "model_signal", "day_close", "enter_point", "stop_point", "target_point", "profit", "risk", "profit_risk_ratio", "profit_ratio", "week_close_ema_short", "week_close_ema_long", "day_atr1_high", "day_atr1_low"]]

    f = open("./data.js", "w")

    day_data = single_result.ix[:, ["day_date", "day_open", "day_close", "day_low", "day_high", "week_pulse", "week_pulse_signal", "enter_point", "target_point", "stop_point", "day_force_raw", "day_force_ema", "day_force_signal", "model_signal"]]
    day_data_str = df_to_js(day_data, "day_data")

    f.write(day_data_str)
    f.write("\n")

    f.close()

    return


if __name__ == "__main__":
    main()


