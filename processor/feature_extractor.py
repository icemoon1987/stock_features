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
import math
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

                #print k, input_list[i], (1.0-k), result_list[i-1], result

        input_df[output_col] = result_list

        return input_df


    def macd(self, input_df, input_col, macd_col, signal_col, macd_bar_col, quick_ema_day_num, slow_ema_day_num, signal_day_num):

        result_df = self.ema(input_df, input_col, "quick_ema", quick_ema_day_num)
        result_df = self.ema(result_df, input_col, "slow_ema", slow_ema_day_num)

        result_df[macd_col] = result_df["quick_ema"] - result_df["slow_ema"]

        result_df = self.ema(result_df, macd_col, signal_col, signal_day_num)

        result_df[macd_bar_col] = result_df[macd_col] - result_df[signal_col]

        #print result_df

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


    def atr(self, input_df, close_price_col, high_price_col, low_price_col, day_num, tr_col, atr_col):

        close_price_list = list(input_df[close_price_col])
        high_price_list = list(input_df[high_price_col])
        low_price_list = list(input_df[low_price_col])

        tr_result = []

        for i in range(len(close_price_list)):
            if i == 0:
                tr_result.append(abs(high_price_list[i] - low_price_list[i]))
            else:
                gap1 = abs(high_price_list[i] - low_price_list[i])
                gap2 = abs(high_price_list[i] - close_price_list[i-1])
                gap3 = abs(low_price_list[i] - close_price_list[i-1])

                tr_result.append(max([gap1, gap2, gap3]))

        input_df[tr_col] = tr_result

        input_df = self.ma(input_df, tr_col, atr_col, day_num)

        input_df[atr_col + "1_high"] = input_df[close_price_col] + input_df[atr_col]
        input_df[atr_col + "1_low"] = input_df[close_price_col] - input_df[atr_col]

        input_df[atr_col + "2_high"] = input_df[close_price_col] + 2 * input_df[atr_col]
        input_df[atr_col + "2_low"] = input_df[close_price_col] - 2 * input_df[atr_col]

        return input_df


    def rise_rate(self, input_df, open_col, close_col, rise_rate_col):

        open_col_list = list(input_df[open_col])
        close_col_list = list(input_df[close_col])

        result_list = []

        for i in range(len(open_col_list)):
            if open_col_list[i] == -1:
                result_list.append(-1)
                continue

            result_list.append((close_col_list[i] - open_col_list[i]) / open_col_list[i])

        input_df[rise_rate_col] = result_list

        return input_df


    def merge_target(self, input_df, target_df, date_col, open_col, close_col, target_open_col, target_close_col):

        src_date_list = list(input_df[date_col])
        target_date_list = list(target_df[date_col])
        open_list = list(target_df[open_col])
        close_list = list(target_df[close_col])

        result_open = []
        result_close = []

        for i in range(len(src_date_list)):

            try:
                target_index = target_date_list.index(src_date_list[i])
            except:
                result_open.append(-1)
                result_close.append(-1)
                continue

            result_open.append(open_list[target_index])
            result_close.append(close_list[target_index])

        input_df[target_open_col] = result_open
        input_df[target_close_col] = result_close

        return input_df



    def will_profit(self, input_df, close_col, will_profit_col, time_gap, target_profit):

        close_list = list(input_df[close_col])

        will_profit = []

        for i in range(len(close_list)):
            eval_close_list = close_list[i + 1 : i + time_gap + 1]
            target_close = close_list[i] * ( 1 + target_profit )

            will_profit.append(0)

            for eval_close in eval_close_list:
                if eval_close > target_close:
                    will_profit[-1] = 1

        input_df[will_profit_col] = will_profit
        
        return input_df



