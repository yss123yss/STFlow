# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 18:05:38 2021

@author: SYue
"""

import pandas as pd
import numpy as np
from streamdatahandle import streamdatahandle
from streamflowhandle import streamflowhandle
from flowvisualhandle import flowvisualhandle

#******************************************************************************
stream_data = pd.read_csv('C:/GeoDenStream/Twitter2020/US/daily_twitter_od_2020_1_sorted.csv',index_col=[0])

stream_handle = streamdatahandle(stream_data,"time","o_lon","o_lat","d_lon","d_lat")

statistical_info = stream_handle.get_statistical_info('2020-1-1','2020-2-1',60*60*24)
stream_data_sliced = stream_handle.slice_stream_data('2020-1-1','2020-1-5')
stream_handle.reset_stream_data(stream_data_sliced)
stream_handle.get_statistical_info('2020-1-1','2020-1-7',60*60*24)

stream_handle = streamdatahandle(stream_data,"time","o_lon","o_lat","d_lon","d_lat")
stream_handle.gen_period_points_shp('C:/GeoDenStream/Twitter2020/US/test.shp', '2020-1-2', '2020-1-2', False, ["d_lon","d_lat"])
stream_handle.gen_serial_points_shp('C:/GeoDenStream/Twitter2020/US/points','2020-1-1', '2020-2-1', 24*60*60, True)
stream_handle.gen_period_lines_shp('C:/GeoDenStream/Twitter2020/US/test_line.shp', '2020-1-1', '2020-1-1',True)
stream_handle.gen_serial_lines_shp('C:/GeoDenStream/Twitter2020/US/lines','2020-1-1', '2020-2-1', 24*60*60, True)

#******************************************************************************
cluster_file_name = 'C:/manqi/Sandy_Weather/clusterdata_e_0.5_tp_Median/clusters_den_stream/GeoDenStream_Cluster17.csv'
cluster_info_name = 'C:/manqi/Sandy_Weather/clusterdata_e_0.5_tp_Median/clusters_den_stream/GeoDenStream_ClusterInfo17.csv'
combind_cluster_data = pd.read_csv(cluster_file_name, index_col=[0])
combind_cluster_info = pd.read_csv(cluster_info_name, index_col=[0])

flow_handle = streamflowhandle()
flow_matrix = flow_handle.gen_flow_matrix_combind(combind_cluster_data,"source_cluster","sink_cluster")
flow_list = flow_handle.gen_flow_list_combind(flow_matrix,combind_cluster_info)

acc_val = flow_list['count'].sum()*0.9
flow_list_sliced1 = flow_handle.slice_flow_list(flow_list,acc_val,5,30)
flow_list_sliced2 = flow_handle.slice_flow_list_unself(flow_list,acc_val,5,30)
flow_list_sliced3 = flow_handle.slice_flow_list_single(flow_list,13)
flow_list_sliced4 = flow_handle.slice_flow_list_interested(flow_list,[1,13])
acc_val = flow_list_sliced4['count'].sum()*0.9
flow_list_sliced5 = flow_handle.slice_flow_list(flow_list_sliced4,acc_val,5,30)
flow_list_sliced6 = flow_handle.slice_flow_list_self(flow_list,flow_list['count'].sum(),0,5)


#******************************************************************************
visual_handle = flowvisualhandle()
visual_handle.set_map_extent(-88,-67,34,45)
visual_handle.set_flow_visual_parameter('D:/Data/World/world.shp','',0.15, 0.135, 0.35, 0.015)
visual_handle.get_flow_map(flow_list_sliced3, 'T1', 'C:/manqi/Sandy_Weather/test')
visual_handle.get_flow_map_shp(flow_list_sliced3, 'C:/manqi/Sandy_Weather/test.shp')
visual_handle.gen_points_cover_shp(combind_cluster_data,'sink_cluster','x','y','C:/manqi/Sandy_Weather/test_region.shp')

