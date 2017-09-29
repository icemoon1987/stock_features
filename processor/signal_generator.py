#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################
#
# File Name:  signal_generator.py
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

class SignalGenerator(object):

    def __init__(self):
        return


    def pulse_signal(self, input_df, pulse_col, signal_col):

        pulse_list = list(input_df[pulse_col])
        result_list = []

        for i in range(len(pulse_list)):
            if i == 0:
                result_list.append(0)
                continue

            if pulse_list[i-1] == "g":

                if pulse_list[i] == "r":
                    result_list.append(-4)
                elif pulse_list[i] == "b":
                    result_list.append(-3)
                else:
                    result_list.append(1)

            elif pulse_list[i-1] == "r":

                if pulse_list[i] == "g":
                    result_list.append(4)
                elif pulse_list[i] == "b":
                    result_list.append(3)
                else:
                    result_list.append(-1)

            elif pulse_list[i-1] == "b":

                if pulse_list[i] == "g":
                    result_list.append(2)
                elif pulse_list[i] == "r":
                    result_list.append(-2)
                else:
                    result_list.append(0)
            else:
                result_list.append(0)

        input_df[signal_col] = result_list

        return input_df


    def force_signal(self, input_df, force_col, day_window, signal_col):

        force_max = input_df.ix[:, [force_col]].rolling(window=day_window, min_periods=0).max()
        force_max_list = list(force_max[force_col])

        force_min = input_df.ix[:, [force_col]].rolling(window=day_window, min_periods=0).min()
        force_min_list = list(force_min[force_col])

        force_list = list(input_df[force_col])

        result_list = []

        for i in range(len(force_list)):
            if force_list[i] > 0:
                if force_list[i] < force_max_list[i]:
                    result_list.append(-1)
                else:
                    result_list.append(0)

            elif force_list[i] < 0:
                if force_list[i] > force_min_list[i]:
                    result_list.append(1)
                else:
                    result_list.append(0)

            else:
                result_list.append(0)

        input_df[signal_col] = result_list

        return input_df


    def deviation_signal(self, input_df, close_col, macd_bar_col, window, signal_col):

        close = list(input_df[close_col])
        macd_bar = list(input_df[macd_bar_col])
        last_min = []
        result = []

        for i in range(len(close)):
            start_index = i - window + 1
            if start_index < 0:
                start_index = 0

            close_min_index = start_index

            for j in range(start_index, i):
                if close[j] < close[close_min_index]:
                    close_min_index = j

            if close[i] <= close[close_min_index] and macd_bar[i] > macd_bar[close_min_index]:

                valid = False
                for j in range(close_min_index, i):
                    if macd_bar[j] > 0:
                        valid = True
                        break

                if valid:
                    last_min.append(close[close_min_index])
                    result.append(1)
                else:
                    last_min.append(close[close_min_index])
                    result.append(0)
            else:
                last_min.append(close[close_min_index])
                result.append(0)

        input_df[signal_col] = result
        input_df["day_last_min"] = last_min

        return input_df


