# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 12:32:40 2021

@author: SYue
"""

import os
import math
import datetime
import pandas as pd
import numpy as np
from scipy.special import binom

class StreamFlowHandle:
    def __init__(self):
        self._curve_sampling_length = 10000
        self._self_directed_sampling_size = 100
        self._self_directed_size = 80000
        pass
    
    def gen_flow_matrix_combind(self, cluster_data, origin_cluster_tag_name, destin_cluster_tag_name, weight_tag_name=None):
        m=(cluster_data[origin_cluster_tag_name].max())
        n=(cluster_data[destin_cluster_tag_name].max())
        flow_matrix = np.zeros([m,n])
        flag=0
        for index,row in cluster_data.iterrows():
            flag=flag+1
            if flag%10000==0: print(flag)
            origin_cluster_id = int(row[origin_cluster_tag_name])-1
            destin_cluster_id = int(row[destin_cluster_tag_name])-1
            flow_count = 1
            if weight_tag_name!=None: flow_count = int(row[weight_tag_name])
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
        for iRow in range(1, flow_matrix.shape[0]):
            flag=flag+1
            #if flag>=200: break
            origin_cluster = iRow
            temp_origin_x = cluster_info[(cluster_info.index==origin_cluster)].iloc[0,0]
            temp_origin_y = cluster_info[(cluster_info.index==origin_cluster)].iloc[0,1]
            for iColumn in range(1, flow_matrix.shape[1]):
                if (flow_matrix[iRow, iColumn]==0): continue
                destin_cluster = iColumn
                temp_destin_x = cluster_info[(cluster_info.index==destin_cluster)].iloc[0,0]
                temp_destin_y = cluster_info[(cluster_info.index==destin_cluster)].iloc[0,1]
                
                origin_id.append(iRow)
                destin_id.append(iColumn)
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
    
    def gen_flow_matrix_separated(origin_cluster_data, destin_cluster_data):
        m=(origin_cluster_data['cluster'].max())
        n=(destin_cluster_data['cluster'].max())
        #flow_matrix = [[0 for i in range(n)] for j in range(m)]
        flow_matrix = np.zeros([m,n])
        flag=0
        for index,row in origin_cluster_data.iterrows():
            flag=flag+1
            origin_cluster_id = int(row['cluster'])-1
            flow_count = int(row['cnt'])
            qq=destin_cluster_data[(destin_cluster_data.index==index)]
            if len(qq) > 0:
                destin_cluster_id = qq.iloc[0,-1]-1
                flow_matrix[origin_cluster_id,destin_cluster_id] += flow_count
                #print([origin_cluster_id,destin_cluster_id])
            #end if
            #if flag>=200: break
        #end for origin
        fileName_save = "C:/GeoDenStream/Safe/geodenstream_clusterdata/flowmatrix.csv"
        file_writer = open(fileName_save, "w+", encoding='UTF-8')
        for iRow in range(0,m):
            for iColumn in range(0,n-1):
                file_writer.write(str(flow_matrix[iRow,iColumn])+",")
            file_writer.write(str(flow_matrix[iRow,iColumn])+"\n")
        file_writer.close()
        return flow_matrix
    
    def gen_flow_list(flow_matrix, origin_cluster_info, destin_cluster_info):
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
                
                origin_id.append(iRow)
                destin_id.append(iColumn)
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

    # =============================================================================
    # get coordinates of a curve line
    # =============================================================================
    def _get_curve(self,x1,y1,x2,y2):
        if (x1-x2)*(x1-x2)+(y1-y2)*(y1-y2)<10000000000:
            return self._get_curve_close(x1, y1, x2, y2)
    
        tempX1 = -(y1 - y2)/3 + (x1+x2)/2
        tempY1 = (x1 - x2)/3 + (y1+y2)/2
        
        line_len = math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))
        P=(x1,y1),(tempX1,tempY1),(x2,y2)
        n = len(P)-1
        
        Num_t=int(line_len/10000)
        if (Num_t<=1): return self._get_curve_close(x1, y1, x2, y2)
        px, py = [None]*(Num_t+1),[None]*(Num_t+1)
        
        for j in range(Num_t+1):
            t = j / float(Num_t)
            px[j],py[j]=0.0,0.0
            for i in range(len(P)):
                px[j] += binom(n,i)*t**i*(1-t)**(n-i)*P[i][0]
                py[j] += binom(n,i)*t**i*(1-t)**(n-i)*P[i][1]
        
        px1, py1 = [None]*(Num_t-1),[None]*(Num_t-1)
        for j in range(Num_t-1):
            px1[j] = px[j+1]
            py1[j] = py[j+1]
        return px1, py1
    
    # =============================================================================
    # get coordinates of a closed curve line
    # =============================================================================
    def _get_curve_close(self,x1,y1,x2,y2):
        size = 80000 #800000
        tempX1 = size/1.2 + (x1+x2)/2
        tempY1 = size + (y1+y2)/2
        
        tempX2 = (x1+x2)/2
        tempY2 = size + (y1+y2)/2
        
        tempX3 = -size/1.2 + (x1+x2)/2
        tempY3 = size + (y1+y2)/2
        
        P=(x1,y1),(tempX1,tempY1),(tempX2,tempY2),(tempX3,tempY3),(x2,y2)
        n = len(P)-1
        
        Num_t=100
        px, py = [None]*(Num_t+1),[None]*(Num_t+1)
        
        for j in range(Num_t+1):
            t = j / float(Num_t)
            px[j],py[j]=0.0,0.0
            for i in range(len(P)):
                px[j] += binom(n,i)*t**i*(1-t)**(n-i)*P[i][0]
                py[j] += binom(n,i)*t**i*(1-t)**(n-i)*P[i][1]
        return px, py
    
    # =============================================================================
    # get coordinates of an arrow
    # =============================================================================
    def _get_arrow_xy_list(self, x,y,arrow_angle,arrow_size):
        last_lon1 = x[len(x)-2]
        last_lat1 = y[len(y)-2]
        last_lon2 = x[len(x)-1]
        last_lat2 = y[len(y)-1]
     
        #########################Left arrow line############################
        cs = math.cos(math.radians(arrow_angle))
        sn = math.sin(math.radians(arrow_angle))
        
        tempX = last_lon1 - last_lon2;
        tempY = last_lat1 - last_lat2;
        
        tempX = tempX*cs - tempY*sn;
        tempY = tempX*sn + tempY*cs;
        		
        tempX1 = tempX*arrow_size + last_lon2;
        tempY1 = tempY*arrow_size + last_lat2;
        
        #########################right arrow line############################
        cs = math.cos(math.radians(-arrow_angle))
        sn = math.sin(math.radians(-arrow_angle))
        
        tempX = last_lon1 - last_lon2;
        tempY = last_lat1 - last_lat2;
        
        tempX = tempX*cs - tempY*sn;
        tempY = tempX*sn + tempY*cs;
        		
        tempX2 = tempX*arrow_size + last_lon2;
        tempY2 = tempY*arrow_size + last_lat2;
        
        #########################combine two arrow lines############################
        arrow_x = [tempX1, last_lon2, tempX2]
        arrow_y = [tempY1, last_lat2, tempY2]
        return arrow_x, arrow_y
