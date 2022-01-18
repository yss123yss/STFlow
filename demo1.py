# -*- coding: utf-8 -*-
"""
Created on Tue Aug 31 20:31:16 2021

@author: SYue
"""
import os
import pandas as pd
import numpy as np
from streamdatahandle import streamdatahandle
from streamflowhandle import streamflowhandle
from flowvisualhandle import flowvisualhandle



def oridata_draw(ori_path):
    #加载CSV数据
    try:
        stream_data = pd.read_csv(ori_path)
    except Exception as e:
        print(e)
        print("无法打开文件！")      
    
    #利用stream数据构建Stream Handle。注意Header的设置，retweeted_x和retweeted_y表示转发自谁，x,y表示转发者
    stream_handle = streamdatahandle(stream_data,"T","re_x","re_y","x","y")
    
    #利用Stream Handle，对数据进行统计分析，60*60*24表示按照秒来进行统计
    statistical_info = stream_handle.get_statistical_info('2014-08-21','2014-12-18',60*60*24*30)
    
    #利用Stream Handle，对数据进行时间区间的裁切，从而获取一段时间内的数据
    stream_data_sliced = stream_handle.slice_stream_data('2014-08-21','2014-12-18')
    #将裁切后的数据，重新设置给Stream Handle
    stream_handle.reset_stream_data(stream_data_sliced)
    #再进行统计，按照半天进行，所以是60*60*12，注意此处结果是直接打印在Console中
    stream_handle.get_statistical_info('2014-08-21','2014-12-18',60*60*24*30)
    
    #---------------------------EXAMPLE2
    #加载CSV数据
    stream_handle = streamdatahandle(stream_data,"T","re_x","re_y","x","y")
    
    #生成一个时间段的所有点数据Shapefile,具体参数看代码吧
    stream_handle.gen_period_points_shp(r'F:\Cluster\Argo海洋浮标数据\导出表\result\clusters_den_stream\result1\新建文件夹\total_point_ori.shp', '2010-01-01', '2010-01-01', False, ['mention','mood','lang','hashtag','length','word_count'])
    #按照时间间隔生成所有点数据Shapefile,具体参数看代码吧
    stream_handle.gen_serial_points_shp(r'F:\Cluster\stream-cluster\visual\points','2012-10-27', '2012-11-11', 24*60*60, True)
    
    #生成一个时间段的所有OD点之间的线数据Shapefile,具体参数看代码吧
    stream_handle.gen_period_lines_shp(r'F:\Cluster\Argo海洋浮标数据\带有时间的数据\line_data\total_line.shp', '2010-01-01', '2010-12-31', False, [])
    #按照时间间隔生成所有OD点之间的线数据Shapefile,具体参数看代码吧
    stream_handle.gen_serial_lines_shp(r'F:\Cluster\stream-cluster\visual\lines','2012-10-22', '2012-10-28', 24*60*60, True)



def result_draw(cluster_file_name, cluster_info_name, result_shp_line, result_shp_region, result_pdf):

    combind_cluster_data = pd.read_csv(cluster_file_name, index_col=[0])
    combind_cluster_info = pd.read_csv(cluster_info_name, index_col=[0])

    flow_handle = streamflowhandle()
    flow_matrix = flow_handle.gen_flow_matrix_combind(combind_cluster_data,"source_cluster","sink_cluster")
    flow_list = flow_handle.gen_flow_list_combind(flow_matrix,combind_cluster_info)
    flow_list_sliced1 = flow_list
    
    
#*******************获取结果切片*************************************
    acc_val = flow_list['count'].sum()*0.90
    
    # 权重最小不低于5，类簇不超过30
    flow_list_sliced1 = flow_handle.slice_flow_list(flow_list,acc_val,5,30)
    # 剔除self-self的类簇
    flow_list_sliced2 = flow_handle.slice_flow_list_unself(flow_list,acc_val,5,30)
    # id为13的类簇
    flow_list_sliced3 = flow_handle.slice_flow_list_single(flow_list,13)
    # 从id为1的类簇流向id为13的类簇
    flow_list_sliced4 = flow_handle.slice_flow_list_interested(flow_list,[1,13])
    acc_val = flow_list_sliced4['count'].sum()*0.95
    flow_list_sliced5 = flow_handle.slice_flow_list(flow_list_sliced4,acc_val,5,30)
    # 选择self-self的类簇
    flow_list_sliced6 = flow_handle.slice_flow_list_self(flow_list,flow_list['count'].sum(),0,5)
    
#*******************根据切片绘制结果*************************************
    visual_handle = flowvisualhandle()
    visual_handle.set_map_extent(-180,180,-90,90)
    # 设置world底图位置
    visual_handle.set_flow_visual_parameter(r'F:/Cluster/stream-cluster/World/world.shp','',0.05, 0.2, 0.35, 0.015)
    # visual_handle.get_flow_map_shp(flow_list_sliced1, result_shp_line)
    visual_handle.get_flow_map(flow_list_sliced1, 'legend', result_pdf, [])
    # visual_handle.gen_points_cover_shp(combind_cluster_data,'sink_cluster','x','y',result_shp_region)
    
def result_visual(filepath):
    
    split = filepath.split('\\')
    if len(split) == 0:
        split = filepath.split('//')
    
    file_name = split[len(split) - 1]
    index = (file_name[file_name.find('_'):]).find('Info')
    num = "".join(filter(str.isdigit, file_name))
    file_path= "\\".join(split[:len(split) - 1]) + '\\'
    result_path = file_path + "result" + str(num) + "\\"

        
    
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    
    info_name = file_path + "GeoDenStream_ClusterInfo" + str(num) + ".csv"
    result_shp_region = result_path + "region_"+ str(num)   + ".shp"
    result_shp_line = result_path + "line_" + str(num) + ".shp"
    result_pdf = result_path + "result_" + str(num)
    if index != -1:
        filepath = file_path + "GeoDenStream_Cluster" + str(num) + ".csv"
    print(filepath+'\n', info_name+'\n', result_shp_line+'\n', result_pdf+'\n')
    result_draw(filepath, info_name, result_shp_line, result_shp_region, result_pdf)
  
def all_result_visual(cluster_file_path):
    for file in os.listdir(cluster_file_path):
        index = (file[file.find('_'):]).find('Info')
        
        if index == -1:
            print("文件 %s 正在处理" %(file))
            result_visual(cluster_file_path + '\\' + file)
            print("文件 %s 处理完毕" %(file))
if __name__ == '__main__':
    all_result_visual(r"F:\Cluster\论文修改\数据\clusterdata_e_3.0_week_tp_Median\clusters_den_stream")
