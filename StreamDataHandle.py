# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 20:34:40 2021

@author: SYue
"""

import os
import math
import datetime
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib as mpl
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from scipy.special import binom
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import ColorbarBase

class StreamDataToShapefile:
    def __init__(self, stream_data, time_flag, lon_flag, lat_flag):
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
        gdal.SetConfigOption("SHAPE_ENCODING", "")
        ogr.RegisterAll()
        
        self._stream_data = stream_data
        self._time_flag = time_flag;
        self._lon_flag = lon_flag;
        self._lat_flag = lat_flag;
        self._srs_str = "GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]]"
        pass
    
    def gen_all_points_shp(self, shpPath, withAllFields=False, fields=[]):
        pass
    
    def gen_all_points_shp_compressed(self, shpPath, withAllFields=False, fields=[]):
        pass
    
    def gen_period_points_shp(self, shpPath, withAllFields=False, fields=[], withCompress=False):
        shpName = self._checkExistFiles(shpPath)
        poDS = None
        try:
            pszDriverName = "ESRI Shapefile"
            poDriver = ogr.GetDriverByName(pszDriverName)
            poDS = poDriver.CreateDataSource(shpPath)
            
            geomType = ogr.wkbPoint
            srs = osr.SpatialReference(self._srs_str)
            poLayer = poDS.CreateLayer(shpName, srs, geomType)
            
            oField1 = ogr.FieldDefn(self._time_flag, ogr.OFTString)
            oField2 = ogr.FieldDefn(self._lon_flag, ogr.OFTReal)
            oField3 = ogr.FieldDefn(self._lat_flag, ogr.OFTReal)
            
            poLayer.CreateField(oField1, 1)
            poLayer.CreateField(oField2, 1)
            poLayer.CreateField(oField3, 1)
            if (withAllFields==True):
                for index, row in self._stream_data.iteritems():
                    if index==self._time_flag or index==self._lon_flag or index==self._lat_flag:
                        continue
                    temp_field_type = np.dtype(self._stream_data[index])
                    temp_field=None
                    if temp_field_type==np.int64 or temp_field_type==np.int32 or temp_field_type==np.int16 or temp_field_type==np.int8 :
                        temp_field = ogr.FieldDefn(index, ogr.OFTInteger)
                    elif temp_field_type==np.float64 or temp_field_type==np.float32:
                        temp_field = ogr.FieldDefn(index, ogr.OFTReal)
                    else:
                        temp_field = ogr.FieldDefn(index, ogr.OFTString)
                    poLayer.CreateField(temp_field, 1)
            else:
                for item in fields:
                    if item==self._time_flag or item==self._lon_flag or item==self._lat_flag:
                        continue
                    temp_field_type = np.dtype(self._stream_data[item])
                    temp_field=None
                    if temp_field_type==np.int64 or temp_field_type==np.int32 or temp_field_type==np.int16 or temp_field_type==np.int8 :
                        temp_field = ogr.FieldDefn(item, ogr.OFTInteger)
                    elif temp_field_type==np.float64 or temp_field_type==np.float32:
                        temp_field = ogr.FieldDefn(item, ogr.OFTReal)
                    else:
                        temp_field = ogr.FieldDefn(item, ogr.OFTString)
                    poLayer.CreateField(temp_field, 1)
            #end if (withAllFields==True):
            
            
            ##########################Begin for iteration################################   
            oDefn = poLayer.GetLayerDefn()
            field_count = oDefn.GetFieldCount()
            coord_dict={}
            for index,item in self._stream_data.iterrows():
                temp_x = '%.5f' % item[self._lon_flag]
                temp_y = '%.5f' % item[self._lat_flag]
                temp_key = temp_x + '_' + temp_y
                
                if withCompress==True:
                    if temp_key in coord_dict.keys():
                        continue
                    else:
                        coord_dict[temp_key] = 0
                        
                tempGeom = ogr.Geometry(ogr.wkbPoint)
                tempGeom.SetPoint(0, item[self._lon_flag], item[self._lat_flag], 0)
                tempFeature = ogr.Feature(oDefn)
                tempFeature.SetGeometry(tempGeom)
                tempFeature.SetField(0, item[self._time_flag])
                tempFeature.SetField(1, item[self._lon_flag])
                tempFeature.SetField(2, item[self._lat_flag])
                for idx in range(3, field_count):
                    temp_name = oDefn.GetFieldDefn(idx).GetName()
                    tempFeature.SetField(idx, item[temp_name])
                
                poLayer.CreateFeature(tempFeature)
                del tempFeature
            ##########################End for iteration################################   
            poDS.FlushCache()
            del poDS
        except:
            if poDS != None: del poDS
        pass
    
    def _mkdir(self, path):
        path=path.strip()
        path=path.rstrip("\\")
        isExists=os.path.exists(path)
        if not isExists:
            os.makedirs(path)
            return True
        else:
            return False
    
    def _checkExistFiles(self, shpPath):
        path_tuple = os.path.split(shpPath)
        shpdir = path_tuple[0]
        shpName = path_tuple[1].split('.')[0]
        if os.path.exists(shpPath) == False:
            if os.path.exists(shpdir) == False: self._mkdir(shpdir)
        else:
            dbfPath = shpdir + '/' + shpName + ".dbf"
            prjPath = shpdir + '/' + shpName + ".prj"
            sbnPath = shpdir + '/' + shpName + ".sbn"
            shxPath = shpdir + '/' + shpName + ".shx"
            if os.path.exists(dbfPath): os.remove(dbfPath)
            if os.path.exists(prjPath): os.remove(prjPath)
            if os.path.exists(sbnPath): os.remove(sbnPath)
            if os.path.exists(shxPath): os.remove(shxPath)
        return shpName

stream_data = pd.read_csv('C:/GeoDenStream/Twitter2020/US/daily_twitter_od_2020_1_sorted.csv',index_col=[0])
stream_handle = StreamDataToShapefile(stream_data,"time","o_lon","o_lat")
stream_handle.gen_period_points_shp('C:/GeoDenStream/Twitter2020/US/test.shp', True, [])