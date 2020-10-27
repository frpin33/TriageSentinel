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
import zipfile, shutil, tempfile, subprocess, sys, pickle
#from resultTest import resultWindow 


class objSentinel : 
    def __init__(self, pathSAFE='', nameIMG='', totalClearPercent=0.0, clearPercent=[0]*16, isTopFile=[False]*16, underPercent=True) :
            self.pathSAFE = pathSAFE
            self.nameIMG = nameIMG
            self.totalClearPercent = totalClearPercent
            self.clearPercent = clearPercent
            self.isTopFile = isTopFile
            self.underPercent = underPercent

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


Path = "I:\\TeleDiff\\Commun\\a-Images-Satellites\\SENTINEL\\Information"
listDir = os.listdir(Path)
for item in listDir :
    newpath = os.path.join(Path, item)
    if newpath == "I:\\TeleDiff\\Commun\\a-Images-Satellites\\SENTINEL\\Information\\T18UVV.txt" :
        pass
    else :
        #pathStoreFile = "I:\\TeleDiff\\Commun\\a-Images-Satellites\\SENTINEL\\Information\\T18UVV.txt"
        listObjSentinel = pickle.load(open(newpath,'rb'))

        for obj in listObjSentinel : 
            oldTable = obj.clearPercent
            tableVal = [0]*16

            tableVal[0] = oldTable[0]
            tableVal[1] = oldTable[4]
            tableVal[2] = oldTable[8]
            tableVal[3] = oldTable[12]
            tableVal[4] = oldTable[1]
            tableVal[5] = oldTable[5]
            tableVal[6] = oldTable[9]
            tableVal[7] = oldTable[13]
            tableVal[8] = oldTable[2]
            tableVal[9] = oldTable[6]
            tableVal[10] = oldTable[10]
            tableVal[11] = oldTable[14]
            tableVal[12] = oldTable[3]
            tableVal[13] = oldTable[7]
            tableVal[14] = oldTable[11]
            tableVal[15] = oldTable[15]
            obj.clearPercent = tableVal

        pickle.dump(listObjSentinel ,open(newpath,"wb"))






"""
for item in years:
    yPath = os.path.join(pathSentinel, item)
    listSAFEDirectory = os.listdir(yPath)
    for safe in listSAFEDirectory :
        num = safe.split('_')[5]
        if num not in listTuile :
            listTuile[num] = 1
        else :
            listTuile[num] = listTuile[num] +1 
         safePath = os.path.join(yPath, safe)
        try : 
            

            param = safe.split('_')
            tile = param[5]
            nameIMG = tile + '_' + param[2] + '.img'
            outIMG = os.path.join(safePath, nameIMG)
            if os.path.exists(outIMG) :
                            pass
            else :
                #print('dont exist')
                subprocess.call(["launchConda.bat", safePath, outIMG, tempDir])
            #newSentinelObj.append(objSentinel(inSAFE,nameIMG))
            
        except :
            pass
#shutil.rmtree(tempDir)
print(sys.argv[1])
#print('done')
path2020 = os.path.join(pathSentinel, '2020')
listSAFEDirectory = os.listdir(path2020)
p1 = listSAFEDirectory[:114]
p2 = listSAFEDirectory[114:228]
p3 = listSAFEDirectory[228:342]
p4 = listSAFEDirectory[342:]

if sys.argv[1] == '1' :
    listSafe = p1
elif sys.argv[1] == '2' :
    listSafe = p2
elif sys.argv[1] == '3' :
    listSafe = p3
elif sys.argv[1] == '4' :
    listSafe = p4
#tempDir = tempfile.mkdtemp()

#storeFileName = tileNumber + '.txt'
#pathStoreFile = os.path.join(yearPath, "Information", storeFileName)

listObjSentinel = []

listNotSize = []

newSentinelObj = []
for dirName in listSafe :
    if dirName.split('.')[-1] == 'SAFE' :
        try :  
            inSAFE = os.path.join(path2020, dirName)
            param = dirName.split('_')
            date = param[2].split('T')
            tile = param[5]
            nameIMG = tile + '_' + param[2] + '.img'
            outIMG = os.path.join(inSAFE, nameIMG)
            if os.path.exists(outIMG) :
                pass
            else :
                #print('dont exist')
                subprocess.call(["launchConda.bat", inSAFE, outIMG, tempDir])
            #newSentinelObj.append(objSentinel(inSAFE,nameIMG))
                    
        except :
            pass
shutil.rmtree(tempDir)

app = QtWidgets.QApplication(sys.argv)

showResultWindow = resultWindow()

for row in listNotSize:
            showResultWindow.addPictureFrame(row)
            
showResultWindow.show()
r=QtCore.QRectF(0,0,1600,1384)
showResultWindow.ui.graphicsView.fitInView(r, QtCore.Qt.KeepAspectRatio)

sys.exit(app.exec_())

size = len(a)
countZip = 0
countSafe = 0

listSafe = []
listTile = []

for i in a :
    tile = i.split('_')[5]
    if tile not in listTile : 
        listTile.append(tile)
listTile.sort()"""
    


"""if i.split('.')[-1] == 'zip' :
        countZip += 1
        inpath = os.path.join(path2018, i)
        listZip.append(inpath)
        try :
            pass
            #os.remove(inpath)
            #shutil.rmtree(inpath)
        except:
            print(inpath)
        #
            #pass
            #files = list(filter(lambda f: f.startswith("subdir"), zip_ref.namelist()))
        #ytr= zip_ref.namelist()[0].split('/')[0]
        #gdf = zip_ref.infolist()
        #print(files)
    else :
        countSafe += 1 
        listSafe.append(i)"""

countMatch = 0

"""
uwu = []
for z in listZip :
    if z[0] =='L1C' :
        if z[1] == 'T18UWU' :
            uwu.append(z)
    if z[0] == 'S2B' or z[0] == 'S2A' :
        if z[5] == 'T18UWU':
            uwu.append(z)

uwus = []   
for safe in listSafe :
        if safe[5] == 'T18UWU' :
            uwus.append(safe)

import collections
ZipL = []
#or safe in listSafe :


    inpath = os.path.join(path2018, z)
    try : 
        with zipfile.ZipFile(inpath, 'r') as zip_ref:
            zip_ref.extractall(path2018)
        #shutil.rmtree(inpath)
    except Exception as e:
        print(e)

    #with zipfile.ZipFile(z, 'r') as zip_ref:
    #    pass
    #ytr= zip_ref.namelist()[0].split('/')[0]
    #ZipL.append(ytr)

print(len(ZipL))
print([item for item, count in collections.Counter(ZipL).items() if count > 1])

for safe in listSafe :
    if safe not in ZipL : 
        print(safe)
  
#if safe == ytr : 
#countMatch +=1

if z[0] =='L1C' :
    if safe[5] == z[1] and safe[2] == z[3] :
        countMatch += 1 
if z[0] == 'S2B' or z[0] == 'S2A' :
    if safe[5] == z[5] and safe[2] == z[2] :
        countMatch += 1""" 
              
#print(countZip/size)
#print(countSafe/size)

"""
        inpath = os.path.join(path2018, i)
        try : 
            with zipfile.ZipFile(inpath, 'r') as zip_ref:
                zip_ref.extractall(path2018)
            shutil.rmtree(inpath)
        except :
            print('here')"""



#import shutil
#shutil.rmtree(path)
"""
class objSentinel : 
    def __init__(self, pathSAFE='', pathIMG='', cloudPercent=0, clearPercent=0) :
            self.pathSAFE = pathSAFE
            self.pathIMG = pathIMG
            self.cloudPercent = cloudPercent
            self.clearPercent = clearPercent

import pickle
keepTopValue = 5
path = "C:/Users/Frederick/Desktop/Work_Git/mosaique/Sentinel_T18TUT/2018/Information/T18TUT.txt"
listObjSentinel = pickle.load(open(path,'rb'))
listObjSentinel = []

topE = [0,0]
topR =[topE]*keepTopValue
topTable = [topR]*16
            
objNumber = 0
list2Edit = list(listObjSentinel)
for obj in listObjSentinel :
    for num in range(16):
        
        topRank = list(topTable[num])
    
        currentVal = obj.clearPercent[num]

        if objNumber < keepTopValue :

            topRank[objNumber] = [currentVal, objNumber]
            obj.isTopFile[num] = True
            if objNumber == keepTopValue - 1  :
                topRank.sort(reverse=True, key = lambda tup: tup[0])


        elif currentVal > topRank[keepTopValue-1][0] : 
            objListPosition = topRank[keepTopValue-1][1]
            #Tester si cette opération est sécuritaire en mémoire
            topFile2Edit = list(list2Edit[objListPosition].isTopFile) 
            topFile2Edit[num]= False
            list2Edit[objListPosition].isTopFile = topFile2Edit
            obj.isTopFile[num] = True
            topRank[keepTopValue-1] = [currentVal, objNumber]
            topRank.sort(reverse=True, key = lambda tup: tup[0])
            
        topTable[num] = topRank
    
    objNumber += 1
            

print(objNumber)



a = objSentinel('a', 'b', 50,49)
b = [1,2]
pickle.dump(a,open("test.txt","wb"))

c = pickle.load(open("test.txt",'rb'))

#i = [x[0] for x in os.walk(pathGranule)]
#j = os.listdir(pathGranule)
#k = os.listdir(pathQI)
t = time.time()
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

