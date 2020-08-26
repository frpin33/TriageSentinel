# -*- coding: utf-8 -*-


import libsentinel as stl
import os
import xml.etree.ElementTree as ET
import time
import numpy as np
import gdal
from PyQt5 import QtCore, QtGui, QtWidgets 
from PIL import Image
import qimage2ndarray
import matplotlib.image as mpimg



#path = "U:/Mosaique_Sentinel/Sentinel_T18TUT/S2A_MSIL1C_20180514T155911_N0206_R097_T18TUT_20180514T194414.SAFE/GRANULE/L1C_T18TUT_A015109_20180514T160535/IMG_DATA"
path = "U:/Mosaique_Sentinel/Sentinel_T18TUT/S2A_MSIL1C_20180613T155901_N0206_R097_T18TUT_20180613T194300.SAFE/GRANULE/L1C_T18TUT_A015538_20180613T155924/IMG_DATA"
outPath = "U:/Mosaique_Sentinel/Sentinel_T18TUT/Out"

mask = "U:/Mosaique_Sentinel/Sentinel_T18TUT/Out/T18TUT_20180514T155911_mask_10m.tif"
reW = "U:/Mosaique_Sentinel/Sentinel_T18TUT/Out/T18TUT_20180514T155911_B02masked.tif"
band = path + "/T18TUT_20180514T155911_B02.jp2"

imgPath = "U:/cloud.img"
smallI = "U:/Mosaique_Sentinel/Sentinel_T18TUT/S2A_MSIL1C_20180514T155911_N0206_R097_T18TUT_20180514T194414.SAFE/GRANULE/L1C_T18TUT_A015109_20180514T160535/QI_DATA/T18TUT_20180514T155911_PVI.jp2"

pathSafe = "U:/Mosaique_Sentinel/Sentinel_T18TUT/S2A_MSIL1C_20180514T155911_N0206_R097_T18TUT_20180514T194414.SAFE"

pathGranule = os.path.join(pathSafe, "GRANULE")
pathQI =  "U:/Mosaique_Sentinel/Sentinel_T18TUT/S2A_MSIL1C_20180514T155911_N0206_R097_T18TUT_20180514T194414.SAFE/GRANULE/L1C_T18TUT_A015109_20180514T160535/QI_DATA"

jpgPath  = "U:/Mosaique_Sentinel/BandDesignation.jpg"

delPath = "U:/Mosaique_Sentinel/test/S2A_MSIL1C_20180613T155901_N0206_R097_T18TUT_20180613T194300.SAFE"

#import shutil
#shutil.rmtree(path)

class objSentinel : 
    def __init__(self, pathSAFE='', pathIMG='', cloudPercent=0, clearPercent=0) :
            self.pathSAFE = pathSAFE
            self.pathIMG = pathIMG
            self.cloudPercent = cloudPercent
            self.clearPercent = clearPercent

import pickle


a = objSentinel('a', 'b', 50,49)
b = [1,2]
pickle.dump(a,open("test.txt","wb"))

c = pickle.load(open("test.txt",'rb'))

#i = [x[0] for x in os.walk(pathGranule)]
#j = os.listdir(pathGranule)
#k = os.listdir(pathQI)

"""t = time.time()
raster = gdal.Open(smallI)
rArray = raster.GetRasterBand(1).ReadAsArray()
gArray = raster.GetRasterBand(2).ReadAsArray()
bArray = raster.GetRasterBand(3).ReadAsArray()

array = np.dstack((rArray,gArray, bArray))
print(time.time() - t)

t = time.time()
c = Image.open(smallI)
#d = c.load()
e = c.getbands()
arrrr = np.array(c)
#tt = arrrr.load()
print(time.time() - t)
#a = QtGui.QImage.load(smallI)"""


"""
imgP = Image.open(jpgPath)
imgNP = np.array(imgP)

raster = gdal.Open(smallI)

redArray = raster.GetRasterBand(1).ReadAsArray()
greenArray = raster.GetRasterBand(2).ReadAsArray()
blueArray = raster.GetRasterBand(3).ReadAsArray()

newArr = np.dstack((redArray,greenArray, blueArray))
image = qimage2ndarray.array2qimage(newArr)

x,y = array.shape

b = np.array_split(array,4,1)
c =[]
for item in b :
    c.append(np.array_split(item,4))

maxVal = x*y/16 

null = 0
clear = 0
cloud = 0
shadow = 0
snow = 0
water = 0

for x in np.nditer(c[3][3]) :
    val = int(x)

    if val == 0 :
        null += 1
    
    elif val == 1 :
        clear += 1
    
    elif val == 2 :
        cloud += 1
    
    elif val == 3 :
        shadow += 1
    
    elif val == 4 :
        snow += 1
    
    elif val == 5 :
        water += 1
  
pNull = null/maxVal
pClear = clear/maxVal
pCloud = cloud/maxVal
pShadow = shadow/maxVal
pSnow = snow/maxVal
pWater = water/maxVal


print(pNull)
print(pClear)
print(pCloud)
print(pShadow)
print(pSnow)
print(pWater)
"""

#s = time.time()
#retBand = stl.apply_mask(band, mask)
#stl.rewrite_band(retBand, reW, 0)

#stl.create_mask(path, outPath)
import subprocess
#subprocess.call(["sandBat.bat", "mask"])
#print(time.time()-s)


#s = time.time()
#path_XML = os.path.join(path, "MTD_MSIL1C.xml")
#str_path = ET.parse(path_XML).getroot()[0][0][11][0][0][0].text[:-27]
#full_path = os.path.join(path, str_path)

