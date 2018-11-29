#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################
#
# File Name:  tushare_interface.py
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
# Create Time:    2017-09-01 18:02:43
#
######################################################

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import time
import tushare as ts
from datetime import datetime, timedelta

class TushareInterface(object):

    def __init__(self):
        return


    def get_all_stocks(self):
        return ts.get_stock_basics()

    
    def get_day_kline(self, stock_id, start_date, end_date):

        start_date = start_date.strftime("%Y-%m-%d")
        end_date = (end_date).strftime("%Y-%m-%d")

        #return ts.get_k_data(stock_id, ktype="D", start=start_date, end=end_date)
        return ts.get_k_data(stock_id, ktype="D")


    def get_realtime_quotes(self, stock_id):
        return ts.get_realtime_quotes(stock_id)


    def get_week_kline(self, stock_id, start_date, end_date):

        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")

        #return ts.get_k_data(stock_id, ktype="W", start=start_date, end=end_date)
        return ts.get_k_data(stock_id, ktype="W")


if __name__ == "__main__":
    data_if = TushareInterface()

    #all_stock = data_if.get_all_stocks()

    #name_list = list(all_stock["name"])

    day_kline = data_if.get_day_kline("sh", datetime.strptime("2018-11-26", "%Y-%m-%d"), datetime.strptime("2018-11-28", "%Y-%m-%d"))

    print day_kline

