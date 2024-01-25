#!/bin/bash

python mode0.py
python receive.py /dev/ttyS0 $1
