#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################
#
# File Name:  feature_extractor.py
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
# Create Time:    2017-09-04 16:48:55
#
######################################################

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import time
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class FeatureExtractor(object):

    def __init__(self):
        return


    def ma(self, input_df, input_col, output_col, day_num):

        result = input_df.ix[:, [input_col]].rolling(window=day_num, min_periods=0).mean()

        input_df[output_col] = result[input_col]

        return input_df


    def ema(self, input_df, input_col, output_col, day_num):

        input_list = list(input_df[input_col])
        result_list = []

        k = 1.0 / (1.0 + day_num)

        for i in range(len(input_list)):

            if i == 0:
                result_list.append(input_list[i])
            else:
                result = k * input_list[i] + (1.0 - k) * result_list[i - 1]
                result_list.append(result)

        input_df[output_col] = result_list

        return input_df


    def macd(self, input_df, input_col, macd_col, signal_col, macd_bar_col, quick_ema_day_num, slow_ema_day_num, signal_day_num):

        result_df = self.ema(input_df, input_col, "quick_ema", quick_ema_day_num)
        result_df = self.ema(result_df, input_col, "slow_ema", slow_ema_day_num)

        result_df[macd_col] = result_df["quick_ema"] - result_df["slow_ema"]

        result_df = self.ema(result_df, macd_col, signal_col, signal_day_num)

        result_df[macd_bar_col] = result_df[macd_col] - result_df[signal_col]

        input_df[macd_col] = result_df[macd_col]
        input_df[signal_col] = result_df[signal_col]
        input_df[macd_bar_col] = result_df[macd_bar_col]

        return input_df


    def pulse(self, input_df, ema_col, macd_bar_col, output_col):

        ema_list = list(input_df[ema_col])
        macd_bar_list = list(input_df[macd_bar_col])

        result_list = []

        for i in range(len(ema_list)):
            if i == 0:
                result_list.append("b")
                continue

            ema_gap = ema_list[i] - ema_list[i-1]
            macd_bar_gap = macd_bar_list[i] - macd_bar_list[i-1]

            if ema_gap >= 0 and macd_bar_gap >= 0:
                result_list.append("g")
            elif ema_gap < 0 and macd_bar_gap < 0:
                result_list.append("r")
            else:
                result_list.append("b")

        input_df[output_col] = result_list

        return input_df


    def force_index(self, input_df, price_col, volume_col, force_raw_col, force_ema_col, ema_day_num):

        price_list = list(input_df[price_col])
        volume_list = list(input_df[volume_col])

        force_raw = []

        for i in range(len(price_list)):
            if i == 0:
                force_raw.append(0.0)
            else:
                force_raw.append( (price_list[i] - price_list[i-1]) * volume_list[i] )

        input_df[force_raw_col] = force_raw

        input_df = self.ema(input_df, force_raw_col, force_ema_col, ema_day_num)

        return input_df



