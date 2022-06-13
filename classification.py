# -*- coding: utf-8 -*-
"""
@author: Ann Mutitu
"""

#--------------------------Data Extraction-----------------------------

init={'l5':'Clipped/LT05/','l7':'Clipped/LT07/','l8':'Clipped/LT08/'}

l5_images={'Band1':'LT05_B1_Clipped.tif','Band2':'LT05_B2_Clipped.tif',
        'Band3':'LT05_B3_Clipped.tif','Band4':'LT05_B4_Clipped.tif',
        'Band5':'LT05_B5_Clipped.tif','Band6':'LT05_B6_Clipped.tif',
        'Band7':'LT05_B7_Clipped.tif'}

l7_images={'Band1':'LT07_B1_Clipped.tif','Band2':'LT07_B2_Clipped.tif',
           'Band3':'LT07_B3_Clipped.tif','Band4':'LT07_B4_Clipped.tif',
           'Band5':'LT07_B5_Clipped.tif','Band6_1':'LT07_B6_VCID_1_Clipped.tif',
           'Band6_2':'LT07_B6_VCID_2_Clipped.tif','Band7':'LT07_B7_Clipped.tif'}

l8_images={'Band1':'LT08_B1_Clipped.tif','Band2':'LT08_B2_Clipped.tif',
           'Band3':'LT08_B3_Clipped.tif','Band4':'LT08_B4_Clipped.tif',
           'Band5':'LT08_B5_Clipped.tif','Band6':'LT08_B6_Clipped.tif',
           'Band7':'LT08_B7_Clipped.tif','Band9':'LT08_B9_Clipped.tif',
           'Band10':'LT08_B10_Clipped.tif','Band11':'LT08_B11_Clipped.tif'}

import rasterio as ro
import pandas as pd

def extract_bands(t,l,initial,x,y):
    bands=list(l.keys())
    data={}
    for b in bands:
        image=ro.open(initial+l[b])
        data[b]=image.read(1).flatten()
    data['X_coord']=x
    data['Y_coord']=y
    df=pd.DataFrame(data)
    df.to_csv(t+'.csv',index=None)
    return('Done')
def extract_coords(image):
    x_coord=[]
    y_coord=[]
    bands=image.read()
    shape=bands.shape
    for r in range(shape[1]):
        for c in range(shape[2]):
            coord=ro.transform.xy(image.transform,r,c)
            x_coord.append(coord[0])
            y_coord.append(coord[1])
    return(x_coord,y_coord)
x,y=extract_coords(ro.open('Clipped/LT05/LT05_B1_Clipped.tif'))
landsat5=extract_bands('Landsat5',l5_images,init['l5'],x,y)
landsat7=extract_bands('Landsat7',l7_images,init['l7'],x,y)
landsat8=extract_bands('Landsat8',l8_images,init['l8'],x,y)

#----------------Random Forest Classification-------------------------
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics

image_data=pd.read_csv('Extracted Data/Landsat8.csv')
unclassified_image=image_data[['Band1','Band2','Band3','Band4',
                               'Band5','Band6','Band7','Band9',
                               'Band10','Band11']]

training_data=pd.read_csv('Training/training_points.csv')

X=training_data[['Band1','Band2','Band3','Band4','Band5','Band6','Band7',
                 'Band9','Band10','Band11']]
y=training_data['class']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25)
clf=RandomForestClassifier(n_estimators=100)

#Train the model using the training sets y_pred=clf.predict(X_test)
clf.fit(X_train,y_train)
y_pred=clf.predict(X_test)
print("Accuracy:",metrics.accuracy_score(y_test, y_pred))
classification=clf.predict(unclassified_image)
image_data['Class']=classification
image_data.to_csv('Classified_Data/Landsat 8 Classified.csv',index=None)

        