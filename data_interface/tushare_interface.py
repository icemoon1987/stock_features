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


    def get_week_kline(self, stock_id, start_date, end_date):

        start_date = start_date.strftime("%Y-%m-%d")
        end_date = end_date.strftime("%Y-%m-%d")

        #return ts.get_k_data(stock_id, ktype="W", start=start_date, end=end_date)
        return ts.get_k_data(stock_id, ktype="W")



