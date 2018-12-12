#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################
#
# File Name:  get_fund_value_by_id.py
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
# Create Time:    2018-12-12 19:59:47
#
######################################################

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import time
import feedparser
import urllib2
from datetime import datetime, timedelta

def get_fund_value(fund_id, date):

    url = "http://data.funds.hexun.com/outxml/detail/openfundnetvalue.aspx?fundcode=%s&startdate=%s&enddate=%s" % (fund_id, date, date)

    header = { 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.81 Safari/537.36', 'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Connection':'keep-alive'}

    req = urllib2.Request(url, headers = header)
    resp = urllib2.urlopen(req, timeout=10)

    for line in resp.readlines():
        if line.find("fld_unitnetvalue") != -1:
            return line.split(">")[1].split("<")[0]

    return None


def main():

    with open(sys.argv[1], "r") as f:
        for line in f:
            ary = line.strip().split("\t")
            fund_id = ary[0]
            date = ary[1]

            value = get_fund_value(fund_id, date)

            result = []
            result.append(fund_id)
            result.append(date)
            result.append(value)

            print "\t".join([str(a) for a in result])

    return


if __name__ == "__main__":
    main()


