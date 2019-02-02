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
sys.path.append(".")
sys.path.append("..")
import os
import time
import json
import shutil
import logging
import progressbar
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


def load_kline_data(data_dir, prefix, stock_id):

    result = pd.DataFrame()

    kline_map = {}

    if stock_id != None:
        file_list = [stock_id, "sh"]
    else:
        file_list = os.listdir(data_dir)


    for file_name in file_list:

        stock_id = file_name
        tmp = pd.read_csv(data_dir + "/" + file_name, parse_dates=["date"])
        rename_map = {}

        for column in tmp.columns:
            rename_map[column] = prefix + "_" + column

        tmp.rename(columns=rename_map, inplace=True)

        kline_map[stock_id] = tmp

    return kline_map


def main():

    if len(sys.argv) == 2:

        stock_id = sys.argv[1]
        if stock_id == "all":
            stock_id = None
        target_date = datetime.strptime(datetime.now().strftime("%Y%m%d"), "%Y%m%d")

    elif len(sys.argv) == 3:

        stock_id = sys.argv[1]
        if stock_id == "all":
            stock_id = None
        target_date = datetime.strptime(sys.argv[2], "%Y%m%d")

    else:
        stock_id = None
        target_date = datetime.strptime(datetime.now().strftime("%Y%m%d"), "%Y%m%d")

    print len(sys.argv)
    print stock_id
    print target_date

    conf_file = "./conf/config.json"

    # Init
    conf_obj = init(conf_file)
    logging.info("init finish")

    day_kline_path = "%s/kline/day/%s" % (conf_obj["data_dir"], target_date.strftime("%Y%m%d"))
    week_kline_path = "%s/kline/week/%s" % (conf_obj["data_dir"], target_date.strftime("%Y%m%d"))

    print day_kline_path
    print week_kline_path

    day_kline = load_kline_data(day_kline_path, "day", stock_id)
    logging.info("init day kline finish")

    week_kline = load_kline_data(week_kline_path, "week", stock_id)
    logging.info("init week kline finish")

    fe = FeatureExtractor()
    sg = SignalGenerator()
    m = ThreeScreen()

    # Calculate features for day kline

    print "analysing day k line, total num: %d" % (len(day_kline))
    pbar = progressbar.ProgressBar(max_value=len(day_kline))

    i = 0
    for stock_id in day_kline:

        pbar.update(i)

        i += 1
        if i % 100 == 0 or i == len(day_kline):
            logging.info("analysing day k line (%d/%d)" % (i, len(day_kline)))

        # add EMA
        day_kline[stock_id] = fe.ema(day_kline[stock_id], "day_close", "day_close_ema_short", 11)
        day_kline[stock_id] = fe.ema(day_kline[stock_id], "day_close", "day_close_ema_long", 22)

        # add MACD
        day_kline[stock_id] = fe.macd(day_kline[stock_id], "day_close", "day_macd", "day_macd_signal", "day_macd_bar", 12, 26, 9)

        # add Pulse
        day_kline[stock_id] = fe.pulse(day_kline[stock_id], "day_close_ema_short", "day_macd_bar", "day_pulse")

        # add Pulse signal
        day_kline[stock_id] = sg.pulse_signal(day_kline[stock_id], "day_pulse", "day_pulse_signal")

        # add Force
        day_kline[stock_id] = fe.force_index(day_kline[stock_id], "day_close", "day_volume", "day_force_raw", "day_force_ema", 2)

        # add Force signal
        day_kline[stock_id] = sg.force_signal(day_kline[stock_id], "day_force_ema", 20, "day_force_signal")

        # add Deviation signal
        day_kline[stock_id] = sg.deviation_signal(day_kline[stock_id], "day_close", "day_macd_bar", 60, "deviation_signal")

        # add tr and atr
        day_kline[stock_id] = fe.atr(day_kline[stock_id], "day_close", "day_high", "day_low", 13, "day_tr", "day_atr")

        # add day_increase_rate
        day_kline[stock_id] = fe.rise_rate(day_kline[stock_id], "day_open", "day_close", "day_rise_rate")

        # merge shangzheng index open, close and increase_rate
        day_kline[stock_id] = fe.merge_target(day_kline[stock_id], day_kline["sh"], "day_date", "day_open", "day_close", "target_day_open", "target_day_close")
        day_kline[stock_id] = fe.rise_rate(day_kline[stock_id], "target_day_open", "target_day_close", "target_day_rise_rate")

        day_kline[stock_id] = sg.win_signal(day_kline[stock_id], "day_rise_rate", "target_day_rise_rate", "day_win_signal")

        day_kline[stock_id] = sg.win_percentage(day_kline[stock_id], "day_win_signal", 180, "day_win_percentage")

        #print day_kline[stock_id].ix[:, ["day_date", "day_open", "day_close", "day_rise_rate", "target_day_open", "target_day_close", "target_day_rise_rate", "day_win_signal", "day_win_percentage"]]



    # Calculate features for week kline

    print "analysing week k line, total num: %d" % (len(week_kline))
    pbar = progressbar.ProgressBar(max_value=len(week_kline))

    i = 0
    for stock_id in week_kline:

        pbar.update(i)

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

        # add tr and atr
        week_kline[stock_id] = fe.atr(week_kline[stock_id], "week_close", "week_high", "week_low", 13, "week_tr", "week_atr")

    #print day_kline
    #print week_kline

    single_result = {}

    single_result_path = "%s/single_result/%s" % (conf_obj["result_dir"], target_date.strftime("%Y%m%d"))

    if not os.path.exists(single_result_path):
        logging.info("%s does not exist." % (single_result_path))
        os.makedirs(single_result_path)


    print "modeling, total num: %d" % (len(day_kline))
    pbar = progressbar.ProgressBar(max_value=len(day_kline))

    i = 0
    for stock_id in day_kline:

        pbar.update(i)

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

    print "merging, total num: %d" % (len(single_result))
    pbar = progressbar.ProgressBar(max_value=len(single_result))

    i = 0
    for stock_id in single_result:

        pbar.update(i)

    	i += 1
        if i % 100 == 0 or i == len(single_result):
            logging.info("merging (%d/%d)" % (i, len(single_result)))

        tmp = single_result[stock_id].where(single_result[stock_id]["day_date"] == target_date).dropna()
        tmp["stock_id"] = stock_id

        if tmp.shape[0] > 0:
            merge_result_list.append(tmp)

    merge_result = pd.concat(merge_result_list)

    merge_result_path = "%s/merge_result" % (conf_obj["result_dir"])

    if not os.path.exists(merge_result_path):
        logging.info("%s does not exist." % (merge_result_path))
        os.makedirs(merge_result_path)

    merge_result.to_csv("%s/%s" % (merge_result_path, target_date.strftime("%Y%m%d")), index=False)

    return


if __name__ == "__main__":
    main()

