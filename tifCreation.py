import sys, ressource, os, subprocess, time, csv, tempfile, pickle, shutil, gdal, osr, fileProcessing
import numpy as np


def createTIF(filePath) :

    toRemove = []

    pathGranule = os.path.join(filePath, 'GRANULE')
    L1CPart = os.listdir(pathGranule)[0]
    pathData = os.path.join(pathGranule, L1CPart, 'IMG_DATA')
    listFileData = os.listdir(pathData)

    dirName = os.path.basename(filePath) 
    paramOfName = dirName.split('_')

    for image in listFileData : 
        if image.split('_')[-1] == "B02.jp2":
            b02Path = os.path.join(pathData, image)
        elif image.split('_')[-1] == "B03.jp2":
            b03Path = os.path.join(pathData, image)
        elif image.split('_')[-1] == "B04.jp2":
            b04Path = os.path.join(pathData, image)
        elif image.split('_')[-1] == "B08.jp2":
            b08Path = os.path.join(pathData, image)
        elif image.split('_')[-1] == "B12.jp2":
            b12Path = os.path.join(pathData, image)
            b12Name = image.split('.')[0]

    gb02 = gdal.Open(b02Path)
    gb03 = gdal.Open(b03Path)
    gb04 = gdal.Open(b04Path)
    gb08 = gdal.Open(b08Path)
    gb12 = gdal.Open(b12Path)

    ab02 = gb02.GetRasterBand(1).ReadAsArray()
    ab03 = gb03.GetRasterBand(1).ReadAsArray()
    ab04 = gb04.GetRasterBand(1).ReadAsArray()
    ab08 = gb08.GetRasterBand(1).ReadAsArray() 

    sizeX = gb04.RasterXSize
    sizeY = gb04.RasterYSize

    b12_10m_Name = b12Name + '_10m.jp2' 
    b12_10m_Path = os.path.join(filePath, b12_10m_Name)
    toRemove.append(b12_10m_Path)
    
    gdal.Translate(b12_10m_Path, gb12, format='JP2OpenJPEG', width=sizeX, height=sizeY, resampleAlg='cubic', outputType=gdal.GDT_UInt16)
    
    
    gb12_10m = gdal.Open(b12_10m_Path)
    ab12 = gb12_10m.GetRasterBand(1).ReadAsArray()


    proj = gb04.GetProjection()
    georef = gb04.GetGeoTransform()
    src = osr.SpatialReference(proj)
    dst = osr.SpatialReference()
    dst.ImportFromEPSG(32198)

    driver = gdal.GetDriverByName('GTiff')

    rgbWarpName = paramOfName[-2] + '_' + paramOfName[-5] + '_RGB_PreWarp.tif'
    rbgWarpPath = os.path.join(filePath, rgbWarpName)
    
    rgbName = paramOfName[-2] + '_' + paramOfName[-5] + '_RGB.tif'
    rbgPath = os.path.join(filePath, rgbName)

    nirWarpName = paramOfName[-2] + '_' + paramOfName[-5] + '_NIR_PreWarp.tif' 
    nirWarpPath = os.path.join(filePath, nirWarpName)

    nirName = paramOfName[-2] + '_' + paramOfName[-5] + '_NIR.tif'
    nirPath = os.path.join(filePath, nirName)

    toRemove.append(rbgWarpPath)
    toRemove.append(nirWarpPath)

    if not os.path.exists(rbgPath) :

        fileout = driver.Create(rbgWarpPath, ab04.shape[0], ab04.shape[1], 3, gdal.GDT_UInt16, ["COMPRESS=LZW","PHOTOMETRIC=RGB"])

        fileout.GetRasterBand(1).WriteArray(ab04)
        fileout.GetRasterBand(2).WriteArray(ab03)
        fileout.GetRasterBand(3).WriteArray(ab02)


        fileout.SetProjection(src.ExportToWkt())
        fileout.SetSpatialRef(src)
        fileout.SetGeoTransform(georef)
        fileout.FlushCache()
        fileout = None

        gdal.Warp(rbgPath, rbgWarpPath, dstSRS=dst, xRes=10, yRes=10, targetAlignedPixels=True, dstNodata=0, resampleAlg='cubic', creationOptions=["COMPRESS=LZW","PHOTOMETRIC=RGB"])

    if not os.path.exists(nirPath) :

        fileout = driver.Create(nirWarpPath, ab04.shape[0], ab04.shape[1], 3, gdal.GDT_UInt16, ["COMPRESS=LZW","PHOTOMETRIC=RGB"])

        fileout.GetRasterBand(1).WriteArray(ab12)
        fileout.GetRasterBand(2).WriteArray(ab08)
        fileout.GetRasterBand(3).WriteArray(ab04)
                
        fileout.SetProjection(src.ExportToWkt())
        fileout.SetSpatialRef(src)
        fileout.SetGeoTransform(georef)

        fileout.FlushCache()
        fileout = None

        gdal.Warp(nirPath, nirWarpPath, dstSRS=dst, xRes=10, yRes=10, targetAlignedPixels=True, dstNodata=0, resampleAlg='cubic', creationOptions=["COMPRESS=LZW","PHOTOMETRIC=RGB"])
        
    imgName = paramOfName[-2] + '_' + paramOfName[-5] + '.img'
    imgPath = os.path.join(filePath, imgName)
    
    if os.path.exists(imgPath) :

        imgNameXML = paramOfName[-2] + '_' + paramOfName[-5] + '.img.aux.xml'
        imgPathXML = os.path.join(filePath, imgNameXML)

        imgName_10m = paramOfName[-2] + '_' + paramOfName[-5] + '_10m.img'
        imgPath_10m = os.path.join(filePath, imgName_10m)

        imgName_xml = paramOfName[-2] + '_' + paramOfName[-5] + '_10m.img.aux.xml'
        imgPath_xml = os.path.join(filePath, imgName_xml)

        toRemove.append(imgPathXML)
        toRemove.append(imgPath_10m)
        toRemove.append(imgPath_xml)

        gdal.Translate(imgPath_10m, imgPath, width=sizeX, height=sizeY, outputType=gdal.GDT_Byte)
            
        cutRGBWarpName = paramOfName[-2] + '_' + paramOfName[-5] + '_rgbcutwarp.tif'
        cutRGBWarpPath = os.path.join(filePath, cutRGBWarpName)

        cutRGBName = paramOfName[-2] + '_' + paramOfName[-5] + '_RGB_Cut.tif'
        cutRGBPath = os.path.join(filePath, cutRGBName)

        cutNIRWarpName = paramOfName[-2] + '_' + paramOfName[-5] + '_nircutwarp.tif'
        cutNIRWarpPath = os.path.join(filePath, cutRGBWarpName)

        cutNIRName = paramOfName[-2] + '_' + paramOfName[-5] + '_NIR_Cut.tif'
        cutNIRPath = os.path.join(filePath, cutNIRName)

        toRemove.append(cutRGBWarpPath)
        toRemove.append(cutNIRWarpPath)

        if not os.path.exists(cutRGBPath) or not os.path.exists(cutNIRPath):

            img = gdal.Open(imgPath_10m)
            imgArray = img.GetRasterBand(1).ReadAsArray()

            redArray  = np.zeros((sizeX,sizeY),dtype=np.uint16)
            greenArray  = np.zeros((sizeX,sizeY),dtype=np.uint16)
            blueArray  = np.zeros((sizeX,sizeY),dtype=np.uint16)
            nirArray = np.zeros((sizeX,sizeY),dtype=np.uint16)
            swirArray = np.zeros((sizeX,sizeY),dtype=np.uint16)

            for ix in range(sizeX):
                for iy in range(sizeY):
                    val = int(imgArray[ix,iy])
                    if val == 0 or val == 2 or val == 3: 
                        redArray[ix,iy] = 0
                        greenArray[ix,iy] = 0 
                        blueArray[ix,iy] = 0
                        nirArray[ix,iy] = 0
                        swirArray[ix,iy] = 0

                    elif val == 1 or val == 4 or val == 5 :
                        redArray[ix,iy] = ab04[ix,iy]
                        greenArray[ix,iy] = ab03[ix,iy]
                        blueArray[ix,iy] =  ab02[ix,iy]
                        nirArray[ix,iy] =  ab08[ix,iy]
                        swirArray[ix,iy] =  ab12[ix,iy]
            img = None 

            if not os.path.exists(cutRGBPath) :
                driver = gdal.GetDriverByName("GTiff")

                fileout = driver.Create(cutRGBWarpPath,sizeX,sizeY, 3, gdal.GDT_UInt16, ["COMPRESS=LZW","PHOTOMETRIC=RGB"])
                fileout.GetRasterBand(1).WriteArray(redArray)
                fileout.GetRasterBand(2).WriteArray(greenArray)
                fileout.GetRasterBand(3).WriteArray(blueArray)
                fileout.GetRasterBand(1).SetNoDataValue(0)
                fileout.GetRasterBand(2).SetNoDataValue(0)
                fileout.GetRasterBand(3).SetNoDataValue(0)

                fileout.SetProjection(src.ExportToWkt())
                fileout.SetSpatialRef(src)
                fileout.SetGeoTransform(georef)
                fileout.FlushCache()
                fileout = None

                gdal.Warp(cutRGBPath, cutRGBWarpPath, dstSRS=dst, xRes=10, yRes=10, targetAlignedPixels=True, dstNodata=0, resampleAlg='cubic', creationOptions=["COMPRESS=LZW","PHOTOMETRIC=RGB"])
                
            if not os.path.exists(cutNIRPath) :
                driver = gdal.GetDriverByName("GTiff")

                fileout = driver.Create(cutRGBWarpPath,sizeX,sizeY, 3, gdal.GDT_UInt16, ["COMPRESS=LZW","PHOTOMETRIC=RGB"])
                fileout.GetRasterBand(1).WriteArray(swirArray)
                fileout.GetRasterBand(2).WriteArray(nirArray)
                fileout.GetRasterBand(3).WriteArray(redArray)
                fileout.GetRasterBand(1).SetNoDataValue(0)
                fileout.GetRasterBand(2).SetNoDataValue(0)
                fileout.GetRasterBand(3).SetNoDataValue(0)

                fileout.SetProjection(src.ExportToWkt())
                fileout.SetSpatialRef(src)
                fileout.SetGeoTransform(georef)
                fileout.FlushCache()
                fileout = None

                gdal.Warp(cutNIRPath, cutNIRWarpPath, dstSRS=dst, xRes=10, yRes=10, targetAlignedPixels=True, dstNodata=0, resampleAlg='cubic', creationOptions=["COMPRESS=LZW","PHOTOMETRIC=RGB"])
                
    gb12_10m = None
    for item in toRemove: 
        if os.path.exists(item) :
            os.remove(item)


def createTIFfromBand(band1, band2, band3): 
    pass #trouver les dimensions 
    #band_10m
    #band_20m 
    #band_60m 
    #if band1 in band_20m 'B01' 


'''
listSAFEDirectory = fileProcessing.getAllSAFEPath()

facteur = int(len(listSAFEDirectory)/4)

p1 = listSAFEDirectory[:facteur]
p2 = listSAFEDirectory[facteur:facteur*2]
p3 = listSAFEDirectory[facteur*2:facteur*3]
p4 = listSAFEDirectory[facteur*3:]



if sys.argv[1] == '1' :
    listSafe = p1
elif sys.argv[1] == '2' :
    listSafe = p2
elif sys.argv[1] == '3' :
    listSafe = p3
elif sys.argv[1] == '4' :
    listSafe = p4

for path in listSafe :
    try :
        createTIF(path)
    except :
        pass'''

path = 'U:/Mosaique_Sentinel/S2B_MSIL1C_20200905T155829_N0209_R097_T18TVT_20200905T193742.SAFE - Copie'
createTIF(path)