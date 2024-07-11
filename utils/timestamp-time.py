#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：UWB
@File    ：timestamp-time.py
@IDE     ：PyCharm
@Author  ：lwb
@Date    ：2024/7/7 9:23
"""
import datetime

import pytz


# 北京时间转时间戳
def time_to_timestamp(Year, Month, Day, Hour, Minute, Second):
    # Define Beijing timezone
    beijing_tz = pytz.timezone('Asia/Shanghai')

    # Create a Beijing datetime object
    beijing_dt = datetime.datetime(Year, Month, Day, Hour, Minute, Second, tzinfo=beijing_tz)

    # Convert Beijing datetime to timestamp (seconds since Unix epoch)
    timestamp = int(beijing_dt.timestamp())
    print(timestamp)


# 时间戳转北京时间
def timestamp_to_time(timestamp):
    # Create a datetime object from timestamp
    dt = datetime.datetime.fromtimestamp(timestamp)

    # Define Beijing timezone
    beijing_tz = pytz.timezone('Asia/Shanghai')

    # Convert timestamp to Beijing time
    beijing_dt = dt.astimezone(beijing_tz)
    print(beijing_dt)


if __name__ == '__main__':
    time_to_timestamp(2024, 5, 21, 14, 25, 10)
    timestamp_to_time(1716272010)
