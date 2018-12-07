#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################
#
# File Name:  three_screen_evaluator.py
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
# Create Time:    2018-11-29 21:03:04
#
######################################################

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import time
from datetime import datetime, timedelta

class ThreeScreenEvaluator(object):

    def __init__(self):
        return


    def evaluate(self, input_df):

        model_signal_list = list(input_df["model_signal"])
        day_date_list = list(input_df["day_date"])
        profit_risk_ratio_list = list(input_df["profit_risk_ratio"])
        profit_ratio_list = list(input_df["profit_ratio"])
        day_open_list = list(input_df["day_open"])
        day_close_list = list(input_df["day_close"])
        enter_point_list = list(input_df["enter_point"])
        stop_point_list = list(input_df["stop_point"])
        target_point_list = list(input_df["target_point"])
        day_win_list = list(input_df["day_win_percentage"])

        trade_record = []
        #and day_win_list[i] > 0.55 \

        # Filter out trade opportunities
        for i in range(len(day_date_list)):

            if  model_signal_list[i] >= 4 \
                and profit_risk_ratio_list[i] > 2.0 \
                and profit_risk_ratio_list[i] < 10.0 \
                and profit_ratio_list[i] > 0.05 \
                :

                if i < len(day_date_list) - 1:
                    record = {}
                    record["date"] = day_date_list[i+1]
                    record["entry"] = day_open_list[i+1]
                    record["stop"] = stop_point_list[i]
                    record["target"] = target_point_list[i]
                    record["profit"] = 0
                    record["price_gap"] = 0
                    record["finish"] = 0
                    record["timeout"] = 0
                    record["success"] = 0
                    record["stop_flag"] = 0
                    record["out_date"] = None
                    record["out_point"] = 0

                    trade_record.append(record)


        # Evaluate every trade opportunities by compare every dates' data
        for i in range(len(day_date_list)):

            for j in range(len(trade_record)):

                # For already finished trade opportunity, ignore
                if trade_record[j]["finish"] > 0:
                    continue

                # For days before the trade day, ignore
                if day_date_list[i] <= trade_record[j]["date"]:
                    continue

                price_gap = day_close_list[i] - trade_record[j]["entry"] 
                profit = price_gap / trade_record[j]["entry"]

                # When profit is enough, finish
                #if profit >= 0.05:
                if day_close_list[i] >= trade_record[j]["target"]:
                    trade_record[j]["price_gap"] = price_gap
                    trade_record[j]["profit"] = profit
                    trade_record[j]["finish"] = 1
                    trade_record[j]["success"] = 1
                    trade_record[j]["out_date"] = day_date_list[i]
                    trade_record[j]["out_point"] = day_close_list[i]
                    continue

                # When time is up, finish
                if day_date_list[i] - trade_record[j]["date"] >= timedelta(days=30):
                    trade_record[j]["price_gap"] = price_gap
                    trade_record[j]["profit"] = profit
                    trade_record[j]["finish"] = 1
                    trade_record[j]["timeout"] = 1

                    if profit >= 0.05:
                        trade_record[j]["success"] = 1
                    else:
                        trade_record[j]["success"] = 0

                    trade_record[j]["out_date"] = day_date_list[i]
                    trade_record[j]["out_point"] = day_close_list[i]
                    continue

                # When touch the stop point, finish
                if day_close_list[i] <= trade_record[j]["stop"]:
                    trade_record[j]["price_gap"] = price_gap
                    trade_record[j]["profit"] = profit
                    trade_record[j]["finish"] = 1
                    trade_record[j]["success"] = 0
                    trade_record[j]["stop_flag"] = 1
                    trade_record[j]["out_date"] = day_date_list[i]
                    trade_record[j]["out_point"] = day_close_list[i]
                    continue


        return trade_record


if __name__ == "__main__":
    pass


