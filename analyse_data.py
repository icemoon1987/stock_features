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
import traceback  
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

    day_kline_path = "%s/kline/day/%s" % (conf_obj["data_dir"], date.strftime("%Y%m%d"))
    week_kline_path = "%s/kline/week/%s" % (conf_obj["data_dir"], date.strftime("%Y%m%d"))

    day_kline = load_kline_data(day_kline_path, "day")
    logging.info("init day kline finish")

    week_kline = load_kline_data(week_kline_path, "week")
    logging.info("init week kline finish")

    fe = FeatureExtractor()
    sg = SignalGenerator()
    m = ThreeScreen()

    # calculate features for day kline
    i = 0
    for stock_id in day_kline:
        i += 1
        if i % 100 == 0 or i == len(day_kline):
            logging.info("analysing day k line (%d/%d)" % (i, len(day_kline)))

        # add MA
        #day_kline[stock_id] = fe.ma(day_kline[stock_id], "close", "close_ma_11", 11)

        # add EMA
        day_kline[stock_id] = fe.ema(day_kline[stock_id], "day_close", "day_close_ema_short", 11)
        day_kline[stock_id] = fe.ema(day_kline[stock_id], "day_close", "day_close_ema_long", 22)

        # add MACD
        #day_kline[stock_id] = fe.macd(day_kline[stock_id], "close", "macd", "macd_signal", "macd_bar", 12, 26, 9)

        # add Pulse
        #day_kline[stock_id] = fe.pulse(day_kline[stock_id], "close_ema_11", "macd_bar", "pulse")

        # add Force
        day_kline[stock_id] = fe.force_index(day_kline[stock_id], "day_close", "day_volume", "day_force_raw", "day_force_ema", 2)

        # add Force signal
        day_kline[stock_id] = sg.force_signal(day_kline[stock_id], "day_force_ema", 20, "day_force_signal")

    i = 0
    for stock_id in week_kline:
        i += 1
        if i % 100 == 0 or i == len(week_kline):
            logging.info("analysing week k line (%d/%d)" % (i, len(week_kline)))

        # add EMA
        week_kline[stock_id] = fe.ema(week_kline[stock_id], "week_close", "week_close_ema_short", 13)
        week_kline[stock_id] = fe.ema(week_kline[stock_id], "week_close", "week_close_ema_long", 26)

        # add MACD
        week_kline[stock_id] = fe.macd(week_kline[stock_id], "week_close", "week_macd", "week_macd_signal", "week_macd_bar", 12, 26, 9)

        # add Pulse
        week_kline[stock_id] = fe.pulse(week_kline[stock_id], "week_close_ema_short", "week_macd_bar", "week_pulse")

        # add Pulse signal
        week_kline[stock_id] = sg.pulse_signal(week_kline[stock_id], "week_pulse", "week_pulse_signal")

    #print day_kline
    #print week_kline

    single_result = {}

    single_result_path = "%s/single_result/%s" % (conf_obj["result_dir"], date.strftime("%Y%m%d"))

    if not os.path.exists(single_result_path):
        logging.info("%s does not exist." % (single_result_path))
        os.makedirs(single_result_path)

    i = 0
    for stock_id in day_kline:
        i += 1
        if i % 100 == 0 or i == len(day_kline):
            logging.info("modeling (%d/%d)" % (i, len(day_kline)))

        try:
            if day_kline[stock_id].shape[0] == 0:
                continue
            elif stock_id not in week_kline:
                continue
            elif week_kline[stock_id].shape[0] == 0:
                continue
            else:
                single_result[stock_id] = m.signal(day_kline[stock_id], week_kline[stock_id])

            single_result[stock_id].to_csv("%s/%s" % (single_result_path, stock_id), index=False)

        except Exception, ex:
            print str(ex)
            #print week_kline[stock_id]
            print stock_id
            traceback.print_exc()

    merge_result_list = []
    
    i = 0
    for stock_id in single_result:
    	i += 1
        if i % 100 == 0 or i == len(single_result):
            logging.info("merging (%d/%d)" % (i, len(single_result)))

        tmp = single_result[stock_id].where(single_result[stock_id]["day_date"] == date).dropna()
        tmp["stock_id"] = stock_id

        if tmp.shape[0] > 0:
            merge_result_list.append(tmp)

    merge_result = pd.concat(merge_result_list)

    merge_result_path = "%s/merge_result" % (conf_obj["result_dir"])

    if not os.path.exists(merge_result_path):
        logging.info("%s does not exist." % (merge_result_path))
        os.makedirs(merge_result_path)

    merge_result.to_csv("%s/%s" % (merge_result_path, date.strftime("%Y%m%d")), index=False)

    return


if __name__ == "__main__":
    main()

