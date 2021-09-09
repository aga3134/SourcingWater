# @file flwdir.py
# @brief pack pyflwdir to FlwDir() and integrated networkx supported
# @author wuulong@gmail.com
#extend
import rasterio
from rasterio import features
import pyflwdir
import geopandas as gpd
import json

#畫圖要用的函示
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import cm, colors
import cartopy.crs as ccrs
import numpy as np


from shapely import wkt
from shapely.ops import split
from shapely.geometry import *
from shapely.ops import nearest_points
import networkx as nx

np.random.seed(seed=101)
matplotlib.rcParams['savefig.bbox'] = 'tight'
matplotlib.rcParams['savefig.dpi'] = 256
plt.style.use('seaborn-whitegrid')

def to_crs(xy,from_srid,to_srid): #[121.1359083, 24.74512778], 4326, 3826
    s_from = gpd.GeoSeries([Point(xy[0], xy[1])], crs=from_srid)
    s_to = s_from.to_crs(to_srid)
    return [s_to.iloc[0].x,s_to.iloc[0].y]


class FlwDir():
    def __init__(self):

        self.flwdir = None #
        self.transform = None #
        self.crs = None #
        self.latlon = None #

        self.elevtn = None #
        self.prof = None #

        self.flw = None # main flow dir object
        self.gdf = None # stream
        self.gdf_subbas = None # subbasins_streamorder

        self.gdf_paths = None # downstream path
        self.gdf_pnts =  None # downstream point

        self.G = None # stream networkx

    def reload(self,dtm_file='data/catchment/C1300_20m_elv0.tif',flwdir_file='data/catchment/C1300_20m_LDD.tif'):

        with rasterio.open(flwdir_file, 'r') as src1:
            self.flwdir = src1.read(1)
            self.transform = src1.transform
            self.crs = src1.crs
            self.latlon = self.crs.to_epsg() == 4326
            print("%s info:%s" %(flwdir_file,src1))
        with rasterio.open(dtm_file, 'r') as src2:
            self.elevtn = src2.read(1)
            self.elevtn[self.elevtn==-99999]=-9999
            self.prof = src2.profile
            print("%s info:%s" %(dtm_file,src2))
    def init(self):
        ftype='ldd'
        self.flw = pyflwdir.from_array(self.flwdir,ftype=ftype, transform=self.transform, latlon=self.latlon, cache=True) #d8
        print(self.flw)
    def quickplot(self,gdfs=[], maps=[], hillshade=True, title='', filename='flw', save=False):

        fig = plt.figure(figsize=(8,15))
        ax = fig.add_subplot(projection=ccrs.PlateCarree())
        # plot hillshade background
        if hillshade:
            ls = matplotlib.colors.LightSource(azdeg=115, altdeg=45)
            hillshade = ls.hillshade(np.ma.masked_equal(self.elevtn, -9999), vert_exag=1e3)
            ax.imshow(hillshade, origin='upper', extent=self.flw.extent, cmap='Greys', alpha=0.3, zorder=0)
        # plot geopandas GeoDataFrame
        for gdf, kwargs in gdfs:
            gdf.plot(ax=ax, **kwargs)
        for data, nodata, kwargs in maps:
            ax.imshow(np.ma.masked_equal(data, nodata), origin='upper', extent=flw.extent, **kwargs)
        ax.set_aspect('equal')
        ax.set_title(title, fontsize='large')
        ax.text(0.01, 0.01, 'created with pyflwdir', transform=ax.transAxes, fontsize='large')
        if save:
            plt.savefig(f'output/{filename}.png')
        return ax

    # 函式
    def vectorize(self,data, nodata, transform, crs):

        feats_gen = features.shapes(
            data, mask=data!=nodata, transform=transform, connectivity=8,
        )
        feats = [
            {"geometry": geom, "properties": {"value": val}}
            for geom, val in list(feats_gen)
        ]

        # parse to geopandas for plotting / writing to file
        gdf = gpd.GeoDataFrame.from_features(feats, crs=self.crs)

        return gdf
    def upstream_area(self):
        # calculate upstream area
        self.uparea = self.flw.upstream_area(unit='km2')

    def streams(self, min_sto, filename=None): # None: return json, '' use default filename
        #河道
        feats = self.flw.streams(min_sto=min_sto)
        self.gdf = gpd.GeoDataFrame.from_features(feats, crs=self.crs)
        #轉經緯度並簡化
        self.gdf = self.gdf.to_crs("EPSG:4326")
        self.gdf = self.gdf.simplify(0.0001)

        if filename=='':
            filename = 'output/river_c1300_stream_%i.geojson' %(min_sto)

        if filename is None:
            return self.gdf.to_json()
        else:

            self.gdf.to_file(filename, driver='GeoJSON',index=True)
            print("stream saved filename=%s" %(filename))
        self.G = self.stream_gen_networkx()

    def subbasins_streamorder(self,min_sto, filename=None):# None: return json, '' use default filename
        # calculate subbasins with a minimum stream order 7
        subbas = self.flw.subbasins_streamorder(min_sto=min_sto, mask=None)
        self.gdf_subbas = self.vectorize(subbas.astype(np.int32), 0, self.flw.transform,self.crs)
        #轉經緯度
        self.gdf_subbas = self.gdf_subbas.to_crs("EPSG:4326")
        self.gdf_subbas = self.gdf_subbas.simplify(0.0002)

        if filename=='':
            filename = 'output/river_c1300_subbas_%i.geojson' %(min_sto)
        if filename is None:
            return self.gdf_subbas.to_json()
        else:
            self.gdf_subbas.to_file(filename, driver='GeoJSON')
            print("subbas saved filename=%s" %(filename))

    def path(self,points,filename=None): # None: return json, '' use default filename
        # 算通過點的下游路線
        # flow paths return the list of linear indices
        x=[]
        y=[]
        for p in points:
            #轉3826
            pt = to_crs(p,4326,3826)
            x.append(pt[0])
            y.append(pt[1])
        xy = (x,y)
        #points=[[260993,2735861,'油羅上坪匯流'],[253520,2743364,'隆恩堰'],[247785,2746443,'湳雅取水口']]
        #xy=([260993, 253520, 247785], [2735861, 2743364, 2746443])

        if filename=='':
            filename = 'output/river_c1300_path.geojson'
        flowpaths, dists = self.flw.path(xy=xy, max_length=400e3, unit='m')
        # which we than use to vectorize to geofeatures
        feats = self.flw.geofeatures(flowpaths)
        self.gdf_paths = gpd.GeoDataFrame.from_features(feats, crs=self.crs).reset_index()
        #轉回經緯度
        self.gdf_paths = self.gdf_paths.to_crs("EPSG:4326")

        self.gdf_pnts = gpd.GeoDataFrame(geometry=gpd.points_from_xy(*xy)).reset_index()
        if filename is None:
            return self.gdf_paths.to_json()
        else:
            self.gdf_paths.to_file(filename, driver='GeoJSON')
            print("path saved:%s" %(filename))

    def basins(self,points,filename=''): # None: return json, '' use default filename
        # 通過點的上游流域
        #points=[[260993,2735861,'油羅上坪匯流'],[253520,2743364,'隆恩堰'],[247785,2746443,'湳雅取水口']]
    
        nodata=0
        transform = self.flw.transform
        crs = self.crs
        featss = []
        for p in points:
            #轉3826
            pt = to_crs(p,4326,3826)
            x, y = np.array([pt[0], pt[0]]), np.array([pt[1], pt[1]])
            name = p[2]
            subbasins = self.flw.basins(xy=(x,y), streams=self.flw.stream_order()>=4)
            gdf_bas = self.vectorize(subbasins.astype(np.int32), 0, self.flw.transform,self.crs)
            data = subbasins.astype(np.int32)
            feats_gen = features.shapes(
                data, mask=data!=nodata, transform=transform, connectivity=8,
            )
            feats = [
                {"geometry": geom, "properties": {"name": name, "value": val}}
                for geom, val in list(feats_gen)
            ]
            featss.extend(feats)

        self.gdf_bas = gpd.GeoDataFrame.from_features(featss, crs=crs)
        #轉回經緯度
        self.gdf_bas = self.gdf_bas.to_crs("EPSG:4326")

        if filename=='':
            filename = 'output/river_c1300_basin.geojson'

        if filename is None:
            return self.gdf_bas.to_json()
        else:
            self.gdf_bas.to_file(filename, driver='GeoJSON')
            print("point catchment saved: %s" %(filename))


    def desc_stream(self,cfg_dict={'seg_info':1,'link_info':1,'dot_info':1}):
        # 觀察 stream 的連接性
        coords={}
        for index, row in self.gdf.iterrows():
            line = row['geometry']
            idxs=row['idxs']
            points = list(line.coords)
            start = points[0]
            end = points[len(points)-1]
            line_len = line.length
            coords[index]=[start,end,line_len]
            seg_cnt = len(line.coords)
            if cfg_dict['seg_info']==1:
                print("index=%i,length=%i,seg cnt=%i,avg_len=%.1f,start=%s,end=%s,idxs=%i" %(index,line.length,seg_cnt,line.length/seg_cnt,start,end,idxs))

        link={}

        for key in coords.keys():
            no_link=True
            start,end,line_len = coords[key]
            for key2 in coords.keys():
                start2,end2,line_len = coords[key2]
                if end==start2:
                    if key in link:
                        if cfg_dict['link_info']==1:
                            print("index=%i already have start=%i" %(key,link[key]))
                    link[key]=key2
                    no_link=False
            if no_link:
                link[key]=key
        if cfg_dict['link_info']==1:
            print("link=%s" %(link))

        if 0:
            for i in range(len(gdf.index)):
                if i in link.keys():
                    #print("index=%i PASS" %(i))
                    pass
                else:
                    print("index=%i,info=%s" %(index,gdf.iloc[i]))

        for l in link:
            if cfg_dict['dot_info']==1:
                print("N%i->N%i" %(l,link[l]))
        return [coords,link]
    ##### networkx support ###################
    def join_line(self,wkt_str):
        #圳路接入主流
        # line_ori:要修改的線, line_need:想加入的線, line_append:更新起點的想加入線, line_split:要修改的線被匯流點切開的結果
        #取得圳路 linestring

        #wkt_str="MultiLineString ((255779.34444821099168621 2742184.59869130607694387, 255062.52472444207523949 2741882.12604631343856454, 254328.86074706495855935 2742279.99766481388360262))"
        line_need = wkt.loads(wkt_str)
        print("line_need=%s" %(line_need))
        #經由圳路的起點，找到最接近需要修改的線
        start = Point(list(line_need.geoms[0].coords)[0])
        print("start:%s" %(start))
        dist_min=5000
        idx_min=None
        for index, row in self.gdf.iterrows():
            line = row['geometry']
            dist = line.distance(start)
            if dist<dist_min:
                dist_min=dist
                idx_min=index
        print("index=%i, minimal distance=%f" %(idx_min,dist_min))
        #找到匯流點
        line_ori = self.gdf.loc[idx_min]['geometry']
        pt_in = nearest_points(line_ori, start)[0]
        #修改圳路起點為匯流點
        pts = []
        pts.append(list(pt_in.coords)[0])
        for i in range(len(line_need.geoms)):
            pts.extend(list(line_need.geoms[i].coords))
        line_append = LineString(pts)
        print("line_append=%s" %(line_append))
        #取得主流切開後的兩線段
        line_split = split(line_ori, pt_in)
        print("line_split=%s"%(line_split))
        #在 gdf 中刪掉原線段，加入兩新線段,加入修改後的圳路
        idx_start = len(self.gdf.index)

        self.gdf.loc[idx_start]=[line_append,100,False,9] #geometry,idxs,pit,strord
        for i in range(len(line_split)):
            self.gdf.loc[idx_start+i+1]=[line_split[i],100+i+1,False,9]
        self.gdf.drop(idx_min,axis=0,inplace=True)
        self.gdf.to_file('output/river_c1300_mergeline.geojson', driver='GeoJSON')

    #單點到 stream 資訊: 距離，最近點，哪一個線段
    def point_with_streams(self,point_src,dist_min=5000): #[253520,2743364]
        #需先跑self.streams建立self.gdf
        #轉3826
        pt = to_crs(point_src,4326,3826)
        point = Point(pt[0],pt[1])
        #dist_min=5000
        idx_min=None
        for index, row in self.gdf.iterrows():
            line = row['geometry']
            dist = line.distance(point)
            if dist<dist_min:
                dist_min=dist
                idx_min=index
        #print("index=%i, minimal distance=%f" %(idx_min,dist_min))
        if idx_min is None:
            return None
        else:
            line_ori = self.gdf.loc[idx_min]['geometry']

            pt_in = nearest_points(line_ori, point)[0]
            #print(pt_in.coords[0][0])
            xy=pt_in.coords[0]
            #轉回經緯度
            xy = to_crs(xy,3826,4326)

            return [idx_min,dist_min,xy[0],xy[1]] #index, distance, point_x, point_y

    def stream_gen_networkx(self,shp=0): #shp(1): point for shp, shp(0): id base

        #import matplotlib.pyplot as plt
        #fd.streams(9,'')
        G = nx.DiGraph()
        nodes = {}
        for index, row in self.gdf.iterrows():
            line = row['geometry']
            points = list(line.coords)
            start = points[0]
            end = points[len(points)-1]
            line_len = line.length
            seg_cnt = len(line.coords)


            if not start in nodes.keys():

                wkt = "POINT (%s %s)" %(start[0],start[1])
                sname = "S%s" %(index)
                nodes[start]=sname
                if shp==1:
                    G.add_node(start,name=sname,Wkt=wkt)
                else:
                    G.add_node(sname,name=sname,Wkt=wkt)
            else:
                sname = nodes[start]
            if not end in nodes.keys():

                wkt = "POINT (%s %s)" %(end[0],end[1])
                ename = "E%s" %(index)
                nodes[end]=ename
                if shp==1:
                    G.add_node(end,name=ename,Wkt=wkt)
                else:
                    G.add_node(ename,name=ename,Wkt=wkt)
            else:
                ename = nodes[end]

            if shp==1:
                G.add_weighted_edges_from([(start, end,line_len)],edge_id=index,edge_name=index,length=line_len)
            else:
                G.add_weighted_edges_from([(sname, ename,line_len)],edge_id=index,edge_name=index,length=line_len,line=line)

        return G

    def nx_write_shp(self):
        G= self.stream_gen_networkx(1)
        pathname="output/stream"
        nx.write_shp(G,pathname)
        if self.crs.to_epsg() == 3826:
            prj="""PROJCS["TWD_1997_TM_Taiwan",GEOGCS["GCS_TWD_1997",DATUM["D_TWD_1997",SPHEROID["GRS_1980",6378137.0,298.257222101]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Transverse_Mercator"],PARAMETER["False_Easting",250000.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",121.0],PARAMETER["Scale_Factor",0.9999],PARAMETER["Latitude_Of_Origin",0.0],UNIT["Meter",1.0]]"""
            with open("%s/nodes.prj" %(pathname),'w') as f:
                f.write(prj)
            with open("%s/edges.prj" %(pathname),"w") as f:
                f.write(prj)
        self.G = self.stream_gen_networkx()
        print("network shp saved:%s" %(pathname))
    def get_path(self,start,end):
        path = dict(nx.all_pairs_shortest_path(self.G))
        if end in path[start].keys():
            return path[start][end]
        else:
            return None
    def path_get_edge(self,path):
        edge_ids=[]
        for i in range(1,len(path)):
            start = path[i-1]
            end = path[i]
            edge_ids.append(self.G.edges[start,end]['edge_id'])
        return edge_ids
    def path_length(self,path):
        len_total=0
        if path:
            for i in range(1,len(path)):
                start = path[i-1]
                end = path[i]
                length=self.G.edges[start, end]['length']
                edge_id = self.G.edges[start, end]['edge_id']
                print("L%i(%s->%s):%f" %(edge_id,start,end,length))
                len_total+=length
        return len_total
    def point_distance_in_line(self,line_idx, xy): #point:[x,y]
        #get point distance from start of line index, return [line_length, length_from_start]
        point = Point(xy[0], xy[1])
        line = self.gdf.loc[line_idx]['geometry']
        return [line.length, line.project(point)]
    def get_edge_path(self,start_idx,end_idx):
        #get node path from 2 edge
        edges = dict(self.G.edges)
        #print(edges)
        for key in edges.keys():
            if edges[key]['edge_id']==start_idx:
                #print("key=%s,edge=%s" %(key,edges[key]))
                start = key[0]
            if edges[key]['edge_id']==end_idx:
                end = key[1]
        path = self.get_path(start,end)
        return path
    def nx_node_seq(self,start,end):
        path_f = self.get_path(start,end)
        path_r = self.get_path(end,start)
        kind=0
        if path_f:
            kind=1
        else:
            if path_r:
                kind=-1
        #print("kind %s->%s:%i (1: 順向 -1:逆向 0:沒在一條線)" %(start,end,kind))
        return kind
    def nx_desc(self,desc_id=0):
        if self.G is None:
            return
        if 1: #nodes
            nodes = self.G.nodes
            node_desc =",".join(list(nodes))
            print( "nodes=%s" %(node_desc) )
        if 1: #edges
            edges = dict(self.G.edges)
            print("===== edges =====")
            for key in edges.keys():
                print("%s->%s" %(key,edges[key]))

        if 1: #detail
            print("===== all detail  =====")
            data_out = nx.node_link_data(self.G)
            #print(json.dumps(json_out))
            print(data_out)

        if 1: #dump dot format
            print("===== dot format =====")
            edges = nx.edges(self.G)
            print("digraph G {")
            for e in edges:
                print("\t%s->%s [label=\"%s\"]" %(e[0],e[1],self.G.edges[e[0], e[1]]['edge_id']))
            print("}")

