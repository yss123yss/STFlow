# -*- coding: utf-8 -*-
"""
Created on Tue Jan  5 20:34:40 2021

@author: SYue
"""

import os
import math
import datetime
import numpy as np
import pandas as pd
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
from dateutil import parser

class streamdatahandle:
    def __init__(self, stream_data, time_flag, x_flag, y_flag, od_x_flag, od_y_flag):
        gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
        gdal.SetConfigOption("SHAPE_ENCODING", "")
        ogr.RegisterAll()
        
        self._stream_data = stream_data
        self._time_flag = time_flag;
        self._lon_flag = x_flag;
        self._lat_flag = y_flag;
        self._od_lon_flag = od_x_flag;
        self._od_lat_flag = od_y_flag;
        self._srs_str = "GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]]"
        
        if (np.issubdtype(stream_data.index,np.datetime64)==False):
            self._stream_data[self._time_flag] = pd.to_datetime(self._stream_data[self._time_flag])
            self._stream_data = self._stream_data.set_index(self._time_flag)
    
    def reset_stream_data(self, stream_data, time_flag='', x_flag='', y_flag='', od_x_flag='', od_y_flag=''):
        self._stream_data = stream_data
        
        if time_flag!='': self._time_flag = time_flag;
        if x_flag!='': self._lon_flag = x_flag;
        if y_flag!='': self._lat_flag = y_flag;
        if od_x_flag!='': self._od_lon_flag = od_x_flag;
        if od_y_flag!='': self._od_lat_flag = od_y_flag;
        
        if (np.issubdtype(stream_data.index,np.datetime64)==False):
            self._stream_data[self._time_flag] = pd.to_datetime(self._stream_data[self._time_flag])
            self._stream_data = self._stream_data.set_index(self._time_flag)
    
    def slice_stream_data(self, period_begin_str, period_end_str):
        period_data = self._stream_data.truncate(before=period_begin_str, after=period_end_str)
        return period_data
    
    def gen_all_points_shp(self, shpPath, withAllFields=False, fields=[], withCompress=False):
        shpName = self._checkExistFiles(shpPath)
        poDS = None
        try:
            pszDriverName = "ESRI Shapefile"
            poDriver = ogr.GetDriverByName(pszDriverName)
            poDS = poDriver.CreateDataSource(shpPath)
            
            geomType = ogr.wkbPoint
            srs = osr.SpatialReference(self._srs_str)
            poLayer = poDS.CreateLayer(shpName, srs, geomType)
            
            if (withAllFields==True):
                fields = self._stream_data.columns.to_list()
            self._define_fields(poLayer, fields)
            
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
                tempFeature.SetField(0, str(index))
                tempFeature.SetField(1, item[self._lon_flag])
                tempFeature.SetField(2, item[self._lat_flag])
                for idx in range(3, field_count):
                    temp_name = oDefn.GetFieldDefn(idx).GetName()
                    tempFeature.SetField(idx, item[temp_name])
                
                poLayer.CreateFeature(tempFeature)
                del tempFeature
            ##########################End for iteration################################   
            poDS.FlushCache()
            if poDS != None: del poDS
        except:
            if poDS != None: del poDS
    
    def gen_period_points_shp(self, shpPath, period_begin_str, period_end_str, withAllFields=False, fields=[], withCompress=False):
        shpName = self._checkExistFiles(shpPath)
        poDS = None
        try:
            pszDriverName = "ESRI Shapefile"
            poDriver = ogr.GetDriverByName(pszDriverName)
            poDS = poDriver.CreateDataSource(shpPath)
            
            geomType = ogr.wkbPoint
            srs = osr.SpatialReference(self._srs_str)
            poLayer = poDS.CreateLayer(shpName, srs, geomType)
            
            if (withAllFields==True):
                fields = self._stream_data.columns.to_list()
            self._define_fields(poLayer, fields)
            
            ##########################Begin for iteration################################   
            oDefn = poLayer.GetLayerDefn()
            field_count = oDefn.GetFieldCount()
            coord_dict={}
            period_data = self._stream_data.truncate(before=period_begin_str, after=period_end_str)
            for index,item in period_data.iterrows():
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
                tempFeature.SetField(0, str(index))
                tempFeature.SetField(1, item[self._lon_flag])
                tempFeature.SetField(2, item[self._lat_flag])
                for idx in range(3, field_count):
                    temp_name = oDefn.GetFieldDefn(idx).GetName()
                    tempFeature.SetField(idx, item[temp_name])
                
                poLayer.CreateFeature(tempFeature)
                del tempFeature
            ##########################End for iteration################################   
            poDS.FlushCache()
            if poDS != None: del poDS
        except Exception as e:
            print(e)
            if poDS != None: del poDS
    
    def gen_serial_points_shp(self, shpBaseName, period_begin_str, period_end_str, time_step_in_seconds,\
                              withAllFields=False, fields=[], withCompress=False):
        period_info = self.get_statistical_info(period_begin_str, period_end_str, time_step_in_seconds)
        for index,item in period_info.iterrows():
            shpPath = shpBaseName+str(index+1)+".shp"
            begin_str= item['begin']
            end_str = item['end']
            self.gen_period_points_shp(shpPath,begin_str,end_str,withAllFields,fields,withCompress)
            print(index)
        print("Finished")
    
    def gen_all_line_shp(self, shpPath, withAllFields=False, fields=[], withCompress=False):
        shpName = self._checkExistFiles(shpPath)
        poDS = None
        try:
            pszDriverName = "ESRI Shapefile"
            poDriver = ogr.GetDriverByName(pszDriverName)
            poDS = poDriver.CreateDataSource(shpPath)
            
            geomType = ogr.wkbLineString
            srs = osr.SpatialReference(self._srs_str)
            poLayer = poDS.CreateLayer(shpName, srs, geomType)
            
            if (withAllFields==True):
                fields = self._stream_data.columns.to_list()
            self._define_fields(poLayer, fields)
            
            ##########################Begin for iteration################################   
            oDefn = poLayer.GetLayerDefn()
            field_count = oDefn.GetFieldCount()
            coord_dict={}
            acc_flag = 0
            for index,item in self._stream_data.iterrows():
                acc_flag +=1
                if acc_flag%10000: print(acc_flag)
                temp_x1 = '%.5f' % item[self._lon_flag]
                temp_y1 = '%.5f' % item[self._lat_flag]
                temp_x2 = '%.5f' % item[self._od_lon_flag]
                temp_y2 = '%.5f' % item[self._od_lat_flag]
                
                temp_key = temp_x1 + '_' + temp_y1 + '_' + temp_x2 + '_' + temp_y2
                
                if withCompress==True:
                    if temp_key in coord_dict.keys():
                        coord_dict[temp_key] += 1
                        continue
                    else:
                        coord_dict[temp_key] = 0
                
                tempGeom = ogr.Geometry(ogr.wkbLineString)
                tempGeom.SetPoint(0, float(temp_x1), float(temp_y1), 0)
                tempGeom.SetPoint(1, float(temp_x2), float(temp_y2), 0)
                tempFeature = ogr.Feature(oDefn)
                tempFeature.SetGeometry(tempGeom)
                tempFeature.SetField(0, str(index))
                tempFeature.SetField(1, item[self._lon_flag])
                tempFeature.SetField(2, item[self._lat_flag])
                for idx in range(3, field_count):
                    temp_name = oDefn.GetFieldDefn(idx).GetName()
                    tempFeature.SetField(idx, item[temp_name])
                
                poLayer.CreateFeature(tempFeature)
                del tempFeature
            ##########################End for iteration################################   
            poDS.FlushCache()
            if poDS != None: del poDS
        except:
            if poDS != None: del poDS
    
    def gen_period_lines_shp(self, shpPath, period_begin_str, period_end_str, withAllFields=False, fields=[], withCompress=False):
        shpName = self._checkExistFiles(shpPath)
        poDS = None
        try:
            pszDriverName = "ESRI Shapefile"
            poDriver = ogr.GetDriverByName(pszDriverName)
            poDS = poDriver.CreateDataSource(shpPath)
            
            geomType = ogr.wkbLineString
            srs = osr.SpatialReference(self._srs_str)
            poLayer = poDS.CreateLayer(shpName, srs, geomType)
            
            if (withAllFields==True):
                fields = self._stream_data.columns.to_list()
            self._define_fields(poLayer, fields)
            
            ##########################Begin for iteration################################   
            oDefn = poLayer.GetLayerDefn()
            field_count = oDefn.GetFieldCount()
            coord_dict={}
            acc_flag = 0
            period_data = self._stream_data.truncate(before=period_begin_str, after=period_end_str)
            for index,item in period_data.iterrows():
                acc_flag +=1
                print(acc_flag)
                if acc_flag%10000: print(acc_flag)
                temp_x1 = '%.5f' % item[self._lon_flag]
                temp_y1 = '%.5f' % item[self._lat_flag]
                temp_x2 = '%.5f' % item[self._od_lon_flag]
                temp_y2 = '%.5f' % item[self._od_lat_flag]
                
                temp_key = temp_x1 + '_' + temp_y1 + '_' + temp_x2 + '_' + temp_y2
                
                if withCompress==True:
                    if temp_key in coord_dict.keys():
                        coord_dict[temp_key] += 1
                        continue
                    else:
                        coord_dict[temp_key] = 0
                
                tempGeom = ogr.Geometry(ogr.wkbLineString)
                tempGeom.SetPoint(0, float(temp_x1), float(temp_y1), 0)
                tempGeom.SetPoint(1, float(temp_x2), float(temp_y2), 0)
                tempFeature = ogr.Feature(oDefn)
                tempFeature.SetGeometry(tempGeom)
                tempFeature.SetField(0, str(index))
                tempFeature.SetField(1, item[self._lon_flag])
                tempFeature.SetField(2, item[self._lat_flag])
                for idx in range(3, field_count):
                    temp_name = oDefn.GetFieldDefn(idx).GetName()
                    tempFeature.SetField(idx, item[temp_name])
                
                poLayer.CreateFeature(tempFeature)
                del tempFeature
            ##########################End for iteration################################   
            poDS.FlushCache()
            if poDS != None: del poDS
        except:
            if poDS != None: del poDS
    
    def gen_stream_lines_shp(self, shpPath, stream_data, withAllFields=False, fields=[], withCompress=False):
        shpName = self._checkExistFiles(shpPath)
        poDS = None
        try:
            pszDriverName = "ESRI Shapefile"
            poDriver = ogr.GetDriverByName(pszDriverName)
            poDS = poDriver.CreateDataSource(shpPath)
            
            geomType = ogr.wkbLineString
            srs = osr.SpatialReference(self._srs_str)
            poLayer = poDS.CreateLayer(shpName, srs, geomType)
            
            if (withAllFields==True):
                fields = self._stream_data.columns.to_list()
            self._define_fields(poLayer, fields)
            
            ##########################Begin for iteration################################   
            oDefn = poLayer.GetLayerDefn()
            field_count = oDefn.GetFieldCount()
            coord_dict={}
            acc_flag = 0
            
            for index,item in stream_data.iterrows():
                acc_flag +=1
                print(acc_flag)
                if acc_flag%10000: print(acc_flag)
                temp_x1 = '%.5f' % item[self._lon_flag]
                temp_y1 = '%.5f' % item[self._lat_flag]
                temp_x2 = '%.5f' % item[self._od_lon_flag]
                temp_y2 = '%.5f' % item[self._od_lat_flag]
                
                temp_key = temp_x1 + '_' + temp_y1 + '_' + temp_x2 + '_' + temp_y2
                
                if withCompress==True:
                    if temp_key in coord_dict.keys():
                        coord_dict[temp_key] += 1
                        continue
                    else:
                        coord_dict[temp_key] = 0
                
                tempGeom = ogr.Geometry(ogr.wkbLineString)
                tempGeom.SetPoint(0, float(temp_x1), float(temp_y1), 0)
                tempGeom.SetPoint(1, float(temp_x2), float(temp_y2), 0)
                tempFeature = ogr.Feature(oDefn)
                tempFeature.SetGeometry(tempGeom)
                tempFeature.SetField(0, str(index))
                tempFeature.SetField(1, item[self._lon_flag])
                tempFeature.SetField(2, item[self._lat_flag])
                for idx in range(3, field_count):
                    temp_name = oDefn.GetFieldDefn(idx).GetName()
                    tempFeature.SetField(idx, item[temp_name])
                
                poLayer.CreateFeature(tempFeature)
                del tempFeature
            ##########################End for iteration################################   
            poDS.FlushCache()
            if poDS != None: del poDS
        except:
            if poDS != None: del poDS
        
    def gen_serial_lines_shp(self, shpBaseName, period_begin_str, period_end_str, time_step_in_seconds, \
                             withAllFields=False, fields=[], withCompress=False):
        period_info = self.get_statistical_info(period_begin_str, period_end_str, time_step_in_seconds)
        for index,item in period_info.iterrows():
            shpPath = shpBaseName+str(index+1)+".shp"
            begin_str= item['begin']
            end_str = item['end']
            self.gen_period_lines_shp(shpPath,begin_str,end_str,withAllFields,fields,withCompress)
            print(index)
        print("Finished")
    
    def get_statistical_info(self, period_begin_str, period_end_str, time_step_in_seconds):
        total_count = len(self._stream_data)
        begin_list=[]
        end_list=[]
        end_date_time =parser.parse(period_end_str)
        temp_date_time =parser.parse(period_begin_str)
        
        while temp_date_time<end_date_time:
            temp_s_str = temp_date_time.strftime('%Y-%m-%d %H:%M:%S')
            begin_list.append(temp_s_str)
            temp_date_time = temp_date_time + datetime.timedelta(seconds=time_step_in_seconds)
            temp_s_str = (temp_date_time-datetime.timedelta(seconds=1)).strftime('%Y-%m-%d %H:%M:%S')
            end_list.append(temp_s_str)
        
        count_list=[]
        for idx in range(0, len(begin_list)):
            period_data = self._stream_data.truncate(before=begin_list[idx], after=end_list[idx])
            count_list.append(len(period_data))
        statistical_data = pd.DataFrame({'begin':begin_list, 'end':end_list, 'count':count_list})
        return statistical_data
    
    def _define_fields(self, poLayer, fields):
        oField1 = ogr.FieldDefn(self._time_flag, ogr.OFTString)
        oField2 = ogr.FieldDefn(self._lon_flag, ogr.OFTReal)
        oField3 = ogr.FieldDefn(self._lat_flag, ogr.OFTReal)
        
        poLayer.CreateField(oField1, 1)
        poLayer.CreateField(oField2, 1)
        poLayer.CreateField(oField3, 1)
        
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
