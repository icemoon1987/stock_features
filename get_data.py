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
from data_interface.tushare_interface import TushareInterface


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

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)

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


def get_stock_ids(data_if):

    # Get all stocks
    all_stock = data_if.get_all_stocks()

    # Filter ST stocks
    all_stock = all_stock.where(~all_stock["name"].str.contains("ST")).dropna()

    return list(all_stock.index)



def get_and_store_kline(data_if, kline_type, stock_list, data_dir, start_date, end_date):

    for stock_id in stock_list:
        logging.debug("get %s kline for %s, from %s to %s" % (kline_type, stock_id, start_date.strftime("%Y%m%d"), end_date.strftime("%Y%m%d")))

        if kline_type == "day":
            kline = data_if.get_day_kline(stock_id, start_date, end_date)
        elif kline_type == "week":
            kline = data_if.get_week_kline(stock_id, start_date, end_date)

        kline = kline.ix[:, ["date", "open", "close", "high", "low", "volume"]]

        kline.to_csv("%s/%s" % (data_dir, stock_id), index=False)

    return


def load_data(data_dir):

    result = pd.DataFrame()

    day_kline_map = {}
    week_kline_map = {}

    for file_name in os.listdir(data_dir):

        stock_id, data_type = file_name.split(".")

        tmp = pd.read_csv(data_dir + "/" + file_name, parse_dates=["date"])
        print tmp

        if data_type == "day":
            day_kline_map[stock_id] = tmp

        if data_type == "week":
            week_kline_map[stock_id] = tmp

    return day_kline_map, week_kline_map


def main():

    if len(sys.argv) >= 2:
        end_date = datetime.strptime(sys.argv[2], "%Y%m%d")
    else:
        end_date = datetime.now()

    conf_file = "./conf/config.json"

    # Init
    conf_obj = init(conf_file)
    logging.info("init finish")


    data_if = TushareInterface()
    #get_and_store_data(data_if, conf_obj["data_dir"], start_date, end_date)

    # Get all stocks
    all_stock = data_if.get_all_stocks()

    # Filter ST stocks
    all_stock = all_stock.where(~all_stock["name"].str.contains("ST")).dropna()

    stock_set = set(all_stock.index)
    logging.info("get %d stock ids" % (len(stock_set)))

    # Get k line data
    kline_type = ["day", "week"]

    for type in kline_type:

        kline_path = "%s/kline/%s/%s" % (conf_obj["data_dir"], type, end_date.strftime("%Y%m%d"))

        if not os.path.exists(kline_path):
            logging.info("%s does not exist." % (kline_path))
            os.makedirs(kline_path)
            finish_set = set()
        else:
            finish_set = set(os.listdir(kline_path))

        togo_set = stock_set - finish_set
        logging.info("type: %s, %d finished, %d to go." % (type, len(finish_set), len(togo_set)))
    
        if type == "day":
            start_date = end_date - timedelta(days = conf_obj.get("data_days", 365))
        elif type == "week":
            start_date = end_date - timedelta(days = conf_obj.get("data_days", 730))
        else:
            start_date = end_date - timedelta(days = conf_obj.get("data_days", 365))

        get_and_store_kline(data_if, type, list(togo_set), kline_path, start_date, end_date)
        logging.info("get %d %s kline." % (len(togo_set), type))

    return


if __name__ == "__main__":
    main()

