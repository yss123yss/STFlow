# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 12:32:40 2021

@author: SYue
"""

import os
import math
import datetime
import numpy as np
import pandas as pd

class streamflowhandle:
    def __init__(self, flow_volume_tag='', origin_tag='', destination_tag=''):
        if flow_volume_tag=='': flow_volume_tag = 'count'
        if origin_tag=='': origin_tag='origin'
        if destination_tag=='': destination_tag='destination'
        
        self._flow_volume_tag = flow_volume_tag
        self._origin_tag = origin_tag
        self._destination_tag = destination_tag
    
    def slice_flow_list(self, flow_list, accumulate_value, min_volume, max_flow_num):
        flow_count = 0
        temp_acc_val = 0
        flow_list = flow_list.sort_values('count',ascending=False)
        min_val = min_volume
        for index, row in flow_list.iterrows():
            temp_volume = row[self._flow_volume_tag]
            temp_acc_val += temp_volume
            flow_count += 1
            if flow_count >= max_flow_num or temp_acc_val >= accumulate_value or temp_volume < min_volume: 
                min_val = temp_volume
                break
        flow_list_sliced = flow_list[(flow_list['count']>=min_val)]
        return flow_list_sliced
    
    def slice_flow_list_unself(self, flow_list, accumulate_value, min_volume, max_flow_num):
        flow_count = 0
        temp_acc_val = 0
        flow_list_sliced = flow_list[(flow_list[self._origin_tag]!=flow_list[self._destination_tag])]
        flow_list_sliced = flow_list_sliced.sort_values(self._flow_volume_tag,ascending=False)
        min_val = min_volume
        for index, row in flow_list_sliced.iterrows():
            temp_origin = row[self._origin_tag]
            temp_destin = row[self._destination_tag]
            temp_volume = row[self._flow_volume_tag]
            
            temp_acc_val += temp_volume
            flow_count += 1
            if flow_count >= max_flow_num or temp_acc_val >= accumulate_value or temp_volume < min_volume: 
                min_val = temp_volume
                break
        flow_list_sliced = flow_list_sliced[(flow_list_sliced['count']>=min_val)]
        return flow_list_sliced
    
    def slice_flow_list_self(self, flow_list, accumulate_value, min_volume, max_flow_num):
        flow_count = 0
        temp_acc_val = 0
        flow_list_sliced = flow_list[(flow_list[self._origin_tag]==flow_list[self._destination_tag])]
        flow_list_sliced = flow_list_sliced.sort_values(self._flow_volume_tag,ascending=False)
        min_val = min_volume
        for index, row in flow_list_sliced.iterrows():
            temp_origin = row[self._origin_tag]
            temp_destin = row[self._destination_tag]
            temp_volume = row[self._flow_volume_tag]
            
            temp_acc_val += temp_volume
            flow_count += 1
            if flow_count >= max_flow_num or temp_acc_val >= accumulate_value or temp_volume < min_volume: 
                min_val = temp_volume
                break
        flow_list_sliced = flow_list_sliced[(flow_list_sliced['count']>=min_val)]
        return flow_list_sliced
    
    def slice_flow_list_single(self, flow_list, single_id, inout=0):
        if (inout==0): # ==0 both
            flow_list_sliced = flow_list[(flow_list[self._origin_tag]==single_id) \
                                         |(flow_list[self._destination_tag]==single_id)]
        elif (inout>0): # >0 in
            flow_list_sliced = flow_list[(flow_list[self._destination_tag]==single_id)]
        else: # <0 out
            flow_list_sliced = flow_list[(flow_list[self._origin_tag]==single_id)]
        return flow_list_sliced
    
    def slice_flow_list_interested(self, flow_list, cluster_id_list, inout=0):
        if (inout==0): # ==0 both
            flow_list_sliced = flow_list[(flow_list[self._origin_tag].isin(cluster_id_list)) \
                                         | (flow_list[self._destination_tag].isin(cluster_id_list))]
        elif (inout>0): # >0 in
            flow_list_sliced = flow_list[(flow_list[self._destination_tag].isin(cluster_id_list))]
        else: # <0 out
            flow_list_sliced = flow_list[(flow_list[self._origin_tag].isin(cluster_id_list))]
        return flow_list_sliced
    
    def gen_flow_matrix_combind(self, cluster_data, origin_cluster_tag, destin_cluster_tag, weight_tag=None):
        m=(cluster_data[origin_cluster_tag].max())
        n=(cluster_data[destin_cluster_tag].max())
        if n>m: m = n
        flow_matrix = np.zeros([m,m])
        flag=0
        for index,row in cluster_data.iterrows():
            flag=flag+1
            if flag%10000==0: print(flag)
            origin_cluster_id = int(row[origin_cluster_tag])-1
            destin_cluster_id = int(row[destin_cluster_tag])-1
            flow_count = 1
            if weight_tag!=None: flow_count = int(row[self._weight_tag])
            flow_matrix[origin_cluster_id,destin_cluster_id] += flow_count
        #end for
        return flow_matrix
    
    def gen_flow_list_combind(self, flow_matrix, cluster_info):
        flow_list = []
        origin_id = []
        destin_id = []
        origin_x = []
        origin_y = []
        destin_x = []
        destin_y = []
        flag=0
        for iRow in range(0, flow_matrix.shape[0]):
            flag=flag+1
            print(flag)
            #if flag>=200: break
            origin_cluster = iRow
            if origin_cluster not in cluster_info.index: continue
            temp_origin_x = cluster_info[(cluster_info.index==origin_cluster)].iloc[0,0]
            temp_origin_y = cluster_info[(cluster_info.index==origin_cluster)].iloc[0,1]
            for iColumn in range(0, flow_matrix.shape[1]):
                if (flow_matrix[iRow, iColumn]==0): continue
                destin_cluster = iColumn
                temp_destin_x = cluster_info[(cluster_info.index==destin_cluster)].iloc[0,0]
                temp_destin_y = cluster_info[(cluster_info.index==destin_cluster)].iloc[0,1]
                
                origin_id.append(iRow+1) #cluster's ID begin with 1, while the array index starts from 0, so +1
                destin_id.append(iColumn+1)
                origin_x.append(temp_origin_x)
                origin_y.append(temp_origin_y)
                destin_x.append(temp_destin_x)
                destin_y.append(temp_destin_y)
                flow_list.append(flow_matrix[iRow, iColumn])
            #end for iColumn
        #end for iRow
        
        data_tuples = list(zip(origin_id, destin_id, origin_x, origin_y, destin_x, destin_y, flow_list))
        data = pd.DataFrame(data_tuples, columns=['origin','destination','o_x','o_y','d_x','d_y','count'])
        return data
    
    def gen_flow_matrix_separated(self, origin_cluster_data, destin_cluster_data, \
                                  origin_cluster_tag, destin_cluster_tag, weight_tag=None):
        m=(origin_cluster_data[origin_cluster_tag].max())
        n=(destin_cluster_data[destin_cluster_tag].max())
        flow_matrix = np.zeros([m,n])
        flag=0
        for index,row in origin_cluster_data.iterrows():
            flag=flag+1
            origin_cluster_id = int(row[origin_cluster_tag])-1
            flow_count = 1
            if weight_tag!=None: flow_count = int(row[weight_tag])
            qq=destin_cluster_data[(destin_cluster_data.index==index)] #index indicates the unique id of a record
            if len(qq) > 0:
                destin_cluster_id = qq.iloc[0,-1]-1
                flow_matrix[origin_cluster_id,destin_cluster_id] += flow_count
                #print([origin_cluster_id,destin_cluster_id])
            #end if
            #if flag>=200: break
        #end for origin
        return flow_matrix
    
    def gen_flow_list(self, flow_matrix, origin_cluster_info, destin_cluster_info):
        flow_list = []
        origin_id = []
        destin_id = []
        origin_x = []
        origin_y = []
        destin_x = []
        destin_y = []
        flag=0
        for iRow in range(1, flow_matrix.shape[0]):
            flag=flag+1
            #if flag>=200: break
            origin_cluster = iRow
            temp_origin_x = origin_cluster_info[(origin_cluster_info.index==origin_cluster)].iloc[0,0]
            temp_origin_y = origin_cluster_info[(origin_cluster_info.index==origin_cluster)].iloc[0,1]
            for iColumn in range(1, flow_matrix.shape[1]):
                if (flow_matrix[iRow, iColumn]==0): continue
                destin_cluster = iColumn
                temp_destin_x = destin_cluster_info[(destin_cluster_info.index==destin_cluster)].iloc[0,0]
                temp_destin_y = destin_cluster_info[(destin_cluster_info.index==destin_cluster)].iloc[0,1]
                
                origin_id.append(iRow+1) #cluster's ID begin with 1, while the array index starts from 0, so +1
                destin_id.append(iColumn+1)
                origin_x.append(temp_origin_x)
                origin_y.append(temp_origin_y)
                destin_x.append(temp_destin_x)
                destin_y.append(temp_destin_y)
                flow_list.append(flow_matrix[iRow, iColumn])
            #end for iColumn
        #end for iRow
        
        data_tuples = list(zip(origin_id, destin_id, origin_x, origin_y, destin_x, destin_y, flow_list))
        data = pd.DataFrame(data_tuples, columns=['origin','destination','o_x','o_y','d_x','d_y','count'])
        return data
