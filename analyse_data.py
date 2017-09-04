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
import matplotlib.pyplot as plt

pd.set_option("display.width", 300)

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

    logging.basicConfig(level=log_level, filename="%s/%s.%s" % (log_dir, __file__, datetime.now().strftime("%Y%m%d")), filemode='a', format='%(asctime)s [%(levelname)s] [%(filename)s] [%(funcName)s] [%(lineno)d] %(message)s')

    return conf_obj


def print_help():
    print "USAGE: python %s CONF_FILE" % (__file__)
    return


def load_kline_data(data_dir):

    result = pd.DataFrame()

    kline_map = {}

    for file_name in os.listdir(data_dir)[500:501]:

        stock_id = file_name

        tmp = pd.read_csv(data_dir + "/" + file_name, parse_dates=["date"])

        kline_map[stock_id] = tmp

    return kline_map


def main():

    if len(sys.argv) >= 2:
        date = datetime.strptime(sys.argv[2], "%Y%m%d")
    else:
        date = datetime.now()

    conf_file = "./conf/config.json"

    # Init
    conf_obj = init(conf_file)
    logging.info("init finish")

    day_kline_path = "%s/kline/day/%s" % (conf_obj["data_dir"], date.strftime("%Y%m%d"))
    week_kline_path = "%s/kline/week/%s" % (conf_obj["data_dir"], date.strftime("%Y%m%d"))

    day_kline = load_kline_data(day_kline_path)
    logging.info("init day kline finish")

    week_kline = load_kline_data(week_kline_path)
    logging.info("init week kline finish")

    fe = FeatureExtractor()
    sg = SignalGenerator()

    # calculate features for day kline
    i = 0
    for stock_id in day_kline:
        i += 1
        if i % 100 == 0:
            logging.info("analysing day k line (%d/%d)" % (i, len(day_kline)))

        # add MA
        #day_kline[stock_id] = fe.ma(day_kline[stock_id], "close", "close_ma_11", 11)

        # add EMA
        day_kline[stock_id] = fe.ema(day_kline[stock_id], "close", "close_ema_11", 11)
        day_kline[stock_id] = fe.ema(day_kline[stock_id], "close", "close_ema_22", 22)

        # add MACD
        #day_kline[stock_id] = fe.macd(day_kline[stock_id], "close", "macd", "macd_signal", "macd_bar", 12, 26, 9)

        # add pulse
        #day_kline[stock_id] = fe.pulse(day_kline[stock_id], "close_ema_11", "macd_bar", "pulse")

        # add force
        day_kline[stock_id] = fe.force_index(day_kline[stock_id], "close", "volume", "force_raw", "force_ema", 2)

        # add force signal
        day_kline[stock_id] = sg.force_signal(day_kline[stock_id], "force_ema", 20, "force_signal")

    i = 0
    for stock_id in week_kline:
        i += 1
        if i % 100 == 0:
            logging.info("analysing week k line (%d/%d)" % (i, len(week_kline)))

        # add EMA
        week_kline[stock_id] = fe.ema(week_kline[stock_id], "close", "close_ema_13", 13)

        # add MACD
        week_kline[stock_id] = fe.macd(week_kline[stock_id], "close", "macd", "macd_signal", "macd_bar", 12, 26, 9)

        # add pulse
        week_kline[stock_id] = fe.pulse(week_kline[stock_id], "close_ema_13", "macd_bar", "pulse")

        # add pulse signal
        week_kline[stock_id] = sg.pulse_signal(week_kline[stock_id], "pulse", "pulse_signal")

    print day_kline
    print week_kline

    return


if __name__ == "__main__":
    main()

