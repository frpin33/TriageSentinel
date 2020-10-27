import sys, ressource, os, subprocess, time, csv, tempfile, pickle, shutil, gdal
import numpy as np


dataLocation = "I:\\TeleDiff\\Commun\\a-Images-Satellites\\SENTINEL"
possibleYears = ["2017","2018","2019", "2020"]
keepTopValue = 5


def unzipFile() :
    pass

def getAllSAFEPath() :
    listSAFEPath = []
    for year in possibleYears:
        yearPath = os.path.join(dataLocation, year)
        dirList = os.listdir(yearPath)
        for dirName in dirList :
            if dirName.split('.')[-1] == 'SAFE' :
                SAFEPath = os.path.join(yearPath, dirName)
                if os.path.exists(SAFEPath) :
                    listSAFEPath.append(SAFEPath)
    return listSAFEPath

def getTileNumber() :
    dictResult = {}
    for year in possibleYears:  
        yearPath = os.path.join(dataLocation, year)
        dirList = os.listdir(yearPath)
        for safe in dirList :
            num = safe.split('_')[5]
            if num not in dictResult :
                dictResult[num] = 1
            else :
                dictResult[num] = dictResult[num] +1 
    return dictResult


def cloudProcess(delete=False) :
    tempDir = tempfile.mkdtemp()

    listSAFEDirectory = getAllSAFEPath()

    for dirPath in listSAFEDirectory :
        try :
            dirName = os.path.basename(dirPath) 
            param = dirName.split('_')
            nameIMG = param[5] + '_' + param[2] + '.img'
            outIMG = os.path.join(dirPath, nameIMG)
            if os.path.exists(outIMG) :
                pass
            else :
                if delete : 
                    pathGranule = os.path.join(inSAFE, 'GRANULE')
                    L1CPart = os.listdir(pathGranule)[0]
                    pathData = os.path.join(pathGranule, L1CPart, 'IMG_DATA')
                    listFileData = os.listdir(pathData)
                    for image in listFileData : 
                        if image.split('_')[-1] == "TCI.jp2":
                            TCIPath = os.path.join(pathData, image)
                            if os.path.getsize(TCIPath) > 50*10**6 : 
                                subprocess.call(["launchConda.bat", dirPath, outIMG, tempDir])
                            else : 
                                shutil.rmtree(dirPath)

                else :     
                    subprocess.call(["launchConda.bat", dirPath, outIMG, tempDir])
        except :
            pass
    shutil.rmtree(tempDir)


def mainProcess(delete=False) : 
    
    listTileNB = [] 
    for year in possibleYears:
        yearPath = os.path.join(dataLocation, year)
        listSAFE = os.listdir(yearPath)
        for safe in listSAFE :
            tile = safe.split('_')[5]
            if tile not in listTileNB :
                listTileNB.append(tile)
    
    
    for tileNum in listTileNB :
        infoFileName = tileNum + '.txt'
        pathStoreFile = os.path.join(dataLocation, "Information", infoFileName)
        if os.path.exists(pathStoreFile) : 
            listObjSentinel = pickle.load(open(pathStoreFile,'rb'))
        else : 
            listObjSentinel = []
     
        allSentinelObj = []
        newSentinelObj = []
        for year in possibleYears:
            yearPath = os.path.join(dataLocation, year)
            listSAFEDirectory = os.listdir(yearPath)
            for safe in listSAFEDirectory :
                tile = safe.split('_')[5]
                date = safe.split('_')[2]
                nameIMG = tile + '_' + date + '.img'
                if tile == tileNum:
                    safePath = os.path.join(yearPath, safe)
                    allSentinelObj.append(objSentinel(safePath,nameIMG))
            
        for obj in allSentinelObj :
            if listObjSentinel :
                for safe in listObjSentinel :
                    if safe.pathSAFE == obj.pathSAFE :
                        break
                else :
                    newSentinelObj.append(obj)
            else : 
                newSentinelObj = allSentinelObj

        if newSentinelObj : 

            for obj in newSentinelObj :

                pathIMG = os.path.join(obj.pathSAFE, obj.nameIMG)
                if os.path.exists(pathIMG) : 
                    imgFile = gdal.Open(pathIMG)
                    array = imgFile.GetRasterBand(1).ReadAsArray()
                    
                    x,y = array.shape

                    firstSplit = np.array_split(array,4)
                    splitArray = []
                    for item in firstSplit :
                        splitArray.append(np.array_split(item,4,1))
                    
                    countCloud = [0.0]*16
                    countClear = [0.0]*16
                    null = 0
                    totalClear = 0
                    totalCloud = 0
                    for num in range(16):
                        firstNum = int(num/4)
                        secondNum = num%4
                        maxVal = x*y/16 

                        clear = 0
                        cloud = 0
                        shadow = 0
                        water = 0
                        snow = 0

                        for v in np.nditer(splitArray[firstNum][secondNum]) :
                            val = int(v)
                            
                            if val == 0 :
                                null += 1
                            
                            elif val == 1 :
                                clear += 1
                                totalClear += 1
                            
                            elif val == 2 :
                                cloud += 1
                                totalCloud += 1
                            
                            elif val == 3 :
                                shadow += 1
                                totalCloud += 1
                            
                            elif val == 4 :
                                snow += 1
                                totalClear += 1
                            
                            elif val == 5 :
                                water += 1
                                totalClear += 1

                        pClear = clear/maxVal
                        pCloud = cloud/maxVal
                        pShadow = shadow/maxVal
                        pSnow = snow/maxVal
                        pWater = water/maxVal
                        
                        countCloud[num] = (pCloud+pShadow)
                        countClear[num] = (pClear+pWater+pSnow)
                    
                    divFact = x*y
                    pNull = null/divFact
                    pTCloud = totalCloud/divFact
                    pTClear = totalClear/divFact
                    
                    if pNull > pTClear + pTCloud :
                        obj.underPercent = False
                    else :
                        if pTCloud >= 0.5 : 
                            obj.underPercent = False
                        obj.clearPercent = countClear
                        obj.totalClearPercent = pTClear
                
            completeListObjSentinel = listObjSentinel + newSentinelObj
                    
            topTable =[[(0,0) for j in range(keepTopValue)] for i in range(16)]

            isTopFile = [[False for j in range(16)] for i in range(len(completeListObjSentinel))]
            
            objNumber = 0

            for obj in completeListObjSentinel :
                for num in range(16):
                    
                    topRank = topTable[num]

                    currentVal = obj.clearPercent[num]

                    if objNumber < keepTopValue :

                        topRank[objNumber] = (currentVal, objNumber)
                        isTopFile[objNumber][num] = True
                        if objNumber == keepTopValue - 1  :
                            topRank.sort(reverse=True, key = lambda tup: tup[0])


                    elif currentVal > topRank[keepTopValue-1][0] : 
                        objListPosition = topRank[keepTopValue-1][1]
                        isTopFile[objListPosition][num] = False
                        isTopFile[objNumber][num]= True
                        topRank[keepTopValue-1] = (currentVal, objNumber)
                        topRank.sort(reverse=True, key = lambda tup: tup[0])
                        
                    topTable[num] = topRank
                
                objNumber += 1

            for i in range(len(completeListObjSentinel)) :
                completeListObjSentinel[i].isTopFile = isTopFile[i]

            if delete : 
                for obj in completeListObjSentinel :
                    if not any(obj.isTopFile) and not obj.underPercent : 
                        shutil.rmtree(obj.pathSAFE)
                        completeListObjSentinel.remove(obj)

            completeListObjSentinel.sort(reverse=True, key= lambda x : x.totalClearPercent)
            pickle.dump( completeListObjSentinel ,open(pathStoreFile,"wb"))



def create_RGB_NIR_TIF(path) : 
    pathGranule = os.path.join(path, 'GRANULE')
    L1CPart = os.listdir(pathGranule)[0]
    pathData = os.path.join(pathGranule, L1CPart, 'IMG_DATA')
    listFileData = os.listdir(pathData)
    jp2PathList = [] 
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
    
    driver = gdal.GetDriverByName('JPEG2000')
    gb02 = gdal.Open(b02Path)
    gb03 = gdal.Open(b03Path)
    gb04 = gdal.Open(b04Path)
    gb08 = gdal.Open(b08Path)
    gb12 = gdal.Open(b12Path)

    ab02 = gb02.GetRasterBand(1).ReadAsArray()
    ab03 = gb03.GetRasterBand(1).ReadAsArray()
    ab04 = gb04.GetRasterBand(1).ReadAsArray()
    ab08 = gb08.GetRasterBand(1).ReadAsArray()
    ab12 = gb12.GetRasterBand(1).ReadAsArray()
    
    print('here')


gdal.Translate()


class objSentinel : 
    def __init__(self, pathSAFE='', nameIMG='', totalClearPercent=0.0, clearPercent=[0]*16, isTopFile=[False]*16, underPercent=True) :
            self.pathSAFE = pathSAFE
            self.nameIMG = nameIMG
            self.totalClearPercent = totalClearPercent
            self.clearPercent = clearPercent
            self.isTopFile = isTopFile
            self.underPercent = underPercent

path = "U:/Mosaique_Sentinel/Sentinel_T18TUT/S2A_MSIL1C_20180514T155911_N0206_R097_T18TUT_20180514T194414.SAFE"
create_RGB_NIR_TIF(path)