#!/usr/bin/bash


######################################################
#
# File Name:  main.sh
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
# Create Time:    2018-08-06 16:34:45
#
######################################################

PYTHON="/usr/bin/python"

$PYTHON ./tools/get_data.py
$PYTHON ./tools/analyse_data.py
$PYTHON ./tools/evaluate_data.py

