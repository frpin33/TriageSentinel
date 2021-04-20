'''
L'entièreté du code a été réalisé par Frédérick Pineault (frederick.pineault@mffp.gouv.qc.ca)

Ce fichier plusieurs fonctions essentielles pour la gestion des dossiers SAFE sur
le serveur F1271I (\\SEF1271A) du MFFP

Le fichier est aussi utiliser par le planificateur de tâche Windows pour faire
une analyse journalière des dossiers présents sur le serveur
L'analyse permet de : 
    -Créer les masques de nuages manquants dans les dossiers du serveur 
    -Trier les listes d'objets par numéro selon le pourcentage de nuage 
    -Créer un agencement RGB et NIR ainsi qu'un découpage selon le masque de nuage pour chaque tuile

'''

import sys, ressource, os, subprocess, time, csv, tempfile, pickle, shutil, gdal, osr
from tifCreation import createTIF, createNBR_NDVI
import numpy as np

dataLocation = "\\\\Sef1271a\\f1271i\\TeleDiff\\Commun\\a-Images-Satellites\\SENTINEL"
pathConda = "\\Seapriv\\usagers\\Pinfr1\\Mosaique_Sentinel\\Code\\launchConda.bat"
possibleYears = ["2017","2018","2019", "2020"]
keepTopValue = 5


def unzipFile() :
    pass

#Récupère tous les fichiers SAFE disponible sur le serveur
#Retourne la liste remplit
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

#Récupère les numéros de tuiles
#Le nombre de tuile pour chaque numéro est compté 
#Retourne un dictionnaire avec le numéro et le compte 
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

#Calcul le masque de nuage avec l'outil fmask avec un résolution de 20m par pixel
#pour tous les fichiers SAFE ou en fonction de l'argument listNew
#Permet d'actualiser la liste complète pour que chaque tuile contienne un masque
def cloudProcess(delete=False, listNew=None) :
    tempDir = tempfile.mkdtemp()
    if listNew :
        listSAFEDirectory = listNew
    else :
        listSAFEDirectory = getAllSAFEPath()
    print(listSAFEDirectory)
    for dirPath in listSAFEDirectory :
        try :
            dirName = os.path.basename(dirPath) 
            param = dirName.split('_')
            nameIMG = param[5] + '_' + param[2] + '.img'
            outIMG = os.path.join(dirPath, nameIMG)
            if not os.path.exists(outIMG) :
                if delete : 
                    pathGranule = os.path.join(inSAFE, 'GRANULE')
                    L1CPart = os.listdir(pathGranule)[0]
                    pathData = os.path.join(pathGranule, L1CPart, 'IMG_DATA')
                    listFileData = os.listdir(pathData)
                    for image in listFileData : 
                        if image.split('_')[-1] == "TCI.jp2":
                            TCIPath = os.path.join(pathData, image)
                            if os.path.getsize(TCIPath) > 50*10**6 : 
                                subprocess.call([pathConda, dirPath, outIMG, tempDir])
                            else : 
                                shutil.rmtree(dirPath)

                else :     
                    subprocess.call([pathConda, dirPath, outIMG, tempDir])
        except :
            pass
    shutil.rmtree(tempDir)

#Permet de déterminer quelles tuiles présentes dans les dossiers du serveur 
#qui n'ont pas encore été ajoutées dans les fichiers textes
def isNewSAFE():
    listSAFEDirectory = getAllSAFEPath()
    newSAFE = []
    for dirPath in listSAFEDirectory :
        dirName = os.path.basename(dirPath) 
        param = dirName.split('_')
        tileNum = param[5]  
        infoFileName = tileNum + '.txt'
        pathStoreFile = os.path.join(dataLocation, "Information", infoFileName)
        listObj = pickle.load(open(pathStoreFile,'rb'))
        for obj in listObj :
            if obj.pathSAFE == dirPath :
                break

        else : 
            newSAFE.append(dirPath)

    return(newSAFE)

#Permet de déterminer quelles tuiles n'ont pas de masque de nuage
def isIMGMissing():
    listSAFEDirectory = getAllSAFEPath()
    imgMissing = []
    for dirPath in listSAFEDirectory :
        dirName = os.path.basename(dirPath) 
        param = dirName.split('_')
        nameIMG = param[5] + '_' + param[2] + '.img'
        outIMG = os.path.join(dirPath, nameIMG)
        if not os.path.exists(outIMG) :
            imgMissing.append(dirPath)
    
    return(imgMissing)

#Permet de déterminer quelles tuiles n'ont pas été agencées et découpées
#Si une tuile n'a pas de masque et donc pas de TIF découpé, elle sera ajouté à la liste
def isTIFProcessDone():

    listSAFEDirectory = getAllSAFEPath()
    tifMissing = []
    fileList = []
    for dirPath in listSAFEDirectory :
        fileList = []
        dirName = os.path.basename(dirPath) 
        param = dirName.split('_')
        
        nircut = param[5] + '_' + param[2] +'_NIR_Cut.tif'
        fileList.append(os.path.join(dirPath, nircut)) 
        
        rgbcut = param[5] + '_' + param[2] +'_RGB_Cut.tif'
        fileList.append(os.path.join(dirPath, rgbcut))
        
        nirtif = param[5] + '_' + param[2] +'_NIR.tif'
        fileList.append(os.path.join(dirPath, nirtif))
        
        rgbtif = param[5] + '_' + param[2] +'_RGB.tif'
        fileList.append(os.path.join(dirPath, rgbtif)) 
        for item in fileList :
            if not os.path.exists(item) :
                tifMissing.append(dirPath)
                break
    
    return(tifMissing)

def isNBRMissing() :
    listSAFEDirectory = getAllSAFEPath()
    tifMissing = {}
    for dirPath in listSAFEDirectory :

        dirName = os.path.basename(dirPath) 
        param = dirName.split('_')
        
        nircut = param[5] + '_' + param[2] +'_NIR_Cut.tif'
        nbrName = param[-2] + '_' + param[-5] + '_NBR.tif'

        nirPath = os.path.join(dirPath, nircut)
        nbrPath = os.path.join(dirPath, nbrName)
        
        if os.path.exists(nirPath) and not os.path.exists(nbrPath) :
            tifMissing[nirPath] = nbrPath
    
    return(tifMissing)

#Gestion des fichiers textes 
#Récupère une liste complète de tuiles pour chaque numéro
#Pour chaque liste, le même traitement est réalisé
#Si le fichier SAFE n'est pas dans son fichier texte respectif, son masque doit être analyser 
#Le masque est analysé sur 16 zones de même taille pour déterminer le pourcentage sans nuage
#Combine la liste nouvellement traitée et les anciens fichiers
#Trie les tuiles en fonction du plus haut pourcentage sans nuage
#Pour chaque zone, les 5(keepTopValue) tuiles aillant le plus haut pourcentage sont identifiés
#Écriture de la nouvelle liste dans le fichier texte
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
                        if safe.totalClearPercent == 0 : 
                            newSentinelObj.append(obj)   
                            listObjSentinel.remove(safe)
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
                    
                    if pNull > pTClear + pTCloud  or pTCloud >= 0.5 :
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


#Class qui contient les informations enregistrer pour chaque tuile
class objSentinel : 
    def __init__(self, pathSAFE='', nameIMG='', totalClearPercent=0.0, clearPercent=[0]*16, isTopFile=[False]*16, underPercent=True) :
            self.pathSAFE = pathSAFE
            self.nameIMG = nameIMG
            self.totalClearPercent = totalClearPercent
            self.clearPercent = clearPercent
            self.isTopFile = isTopFile
            self.underPercent = underPercent


if __name__ == "__main__":
    
    try : cloudProcess()
    except : pass

    try : mainProcess()
    except : pass

    toDo = isTIFProcessDone()

    for item in toDo :
        try : createTIF(item)
        except : pass
    
    nbrDict = isNBRMissing()
    for key, value in nbrDict.items():
        try: createNBR_NDVI(key, value)
        except : pass



