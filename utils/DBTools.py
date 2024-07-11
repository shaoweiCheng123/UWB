#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：UWB 
@File    ：DBTools.py
@IDE     ：PyCharm 
@Author  ：lwb
@Date    ：2024/7/4 9:56 
'''

import csv
import json
import os
import sqlite3
import time
import pytz
from datetime import datetime


def create_original_database(filepath):
    con = sqlite3.connect("../resources/database/uwb_data.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS original_data("  # 创建原始uwb数据表
                "id INTEGER PRIMARY KEY,"
                "time TEXT,"
                "bltMac TEXT,"
                "range REAL,"
                "uwbMac TEXT,"
                "uwbRssi REAL)")
        # 拼接文件的完整路径
    with open(filepath, "r") as csvfile:
        lines = csv.reader(csvfile)
        select_columns = [1, 3, 9, 10, 11]
        next(lines)  # 首行表头跳过
        for line in lines:
            select_data = [line[i] for i in select_columns]
            if is_valid_format(select_data[0], '%Y-%m-%dT%H:%M:%S.%fZ'):
                # UTC时间转北京时间戳
                utc_time = datetime.strptime(select_data[0], '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                # UTC时间转北京时间戳
                utc_time = datetime.strptime(select_data[0], '%Y-%m-%dT%H:%M:%SZ')
            # 定义北京时区
            beijing_tz = pytz.timezone('Asia/Shanghai')
            # 将 UTC 时间转换为北京时间
            beijing_time = utc_time.replace(tzinfo=pytz.utc).astimezone(beijing_tz)
            # 将北京时间时间转换为时间戳
            select_data[0] = str(int(beijing_time.timestamp()))
            cur.execute('INSERT INTO original_data(time, bltMac, range, uwbMac, uwbRssi) VALUES(?, ?, ?, ?, ?)', select_data)
    con.commit()
    cur.close()
    con.close()

def is_valid_format(date_string, date_format):
    try:
        datetime_object = datetime.strptime(date_string, date_format)
        return True
    except ValueError:
        return False
def create_test_database(file_path):  # 输入level_range
    con = sqlite3.connect("../resources/database/uwb_data.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS test_data("  # 创建测试uwb数据表
                "id INTEGER PRIMARY KEY,"
                "time TEXT,"
                "bltMac TEXT,"
                "range REAL,"
                "uwbMac TEXT,"
                "uwbRssi REAL)")

    with open(file_path, "r") as csvfile:
        lines = csv.reader(csvfile)
        select_columns = [1, 3, 9, 10, 11]
        next(lines)  # 首行表头跳过
        for line in lines:
            select_data = [line[i] for i in select_columns]
            if is_valid_format(select_data[0], '%Y-%m-%dT%H:%M:%S.%fZ'):
                # UTC时间转北京时间戳
                utc_time = datetime.strptime(select_data[0], '%Y-%m-%dT%H:%M:%S.%fZ')
            else:
                # UTC时间转北京时间戳
                utc_time = datetime.strptime(select_data[0], '%Y-%m-%dT%H:%M:%SZ')
            # 定义北京时区
            beijing_tz = pytz.timezone('Asia/Shanghai')
            # 将 UTC 时间转换为北京时间
            beijing_time = utc_time.replace(tzinfo=pytz.utc).astimezone(beijing_tz)
            # 将北京时间时间转换为时间戳
            select_data[0] = str(int(beijing_time.timestamp()))
            cur.execute('INSERT INTO test_data(time, bltMac, range, uwbMac, uwbRssi) VALUES(?, ?, ?, ?, ?)', select_data)
    con.commit()
    cur.close()
    con.close()


def create_fingerprint_database(file_path):
    con = sqlite3.connect("../resources/database/uwb_data.db")
    cur = con.cursor()
    fp_index = file_path.split(".txt")[0][-1]
    cur.execute(f"CREATE TABLE IF NOT EXISTS fingerprint{fp_index}_data("  # 创建指纹点数据表
                "fp_index INTEGER,"
                "true_x REAL,"
                "true_y REAL,"
                "uwb_mac1_mean REAL,"
                "uwb_mac2_mean REAL,"
                "uwb_mac3_mean REAL,"
                "uwb_mac4_mean REAL,"
                "uwb_mac5_mean REAL,"
                "uwb_mac6_mean REAL,"
                "uwb_mac7_mean REAL,"
                "uwb_mac8_mean REAL,"
                "uwb_mac9_mean REAL,"
                "uwb_mac10_mean REAL,"
                "uwb_mac11_mean REAL,"
                "uwb_mac12_mean REAL,"
                "uwb_mac13_mean REAL,"
                "uwb_mac14_mean REAL,"
                "uwb_mac1_var REAL,"
                "uwb_mac2_var REAL,"
                "uwb_mac3_var REAL,"
                "uwb_mac4_var REAL,"
                "uwb_mac5_var REAL,"
                "uwb_mac6_var REAL,"
                "uwb_mac7_var REAL,"
                "uwb_mac8_var REAL,"
                "uwb_mac9_var REAL,"
                "uwb_mac10_var REAL,"
                "uwb_mac11_var REAL,"
                "uwb_mac12_var REAL,"
                "uwb_mac13_var REAL,"
                "uwb_mac14_var REAL,"
                "uwb_mac1_rate REAL,"
                "uwb_mac2_rate REAL,"
                "uwb_mac3_rate REAL,"
                "uwb_mac4_rate REAL,"
                "uwb_mac5_rate REAL,"
                "uwb_mac6_rate REAL,"
                "uwb_mac7_rate REAL,"
                "uwb_mac8_rate REAL,"
                "uwb_mac9_rate REAL,"
                "uwb_mac10_rate REAL,"
                "uwb_mac11_rate REAL,"
                "uwb_mac12_rate REAL,"
                "uwb_mac13_rate REAL,"
                "uwb_mac14_rate REAL)"
                )

    with open(file_path, "r") as fp:
        lines = fp.readlines()
        for line in lines:
            line_data = json.loads(line)
            cur.execute(f'INSERT INTO fingerprint{fp_index}_data VALUES(?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?,?, ?, ?, ?, ?)',
                        [line_data["index"], line_data["true_x"],
                         line_data["true_y"],
                         line_data["uwb_mac1_mean"][0],
                         line_data["uwb_mac2_mean"][0], line_data["uwb_mac3_mean"][0],
                         line_data["uwb_mac4_mean"][0], line_data["uwb_mac5_mean"][0],
                         line_data["uwb_mac6_mean"][0], line_data["uwb_mac7_mean"][0],
                         line_data["uwb_mac8_mean"][0], line_data["uwb_mac9_mean"][0],
                         line_data["uwb_mac10_mean"][0], line_data["uwb_mac11_mean"][0],
                         line_data["uwb_mac12_mean"][0], line_data["uwb_mac13_mean"][0],
                         line_data["uwb_mac14_mean"][0],
                         line_data["uwb_mac1_var"][0],
                         line_data["uwb_mac2_var"][0], line_data["uwb_mac3_var"][0],
                         line_data["uwb_mac4_var"][0], line_data["uwb_mac5_var"][0],
                         line_data["uwb_mac6_var"][0], line_data["uwb_mac7_var"][0],
                         line_data["uwb_mac8_var"][0], line_data["uwb_mac9_var"][0],
                         line_data["uwb_mac10_var"][0], line_data["uwb_mac11_var"][0],
                         line_data["uwb_mac12_var"][0], line_data["uwb_mac13_var"][0],
                         line_data["uwb_mac14_var"][0],
                         line_data["uwb_mac1_rate"],
                         line_data["uwb_mac2_rate"], line_data["uwb_mac3_rate"],
                         line_data["uwb_mac4_rate"], line_data["uwb_mac5_rate"],
                         line_data["uwb_mac6_rate"], line_data["uwb_mac7_rate"],
                         line_data["uwb_mac8_rate"], line_data["uwb_mac9_rate"],
                         line_data["uwb_mac10_rate"], line_data["uwb_mac11_rate"],
                         line_data["uwb_mac12_rate"], line_data["uwb_mac13_rate"],
                         line_data["uwb_mac14_rate"]]
                        )
    con.commit()
    cur.close()
    con.close()


def search_range_by_time_and_bltMac(time_range, bltMac, uwbMac):
    con = sqlite3.connect("../resources/database/uwb_data.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM original_data WHERE time >= ? and time <= ? and bltMac = ? and uwbMac = ?",
                         [time_range[0], time_range[1], bltMac, uwbMac])
    result = result.fetchall()
    # print(result)
    con.commit()
    cur.close()
    con.close()
    return result


def search_test_range_by_time_and_uwbMac(time_range, uwbMac):
    con = sqlite3.connect("../resources/database/uwb_data.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM test_data WHERE time >= ? and time <= ? and uwbMac = ?",
                         [time_range[0], time_range[1], uwbMac])
    result = result.fetchall()
    # print(result)
    con.commit()
    cur.close()
    con.close()
    return result

def search_range_and_rssi_by_time_and_uwbMac_bltMac(timestamp, bltMac, uwbMac):
    con = sqlite3.connect("../resources/database/uwb_data.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM original_data WHERE time = ?  and bltMac = ? and uwbMac = ?",
                         [f'{timestamp}', bltMac, uwbMac])
    result = result.fetchall()
    # print(result)
    con.commit()
    cur.close()
    con.close()
    return result


def search_coordinate_by_index(fp_index):
    con = sqlite3.connect("../resources/database/uwb_data.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM fingerprint1_data WHERE fp_index = ?",
                         [fp_index])
    result = result.fetchone()
    con.commit()
    cur.close()
    con.close()
    return [result[1], result[2]]


def search_signal_by_index(fp_index):
    con = sqlite3.connect("../resources/database/uwb_data.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM fingerprint1_data WHERE fp_index = ?",
                         [fp_index])
    result = result.fetchone()
    con.commit()
    cur.close()
    con.close()
    return [result[3], result[4],result[5],result[6],result[7],result[8],result[9],result[10],result[11],result[12]
            ,result[13],result[14],result[15],result[16]]

def search_sig_val_by_index(fp_index):
    con = sqlite3.connect("../resources/database/uwb_data.db")
    cur = con.cursor()
    result = cur.execute("SELECT * FROM fingerprint1_data WHERE fp_index = ?",
                         [fp_index])
    result = result.fetchone()
    con.commit()
    cur.close()
    con.close()
    return [result[17], result[18],result[19],result[20],result[21],result[22],result[23],result[24],result[25],result[26]
            ,result[27],result[28],result[29],result[30]]
if __name__ == '__main__':
    create_original_database("../resources/UWB_data/uwb-blt_data-0521.csv")
    create_test_database("../resources/UWB_data/uwb-blt_data-0521-2.csv")
    create_fingerprint_database("../resources/database/database1.txt")
    create_fingerprint_database("../resources/database/database2.txt")