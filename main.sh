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

# Get data
$PYTHON    ./tools/get_data.py

# Analyse data
$PYTHON    ./tools/analyse_data.py

# evaluate data
$PYTHON    ./tools/evaluate_data.py

