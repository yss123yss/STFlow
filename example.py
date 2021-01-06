# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 18:05:38 2021

@author: SYue
"""

import pandas as pd
import numpy as np
from streamdatahandle import streamdatahandle

stream_data = pd.read_csv('C:/GeoDenStream/Twitter2020/US/daily_twitter_od_2020_1_sorted.csv',index_col=[0])
stream_handle = streamdatahandle(stream_data,"time","o_lon","o_lat")
stream_handle.gen_period_points_shp('C:/GeoDenStream/Twitter2020/US/test.shp', '2020-1-2', '2020-1-2', False, ["d_lon","d_lat"])


stream_handle.get_statistical_info('2020-1-1','2020-1-31',60*60*24)

stream_handle.gen_serial_points_shp('C:/GeoDenStream/Twitter2020/US/points','2020-1-1', '2020-1-31', 24*60*60, True)


stream_handle = streamdatahandle(stream_data,"time","o_lon","o_lat","d_lon","d_lat")
stream_handle.gen_period_lines_shp('C:/GeoDenStream/Twitter2020/US/test_line.shp', '2020-1-1', '2020-1-1',True)









