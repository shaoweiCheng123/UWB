#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：UWB
@File    ：UWB_location.py
@IDE     ：PyCharm
@Author  ：lwb
@Date    ：2024/7/4 11:28
"""

import csv
import jsons
import os
from cmath import sqrt

from matplotlib import pyplot as plt

import DBTools
import numpy as np
from scipy import stats
from sklearn.metrics.pairwise import cosine_similarity
import pytz
from datetime import datetime

TEST_BLT_MAC = "1918B2011387"  # 测试标签编号
# TEST_BLT_MAC = "1918B2011394"  # 测试标签编号
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
                '1918FD00C4E7': 'MAC14'}
UWB_MAC_NUMBER = 14

TEST_START_TIME = [[1716271293, 1716271318], [1716271323, 1716271346], [1716271350, 1716271371], [1716271375, 1716271401], [1716271404, 1716271433], [1716271439, 1716271468], [1716271473, 1716271507], [1716271514, 1716271551], [1716271557, 1716271588], [1716271591, 1716271619], [1716271622, 1716271657], [1716271662, 1716271684], [1716271699, 1716271728], [1716271732, 1716271763], [1716271769, 1716271801], [1716271807, 1716271836], [1716271848, 1716271874], [1716271879, 1716271905], [1716271918, 1716271949], [1716271955, 1716271983]]

TRUR_XY = [[5.198020502235384, 5.660212220407791], [5.816103459584049, 3.0523738703657726], [5.935271767031102, -0.2674310371266646], [5.840597818180661, -3.7332485402549427], [8.822592931172839, -3.723902739914535], [12.973737622939622, -3.7738698473805288], [16.784225349037, -3.346988480280501], [21.56073828440754, -3.3799288851806573], [25.314206728987017, -1.6000870659882818], [24.584564072896157, 0.9812890391754134], [25.18842090125616, 3.361262980273777], [24.188883946298375, 7.304565493113173], [22.039393404702103, 8.544871847894804], [18.96012877978167, 8.408889105858394], [14.311708980021546, 8.095109652528155], [9.367133134971198, 6.15709404360243], [9.803249448398443, 1.699308650613589], [12.303335295896073, -0.21622511478934836], [16.21850699414447, 1.1666249965017554], [21.018015919659184, 2.0450659654026975]]


# 计算测试点的各基站数据平均值，作为该点的数据
def get_point_data(time_range):
    point_data = []
    for uwb_mac in list(TEST_UWB_MAC.keys()):
        original_point_data = DBTools.search_test_range_by_time_and_uwbMac([time_range[0], time_range[1]], uwb_mac)
        range_data = [test_range[3] for test_range in original_point_data]
        new_range = []
        for tmp in range_data:
            if tmp != 0:
                new_range.append(tmp)
        mean_range = 0
        if len(new_range) != 0:
            mean_range = np.mean(new_range)
        point_data.append(mean_range)
    return point_data


# 根据单点uwb样本数据，得到单点定位匹配的距离最近的几个指纹点
def calculate_point_coordinate(point_data):  # point_data[range_1-range_14], return [x, y]
    with open("../resources/database/database1.txt") as db:
        lines = db.readlines()
        distances = {}
        for line in lines:
            json_line = jsons.loads(line)
            distance = 0
            use_mac_num: int = 0
            stand_index=[]
            available_mac_range = {}
            available_mac_index = []
            mylist=[1,2,3,4,5,6,7,8,10]
            # mylist = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
            # 记录样本数据中不为0的信标序号
            for i in mylist:
                if point_data[i-1] != 0:
                    available_mac_index.append(i)
            # 记录指纹库数据中不为0的信标序号
            for i in mylist:
                if len(json_line[f"uwb_mac{i}_mean"]) != 0 and json_line[f"uwb_mac{i}_mean"][0] != 0:
                    stand_index.append(i)
            # 记录样本数据和指纹库数据都不为0的信标指纹数据
            for i in available_mac_index:
                if len(json_line[f"uwb_mac{i}_mean"]) != 0 and json_line[f"uwb_mac{i}_mean"][0] != 0:
                    fp_mean = json_line[f"uwb_mac{i}_mean"][0]
                    available_mac_range[f"uwb_mac{i}_mean"] = fp_mean
            # 如果交集信标数少于等于2，则不与该指纹点进行匹配
            if len(available_mac_range) <= 2:
                continue
            # 记录测试点比指纹点多出来的基站信号个数
            count=0
            for tmp in available_mac_index:
                if(tmp not in stand_index):
                    count+=1

            if available_mac_range:
                min_range_value = min(available_mac_range.values())
                # 记录指纹点比测试点多出来的基站信号个数
                lack_list=[]
                for i in stand_index:
                    fp_mean = json_line[f"uwb_mac{i}_mean"][0]
                    fp_var = json_line[f"uwb_mac{i}_var"][0]
                    if i not in available_mac_index:  # 对于该指纹来说，i信标缺失数据
                        lack_list.append(i)
                    else:
                        if fp_var > 1000000:
                            distance_possibility = min_range_value / available_mac_range[f"uwb_mac{i}_mean"]
                            distance += abs(point_data[i - 1] - fp_mean) * distance_possibility  # 计算距离
                        else:
                            use_mac_num += 1
                            # print(point_data[i-1], " ", fp_mean)
                            distance += abs(point_data[i - 1] - fp_mean)

                if use_mac_num != 0:
                    # 先对测试点多出来的信号个数进行惩罚
                    distance = (1.1 ** (len(stand_index)+len(available_mac_index)-2*len(available_mac_range)))* distance
                    # 再对指纹点多出来的信号个数进行惩罚
                    # for tmp in lack_list:
                    #     distance+=json_line[f"uwb_mac{i}_mean"][0]*json_line[f"uwb_mac{i}_rate"]
                    distances[f"{json_line['index']}"] = distance / use_mac_num
                else:
                    distances[f"{json_line['index']}"] = distance

        min_coordinates = []
        min_index_list=[]
        min_distance_list=[]
        while len(min_coordinates) < 4 and distances:
            min_distance_value = min(distances.values())
            if min_distance_value == 0:
                min_distance_key = [key for key, value in distances.items() if value == min_distance_value][0]
                del distances[min_distance_key]
                continue

            min_distance_key = [key for key, value in distances.items() if value == min_distance_value][0]
            min_index_list.append(min_distance_key)
            min_distance_list.append(min_distance_value)

            min_coordinates.append(DBTools.search_coordinate_by_index(min_distance_key))
            del distances[min_distance_key]
        # print(min_coordinates)
        return min_index_list, min_distance_list


# 根据匹配到的几个最近指纹点，得到最终单点定位坐标
def calculate_xy(min_index_list,min_distance_list):
    sum_distance = 0.0
    for distance in min_distance_list:
        sum_distance += 1/distance
    i = 0
    true_x = 0.0
    true_y = 0.0
    while i < len(min_index_list):
        true_x += DBTools.search_coordinate_by_index(min_index_list[i])[0]*(1/min_distance_list[i]) / sum_distance
        true_y += DBTools.search_coordinate_by_index(min_index_list[i])[1]*(1/min_distance_list[i]) / sum_distance
        i+=1
    return [true_x,true_y]


# 根据匹配到的几个最近指纹点，删去物理上离群最远的指纹点，得到最终单点定位坐标
def calculate_xy_delone(min_index_list,min_distance_list):
    true_xy_list=[]
    for index in min_index_list:
        true_xy_list.append(DBTools.search_coordinate_by_index(index))
    max_index=-1
    max_dis=-1
    for i in range(0,len(min_index_list)):
        sum_dis=0.0
        point1=true_xy_list[i]
        for j in range(0,len(min_index_list)):
            if i != j:
                point2=true_xy_list[j]
                sum_dis+=sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2).real
        if sum_dis>max_dis:
            max_dis=sum_dis
            max_index=i
    # del min_index_list[max_index]
    # del min_distance_list[max_index]
    if len(min_index_list) > 0:
        del min_index_list[-1]
        del min_distance_list[-1]
    return calculate_xy(min_index_list,min_distance_list)

# 计算特定的某个信号与特定的指纹点之间的观测距离
def calculate_see_dis(fp_index,signal):
    mylist = [1, 2, 3, 4, 5, 6, 7, 8, 10]
    fp_signal=DBTools.search_signal_by_index(fp_index)
    fp_signal_val=DBTools.search_signal_by_index(fp_index)
    distance = 0
    use_mac_num: int = 0
    stand_index = []
    available_mac_range = {}
    available_mac_index = []
    # 记录样本数据中不为0的信标序号
    for i in mylist:
        if signal[i - 1] != 0:
            available_mac_index.append(i)
    # 记录指纹库数据中不为0的信标序号
    for i in mylist:
        if fp_signal[i - 1] != 0:
            stand_index.append(i)
    # 记录样本数据和指纹库数据都不为0的信标指纹数据
    for i in available_mac_index:
        if i in stand_index:
            fp_mean = fp_signal[i]
            available_mac_range[f"uwb_mac{i}_mean"] = fp_mean
    # 如果交集信标数少于等于2，则不与该指纹点进行匹配
    if len(available_mac_range) <= 2:
        return 4000
    # 记录测试点比指纹点多出来的基站信号个数
    count = 0
    for tmp in available_mac_index:
        if (tmp not in stand_index):
            count += 1

    if available_mac_range:
        min_range_value = min(available_mac_range.values())
        # 记录指纹点比测试点多出来的基站信号个数
        lack_list = []
        for i in stand_index:
            fp_mean = fp_signal[i]
            fp_var =  fp_signal_val[i]
            if i not in available_mac_index:  # 对于该指纹来说，i信标缺失数据
                lack_list.append(i)
            else:
                if fp_var > 1000000:
                    distance_possibility = min_range_value / available_mac_range[f"uwb_mac{i}_mean"]
                    distance += abs(signal[i - 1] - fp_mean) * distance_possibility  # 计算距离
                else:
                    use_mac_num += 1
                    # print(point_data[i-1], " ", fp_mean)
                    distance += abs(signal[i - 1] - fp_mean)

        if use_mac_num != 0:
            # 先对测试点多出来的信号个数进行惩罚
            distance = (1.1 ** (len(stand_index) + len(available_mac_index) - 2 * len(available_mac_range))) * distance
            # 再对指纹点多出来的信号个数进行惩罚
            # for tmp in lack_list:
            #     distance+=json_line[f"uwb_mac{i}_mean"][0]*json_line[f"uwb_mac{i}_rate"]
        return distance / use_mac_num


# 计算定位结果的可信度
def calculate_reliability(need_tuple,calculate_coordinate_distance):
    true_xy=[]
    for tmp in need_tuple[0]:
        true_xy.append(DBTools.search_coordinate_by_index(tmp))
    min_distance=10
    min_each_sum=-1
    for i in range(0,len(true_xy)):
        tmp_distance=0
        tmp_each=[]
        for j in range(0,len(true_xy)):
            if(i!=j):
                dis=sqrt((true_xy[i][0] - true_xy[j][0]) ** 2 + (true_xy[i][1] - true_xy[j][1]) ** 2).real
                tmp_distance+=dis
                tmp_each.append(dis)

        if(tmp_distance<min_distance):
            min_distance=tmp_distance
            min_each_sum=tmp_each[0]+tmp_each[1]

    return min_each_sum

if __name__ == '__main__':
    for tmp in range(TEST_START_TIME[10][0],TEST_START_TIME[10][1]):
        calculate_point_coordinate(get_point_data([tmp,tmp]))