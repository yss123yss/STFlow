# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 22:42:01 2021

@author: SYue
"""

import os
import math
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from scipy.special import binom
from scipy.spatial import Delaunay
from mpl_toolkits.basemap import Basemap
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable
from matplotlib.colorbar import ColorbarBase
from osgeo import gdal
from osgeo import ogr
from osgeo import osr
import shapely
from shapely import wkt, geometry
from shapely.ops import cascaded_union


class flowvisualhandle:
    def __init__(self):
        self._low_left_lon=-180
        self._low_left_lat=-90
        self._up_right_lon=180
        self._up_right_lat=90
        self._projection = 'merc'
        
        self._origin_id = 'origin'
        self._destination_id = 'destination'
        self._origin_x_tag = "o_x"
        self._origin_y_tag = "o_y"
        self._destination_x_tag = "d_x"
        self._destination_y_tag = "d_y"
        self._flow_count = 'count'
        
        self._curve_sample_number = 10000
        self._close_curve_sample_number =  100
        self._close_curve_size = 80000
        
        self._self_directed_threshold = 0.001;
        self._line_width = 0.4
        self._arrow_size = 3
        self._arrow_angle = 15
        self._alpha_value = 1.0
        
        self._background_shape_file = ""
        self._label_font = "Times New Roman"
        self._legend_x = 0.13
        self._legend_y = 0.165
        self._legend_height = 0.35
        self._legend_width = 0.015
    
    def set_map_extent(self, left_lon, right_lon, bottom_lat, up_lat):
        self._low_left_lon = left_lon
        self._up_right_lon = right_lon
        self._low_left_lat = bottom_lat
        self._up_right_lat = up_lat
    
    def set_flow_list_header(self, o_tag,d_tag, o_x_tag,o_y_tag, d_x_tag,d_y_tag, count_tag):
        self._origin_id = o_tag
        self._destination_id = d_tag
        self._origin_x_tag = o_x_tag
        self._origin_y_tag = o_y_tag
        self._destination_x_tag = d_x_tag
        self._destination_y_tag = d_y_tag
        self._flow_count = count_tag
    
    def set_flow_visual_parameter(self, backgrond_shap, label_font_family=None, 
                                  legend_pos_x=None, legend_pos_y=None, legend_height=None, legend_width=None):
        self._background_shape_file = backgrond_shap
        if (label_font_family!=None): self._label_font = label_font_family
        if (legend_pos_x!=None): self._legend_x = legend_pos_x
        if (legend_pos_y!=None): self._legend_y = legend_pos_y
        if (legend_height!=None): self._legend_height = legend_height
        if (legend_width!=None): self._legend_width = legend_width
    
    def set_curve_sample_number(self, curve_sample_number, close_curve_sample_number):
        self._curve_sample_number = curve_sample_number
        self._close_curve_sample_number = close_curve_sample_number
    
    def set_close_curve_size(self, close_curve_size):
        self._close_curve_size = close_curve_size
    
    def get_flow_map(self, flow_list, legend_name, file_name, map_dpi=600, file_formats=[".pdf"]):
        m = Basemap(projection='merc', \
                    llcrnrlat=self._low_left_lat, urcrnrlat=self._up_right_lat, \
                    llcrnrlon=self._low_left_lon, urcrnrlon=self._up_right_lon, \
                    lat_ts=20,resolution='c')
        
        if (self._background_shape_file==""):
            m.fillcontinents(zorder=1)
            m.drawcountries(linewidth = 0.1, color='#808080')
            m.drawcoastlines(linewidth = 0.12)
        else:
            path_tuple = os.path.split(self._background_shape_file)
            shpdir = path_tuple[0]
            shpName = path_tuple[1].split('.')[0]
            m.readshapefile(shpdir+'/'+shpName, shpName, linewidth = 0.2, color='#808080', default_encoding='iso-8859-15')
            m.drawmapboundary(linewidth = 0.5, fill_color='White')
        
        # *************************************************************************
        #cmap = plt.cm.summer
        # cmap = mpl.colors.ListedColormap(['#4987B8','#A6D29A', '#E9F3A3', '#FAE096', '#EE9264','#BB464F']) #光谱
        cmap = plt.cm.coolwarm
        norm = Normalize(vmin=flow_list['count'].min(), vmax=flow_list['count'].max())
        mapper = ScalarMappable(norm=norm, cmap=cmap)
        
        max_flowcount = flow_list['count'].max()
        min_flowcount = flow_list['count'].min()
        
        cluster_id_dict={}
        for index, row in flow_list.iterrows():
            temp_source = row[self._origin_id]
            temp_sink = row[self._destination_id]
            temp_x1 = row[self._origin_x_tag]
            temp_y1 = row[self._origin_y_tag]
            temp_x2 = row[self._destination_x_tag]
            temp_y2 = row[self._destination_y_tag]
            temp_flow_count = row[self._flow_count]
            temp_linw_width = (temp_flow_count - min_flowcount)/(max_flowcount - min_flowcount)
            
            color_val=mapper.to_rgba(temp_flow_count)
            
            ######################--draw curve coordinate--########################
            x1,y1=m(temp_x1, temp_y1)
            x2,y2=m(temp_x2, temp_y2)
            
            if (temp_x1-temp_x2)*(temp_x1-temp_x2)+(temp_y1-temp_y2)*(temp_y1-temp_y2) \
                    <self._self_directed_threshold*self._self_directed_threshold:
                x, y = self._get_curve_close(x1, y1, x2, y2)
            else:
                x, y = self._get_curve(x1,y1,x2,y2)
            
            
            
            m.plot(x,y,linewidth=self._line_width + temp_linw_width / 2, solid_capstyle='round',color=color_val, alpha=self._alpha_value)
            
            ######################--draw arrow coordinate--########################
            seg1_x, seg1_y = self._get_arrow_xy_list(x,y,self._arrow_angle,self._arrow_size)
            m.plot(seg1_x, seg1_y, linewidth=self._line_width, solid_capstyle='round', color=color_val, alpha=self._alpha_value)
            
            ######################-- get clusters center --########################
            if temp_source not in cluster_id_dict.keys():
                cluster_id_dict[temp_source]=[temp_x1,temp_y1]               
            if temp_sink not in cluster_id_dict.keys():
                cluster_id_dict[temp_sink]=[temp_x2,temp_y2]
        #end for iteration
        
        # *************************************************************************
        for key, value in cluster_id_dict.items():
            x1,y1=m(value[0]+0.1, value[1]-0.3)
            plt.text(x1,y1,str(int(key)),fontsize=7)
        
        # *************************************************************************
        plt.figtext(self._legend_x,self._legend_y+self._legend_height+0.01, legend_name, fontsize=6, ha='left')
        
        # ************************************************************************* 
        fig = plt.gcf()
        cax = fig.add_axes([self._legend_x, self._legend_y, self._legend_width, self._legend_height]) # posititon
        cax.tick_params(labelsize=5, gridOn=False)
        cb = ColorbarBase(cax,cmap=cmap,norm=norm, orientation='vertical',drawedges=False)
        cb.outline.set_visible(False)
        cb.ax.tick_params(size=0)
        
        for item in file_formats:
            plt.savefig(file_name+'.jpg',bbox_inches='tight', dpi=600)
        if len(file_formats)==0:
            plt.savefig(file_name+'.pdf',bbox_inches='tight', map_dpi=600)
            plt.savefig(file_name+'.jpg',bbox_inches='tight', map_dpi=600)
        plt.close()
    
    def get_flow_map_shp(self, flow_list, flow_map_file):
        shpName = self._checkExistFiles(flow_map_file)
        m = Basemap(projection='merc', \
                    llcrnrlat=self._low_left_lat, urcrnrlat=self._up_right_lat, \
                    llcrnrlon=self._low_left_lon, urcrnrlon=self._up_right_lon, \
                    lat_ts=20,resolution='c')
        
        node_dict = {}
        poDS = None
        try:
            gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
            gdal.SetConfigOption("SHAPE_ENCODING", "")
    
            pszDriverName = "ESRI Shapefile"
            ogr.RegisterAll()
            poDriver = ogr.GetDriverByName(pszDriverName)
            poDS = poDriver.CreateDataSource(flow_map_file)
            
            geomType = ogr.wkbLineString
            srs_str = "GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]]"
            srs = osr.SpatialReference(srs_str)
            poLayer = poDS.CreateLayer(shpName, srs, geomType)
            
            oField1 = ogr.FieldDefn("count", ogr.OFTInteger)
            oField2 = ogr.FieldDefn("percentage", ogr.OFTReal)
            oField3 = ogr.FieldDefn("sink_id", ogr.OFTInteger)
            oField4 = ogr.FieldDefn("source_id", ogr.OFTInteger)
            poLayer.CreateField(oField1, 1)
            poLayer.CreateField(oField2, 1)
            poLayer.CreateField(oField3, 1)
            poLayer.CreateField(oField4, 1)
        
            oDefn = poLayer.GetLayerDefn()
            temp_acc_val = flow_list[self._flow_count].sum()
            for index, row in flow_list.iterrows():
                temp_source = row[self._origin_id]
                temp_sink = row[self._destination_id]
                temp_x1 = row[self._origin_x_tag]
                temp_y1 = row[self._origin_y_tag]
                temp_x2 = row[self._destination_x_tag]
                temp_y2 = row[self._destination_y_tag]
                temp_flow_count = row[self._flow_count]
                                
                x1,y1=m(temp_x1, temp_y1)
                x2,y2=m(temp_x2, temp_y2)
                
                #********************************************************
                if temp_source not in node_dict.keys():
                    node_dict[temp_source]={}
                    node_dict[temp_source]["id"] = int(temp_source)
                    node_dict[temp_source]["x"] = int(x1)
                    node_dict[temp_source]["y"] = int(y1)
                
                if temp_sink not in node_dict.keys():
                    node_dict[temp_sink]={}
                    node_dict[temp_sink]["id"] = int(temp_sink)
                    node_dict[temp_sink]["x"] = int(x2)
                    node_dict[temp_sink]["y"] = int(y2)
                #********************************************************
                
                if (temp_x1-temp_x2)*(temp_x1-temp_x2)+(temp_y1-temp_y2)*(temp_y1-temp_y2) \
                        <self._self_directed_threshold*self._self_directed_threshold:
                    x, y = self._get_curve_close(x1, y1, x2, y2)
                else:
                    x, y = self._get_curve(x1,y1,x2,y2)
                            
                tempGeom = ogr.Geometry(ogr.wkbLineString)
                for temp_idx in range(0,len(x)):
                    temp_x, temp_y=m(x[temp_idx], y[temp_idx], True)
                    tempGeom.SetPoint(temp_idx, temp_x, temp_y, 0)
                tempFeature = ogr.Feature(oDefn)
                tempFeature.SetGeometry(tempGeom)
                tempFeature.SetField(0, temp_flow_count)
                tempFeature.SetField(1, temp_flow_count/temp_acc_val)
                tempFeature.SetField(2, temp_sink)
                tempFeature.SetField(3, temp_source)
                
                poLayer.CreateFeature(tempFeature)
                del tempFeature
            #end for iteration
        
            poDS.FlushCache()
            if poDS != None: del poDS
        except:
            if poDS != None: del poDS
        return node_dict

    def gen_points_cover_shp(self, clustered_data, cluster_id_tag, x_tag, y_tag, shpPath):
        shpName = self._checkExistFiles(shpPath)  
    
        poDS = None
        try:
            ##########################Begin for Shapefile################################
            gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "YES")
            gdal.SetConfigOption("SHAPE_ENCODING", "")
        
            pszDriverName = "ESRI Shapefile"
            ogr.RegisterAll()
            poDriver = ogr.GetDriverByName(pszDriverName)
            poDS = poDriver.CreateDataSource(shpPath)
            
            geomType = ogr.wkbPolygon
            srs_str = "GEOGCS[\"GCS_WGS_1984\",DATUM[\"D_WGS_1984\",SPHEROID[\"WGS_1984\",6378137.0,298.257223563]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]]"
            srs = osr.SpatialReference(srs_str)
            poLayer = poDS.CreateLayer(shpName, srs, geomType)
        
            oField1 = ogr.FieldDefn("c_id", ogr.OFTInteger)
            oField2 = ogr.FieldDefn("p_count", ogr.OFTInteger)
            poLayer.CreateField(oField1, 1)
            poLayer.CreateField(oField2, 1)
            
            oDefn = poLayer.GetLayerDefn()
            ##########################End for Shapefile################################
            
            ##########################Begin for preparing group################################
            id_points_group_map = {}
            coord_dict = {}
            id_points_count={}
            for index,item in clustered_data.iterrows():
                temp_cluster = item[cluster_id_tag]
                temp_x = '%.5f' % item[x_tag]
                temp_y = '%.5f' % item[y_tag]
                temp_key = temp_x + '_' + temp_y
                
                #if (item['y']>72 or item['y']<-60): continue
                if temp_key in coord_dict.keys():
                    continue
                else:
                    coord_dict[temp_key] = 0
                
                if temp_cluster in id_points_group_map.keys():
                    id_points_group_map[temp_cluster].append(item)
                else:
                    id_points_group_map[temp_cluster]=[]
                    id_points_group_map[temp_cluster].append(item)
                    
                if temp_cluster in id_points_count.keys():
                    id_points_count[temp_cluster]=id_points_count[temp_cluster]+1
                else:
                    id_points_count[temp_cluster]=1
            ##########################End for preparing group################################
            
            ##########################Begin for preparing points################################
            multi_points_list = []
            group_id_sorted_list = sorted(id_points_group_map.keys())
            for group_id in group_id_sorted_list:
                temp_point_count = len(id_points_group_map[group_id])
                allPointsGeom = ogr.Geometry(ogr.wkbMultiPoint)
                for point_idx in range(0,temp_point_count):
                    tempGeom = ogr.Geometry(ogr.wkbPoint)
                    tempGeom.SetPoint(0, id_points_group_map[group_id][point_idx]['x'], id_points_group_map[group_id][point_idx]['y'], 0)
                    allPointsGeom.AddGeometry(tempGeom)
                multi_points_list.append(allPointsGeom)
            ##########################End for preparing points################################
            
            buffer_list = []
            buffer_id_list = []
            convex_list = []
            convex_id_list = []
            group_id_sorted_list = sorted(id_points_group_map.keys())
            #*************************************************************
            for group_id in group_id_sorted_list:
                temp_point_count = len(id_points_group_map[group_id])
                if (temp_point_count==2):
                    tempGeom = ogr.Geometry(ogr.wkbLineString)
                    tempGeom.SetPoint(0, id_points_group_map[group_id][0]['x'], id_points_group_map[group_id][0]['y'], 0)
                    tempGeom.SetPoint(1, id_points_group_map[group_id][1]['x'], id_points_group_map[group_id][1]['y'], 0)
                    buffer_area=tempGeom.Buffer(0.1)
                    buffer_list.append(buffer_area)
                    buffer_id_list.append(group_id)
                elif (temp_point_count==1):
                    tempGeom = ogr.Geometry(ogr.wkbPoint)
                    tempGeom.SetPoint(0, id_points_group_map[group_id][0]['x'], id_points_group_map[group_id][0]['y'], 0)
                    buffer_area=tempGeom.Buffer(0.1)
                    buffer_list.append(buffer_area)
                    buffer_id_list.append(group_id)
            
            #*************************************************************
            for group_id in group_id_sorted_list:
                temp_point_count = len(id_points_group_map[group_id])
                if (temp_point_count>2):
                    points = np.zeros((temp_point_count, 2))
                    for point_idx in range(0,temp_point_count):
                        points[point_idx][0] = id_points_group_map[group_id][point_idx]['x']
                        points[point_idx][1] = id_points_group_map[group_id][point_idx]['y']
                    tri = Delaunay(points)
                    triangle_count = len(tri.simplices)
                    multiGeom = ogr.Geometry(ogr.wkbMultiPolygon)
                    for tri_idx in range(0, triangle_count):
                        v_idx1 = tri.simplices[tri_idx][0]
                        v_idx2 = tri.simplices[tri_idx][1]
                        v_idx3 = tri.simplices[tri_idx][2]
                        tempGeom = ogr.Geometry(ogr.wkbLinearRing)
                        tempGeom.SetPoint(0, points[v_idx1][0], points[v_idx1][1], 0)
                        tempGeom.SetPoint(1, points[v_idx2][0], points[v_idx2][1], 0)
                        tempGeom.SetPoint(2, points[v_idx3][0], points[v_idx3][1], 0)
                        tempGeom.CloseRings()
                        tempPolygon = ogr.Geometry(ogr.wkbPolygon)
                        tempPolygon.AddGeometry(tempGeom)
        
                        flag = False
                        for idx in range(0,len(multi_points_list)):
                            group_id_1=group_id_sorted_list[idx]
                            if(group_id_1==group_id): continue
                            if (tempPolygon.Intersects(multi_points_list[idx])):
                                flag=True                     
                        if(flag==False):
                            tempPolygon = ogr.Geometry(ogr.wkbPolygon)
                            tempPolygon.AddGeometry(tempGeom)
                            multiGeom.AddGeometry(tempPolygon)
                    convex_list.append(multiGeom)
                    convex_id_list.append(group_id)
            
            #*************************************************************
            for convex_idx1 in range(0, len(convex_list)-1):
                temp_geom1 = convex_list[convex_idx1]
                temp_count1 = temp_geom1.GetGeometryCount()
                for convex_idx2 in range(convex_idx1+1, len(convex_list)):
                    temp_geom2 = convex_list[convex_idx2]
                    temp_count2 = temp_geom2.GetGeometryCount()
                    if (temp_geom1.Intersects(temp_geom2)):
                        if(temp_geom1.GetArea() > temp_geom2.GetArea()):
                            temp_geom1_copy = ogr.Geometry(ogr.wkbMultiPolygon)
                            for temp_p_idx in range(0, temp_count1):
                                if (temp_geom1.GetGeometryRef(temp_p_idx).Intersects(temp_geom2)==False):
                                    temp_geom1_copy.AddGeometry(temp_geom1.GetGeometryRef(temp_p_idx).Clone())
                            convex_list[convex_idx1]=temp_geom1_copy
                        else:
                            temp_geom2_copy = ogr.Geometry(ogr.wkbMultiPolygon)
                            for temp_p_idx in range(0, temp_count2):
                                if (temp_geom2.GetGeometryRef(temp_p_idx).Intersects(temp_geom1)==False):
                                    temp_geom2_copy.AddGeometry(temp_geom2.GetGeometryRef(temp_p_idx).Clone())
                            convex_list[convex_idx2]=temp_geom2_copy
                
            #*************************************************************
            for convex_idx in range(0, len(convex_list)):
                temp_geom = convex_list[convex_idx]
                temp_count = temp_geom.GetGeometryCount()
                for buffer_idx in range(0, len(buffer_list)):
                    temp_buffer = buffer_list[buffer_idx]
                    if (temp_geom.Intersects(temp_buffer)):
                        temp_geom_copy = ogr.Geometry(ogr.wkbMultiPolygon)
                        for temp_p_idx in range(0, temp_count):
                            if (temp_geom.GetGeometryRef(temp_p_idx).Intersects(temp_buffer)==False):
                                temp_geom_copy.AddGeometry(temp_geom.GetGeometryRef(temp_p_idx).Clone())
                        convex_list[convex_idx]=temp_geom_copy
            
            #*************************************************************
            for convex_idx in range(0, len(convex_list)):
                temp_geom = convex_list[convex_idx]
                temp_geos_geom = shapely.wkt.loads(temp_geom.ExportToWkt())
                dissolved = cascaded_union(temp_geos_geom)
                if (dissolved.geom_type=='MultiPolygon'):
                    temp_count = len(dissolved)
                    max_area = dissolved[0].area
                    max_id = 0
                    for temp_poly_idx in range(1, temp_count):
                        if (dissolved[temp_poly_idx].area > max_area):
                            max_area = dissolved[temp_poly_idx].area
                            max_id = temp_poly_idx
                    temp_p_count = len(dissolved[max_id].exterior.coords)
                    temp_exterior = ogr.Geometry(ogr.wkbLinearRing)
                    for p_idx in range(0, temp_p_count):
                        temp_exterior.SetPoint(p_idx, dissolved[max_id].exterior.coords[p_idx][0], \
                                                      dissolved[max_id].exterior.coords[p_idx][1], \
                                                      dissolved[max_id].exterior.coords[p_idx][2])
                    
                    temp_polygon = ogr.Geometry(ogr.wkbPolygon)
                    temp_polygon.AddGeometry(temp_exterior)
                    convex_list[convex_idx]=temp_polygon
                else:
                    temp_p_count = len(dissolved.exterior.coords)
                    temp_exterior = ogr.Geometry(ogr.wkbLinearRing)
                    for p_idx in range(0, temp_p_count):
                        temp_exterior.SetPoint(p_idx, dissolved.exterior.coords[p_idx][0], \
                                                      dissolved.exterior.coords[p_idx][1], \
                                                      dissolved.exterior.coords[p_idx][2])
                    
                    temp_polygon = ogr.Geometry(ogr.wkbPolygon)
                    temp_polygon.AddGeometry(temp_exterior)
                    convex_list[convex_idx]=temp_polygon
              
            #*************************************************************
            for convex_idx1 in range(0, len(convex_list)-1):
                temp_geom1 = convex_list[convex_idx1]
                for convex_idx2 in range(convex_idx1+1, len(convex_list)):
                    temp_geom2 = convex_list[convex_idx2]
                    if (temp_geom1.Intersects(temp_geom2)):
                        if(temp_geom1.GetArea() > temp_geom2.GetArea()):
                            temp_geom1 = temp_geom1.Difference(temp_geom2)
                            convex_list[convex_idx1]=temp_geom1
                        else:
                            temp_geom2 = temp_geom2.Difference(temp_geom1)
                            convex_list[convex_idx2]=temp_geom2
                            
            #*************************************************************
            for convex_idx in range(0, len(convex_list)):
                group_id = convex_id_list[convex_idx]
                tempFeature = ogr.Feature(oDefn)
                tempFeature.SetGeometry(convex_list[convex_idx])
                tempFeature.SetField(0, group_id)
                tempFeature.SetField(1, id_points_count[group_id])
                poLayer.CreateFeature(tempFeature)
                del tempFeature
                
            for buffer_idx in range(0, len(buffer_list)):
                group_id = buffer_id_list[buffer_idx]
                tempFeature = ogr.Feature(oDefn)
                tempFeature.SetGeometry(buffer_list[buffer_idx])
                tempFeature.SetField(0, group_id)
                tempFeature.SetField(1, id_points_count[group_id])
                poLayer.CreateFeature(tempFeature)
                del tempFeature
            poDS.FlushCache()
            if poDS!=None: del poDS
            ##########################End Write################################
        except Exception as e:
            print(e)
            if poDS!=None: del poDS
    
    def _bernstein(self,n, k):
        """Bernstein polynomial.
        """
        coeff = binom(n, k)
        def _bpoly(x):
            return coeff * x ** k * (1 - x) ** (n - k)
        return _bpoly
    
    def _bezier(self, xList, yList, num=200):
        """Build Bézier curve from points.
        """
        points = (list(zip(xList, yList)))
        N = len(points)
        t = np.linspace(0, 1, num=num)
        curve = np.zeros((num, 2))
        for ii in range(N):
            curve += np.outer(self._bernstein(N-1, ii)(t), points[ii])
        return curve

    # =============================================================================
    # get coordinates of a curve line
    # =============================================================================
    def _get_curve(self,x1,y1,x2,y2):
        tempX1 = -(y1 - y2)/3 + (x1+x2)/2
        tempY1 = (x1 - x2)/3 + (y1+y2)/2
        
        line_len = math.sqrt((x1-x2)*(x1-x2) + (y1-y2)*(y1-y2))
        P=(x1,y1),(tempX1,tempY1),(x2,y2)
        n = len(P)-1
        
        Num_t=int(line_len/self._curve_sample_number)
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
        size = self._close_curve_size #80000 #800000
        tempX1 = size/1.2 + (x1+x2)/2
        tempY1 = size + (y1+y2)/2
        
        tempX2 = (x1+x2)/2
        tempY2 = size + (y1+y2)/2
        
        tempX3 = -size/1.2 + (x1+x2)/2
        tempY3 = size + (y1+y2)/2
        
        P=(x1,y1),(tempX1,tempY1),(tempX2,tempY2),(tempX3,tempY3),(x2,y2)
        n = len(P)-1
        
        Num_t=self._close_curve_sample_number
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