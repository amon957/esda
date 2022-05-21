import numpy as np
import pandas as pd
import math

def combine_coordinates(x,y):
    coords=[]
    for a,b in zip(x,y):
        coords.append((a,b))
    return(coords)

def calculate_angle_distance_matrix(coords):
    row_dist=[]
    row_angles=[]
    for i in range(len(coords)):
        dist=[]
        angle=[]
        for j in range(len(coords)):
            if j==i:
                dist.append(0)
                angle.append(0)
            else:
                change_x=coords[i][0]-coords[j][0]
                change_y=coords[i][1]-coords[j][1]
                dist.append(round(math.sqrt(math.pow(change_x,2)+math.pow(change_y,2)),3))
                angle.append(round(math.degrees(math.atan(change_y/change_x)),3))
        row_dist.append(dist)
        row_angles.append(angle)
    return(row_dist,row_angles)

def calculate_tpp(dist,angles,type_):
    tpp=[]
    ind=dist.sort_values().index
    if type_=='raster':
        range_=len(dist)
    else:
        range_=int(0.1*len(dist))
    for i in range(range_):
        r=dist[ind[i]]
        theta=angles[ind[i]]
        if theta<0:
            theta=(theta*-1)+180
        tpp.append((r*math.cos(math.radians(theta)),r*math.sin(math.radians(theta))))
    return(tpp)

def find_cpp(tpp_r,vector_distances,vector_angles):
    threshold=1
    def iterrate_threshold(threshold):
        found_cpp=[]
        for j in range(len(vector_distances)):
            tpp_v=calculate_tpp(vector_distances[j],vector_angles[j],'vector')
            for i in range(len(tpp_v)):
                test=(tpp_v[i][0]-tpp_r[1][0])-(tpp_v[i][1]-tpp_r[1][1])
                if test<0:
                    test=test*-1
                if test<threshold:
                    found_cpp.append(j)
                    break
        return(found_cpp)
    final_cpp=[]
    while threshold<=10:
        cpp=iterrate_threshold(threshold)
        if len(cpp)==2:
            threshold=11
            final_cpp.append(tuple(cpp))
        else:
            threshold=threshold+1
    return(final_cpp)

raster_intersections=pd.read_csv('raster.csv')
vector_intersections=pd.read_csv('vector.csv')


x_r=np.array(raster_intersections['x'])
y_r=np.array(raster_intersections['y'])
x_v=np.array(vector_intersections['x'])
y_v=np.array(vector_intersections['y'])
    
raster_coords=combine_coordinates(x_r,y_r)
vector_coords=combine_coordinates(x_v,y_v)

dist_r,angles_r=calculate_angle_distance_matrix(raster_coords)
dist_v,angles_v=calculate_angle_distance_matrix(vector_coords)

df_raster_dist=pd.DataFrame(dist_r)
df_raster_angles=pd.DataFrame(angles_r)

df_vector_dist=pd.DataFrame(dist_v)
df_vector_angles=pd.DataFrame(angles_v)
cpp_f=[]
for k in range(len(df_raster_dist)):
    tpp_r=calculate_tpp(df_raster_dist[k],df_raster_angles[k],'raster')
    cpp=find_cpp(tpp_r,df_vector_dist,df_vector_angles)
    try:
        if cpp[0][0] in cpp_f:
            cpp_f.append(cpp[0][1])
        else:
            cpp_f.append(cpp[0][0])
    except IndexError:
        cpp_f.append(None)
x_coord=[]
y_coord=[]
for i in range(len(cpp_f)):
    if cpp_f[i]==None:
        x_coord.append(None)
        y_coord.append(None)
    else:
        x_coord.append(x_v[cpp_f[i]])
        y_coord.append(y_v[cpp_f[i]])
raster_intersections['Corresponding Vector X']=x_coord
raster_intersections['Corresponding Vector Y']=y_coord
raster_intersections.to_csv('Populated Raster Points.csv')
print('Autogeorefencing Done')