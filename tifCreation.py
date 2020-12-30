'''
L'entièreté du code a été réalisé par Frédérick Pineault (frederick.pineault@mffp.gouv.qc.ca)

Ce fichier contient 2 fonctions très similaire qui permettent la création de fichiers TIF
via les différentes couches jp2 Sentinel
Pour chaque tuile, 4 images tifs sont créées soit RGB, NIR et leur version découpé selon le masque

Pour simplifier le code, la fonction createTIF pourrait faire appel à createTIFfromBand 
pour éviter d'avoir beaucoup de ligne de code qui se répète 
'''

import sys, ressource, os, subprocess, time, csv, tempfile, pickle, shutil, fileProcessing, gdal, osr, projTxt
import numpy as np
#from osgeo import *

#Récupère les bandes 2-3-4-8-12, la bande 12 doit être transformer vers une résolution de 10m
#Prépare les noms d'enregistrement, récupère les données géospatiales
#Création d'une image tif RGB et d'une image tif NIR que l'on transpose en Québec Lambert
#Transformation du masque vers une résolution de 10m
#Création des bandes RGB et NIR en fonction du masque, si le pixel est un nuage, il devient no-data
#Tous fichiers nécessaire pour la création des TIF sont supprimés (ex. B12_10m)

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

                fileout = driver.Create(cutNIRWarpPath,sizeX,sizeY, 3, gdal.GDT_UInt16, ["COMPRESS=LZW","PHOTOMETRIC=RGB"])
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

#Similaire à createTIF, permet la création d'un agencement de 3 bandes vers une image TIF
#La résolution finale peut être de 10, 20 ou 60m. Il est possible de créer la version découpée
def createTIFfromBand(band1, band2, band3, proj, pixelSize, savePath, cutPath='', imgPath=''): 
    
    try :
        tempDir = tempfile.mkdtemp()
        B01 = gdal.Open(band1)
        B02 = gdal.Open(band2)
        B03 = gdal.Open(band3)
        

        tempgeoref = B01.GetGeoTransform()
        
        if proj == '17' : src = osr.SpatialReference(projTxt.projUTM17N)
        elif proj == '18' : src = osr.SpatialReference(projTxt.projUTM18N)
        elif proj == '19' : src = osr.SpatialReference(projTxt.projUTM19N)
        elif proj == '20' : src = osr.SpatialReference(projTxt.projUTM20N)
        elif proj == '21' : src = osr.SpatialReference(projTxt.projUTM21N)
        else : return False


        dst = osr.SpatialReference()
        dst.ImportFromWkt(projTxt.projQBLambert)
        
        toRemove = []

        if pixelSize == '60 m' :
            lenght = 1830
            PPM = 60
        elif pixelSize == '20 m' :
            lenght = 5490
            PPM = 20
        elif pixelSize == '10 m' :
            lenght = 10980
            PPM = 10

        georef = (tempgeoref[0], PPM, 0.0, tempgeoref[3], 0.0, -PPM)
        
        
        if B01.RasterXSize != lenght :
            newB01Path = os.path.join(tempDir,'resizeB01.tif')
            b01XML = newB01Path + '.aux.xml'
            path01XML = os.path.join(tempDir,b01XML)
            toRemove.append(newB01Path)
            toRemove.append(path01XML)
            gdal.Translate(newB01Path, B01, format='JP2OpenJPEG', width=lenght, height=lenght, resampleAlg='cubic', outputType=gdal.GDT_UInt16)
            B01 = gdal.Open(newB01Path)
        
        if B02.RasterXSize != lenght :
            newB02Path = os.path.join(tempDir,'resizeB02.tif')
            b02XML = newB02Path + '.aux.xml'
            path02XML = os.path.join(tempDir, b02XML)
            toRemove.append(newB02Path)
            toRemove.append(path02XML)
            gdal.Translate(newB02Path, B02, format='JP2OpenJPEG', width=lenght, height=lenght, resampleAlg='cubic', outputType=gdal.GDT_UInt16)
            B02 = gdal.Open(newB02Path)
        
        if B03.RasterXSize != lenght :
            newB03Path = os.path.join(tempDir,'resizeB03.tif')
            b03XML = newB03Path + '.aux.xml'
            path03XML = os.path.join(tempDir,b03XML)
            toRemove.append(newB03Path)
            toRemove.append(path03XML)
            gdal.Translate(newB03Path, B03, format='JP2OpenJPEG', width=lenght, height=lenght, resampleAlg='cubic', outputType=gdal.GDT_UInt16)
            B03 = gdal.Open(newB03Path)
        

        band1Array = B01.GetRasterBand(1).ReadAsArray()
        band2Array = B02.GetRasterBand(1).ReadAsArray()
        band3Array = B03.GetRasterBand(1).ReadAsArray()
        
        preWarpPath = os.path.join(tempDir,'preWarp.tif')
        toRemove.append(preWarpPath)

        driver = gdal.GetDriverByName("GTiff")
        fileout = driver.Create(savePath,lenght,lenght, 3, gdal.GDT_UInt16, ["COMPRESS=LZW","PHOTOMETRIC=RGB"])
        fileout.GetRasterBand(1).WriteArray(band1Array)
        fileout.GetRasterBand(2).WriteArray(band2Array)
        fileout.GetRasterBand(3).WriteArray(band3Array)
        fileout.GetRasterBand(1).SetNoDataValue(0)
        fileout.GetRasterBand(2).SetNoDataValue(0)
        fileout.GetRasterBand(3).SetNoDataValue(0)


        fileout.SetProjection(src.ExportToWkt())
        fileout.SetSpatialRef(src)
        fileout.SetGeoTransform(georef)
        fileout.FlushCache()
        fileout = None

        gdal.Warp(savePath, preWarpPath, dstSRS=dst, xRes=PPM, yRes=PPM, targetAlignedPixels=True, dstNodata=0, resampleAlg='cubic', creationOptions=["COMPRESS=LZW","PHOTOMETRIC=RGB"])

        if cutPath :

            img = gdal.Open(imgPath)
            preWarpCut = preWarpPath = os.path.join(tempDir,'preCutWarp.tif')
            toRemove.append(preWarpCut)

            if pixelSize == '10 m' or pixelSize == '60 m' :
                newImageSize = preWarpPath = os.path.join(tempDir,'imgResize.img')
                resizeXML = preWarpPath = os.path.join(tempDir,'imgResize.img.aux.xml')
                toRemove.append(newImageSize)
                toRemove.append(resizeXML)
                imgResize = gdal.Translate(newImageSize, img, width=lenght, height=lenght, outputType=gdal.GDT_Byte)
                imgArray = imgResize.GetRasterBand(1).ReadAsArray()
            
            else :
                imgResize = None
                imgArray = img.GetRasterBand(1).ReadAsArray()

            new1Array  = np.zeros((lenght,lenght),dtype=np.uint16)
            new2Array  = np.zeros((lenght,lenght),dtype=np.uint16)
            new3Array  = np.zeros((lenght,lenght),dtype=np.uint16)

            for ix in range(lenght):
                for iy in range(lenght):
                    val = int(imgArray[ix,iy])
                    if val == 0 or val == 2 or val == 3: 
                        new1Array[ix,iy] = 0
                        new2Array[ix,iy] = 0 
                        new3Array[ix,iy] = 0

                    elif val == 1 or val == 4 or val == 5 :
                        new1Array[ix,iy] = band1Array[ix,iy]
                        new2Array[ix,iy] = band2Array[ix,iy]
                        new3Array[ix,iy] = band3Array[ix,iy]
        
            fileout = driver.Create(preWarpCut,lenght,lenght, 3, gdal.GDT_UInt16, ["COMPRESS=LZW","PHOTOMETRIC=RGB"])
            fileout.GetRasterBand(1).WriteArray(new1Array)
            fileout.GetRasterBand(2).WriteArray(new2Array)
            fileout.GetRasterBand(3).WriteArray(new3Array)
            fileout.GetRasterBand(1).SetNoDataValue(0)
            fileout.GetRasterBand(2).SetNoDataValue(0)
            fileout.GetRasterBand(3).SetNoDataValue(0)


            fileout.SetProjection(src.ExportToWkt())
            fileout.SetSpatialRef(src)
            fileout.SetGeoTransform(georef)
            fileout.FlushCache()
            fileout = None

            gdal.Warp(cutPath, preWarpCut, dstSRS=dst, xRes=PPM, yRes=PPM, targetAlignedPixels=True, dstNodata=0, resampleAlg='cubic', creationOptions=["COMPRESS=LZW","PHOTOMETRIC=RGB"])
            
        
        B01 = B02 = B03 = imgResize = None
        for item in toRemove: 
            if os.path.exists(item) :
                os.remove(item)
        
        shutil.rmtree(tempDir)
        return True

    except :    
        B01 = B02 = B03 = imgResize = None
        for item in toRemove: 
            if os.path.exists(item) :
                os.remove(item)
        
        shutil.rmtree(tempDir)
        return False

#U:\Mosaique_Sentinel\S2B_MSIL1C_20200905T155829_N0209_R097_T18TVT_20200905T193742.SAFE

#b1 = 'U:\\Mosaique_Sentinel\\S2B_MSIL1C_20200905T155829_N0209_R097_T18TVT_20200905T193742.SAFE\\GRANULE\\L1C_T18TVT_A018284_20200905T160134\\IMG_DATA\\T18TVT_20200905T155829_B01.jp2'
#b2 = 'U:\\Mosaique_Sentinel\\S2B_MSIL1C_20200905T155829_N0209_R097_T18TVT_20200905T193742.SAFE\\GRANULE\\L1C_T18TVT_A018284_20200905T160134\\IMG_DATA\\T18TVT_20200905T155829_B04.jp2'
#b3 = 'U:\\Mosaique_Sentinel\\S2B_MSIL1C_20200905T155829_N0209_R097_T18TVT_20200905T193742.SAFE\\GRANULE\\L1C_T18TVT_A018284_20200905T160134\\IMG_DATA\\T18TVT_20200905T155829_B8A.jp2'
#sPath = 'U:\\Mosaique_Sentinel\\S2B_MSIL1C_20200905T155829_N0209_R097_T18TVT_20200905T193742.SAFE\\norm.tif'
#cPath = 'U:\\Mosaique_Sentinel\\S2B_MSIL1C_20200905T155829_N0209_R097_T18TVT_20200905T193742.SAFE\\cut.tif'
#img = 'U:\\Mosaique_Sentinel\\S2B_MSIL1C_20200905T155829_N0209_R097_T18TVT_20200905T193742.SAFE\\T18TVT_20200905T155829.img'
#createTIFfromBand(b1, b2, b3, '60 m', sPath, cPath, img)
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
        pass
'''
#path = 'U:/Mosaique_Sentinel/S2B_MSIL1C_20200905T155829_N0209_R097_T18TVT_20200905T193742.SAFE - Copie'
#createTIF(path)