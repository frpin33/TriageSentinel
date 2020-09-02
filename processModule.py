import sys, ressource, os, subprocess, time, csv, tempfile, pickle, shutil, gdal
from PyQt5 import QtCore, QtGui, QtWidgets
from ui_menuProcess import Ui_MainWindow
#from resultTest import resultWindow
import numpy as np


#DEFINE PATH TO MAIN DIRECTORY
#dataLocation = "D:/Mosaique_Sentinel/Sentinel_T18TUT"+
dataLocation = "U:/Mosaique_Sentinel/test"

keepTopValue = 5 

#Normalement dans datalocation, il va avoir un dossier pour chaque année et dans le dossier tout les SAFE de l'année 
#Attention si le dossier de l'année n'existe pas  os.path.exists(dataLocation+"/2020")
#Créer manuellement les fichiers Information pour chaque année
#TXT FILE WILL BE STORE BY YEAR and TILE NUMBER

#Delete un SAFE si taille trop petite / trop de NULL / 60% de nuage et plus --> shutil.rmtree(path)
#Pour chaque SAFE marquer sa destruction 60% et plus puisqu'il est possible qu'il soit dans le top 5 au début 
#Fonction d'entré et de sortie du top 5 
#loop sur chaque zone
#store in CSV ou pickle ou json, avoir des données pour les 16 tuiles (min 5)  
#Check if IMG in SAFE file? 
#Est-ce que la tuile à déjà des données?
#Lieu de stockage à déterminer

#try except dans le code pour pas fermer abruptement

class searchWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(searchWindow,self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButtonLaunch.clicked.connect(self.launchProcess)


    def launchProcess(self): 
        sDate = self.ui.startDateEdit.date()
        sYear = sDate.year()
        eDate = self.ui.endDateEdit.date()
        eYear = eDate.year()
        tileNumber = self.ui.lineEditNumero.text()
        
        
        listYearDirectory = []
        if eYear - sYear == 0 :
            path = os.path.join(dataLocation, str(eYear))
            if os.path.exists(path) :
                listYearDirectory.append(path)
            else :
                return

        elif eYear - sYear > 0 :
            val = eYear - sYear
            for i in range(val+1) : 
                path = os.path.join(dataLocation, str(sYear+i))
                if os.path.exists(path) :
                    listYearDirectory.append(path)

        else :
            return
        
        
        for yearPath in listYearDirectory :
            tempDir = tempfile.mkdtemp()

            storeFileName = tileNumber + '.txt'
            pathStoreFile = os.path.join(yearPath, "Information", storeFileName)
            if os.path.exists(pathStoreFile) : 
                self.listObjSentinel = pickle.load(open(pathStoreFile,'rb'))
            else : 
                self.listObjSentinel = []
            
            listSAFEDirectory = os.listdir(yearPath)

        
            newSentinelObj = []
            for dirName in listSAFEDirectory :
                if dirName.split('.')[-1] == 'SAFE' :
                    inSAFE = os.path.join(yearPath, dirName)
                    for obj in self.listObjSentinel :
                        if obj.pathSAFE == inSAFE :
                            break
                    else :
                        pathGranule = os.path.join(inSAFE, 'GRANULE')
                        L1CPart = os.listdir(pathGranule)[0]
                        pathData = os.path.join(pathGranule, L1CPart, 'IMG_DATA')
                        listFileData = os.listdir(pathData)
                        for image in listFileData : 
                            if image.split('_')[-1] == "TCI.jp2":
                                TCIPath = os.path.join(pathData, image)
                                if os.path.getsize(TCIPath) > 50*10**6 : 

                                    param = dirName.split('_')
                                    date = param[2].split('T')
                                    qDate = QtCore.QDate.fromString(date[0],"yyyyMMdd")
                                    tile = param[5]
                                    if tile == tileNumber and qDate > sDate and qDate < eDate :
                                        nameIMG = tile + '_' + param[2] + '.img'
                                        outIMG = os.path.join(inSAFE, nameIMG)
                                        subprocess.call(["launchConda.bat", inSAFE, outIMG, tempDir])
                                        newSentinelObj.append(objSentinel(inSAFE,nameIMG))
                                else :
                                    shutil.rmtree(inSAFE)
                                break
                                    

            shutil.rmtree(tempDir)

            for obj in newSentinelObj :

                pathIMG = outIMG = os.path.join(obj.pathSAFE, obj.nameIMG)
                imgFile = gdal.Open(pathIMG)
                array = imgFile.GetRasterBand(1).ReadAsArray()
                
                x,y = array.shape

                firstSplit = np.array_split(array,4,1)
                splitArray = []
                for item in firstSplit :
                    splitArray.append(np.array_split(item,4))
                
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
                    obj.under60 = False
                else :
                    if pTCloud >= 0.6 : 
                        obj.under60 = False
                    obj.clearPercent = countClear
                    obj.totalClearPercent = pTClear
                
            self.listObjSentinel = self.listObjSentinel + newSentinelObj
            
            topTable = [[(0,0)]*keepTopValue]*16
            
            objNumber = 0
            for obj in self.listObjSentinel :
                for num in range(16):
                    
                    topRank = topTable[num]
                
                    currentVal = obj.clearPercent[num]

                    if objNumber < keepTopValue :

                        topRank[objNumber] = (currentVal, objNumber)
                        obj.isTopFile[num] = True
                        if objNumber == keepTopValue - 1  :
                            topRank.sort(reverse=True, key = lambda tup: tup[0])


                    elif currentVal > topRank[keepTopValue-1][0] : 
                        objListPosition = topRank[keepTopValue-1][1]
                        #Tester si cette opération est sécuritaire en mémoire
                        self.listObjSentinel[objListPosition].isTopFile[num] = False
                        obj.isTopFile[num] = True
                        topRank[keepTopValue-1] = (currentVal, objNumber)
                        topRank.sort(reverse=True, key = lambda tup: tup[0])
                        
                    topTable[num] = topRank
                
                objNumber += 1
            
            for obj in self.listObjSentinel :
                if not any(obj.isTopFile) and not obj.under60 : 
                    shutil.rmtree(obj.pathSAFE)

            self.listObjSentinel.sort(reverse=True, key= lambda x : x.totalClearPercent)
            pickle.dump(self.listObjSentinel,open(pathStoreFile,"wb"))
        
        """
        row_list =[] #[["pathSAFE", "clearPercent","cloudPercent"]]
        pathCSV = 'results.csv'
        for obj in self.listObjSentinel :
            row_list.append([str(obj.pathSAFE)])#, str(obj.clearPercent), str(obj.cloudPercent)])
        
        with open(pathCSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(row_list)

        self.showResultWindow = resultWindow()
        
        self.showResultWindow.readCSV(pathCSV)


        for obj in self.listObjSentinel :
            self.showResultWindow.addPictureFrame(obj.pathSAFE)

        self.showResultWindow.show()
        r=QtCore.QRectF(0,0,1600,1384)
        self.showResultWindow.ui.graphicsView.fitInView(r, QtCore.Qt.KeepAspectRatio)"""


         
class objSentinel : 
    def __init__(self, pathSAFE='', nameIMG='', totalClearPercent=0.0, clearPercent=[0]*16, isTopFile=[False]*16, under60=True) :
            self.pathSAFE = pathSAFE
            self.nameIMG = nameIMG
            self.totalClearPercent = totalClearPercent
            self.clearPercent = clearPercent
            self.isTopFile = isTopFile
            self.under60 = under60



app = QtWidgets.QApplication(sys.argv)
a = searchWindow()
a.show()
sys.exit(app.exec_())