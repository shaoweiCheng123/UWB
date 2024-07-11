#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：UWB
@File    ：get_uwb_data.py
@IDE     ：PyCharm
@Author  ：lwb
@Date    ：2024/7/4 9:58
"""

import csv
import time
from typing import Tuple, List, Any
import numpy as np
import os
import json
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
import DBTools

TEST_BLT_MAC = "1918B2011387"  # 帽子标签编号
TEST_BLT_MAC2 = "1918B2011394"  # 裤兜标签编号
TEST_UWB_MAC = {"1918FD00C4FD": "MAC1",
                "1918FD00C5FE": "MAC2",
                "1918FD00C4D4": "MAC3",
                "1918FD00C4FB": "MAC4",
                "1918FD00C4FC": "MAC5",
                "1918FD00C618": "MAC6",
                "1918FD00C4DE": "MAC7",
                "1918FD00C569": "MAC8",
                "1918FD00C476": "MAC9",
                "1918FD00C44E": "MAC10",
                "1918FD00C478": "MAC11",
                "1918FD00C4DF": "MAC12",
                "1918FD00C4DD": "MAC13",
                '1918FD00C4E7': 'MAC14'
                }  # 14个信标id
UWB_MAC_NUMBER = 14  # 信标数量
CLUSTER_NUMBER = 1  # 预定义KMeans聚类数量
CLUSTER_POINTS = 20  # 预定义一个聚类至少应该包含的样本点数
MERGE_THRESHOLD = 1000.0  # 聚类合并门限值
FINGER_FILE = '../resources/database/database1.txt'  # 指纹库默认位置
FINGER_FILE2 = '../resources/database/database2.txt'  # 指纹库默认位置
colors = ['r', 'm', 'g', 'c', 'b', 'violet', 'y', 'k', 'aquamarine', 'brown', 'chocolate', 'chartreuse', 'bisque',
          'gold']
plt.rcParams['font.sans-serif'] = 'SimHei'
plt.rcParams['axes.unicode_minus'] = False


def find_fingerprint_point(file_path: str):
    """
        对激光雷达数据进行切片，得到各指纹点的坐标与UWB采数时间范围
        :param file_path: 激光雷达数据文件
        :return start_and_end_time: 文件中各指纹点数据的接收的起止时间
        :return coordinates: 文件中各指纹点坐标
    """
    start_and_end_time = []
    coordinates = []
    times = []
    xs = []
    ys = []
    with open(file_path, "r") as txt_file:
        lines = txt_file.readlines()
        # next(lines)
        for line in lines:
            str_list = line.split()
            if len(str_list) >= 4:
                times.append(int(float(str_list[1])))
                xs.append(float(str_list[2]))
                ys.append(float(str_list[3]))
    id_s = []
    x_s = []
    y_s = []
    pointer = 0
    while pointer < len(xs):
        for i in range(pointer, len(xs)):
            if len(x_s) == 0:
                x_s.append(xs[i])
                y_s.append(ys[i])
            else:
                if abs(max(x_s) - min(x_s)) > 0.25 or abs(max(y_s) - min(y_s)) > 0.25:
                    if times[i] - times[id_s[0]] > 20:
                        cp_x = np.mean(x_s)
                        cp_y = np.mean(y_s)
                        if len(coordinates) != 0 and abs(cp_x - coordinates[-1][0]) < 0.5 and abs(
                                cp_y - coordinates[-1][1]) < 0.5:
                            cp_x = (cp_x + coordinates[-1][0]) / 2
                            cp_y = (cp_y + coordinates[-1][1]) / 2
                            s_and_e_time = [start_and_end_time[-1][0], times[i]]
                            coordinates = coordinates[:-1]
                            start_and_end_time = start_and_end_time[0:-1]
                            start_and_end_time.append(s_and_e_time)
                            coordinates.append([cp_x, cp_y])
                            # print("第", len(coordinates))
                        else:
                            start_and_end_time.append([times[id_s[0]], times[i]])
                            coordinates.append([cp_x, cp_y])
                        pointer = i + 1
                    else:
                        pointer = id_s[0] + 2
                    id_s = []
                    x_s = []
                    y_s = []
                    break
                else:
                    id_s.append(i)
                    x_s.append(float(xs[i]))
                    y_s.append(float(ys[i]))
        pointer += 1
    return start_and_end_time, coordinates


# 对激光雷达数据切片，得到各指纹点坐标及采数时间范围，根据时间范围对UWB原始数据文件进行切片与处理，得到各指纹点的UWB原始数据与坐标的文件
def process_point_data_file(lidar_directory: str, save_directory: str, blt_mac: str):
    """
        将激光雷达数据文件转化为若干个单个指纹点的文件
        :param lidar_directory: 激光雷达数据文件目录
        :param save_directory: 指纹点数据文件存储目录
    """
    cp_coordinates = []
    s_e_ts = []
    for filename in os.listdir(lidar_directory):
        # 拼接文件的完整路径
        filepath = os.path.join(lidar_directory, filename)
        s_e_t, cp_coordinate = find_fingerprint_point(filepath)
        for coordinate in cp_coordinate:
            cp_coordinates.append(coordinate)
        for each in s_e_t:
            s_e_ts.append(each)
    for point_index in range(len(cp_coordinates)):
        for each_second in range(s_e_ts[point_index][0], s_e_ts[point_index][1]):
            point_data = {
                'timestamp': each_second,
                'x': cp_coordinates[point_index][0],
                'y': cp_coordinates[point_index][1],
            }
            point_data2 = {
                'timestamp': each_second,
                'x': cp_coordinates[point_index][0],
                'y': cp_coordinates[point_index][1],
            }
            for uwb_mac in list(TEST_UWB_MAC.keys()):
                result = DBTools.search_range_and_rssi_by_time_and_uwbMac_bltMac(each_second, blt_mac, uwb_mac)
                if len(result) == 0:
                    point_data[f'{TEST_UWB_MAC[uwb_mac]}_range'] = 0
                    point_data[f'{TEST_UWB_MAC[uwb_mac]}_rssi'] = -100
                    point_data2[f'{TEST_UWB_MAC[uwb_mac]}_range'] = 0
                    point_data2[f'{TEST_UWB_MAC[uwb_mac]}_rssi'] = -100
                else:
                    point_data[f'{TEST_UWB_MAC[uwb_mac]}_range'] = result[0][3]
                    point_data[f'{TEST_UWB_MAC[uwb_mac]}_rssi'] = result[0][5]
                    if len(result) > 1:
                        point_data2[f'{TEST_UWB_MAC[uwb_mac]}_range'] = result[1][3]
                        point_data2[f'{TEST_UWB_MAC[uwb_mac]}_rssi'] = result[1][5]
                    else:
                        point_data2[f'{TEST_UWB_MAC[uwb_mac]}_range'] = result[0][3]
                        point_data2[f'{TEST_UWB_MAC[uwb_mac]}_rssi'] = result[0][5]
            with open(f'{save_directory}/{point_index}.json', 'a') as json_file:
                json_string = json.dumps(point_data)
                json_file.write(json_string)
                json_file.write('\n')
                json_string = json.dumps(point_data2)
                json_file.write(json_string)
                json_file.write('\n')


# 对单个指纹点单基站的原始数据进行聚类，得到指纹特征（目前聚类数量为1，即没有聚类，直接取平均值）
def merge_cluster(cluster_data: list, threshold: float = MERGE_THRESHOLD) -> list:
    """
    合并聚类, 按照阈值合并当前聚类, 减少不必要的冗余

    :param cluster_data: 原始聚类数据
    :param threshold:    阈值
    :return:             合并后的聚类数据
    """
    sorted(cluster_data)
    idx = 0
    length = len(cluster_data)

    merged_data = []

    while idx < length:
        # 待合并聚类值
        merged_val = cluster_data[idx]
        idx += 1
        merged_len = 1
        while idx < length and abs(cluster_data[idx] - merged_val) <= threshold:
            # idx和idx - 1两个聚类值的距离小于门限值, 需要合并
            merged_val = merged_val + cluster_data[idx]
            merged_len += 1

        merged_data.append(merged_val / merged_len)

    return merged_data


# 对单个指纹点单个基站接收的原始数据进行处理，得到单个指纹点该基站的指纹特征
def data_analyze(data: np.ndarray, n_clusters: int = CLUSTER_NUMBER,
                 threshold: float = MERGE_THRESHOLD, cluster_points: int = CLUSTER_POINTS):
    if not np.any(data):
        # 如果数据均为0
        return [0], [0], 0

    total_num = len(data)
    data = data[data != 0]
    no_zero_num = len(data)
    rate = no_zero_num / total_num
    model = KMeans(n_clusters, n_init=10)
    try:
        label = model.fit_predict(data.reshape(-1, 1))
    except Exception as e:
        label = np.zeros_like(data)
        print(e)

    means = []
    variances = []
    # 对于每一类数据计算均值
    for lb in np.unique(label):
        # print("length", len(data[label == lb]))
        if len(data[label == lb]) >= cluster_points:  # 若采集的数据量大于一定个数，才进行统计，数据太少则忽略该数据
            l_data = data[label == lb]  # 筛选该类数据
            # means.append(round(l_data.mean(), 2))
            # variances.append(round(np.var(l_data), 2))
            z_scores = np.abs((l_data - np.mean(l_data)) / np.std(l_data))  # 使用Z-Score方法筛去离群值
            filtered_data = l_data[z_scores < 2]  # 筛去差值大于2个标准差的数
            if len(filtered_data) >= 40:
                means.append(round(filtered_data[:40].mean(), 2))
                variances.append(round(np.var(filtered_data[:40]), 2))
            else:
                means.append(round(filtered_data.mean(), 2))
                variances.append(round(np.var(filtered_data), 2))
    if len(means) == 0:
        return [0], [0], 0
    return merge_cluster(means, threshold), variances, rate


# 处理每个指纹点的数据，生成指纹库，文件存入database.txt
def process_fingerprint_data(data_list_file_path: str, database_file_path: str):
    for data_file in os.listdir(data_list_file_path):
        point_index = int(data_file.split(".")[0])  # 指纹点编号
        true_x, true_y = -1, -1
        with open(f"{data_list_file_path}/{data_file}", "r") as data:
            file_data = data.readlines()
            first_line = json.loads(file_data[0])
            true_x = first_line["x"]
            true_y = first_line["y"]
            if len(file_data) > 0:
                cell_range_data = np.zeros((14, len(file_data)))
                cell_rssi_data = np.zeros((14, len(file_data)))
                for idx, line in enumerate(file_data):
                    dict_data = json.loads(line)
                    for i in range(1, UWB_MAC_NUMBER + 1):
                        cell_range_data[i - 1][idx] = dict_data[f'MAC{i}_range']
                        cell_rssi_data[i - 1][idx] = dict_data[f'MAC{i}_rssi']

                fingerprint_dict = {
                    'index': point_index,
                    'true_x': true_x,
                    'true_y': true_y
                }

                for i in range(UWB_MAC_NUMBER):
                    mean_vals, var_vals, rate = data_analyze(cell_range_data[i], n_clusters=CLUSTER_NUMBER,
                                                             threshold=MERGE_THRESHOLD, cluster_points=CLUSTER_POINTS)
                    fingerprint_dict[f'uwb_mac{i + 1}_mean'] = mean_vals
                    fingerprint_dict[f'uwb_mac{i + 1}_var'] = var_vals
                    fingerprint_dict[f'uwb_mac{i + 1}_rate'] = rate

                with open(database_file_path, 'a') as fp:
                    fp.write(json.dumps(fingerprint_dict) + '\n')


if __name__ == '__main__':
    process_point_data_file("../resources/LiDAR_data", "../resources/points2_data", TEST_BLT_MAC2)
    process_fingerprint_data("../resources/points2_data", FINGER_FILE2)
