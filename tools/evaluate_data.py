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
from evaluator.three_screen_evaluator import ThreeScreenEvaluator
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
    result_dir = conf_obj["result_dir"]

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

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


def load_single_result(result_dir, stock_id):

    result = pd.DataFrame()

    result_map = {}

    if stock_id != None:
        file_list = [stock_id]
    else:
        file_list = os.listdir(result_dir)


    for file_name in file_list:
        stock_id = file_name
        tmp = pd.read_csv(result_dir + "/" + file_name, parse_dates=["day_date"])

        result_map[stock_id] = tmp

    return result_map 


def write_trade_plan(trade_plan, file_out):

    with open(file_out, "w") as f:
        for item in trade_plan:
            f.write(str(item))
            f.write("\n")

    return


def output_sum_result(sum_result):

    output_list = [
        "trade_num",
        "success_num",
        "stop_num",
        "timeout_num",
        "success_rate",
        "stop_rate",
        "timeout_rate",
        "price_gap_sum",
        "entry_sum",
        "avg_profit"
    ]

    result = []

    for field in output_list:
        result.append(sum_result[field])

    print "\t".join(output_list)
    print "\t".join([str(a) for a in result])
    
    return



def main():

    if len(sys.argv) == 2:

        stock_id = sys.argv[1]
        target_date = datetime.strptime(datetime.now().strftime("%Y%m%d"), "%Y%m%d")

    elif len(sys.argv) == 3:

        stock_id = sys.argv[1]
        target_date = datetime.strptime(sys.argv[2], "%Y%m%d")

    else:
        stock_id = None
        target_date = datetime.strptime(datetime.now().strftime("%Y%m%d"), "%Y%m%d")

    #print len(sys.argv)
    #print stock_id
    #print target_date

    conf_file = "./conf/config.json"

    # Init
    conf_obj = init(conf_file)
    logging.info("init finish")

    single_result_path = "%s/single_result/%s" % (conf_obj["result_dir"], target_date.strftime("%Y%m%d"))

    single_result = load_single_result(single_result_path, stock_id)
    logging.info("load single result finish")

    trade_plan_path = "%s/trade_plan/%s" % (conf_obj["result_dir"], target_date.strftime("%Y%m%d"))
    win_result_path = "%s/win_result" % (conf_obj["result_dir"])

    if not os.path.exists(trade_plan_path):
        logging.info("%s does not exist." % (trade_plan_path))
        os.makedirs(trade_plan_path)

    if not os.path.exists(win_result_path):
        logging.info("%s does not exist." % (win_result_path))
        os.makedirs(win_result_path)

    ts_eval = ThreeScreenEvaluator()

    # Calculate features for day kline
    result = {}

    i = 0
    for stock_id in single_result:

        i += 1
        if i % 100 == 0 or i == len(single_result):
            logging.info("evaluating day k line (%d/%d)" % (i, len(single_result)))

        trade_plan = ts_eval.evaluate(single_result[stock_id])

        trade_num = 0
        success_num = 0
        timeout_num = 0
        stop_num = 0
        price_gap_sum = 0
        entry_sum = 0

        for item in trade_plan:
            if item["finish"] == 1:
                trade_num += 1

            if item["success"] == 1:
                success_num += 1

            if item["timeout"] == 1:
                timeout_num += 1

            if item["stop_flag"] == 1:
                stop_num += 1

            price_gap_sum += item["price_gap"]
            entry_sum += item["entry"]

        tmp = {}
        tmp["trade_num"] = trade_num
        tmp["success_num"] = success_num
        tmp["timeout_num"] = timeout_num
        tmp["stop_num"] = stop_num 
        tmp["price_gap_sum"] = price_gap_sum
        tmp["entry_sum"] = entry_sum

        try:
            tmp["avg_profit"] = price_gap_sum / entry_sum
        except:
            tmp["avg_profit"] = 0.0

        try:
            tmp["success_rate"] = float(success_num) / trade_num
        except:
            tmp["success_rate"] = 0.0

        try:
            tmp["timeout_rate"] = float(timeout_num) / trade_num
        except:
            tmp["timeout_rate"] = 0.0

        try:
            tmp["stop_rate"] = float(stop_num) / trade_num
        except:
            tmp["stop_rate"] = 0.0

        result[stock_id] = tmp

        write_trade_plan(trade_plan, "%s/%s" % (trade_plan_path, stock_id))

        #for item in trade_plan:
            #print item

        #print stock_id, result[stock_id]

    with open("%s/%s" % (win_result_path, target_date.strftime("%Y%m%d")), "w") as f:
        for stock_id in result:
            f.write(stock_id + "\t" + json.dumps(result[stock_id]))
            f.write("\n")

    sum_result = {}
    sum_result["trade_num"] = 0 
    sum_result["success_num"] = 0 
    sum_result["stop_num"] = 0 
    sum_result["timeout_num"] = 0 
    sum_result["price_gap_sum"] = 0
    sum_result["entry_sum"] = 0
    sum_result["success_rate"] = 0.0
    sum_result["timeout_rate"] = 0.0
    sum_result["stop_rate"] = 0.0
    sum_result["avg_profit"] = 0.0

    for stock_id in result:
        sum_result["trade_num"] += result[stock_id]["trade_num"]
        sum_result["success_num"] += result[stock_id]["success_num"]
        sum_result["stop_num"] += result[stock_id]["stop_num"]
        sum_result["timeout_num"] += result[stock_id]["timeout_num"]
        sum_result["price_gap_sum"] += result[stock_id]["price_gap_sum"]
        sum_result["entry_sum"] += result[stock_id]["entry_sum"]

    try:
        sum_result["success_rate"] = float(sum_result["success_num"]) / sum_result["trade_num"]
    except:
        sum_result["success_rate"] = 0.0

    try:
        sum_result["timeout_rate"] = float(sum_result["timeout_num"]) / sum_result["trade_num"]
    except:
        sum_result["timeout_rate"] = 0.0

    try:
        sum_result["stop_rate"] = float(sum_result["stop_num"]) / sum_result["trade_num"]
    except:
        sum_result["stop_rate"] = 0.0

    sum_result["avg_profit"] = sum_result["price_gap_sum"] / sum_result["entry_sum"]

    output_sum_result(sum_result)

    return


if __name__ == "__main__":
    main()

