import pickle, os, shutil, gdal, osr, sys, pathlib
import fileProcessing


listSAFEDirectory= fileProcessing.getAllSAFEPath()

dirName = os.path.basename(listSAFEDirectory[0])
param = dirName.split('_')
date = param[2].split('T')
tile = param[5] 

nameRGBCut = tile + '_' + param[2] + '_RGB_Cut.tif'
path = os.path.join(listSAFEDirectory[0], nameRGBCut)

#import pathlib, datetime
#b = pathlib.Path(path).stat().st_mtime

#1613584764.970262

p1 = listSAFEDirectory[:337]
p2 = listSAFEDirectory[337:674]
p3 = listSAFEDirectory[674:1011]
p4 = listSAFEDirectory[1011:]


if sys.argv[1] == '1' :
    listSafe = p1
elif sys.argv[1] == '2' :
    listSafe = p2
elif sys.argv[1] == '3' :
    listSafe = p3
elif sys.argv[1] == '4' :
    listSafe = p4

tab = []
for i in range(1,9):
    tab.append(2**i)

for item in listSAFEDirectory :
    try : 
        dirName = os.path.basename(item)
        param = dirName.split('_')
        date = param[2].split('T')
        tile = param[5] 

        nameRGBCut = tile + '_' + param[2] + '_RGB_Cut.tif'
        1613584764.970262
        
        path = os.path.join(item, nameRGBCut)

        #if pathlib.Path(path).stat().st_mtime < 1613584764.970262
        if os.path.exists(path) and pathlib.Path(path).stat().st_mtime < 1613584764.970262: 
            ret = gdal.Open(path, 1)
            ret.BuildOverviews('AVERAGE', tab)
            ret=None

        nameNIRCut = tile + '_' + param[2] + '_NIR_Cut.tif'
        path = os.path.join(item, nameNIRCut)
        if os.path.exists(path) and pathlib.Path(path).stat().st_mtime < 1613584764.970262: 
            ret = gdal.Open(path, 1)
            ret.BuildOverviews('AVERAGE', tab)
            ret=None

        nameRGB = tile + '_' + param[2] + '_RGB.tif'
        path = os.path.join(item, nameRGB)
        if os.path.exists(path) and pathlib.Path(path).stat().st_mtime < 1613584764.970262 : 
            ret = gdal.Open(path, 1)
            ret.BuildOverviews('AVERAGE', tab)
            ret=None

        nameNIR = tile + '_' + param[2] + '_NIR.tif'
        path = os.path.join(item, nameNIR)
        if os.path.exists(path) and pathlib.Path(path).stat().st_mtime < 1613584764.970262 : 
            ret = gdal.Open(path, 1)
            ret.BuildOverviews('AVERAGE', tab)
            ret=None
    except : pass


#ret = gdal.Open(path, 1)
#gdal.Translate(path, ret, options=['TILED=YES'])

#ret.__getattr__('TILED')
#ret.__getattribute__('TILED')
#print(path)
#ret = gdal.Open(path)
#ret.BuildOverviews('AVERAGE', tab)
#ret.FlushCache()
#ret = None#