import numpy as np
import pandas as pd
import math

def combine_coordinates(x,y):
    coords=[]
    for a,b in zip(x,y):
        coords.append((a,b))
    return(coords)
def calculate_distance_matrix(coords):
    row_dist=[]
    for i in range(len(coords)):
        dist=[]
        for j in range(len(coords)):
            if j==i:
                dist.append(0)
            else:
                change_x=coords[j][0]-coords[i][0]
                change_y=coords[j][1]-coords[i][1]
                dist.append(np.sqrt(np.square(change_x)+np.square(change_y)))
        row_dist.append(dist)
    return(row_dist)
def calculate_bearing(point_1,point_2): #Bearing from point 1 to point 2
    c_y=point_2[1]-point_1[1]
    c_x=point_2[0]-point_1[0]
    angle=math.degrees(math.atan(c_x/c_y))
    if angle>0 and c_y<0:
        bearing=180+angle #3rd Quad
    elif angle<0 and c_x<0:
        bearing=360+angle #4th Quad
    elif angle<0 and c_y<0:
        bearing=180-abs(angle)
    else:
        bearing=angle
    return bearing
def reverse_theta(f_bearing_i,f_bearing_iv):
    if f_bearing_i<180:
        b_bearing_i=f_bearing_i+180
    else:
        b_bearing_i=f_bearing_i-180
    if f_bearing_iv<180:
        b_bearing_iv=f_bearing_iv+180
    else:
        b_bearing_iv=f_bearing_iv-180
        
    if f_bearing_i<180:
        if f_bearing_iv>f_bearing_i and f_bearing_iv<b_bearing_i:
            return(True)
        else:
            return(False)
    else:
        if b_bearing_iv>b_bearing_i and b_bearing_iv<f_bearing_i:
            return(True)
        else:
            return (False)
def calculate_tpp(dist,x,y,type_):
    tpp=[]
    ind=list(dist.sort_values().index)
    x_coord=[]
    y_coord=[]
    if type_=='raster':
        range_=len(dist)
    else:
        range_=int(0.25*len(dist))
    for i in range(2,range_):
        di=dist[ind[1]]
        dij=dist[ind[i]]
        rij=dij/di
        c_x=x[ind[i]]-x[ind[1]]
        c_y=y[ind[i]]-y[ind[1]]
        d_i_r=np.sqrt(np.square(c_x)+np.square(c_y))
        theta=math.acos((np.square(di)+np.square(dij)-np.square(d_i_r))/(2*di*dij))
        
        brng_anchor_unit=calculate_bearing((x[ind[0]],y[ind[0]]),(x[ind[1]],y[ind[1]]))
        brng_anchor_v=calculate_bearing((x[ind[0]],y[ind[0]]),(x[ind[i]],y[ind[i]]))
        
        reverse_angle=reverse_theta(brng_anchor_unit,brng_anchor_v)
        if reverse_angle==True:
            theta_ij=math.radians(360-math.degrees(theta))
        else:
            theta_ij=theta
        tpp.append((rij*math.cos(theta_ij),rij*math.sin(theta_ij)))
    return(tpp)

#--------------------------------------------------------------------------#
def to_polar_coord(delta_x,delta_y):
    rho=np.sqrt(np.square(delta_x)+np.square(delta_y))
    theta=math.degrees(math.atan(delta_y/delta_x))
    if delta_y<0 and delta_x<0:
        theta=180+abs(theta)
    elif delta_y<0 and delta_x>0:
        theta=360-abs(theta)
    elif delta_y>0 and delta_x<0:
        theta=180-abs(theta)
    else:
        theta=theta
    return(rho,theta)
def find_candidate_cpps(tpp_r,tpp_v,delta_r_tolerance,delta_theta_tolerance):
    max_v=np.array(tpp_r).flatten().max()
    count=0
    sum_delta_r=0
    for i in (tpp_r):
        for j in (tpp_v):
            if j[0]>max_v+delta_r_tolerance:
                break
            else:
                if abs(i[0]-j[0])<=delta_r_tolerance and abs(i[1]-j[1])<=delta_theta_tolerance:
                    count=count+1
                    sum_delta_r=sum_delta_r+abs(i[0]-j[0])
    if count>=len(tpp_r)-4:
        return(True,sum_delta_r/count)
    else:
        return(False,None)
    
raster_intersections=pd.read_csv('raster.csv')
vector_intersections=pd.read_csv('vector.csv')

x_r=np.array(raster_intersections['x'])
y_r=np.array(raster_intersections['y'])

x_v=np.array(vector_intersections['x'])
y_v=np.array(vector_intersections['y'])
    
raster_coords=combine_coordinates(x_r,y_r)
vector_coords=combine_coordinates(x_v,y_v)

dist_r=calculate_distance_matrix(raster_coords)
dist_v=calculate_distance_matrix(vector_coords)

df_raster_dist=pd.DataFrame(dist_r)
df_vector_dist=pd.DataFrame(dist_v)

cpps={}
for j in range(len(df_raster_dist)):
    tpp_r=calculate_tpp(df_raster_dist[j],x_r,y_r,'raster')
    tpp_r_polar=[]
    for p in tpp_r:
        r,t=to_polar_coord(p[0],p[1])
        tpp_r_polar.append((r,t))
        
    matching_cpps=[]
    deltas_ave=[]
    for i in range(len(df_vector_dist)):
        tpp_v=calculate_tpp(df_vector_dist[i],x_v,y_v,'vector')
        tpp_v_polar=[]
        for p in tpp_v:
            r,t=to_polar_coord(p[0],p[1])
            tpp_v_polar.append((r,t))
        
        match_status,delta_=find_candidate_cpps(tpp_r_polar,tpp_v_polar,0.1,8)
        if match_status==True:
            matching_cpps.append(i)
            deltas_ave.append(delta_)
    dict_={'Index':matching_cpps,'Delta':deltas_ave}
    df=pd.DataFrame(dict_)
    optimum_id=list(df['Delta'].sort_values().index)
    if len(matching_cpps)>0:
        cpps[str(j+1)]=df['Index'][optimum_id[0]]
    else:
        cpps[str(j+1)]=None
x_coord=[]
y_coord=[]
for i in range(len(x_r)):
    if cpps[str(i+1)]!=None:
        x_coord.append(x_v[cpps[str(i+1)]])
        y_coord.append(y_v[cpps[str(i+1)]])
    else:
        x_coord.append(None)
        y_coord.append(None)
raster_intersections['Coordinate X']=x_coord
raster_intersections['Coordinate Y']=y_coord
print('Autogeorefencing Done')