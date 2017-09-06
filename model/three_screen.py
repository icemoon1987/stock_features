#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################
#
# File Name:  three_screen.py
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
# Create Time:    2017-09-05 19:49:58
#
######################################################

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import time
import pandas as pd
from datetime import datetime, timedelta

class ThreeScreen(object):

    def __init__(self):
        return


    def target_point(self, week_df):

        week_df["week_close_ema_short_predict"] = 2 * week_df["week_close_ema_short"] - week_df.shift(1)["week_close_ema_short"]

        week_df["week_close_ema_long_predict"] = 2 * week_df["week_close_ema_long"] - week_df.shift(1)["week_close_ema_long"]

        week_df["target_point"] = (week_df["week_close_ema_short_predict"] + week_df["week_close_ema_long_predict"]) / 2.0

        return week_df


    def enter_point(self, day_df, day_window):

        close_price = list(day_df["day_close"])
        close_ema = list(day_df["day_close_ema_short"])
        gap_result = []

        for i in range(len(close_price)):
            gap = close_price[i] - close_ema[i]

            if gap >= 0:
                gap_result.append(0)
            else:
                gap_result.append(gap)

        day_df["day_close_ema_gap"] = gap_result

        mean_gap_result = []

        for i in range(len(gap_result)):
            start_index = i - day_window + 1
            if start_index < 0:
                start_index = 0

            tmp = gap_result[start_index : i + 1]

            sum = 0
            num = 0

            for item in tmp:
                if item < 0:
                    sum += item
                    num += 1

            if num > 0:
                mean_gap_result.append(sum / num)
            else:
                mean_gap_result.append(0.0)

        day_df["day_close_ema_gap_mean"] = mean_gap_result

        day_df["stop_point_threshold"] = day_df["day_close"] + day_df["day_close_ema_gap_mean"]

        day_df["day_close_ema_short_predict"] = 2 * day_df["day_close_ema_short"] - day_df.shift(1)["day_close_ema_short"]

        day_df["enter_point"] = day_df["day_close_ema_short_predict"] + day_df["day_close_ema_gap_mean"]

        return day_df

    
    def stop_point(self, day_df, day_window):

        result = []

        close_price = list(day_df["day_close"])

        for i in range(len(close_price)):
            start_index = i - day_window + 1
            end_index = i

            if start_index < 0:
                start_index = 0

            min_num = 999999
            min_index = 0

            for j in range(start_index, end_index + 1):
                if close_price[j] <= min_num:
                    min_num = close_price[j]
                    min_index = j

            if min_index == i:
                result.append(close_price[min_index])
                continue

            before = min_index - 1
            after = min_index + 1

            if before < 0 and after > i:
                result.append(close_price[min_index])
            elif before < 0 and after <= i:
                result.append(close_price[after])
            elif before >= 0 and after > i:
                result.append(close_price[before])
            else:
                if close_price[before] < close_price[after]:
                    result.append(close_price[before])
                else:
                    result.append(close_price[after])

        day_df["stop_point"] = result

        return day_df


    def signal(self, day_df, week_df):

        week_df = self.target_point(week_df)
        day_df = self.enter_point(day_df, 20)
        day_df = self.stop_point(day_df, 20)

        # resample week kline
        week_df_resampled = week_df.set_index("week_date", inplace = False)
        week_df_resampled = week_df_resampled.resample("D").pad()

        # merge day and week features
        week_df_resampled.reset_index(level = 0, inplace = True)

        merge_result = pd.merge(day_df, week_df_resampled, how="left", left_on=["day_date"], right_on=["week_date"]).dropna()

        # first screen: week pulse signal
        # second screen: day force signal

        week_pulse_signal = list(merge_result["week_pulse_signal"])
        day_force_signal = list(merge_result["day_force_signal"])

        result = []

        for i in range(len(week_pulse_signal)):
            if week_pulse_signal[i] > 0 and day_force_signal[i] > 0:
                result.append(week_pulse_signal[i] + day_force_signal[i])
            elif week_pulse_signal[i] < 0 and day_force_signal[i] < 0:
                result.append(week_pulse_signal[i] + day_force_signal[i])
            else:
                result.append(0)
        
        merge_result["model_signal"] = result

        merge_result["profit"] = merge_result["target_point"] - merge_result["day_close"]
        merge_result["risk"] = merge_result["day_close"] - merge_result["stop_point"]
        merge_result["profit_risk_ratio"] = merge_result["profit"] / merge_result["risk"]

        #print merge_result.ix[:, ["day_date", "day_open", "day_close", "week_pulse", "week_pulse_signal", "day_force_ema", "day_force_signal", "model_signal", "week_close_ema_short_predict", "week_close_ema_long_predict", "enter_point", "target_point", "stop_point", "stop_point_threshold", "profit", "risk"]]

        return merge_result



