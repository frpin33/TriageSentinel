tileList = ['T17UPQ', 'T17UPP', 'T17TPN', 'T17TPM', 'T17UQQ', 'T17UQP', 'T17TQN', 'T17TQM', 'T18UUV', 'T18UUU', 'T18TUT', 'T18UVU', 'T18UVV']
#tileList = ['T17TPM']

textFileLocation = "I:\\TeleDiff\\Commun\\a-Images-Satellites\\SENTINEL\\Information"
pasteDir = "I:\\TeleDiff\\Commun\\a-Images-Satellites\\SENTINEL\\Test_Pyramid_Result"

import pickle, os, shutil, gdal, osr
from PyQt5 import QtCore

class objSentinel : 
    def __init__(self, pathSAFE='', nameIMG='', totalClearPercent=0.0, clearPercent=[0]*16, isTopFile=[False]*16, underPercent=True) :
            self.pathSAFE = pathSAFE
            self.nameIMG = nameIMG
            self.totalClearPercent = totalClearPercent
            self.clearPercent = clearPercent
            self.isTopFile = isTopFile
            self.underPercent = underPercent
#Le but de ce fichier est de créer un TIF RGB pour chaque tuile #1 des Tuiles données
#1. Récupération des fichiers
#2. Placer les tuiles dans le dossier I:\TeleDiff\Commun\a-Images-Satellites\SENTINEL\Pyramidal_TIFF
Tile2Use = {}
tab = []
for i in range(1,9):
    tab.append(2**i)

for tile in tileList :
    tileName = tile + ".txt"
    tilePath = os.path.join(textFileLocation, tileName)
    listObj = pickle.load(open(tilePath,'rb'))
    for obj in listObj :
        dirName = obj.pathSAFE
        param = dirName.split('_')
        date = param[2].split('T')
        if date[0] > "20200701" :
            currentDir = obj.pathSAFE
            currentPasteDir = pasteDir + '\\' + obj.nameIMG.split('.')[0]
            os.mkdir(currentPasteDir)
            Tile2Use[currentDir] = currentPasteDir
            break

for currentDir, currentPasteDir in Tile2Use.items() :
    filePath = currentDir
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

    gb02 = gdal.Open(b02Path)
    gb03 = gdal.Open(b03Path)
    gb04 = gdal.Open(b04Path)

    ab02 = gb02.GetRasterBand(1).ReadAsArray()
    ab03 = gb03.GetRasterBand(1).ReadAsArray()
    ab04 = gb04.GetRasterBand(1).ReadAsArray()

    sizeX = gb04.RasterXSize
    sizeY = gb04.RasterYSize

    
    

    proj = gb04.GetProjection()
    georef = gb04.GetGeoTransform()
    src = osr.SpatialReference(proj)
    dst = osr.SpatialReference()
    dst.ImportFromEPSG(32198)

    driver = gdal.GetDriverByName('GTiff')

    rgbWarpName = paramOfName[-2] + '_' + paramOfName[-5] + '_RGB_PreWarp.tif'
    rbgWarpPath = os.path.join(currentPasteDir, rgbWarpName)
    
    rgbName = paramOfName[-2] + '_' + paramOfName[-5] + '_RGB.tif'
    rbgPath = os.path.join(currentPasteDir, rgbName)

    fileout = driver.Create(rbgWarpPath, ab04.shape[0], ab04.shape[1], 3, gdal.GDT_UInt16, ["COMPRESS=LZW","PHOTOMETRIC=RGB"])

    fileout.GetRasterBand(1).WriteArray(ab04)
    fileout.GetRasterBand(2).WriteArray(ab03)
    fileout.GetRasterBand(3).WriteArray(ab02)


    fileout.SetProjection(src.ExportToWkt())
    fileout.SetSpatialRef(src)
    fileout.SetGeoTransform(georef)
    fileout.FlushCache()
    fileout = None

    ret = gdal.Warp(rbgPath, rbgWarpPath, dstSRS=dst, xRes=10, yRes=10, targetAlignedPixels=True, dstNodata=0, resampleAlg='cubic', creationOptions=["COMPRESS=LZW","PHOTOMETRIC=RGB", "TILED=YES"])
    ret.BuildOverviews('AVERAGE', tab)
    ret.FlushCache()
    ret = None

    os.remove(rbgWarpPath)




#3. Supprimer les fichier RGB NIR --> Manuellement

#4. Créer le TIF RGB pyramid 