#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：UWB
@File    ：draw_pictures.py
@IDE     ：PyCharm
@Author  ：lwb
@Date    ：2024/7/4 14:10
"""
import csv
import json

from matplotlib import pyplot as plt
import os
from cmath import sqrt
import DBTools
import get_uwb_data as gud
import UWB_location as ul

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
colors = ['r', 'm', 'g', 'c', 'b', 'violet', 'y', 'k', 'aquamarine', 'brown', 'chocolate', 'chartreuse', 'bisque',
          'gold']

TRUE_XY = [[5.198020502235384, 5.660212220407791], [5.816103459584049, 3.0523738703657726],
           [5.935271767031102, -0.2674310371266646], [5.840597818180661, -3.7332485402549427],
           [8.822592931172839, -3.723902739914535], [12.973737622939622, -3.7738698473805288],
           [16.784225349037, -3.346988480280501], [21.56073828440754, -3.3799288851806573],
           [25.314206728987017, -1.6000870659882818], [24.584564072896157, 0.9812890391754134],
           [25.18842090125616, 3.361262980273777], [24.188883946298375, 7.304565493113173],
           [22.039393404702103, 8.544871847894804], [18.96012877978167, 8.408889105858394],
           [14.311708980021546, 8.095109652528155], [9.367133134971198, 6.15709404360243],
           [9.803249448398443, 1.699308650613589], [12.303335295896073, -0.21622511478934836],
           [16.21850699414447, 1.1666249965017554], [21.018015919659184, 2.0450659654026975]]

TEST_START_TIME = [[1716271293, 1716271318], [1716271323, 1716271346], [1716271350, 1716271371],
                   [1716271375, 1716271401], [1716271404, 1716271433], [1716271439, 1716271468],
                   [1716271473, 1716271507], [1716271514, 1716271551], [1716271557, 1716271588],
                   [1716271591, 1716271619], [1716271622, 1716271657], [1716271662, 1716271684],
                   [1716271699, 1716271728], [1716271732, 1716271763], [1716271769, 1716271801],
                   [1716271807, 1716271836], [1716271848, 1716271874], [1716271879, 1716271905],
                   [1716271918, 1716271949], [1716271955, 1716271983]]

TEST_TRACK_TIME = [1716271293, 1716271983]


# TEST_TRACK_TIME = [1716271293, 1716271300]


# 绘制各控制点距离分布图、信号强度分布图
def plot_data(lidar_directory: str, blt_mac: str, is_range_plot: bool, is_rssi_plot: bool):
    """
        根据指纹点激光雷达文件，绘制距离分布图、信号强度分布图

        :param lidar_directory: 指纹点激光雷达文件所在目录
        :param is_range_plot: 是否绘制距离分布图
        :param is_rssi_plot: 是否绘制信号强度分布图
        :return: 无
    """
    # 存储各指纹点坐标
    fp_coordinates = []
    # 存储各指纹点数据的接收起止时间戳
    s_e_ts = []
    # 存储各UWB信标的mac
    uwb_macs = list(TEST_UWB_MAC.keys())
    # 获得每个指纹点的坐标及数据的接收起止时间戳
    for filename in os.listdir(lidar_directory):
        # 拼接激光雷达文件的完整路径
        lidar_filepath = os.path.join(lidar_directory, filename)
        # 获得文件中指纹点的坐标及数据的接收起止时间戳
        s_e_t, fp_coordinate = gud.find_fingerprint_point(lidar_filepath)
        for coordinate in fp_coordinate:
            fp_coordinates.append(coordinate)
        for each in s_e_t:
            s_e_ts.append([each[0], each[-1]])
    # 绘制距离分布图
    if is_range_plot:
        for i in range(len(fp_coordinates)):
            plt.figure(figsize=(12, 8))
            plt.title(fr"${i}$距离分布图")
            for mac_index in range(len(uwb_macs)):
                mac = uwb_macs[mac_index]
                # 根据时间范围、标签、信标从数据库选出数据
                result = DBTools.search_range_by_time_and_bltMac(s_e_ts[i], blt_mac, mac)
                point_index = []
                mac_range = []
                for index in range(len(result)):
                    point_index.append(index)
                    mac_range.append(result[index][3])
                if len(point_index) != 0:
                    # 绘制距离分布散点图
                    plt.scatter(point_index, mac_range, label=f"{TEST_UWB_MAC[mac]}", c=colors[mac_index])
            plt.xlabel("index")
            plt.ylabel("距离/mm")
            plt.ylim(0, 25000)
            plt.tight_layout()
            plt.legend()
            range_dir = f"../resources/{blt_mac[-3:]}range_plot"
            if not os.path.exists(range_dir):
                os.makedirs(range_dir)
            plt.savefig(f"{range_dir}/{i}距离分布图.jpg")  # 绘制并保存距离分布图
            plt.close()
    # 绘制信号强度分布图
    if is_rssi_plot:
        for j in range(len(fp_coordinates)):
            plt.figure(figsize=(12, 8))
            plt.title(fr"${j}$信号强度分布图")
            for mac_index in range(len(uwb_macs)):
                mac = uwb_macs[mac_index]
                # 根据时间范围、标签、信标从数据库选出数据
                result = DBTools.search_range_by_time_and_bltMac(s_e_ts[j], blt_mac, mac)
                point_index = []
                mac_rssi = []
                for index in range(len(result)):
                    point_index.append(index)
                    mac_rssi.append(result[index][5])
                if len(point_index) != 0:
                    # 绘制信号强度分布散点图
                    plt.scatter(point_index, mac_rssi, label=f"{TEST_UWB_MAC[mac]}", c=colors[mac_index])
            plt.xlabel("index")
            plt.ylabel("信号强度/db")
            plt.tight_layout()
            plt.legend()
            rssi_dir = f"../resources/{blt_mac[-3:]}rssi_plot"
            if not os.path.exists(rssi_dir):
                os.makedirs(rssi_dir)
            plt.savefig(f"{rssi_dir}/{j}信号强度分布图.jpg")  # 绘制并保存信号强度分布图
            plt.close()


# 绘制指纹点地图
def draw_fp_map():
    xs = []
    ys = []
    index = 0
    for file in (os.listdir("../resources/points1_data")):
        path = os.path.join(r"../resources/points1_data", f"{index}.json")
        line = open(path).readline()
        data = json.loads(line)
        index += 1
        # print(idx)
        xs.append(data['x'])
        ys.append(data['y'])
    for idx, (x, y) in enumerate(zip(xs, ys)):
        plt.scatter([x], [y])
        plt.text(x, y + 0.1, f"{idx}")
    # k=1
    # for coordinate in track_test.TRUR_XY:
    #     plt.scatter(coordinate[0],coordinate[1],color='black')
    #     plt.text(coordinate[0], coordinate[1]+0.1,f"{k}")
    #     k+=1
    map_dir = f"../resources/fp_map"
    if not os.path.exists(map_dir):
        os.makedirs(map_dir)
    plt.savefig(f"{map_dir}/指纹点.jpg")
    plt.close()


def draw_xy_picture(ppp, s_time, tmp_point_data, true_coordinate, calculate_coordinate, min_index_list,
                    min_distance_list):
    plt.rcParams['font.sans-serif'] = "Microsoft YaHei"
    plt.xlabel("x/m")
    plt.ylabel("y/m")
    # begin_min_x=100
    # begin_max_x=-100
    # begin_min_y=100
    # begin_max_y=-100
    # x_dir={}
    # y_dir={}
    x_list = []
    y_list = []
    true_xy_list = []
    # for index in min_index_list:
    #     tmp=DBTools.search_coordinate_by_index(index)
    #     true_xy_list.append(tmp)
    #     x_dir[index]=tmp[0]
    #     y_dir[index] = tmp[1]
    #     if(tmp[0]>begin_max_x):
    #         begin_max_x=tmp[0]
    #     if (tmp[0] < begin_min_x):
    #         begin_min_x = tmp[0]
    #     if (tmp[1] > begin_max_y):
    #         begin_max_y = tmp[1]
    #     if (tmp[1] < begin_min_y):
    #         begin_min_y = tmp[1]
    # plt.xlim(begin_min_x-2,begin_max_x+2)
    # plt.ylim(begin_min_y-2,begin_max_y+2)
    for index in min_index_list:
        tmp = DBTools.search_coordinate_by_index(index)
        true_xy_list.append(tmp)
        x_list.append(tmp[0])
        y_list.append(tmp[1])
    for i in range(0, len(min_index_list)):
        plt.text(x_list[i], y_list[i], f"{min_index_list[i]}")
    plt.scatter(x_list, y_list, color='blue')
    plt.scatter(true_coordinate[0], true_coordinate[1], color='black')
    plt.scatter(calculate_coordinate[0], calculate_coordinate[1], color='red')
    for k in range(0, len(true_xy_list)):
        tmp = true_xy_list[k]
        mid_x = (calculate_coordinate[0] + tmp[0]) / 2
        mid_y = (calculate_coordinate[1] + tmp[1]) / 2
        # 计算两点之间的距离
        distance = min_distance_list[k]
        # 标注距离
        plt.text(mid_x, mid_y, f"{distance:.2f}", ha='center', va='center')
    plt.legend(["指纹点", '真值', "计算值"], loc='best')
    if not os.path.exists(f'../resources/three_{s_time}/'):
        # 如果文件夹不存在，则创建它
        os.mkdir(f'../resources/three_{s_time}/')
    directory = f'../resources/three_{s_time}/'
    print(s_time)
    filename = f"{ppp}测试点{tmp_point_data}坐标解算效果图.png"
    filepath = os.path.join(directory, filename)
    plt.savefig(filepath)
    print("save")
    plt.close()


def draw_test_point(calculate_coordinate_list):
    plt.rcParams['font.sans-serif'] = "Microsoft YaHei"
    index = 1
    for tmp in TRUE_XY:
        plt.scatter(tmp[0], tmp[1], color='blue')
        plt.text(tmp[0], tmp[1] + 0.2, index)
        index += 1
    index = 1
    for tmp in calculate_coordinate_list:
        plt.scatter(tmp[0], tmp[1], color='red')
        plt.text(tmp[0], tmp[1] + 0.2, index)
        index += 1
    plt.savefig('./test_pic_mid_7.png')
    plt.close()


def draw_testpoint_time_range(index):
    begin = TEST_START_TIME[index][0]
    end = TEST_START_TIME[index][1]
    plt.xlabel('m/x')
    plt.ylabel('m/y')
    plt.xlim(2, 27)
    plt.ylim(-4, 10)
    plt.scatter(TRUE_XY[index][0], TRUE_XY[index][1], color='black')
    for s_time in range(begin, end + 1):
        point = ul.get_point_data([s_time, s_time])
        need_tuple = ul.calculate_point_coordinate(point)
        calculate_coordinate = ul.calculate_xy_delone(need_tuple[0], need_tuple[1])
        plt.scatter(calculate_coordinate[0], calculate_coordinate[1], color='red')
    plt.savefig(f'../resources/20_13/{index + 1}.png')
    plt.close()

# 对20个测试点选取最好的单点结果进行展示
def draw_test_best():
    min_distance_coordinate = []
    for index in range(0, 20):
        begin = TEST_START_TIME[index][0]
        end = TEST_START_TIME[index][1]
        true_x = TRUE_XY[index][0]
        true_y = TRUE_XY[index][1]
        min_distance = 5.0
        min_coordinate = [[0, 0]]
        for s_time in range(begin, end + 1):
            point = ul.get_point_data([s_time, s_time])
            need_tuple = ul.calculate_point_coordinate(point)
            calculate_coordinate = ul.calculate_xy_delone(need_tuple[0], need_tuple[1])
            tmp_distance = sqrt((calculate_coordinate[0] - true_x) ** 2 + (calculate_coordinate[1] - true_y) ** 2).real
            if (tmp_distance < min_distance):
                min_distance = tmp_distance
                min_coordinate[0] = calculate_coordinate
        min_distance_coordinate.append(min_coordinate[0])
        draw_test_point(min_distance_coordinate)

# 217指纹点匹配指纹点_单点统计特性_387
def draw_fp_test():
    # fp_index_list=[13,36,54,122,128,145,163,176,187,90,102,110,208,201,195]
    fp_index_list = range(0, 217)
    true_xy = []
    mean_xy = []
    mean_point_data = []
    distance_list = []
    for index in fp_index_list:
        true_coordinate = DBTools.search_coordinate_by_index(index)
        true_xy.append(true_coordinate)
        with open(f'../resources/points1_data/{index}.json') as file:
            sum_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            lines = file.readlines()
            if (len(lines) >= 41):
                lines = lines[11:41]
            else:
                lines = lines[11:]
            tmp_point_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            for line in lines:
                line_directory = json.loads(line)
                for i in range(0, 14):
                    data = line_directory[f'MAC{i + 1}_range']
                    if data != 0:
                        sum_list[i] += 1
                        tmp_point_data[i] += data
            for i in range(0, 14):
                if sum_list[i] == 0:
                    tmp_point_data[i] = 0
                else:
                    tmp_point_data[i] /= sum_list[i]
            mean_point_data.append(tmp_point_data)
    for point in mean_point_data:
        need_tuple = ul.calculate_point_coordinate(point)
        calculate_coordinate = ul.calculate_xy_delone(need_tuple[0], need_tuple[1])
        mean_xy.append(calculate_coordinate)
    for k in range(0, len(true_xy)):
        tmp_true_xy = true_xy[k]
        tmp_mean_xy = mean_xy[k]
        tmp_index = fp_index_list[k]
        plt.scatter(tmp_true_xy[0], tmp_true_xy[1], color='black')
        plt.scatter(tmp_mean_xy[0], tmp_mean_xy[1], color='red')
        distance_list.append(sqrt((tmp_mean_xy[0] - tmp_true_xy[0]) ** 2 + (tmp_mean_xy[1] - tmp_true_xy[1]) ** 2).real)
        plt.text(tmp_true_xy[0], tmp_true_xy[1] + 0.1, f"{tmp_index}")
        plt.text(tmp_mean_xy[0], tmp_mean_xy[1] + 0.1, f"{tmp_index}")
    plt.savefig('../resources/testpoint_single_location/387/指纹点匹配指纹点_单点统计特性_387.png')
    plt.close()
    # 对误差大于1m的点进行输出
    for l in range(0, len(fp_index_list)):
        if distance_list[l] > 1:
            print(f"{fp_index_list[l]}:{distance_list[l]}")

# 对15个指纹点进行单点分析而不是用统计特性
def draw_fg_range():
    fp_index_list = [13, 36, 54, 122, 128, 145, 163, 176, 187, 90, 102, 110, 208, 201, 195]
    sum = 0
    # fp_index_list = [176]
    for index in fp_index_list:
        true_coordinate = DBTools.search_coordinate_by_index(index)
        with open(f'../resources/points1_data/{index}.json') as file:
            deviation_list = []
            lines = file.readlines()
            if len(lines) >= 41:
                lines = lines[11:41]
            else:
                lines = lines[11:]
            for line in lines:
                tmp_point_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                line_directory = json.loads(line)
                for i in range(0, 14):
                    data = line_directory[f'MAC{i + 1}_range']
                    tmp_point_data[i] = data
                need_tuple = ul.calculate_point_coordinate(tmp_point_data)
                # print(need_tuple)
                if len(need_tuple[0]) != 0 and len(need_tuple[1]) != 0:
                    calculate_coordinate = ul.calculate_xy_delone(need_tuple[0], need_tuple[1])
                    deviation = sqrt((calculate_coordinate[0] - true_coordinate[0]) ** 2 + (
                            calculate_coordinate[1] - true_coordinate[1]) ** 2).real
                    deviation_list.append(
                        deviation)
                    sum += deviation
                else:
                    deviation_list.append(0)
            plt.ylim(0, 4)

            plt.scatter(range(0, len(lines)), deviation_list)
            if not os.path.exists(f"../resources/testpoint_single_location/387/15_9_387/"):
                os.mkdir(f"../resources/testpoint_single_location/387/15_9_387/")
            plt.savefig(f"../resources/testpoint_single_location/387/15_9_387/{index}.png")
            plt.close()
    print(sum)

# 展示匹配到最近的三个指纹点
def draw_threefp():
    fp_index_list = [118, 119]  # ,128,163,176,187,208,195
    for index in fp_index_list:
        true_coordinate = DBTools.search_coordinate_by_index(index)
        with open(f'../resources/points1_data/{index}.json') as file:
            lines = file.readlines()
            if len(lines) >= 41:
                lines = lines[11:41]
            else:
                lines = lines[11:]
            ppp = 1
            for line in lines:
                tmp_point_data = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                line_directory = json.loads(line)
                for i in range(0, 13):
                    data = line_directory[f'MAC{i + 1}_range']
                    tmp_point_data[i] = data
                need_tuple = ul.calculate_point_coordinate(tmp_point_data)
                calculate_coordinate = ul.calculate_xy_delone(need_tuple[0], need_tuple[1])
                print(calculate_coordinate)
                draw_xy_picture(ppp, index, tmp_point_data, true_coordinate, calculate_coordinate, need_tuple[0],
                                need_tuple[1])
                ppp += 1

# 20个测试点取中间值的单点并根据可信度进行筛选
def draw_mean_20_test():
    index = 1
    for tmp in TRUE_XY:
        plt.text(tmp[0], tmp[1] + 0.2, index)
        plt.scatter(tmp[0], tmp[1],color='black')
        index += 1
    index = 1
    # 用来对真值进行索引
    count=0
    for time in TEST_START_TIME:
        point = ul.get_point_data([(time[0] + time[1]) // 2, (time[0] + time[1]) // 2])
        need_tuple = ul.calculate_point_coordinate(point)
        # print(need_tuple)
        calculate_coordinate = ul.calculate_xy_delone(need_tuple[0], need_tuple[1])
        # 计算误差
        deviation = sqrt((calculate_coordinate[0] - TRUE_XY[count][0]) ** 2 + (
                calculate_coordinate[1] -TRUE_XY[count][1]) ** 2).real
        count+=1
        rate1=1/need_tuple[1][0]/(1/need_tuple[1][0]+1/need_tuple[1][1]+1/need_tuple[1][2])
        rate2=1/need_tuple[1][1]/(1/need_tuple[1][0]+1/need_tuple[1][1]+1/need_tuple[1][2])
        rate3=1/need_tuple[1][2]/(1/need_tuple[1][0]+1/need_tuple[1][1]+1/need_tuple[1][2])
        calculate_coordinate_distance=rate1*need_tuple[1][0]+rate2*need_tuple[1][1]+rate3*need_tuple[1][2]
        print(need_tuple," ",rate1," ",
              rate2," ",
              rate3," ",
            deviation, " ",
              calculate_coordinate_distance, " "
              ,ul.calculate_reliability(need_tuple,calculate_coordinate_distance))
        plt.text(calculate_coordinate[0], calculate_coordinate[1] + 0.2, index)
        plt.scatter(calculate_coordinate[0], calculate_coordinate[1],color='red')
        index += 1
    plt.savefig('../resources/testpoint_single_location/387/mid_point_20.png')
    plt.close()

# 20个测试点的单点测试非统计特性结果
def draw_all_20_test():
    index = 0
    all = 0
    for time in TEST_START_TIME:
        true_coordinate = TRUE_XY[index]
        dir = f"../resources/testpoint_single_location/387/{time}.png"
        deviation_list = []
        for tmp in range(time[0], time[0] + 15):
            point = ul.get_point_data([tmp, tmp])
            need_tuple = ul.calculate_point_coordinate(point)
            if len(need_tuple[0]) != 0 and len(need_tuple[1]) != 0:
                calculate_coordinate = ul.calculate_xy_delone(need_tuple[0], need_tuple[1])
                deviation = sqrt((calculate_coordinate[0] - true_coordinate[0]) ** 2 + (
                        calculate_coordinate[1] - true_coordinate[1]) ** 2).real
                deviation_list.append(deviation)
                all += deviation
            else:
                deviation_list.append(0)
        plt.scatter(range(0, len(deviation_list)), deviation_list, color='blue')
        plt.ylim(0, 5)
        plt.savefig(f"{dir}")
        plt.close()
        index += 1
    print(all)

# 轨迹
def draw_track():
    calculate_coordinate_list = []
    true_xy = []
    need_cal_time = []
    for i in range(len(TEST_START_TIME) - 1):
        mid = int((TEST_START_TIME[i][-1] + TEST_START_TIME[i][0]) / 2)
        need_cal_time.append(mid)
        for j in range(TEST_START_TIME[i][-1] + 1, TEST_START_TIME[i + 1][0]):
            need_cal_time.append(j)
    last_point_time = int((TEST_START_TIME[-1][-1] + TEST_START_TIME[-1][0]) / 2)
    need_cal_time.append(last_point_time)
    print(len(need_cal_time))
    print(need_cal_time)

    index = 1
    for cal_time in need_cal_time:
        print(index)
        index += 1
        point = ul.get_point_data([cal_time, cal_time])
        print(point)
        need_tuple = ul.calculate_point_coordinate(point)
        print(need_tuple)
        calculate_coordinate = ul.calculate_xy_delone(need_tuple[0], need_tuple[1])
        calculate_coordinate_list.append(calculate_coordinate)


    plt.rcParams['font.sans-serif'] = "Microsoft YaHei"
    with open('../resources/LiDAR_test/test_points.txt', 'r', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=' ')  # 如果是 tab 分隔符，修改 delimiter='\t'
        # header = next(reader)  # 读取并跳过首行，如果有标题行的话
        selected_rows = []
        for row in reader:
            try:
                second_column_value = float(row[1])  # 假设第二列的值是数值型的，索引从0开始
                if need_cal_time[0] <= second_column_value <= need_cal_time[-1]+1:
                    selected_rows.append(row)
                    true_xy.append([float(row[2]), float(row[3])])
            except (IndexError, ValueError):
                continue  # 如果第二列的值无法转换成数值型，或者索引超出范围，跳过该行
    index = 1
    for tmp in true_xy:
        plt.scatter(tmp[0], tmp[1], color='blue')
        index += 1
    index = 1
    for tmp in calculate_coordinate_list:
        plt.scatter(tmp[0], tmp[1], color='red')
        plt.text(tmp[0], tmp[1] + 0.2, index)
        index += 1
    plt.show()


if __name__ == '__main__':

    draw_mean_20_test()
