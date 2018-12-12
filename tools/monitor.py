#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################
#
# File Name:  monitor.py
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
# Create Time:    2017-09-28 14:31:13
#
######################################################

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import time
import json
from datetime import datetime, timedelta
from data_interface.tushare_interface import TushareInterface


##
# @brief    init function
#
# @param    conf_file
#
# @return   
def init(conf_file):

    with open(conf_file, "r") as f:
        conf_obj = json.loads(f.read())

    return conf_obj


def main():

    conf_obj = init("./conf/monitor.json")

    data_if = TushareInterface()

    while True:
        os.system("clear")
        try:

            for monitor in conf_obj["monitors"]:
                result = data_if.get_realtime_quotes(monitor["code"])
                price = float(result["price"][0])

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if price >= monitor["upper_limit"] * 0.99:
                    print "%s   WARNING: %s  %f  upper_limit %f" % (now, monitor["code"], price, monitor["upper_limit"])
                elif price <= monitor["lower_limit"] * 1.01:
                    print "%s   WARNING: %s  %f  lower_limit %f" % (now, monitor["code"], price, monitor["lower_limit"])
                else:
                    print "%s   DEBUG: %s  %f" % (now, monitor["code"], price)

        except Exception, ex:
            print str(ex)

        time.sleep(conf_obj["time_gap"])

    return


if __name__ == "__main__":
    main()
