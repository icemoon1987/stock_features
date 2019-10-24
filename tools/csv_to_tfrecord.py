#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""  TODO: module description

Usage:  

Input:  

Output:  

Author: wenhai.pan

Create Time:    2019-08-16 17:21:48

"""

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import os
import time
from datetime import datetime, timedelta
import pandas as pd

def parse_args():
    """parse command line args

    :returns: argparse object

    """

    parser = argparse.ArgumentParser(description="train the model")
    parser.add_argument("--log", help="log directory", type=str, default="./log")
    parser.add_argument("--csv", help="csv file path", type=str, default=None)
    parser.add_argument("--tfrecord", help="tfrecord file path", type=str, default=None)

    return parser.parse_args()


def create_tf_example():

    return


def main():

    args = parse_args()

    if os.path.exists(args.tfrecord):
        shutil.rmtree(args.tfrecord)

    if args.debug:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.getLogger("tensorflow").setLevel(logging.WARNING)
    logging.basicConfig(level=log_level, filename="%s/%s.%s" % (args.log, "log", datetime.now().strftime("%Y%m%d")), filemode='a', format='%(asctime)s [%(levelname)s] [%(filename)s] [%(funcName)s] [%(lineno)d] %(message)s')

    csv_df = pd.read_csv(args.csv)


    return


if __name__ == "__main__":
    main()


