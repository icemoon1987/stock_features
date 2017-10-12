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

pd.set_option("display.width", 300)
#pd.set_option("display.max_rows", None)


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

    logging.basicConfig(level=log_level, filename="%s/%s.%s" % (log_dir, "log", datetime.now().strftime("%Y%m%d")), filemode='a', format='%(asctime)s [%(levelname)s] [%(filename)s] [%(funcName)s] [%(lineno)d] %(message)s')

    return conf_obj


def print_help():
    print "USAGE: python %s CONF_FILE" % (__file__)
    return


def get_and_store_kline(data_if, kline_type, stock_list, data_dir, start_date, end_date):

    i = 0
    for stock_id in stock_list:
        i += 1
        if i % 10 == 0 or i == len(stock_list):
            logging.info("get %s k line (%d/%d)" % (kline_type, i, len(stock_list)))

        if kline_type == "day":
            kline = data_if.get_day_kline(stock_id, start_date, end_date)
        elif kline_type == "week":
            kline = data_if.get_week_kline(stock_id, start_date, end_date)

        kline = kline.ix[:, ["date", "open", "close", "high", "low", "volume"]]

        if kline.shape[0] > 0:
            kline.to_csv("%s/%s" % (data_dir, stock_id), index=False)

    return


def main():

    if len(sys.argv) == 2:
        stock_id = sys.argv[1]
        end_date = datetime.now()

    elif len(sys.argv) == 3:
        stock_id = sys.argv[1]
        end_date = datetime.strptime(sys.argv[2], "%Y%m%d")
    else:
        stock_id = None
        end_date = datetime.now()

    conf_file = "./conf/config.json"

    # Init
    conf_obj = init(conf_file)
    logging.info("init finish")

    data_if = TushareInterface()
    #get_and_store_data(data_if, conf_obj["data_dir"], start_date, end_date)

    # Get all stocks
    if stock_id != None:
        all_stock = data_if.get_all_stocks()

        # Filter ST stocks
        all_stock = all_stock.where(~all_stock["name"].str.contains("ST")).dropna()

    else:
        all_stock = [stock_id]


    # Filter too new stocks
    up_date_limit = (end_date - timedelta(days = 90)).strftime("%Y%m%d")
    all_stock = all_stock.where(all_stock["timeToMarket"] < float(up_date_limit)).dropna()
    all_stock = all_stock.where(all_stock["timeToMarket"] != 0.0).dropna()

    # test
    #all_stock = all_stock[500:520]

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

