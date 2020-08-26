import sys, ressource, os, subprocess, time, gdal, csv, tempfile, pickle, shutil
from PyQt5 import QtCore, QtGui, QtWidgets
from ui_menuRecherche import Ui_MainWindow
from resultTest import resultWindow
import numpy as np


#DEFINE PATH TO MAIN DIRECTORY
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

        self.ui.toolButtonPath.clicked.connect(self.importDirectory)
        self.ui.pushButtonLaunch.clicked.connect(self.launchProcess)

    def importDirectory(self):
        path = os.path.join(os.environ['USERPROFILE']) 
        fname = QtWidgets.QFileDialog.getExistingDirectory(self, 'Choisir le dossier', path)
        if fname:
            self.ui.lineEditPath.setText(fname)

    def launchProcess(self): 
        listDirectory = os.listdir(self.ui.lineEditPath.text())
        sDate = self.ui.startDateEdit.date()
        eDate = self.ui.endDateEdit.date()
        tileNumber = self.ui.lineEditNumero.text()
        tempDir = tempfile.mkdtemp()
        outDir = "U:\\Mosaique_Sentinel\\resultIMG\\"
        

        self.listObjSentinel = []
        #Récupérer la liste pour la tuile si elle existe déjà
        for item in listDirectory :
            if item.split('.')[-1] == 'SAFE' :
                inSAFE = os.path.join(self.ui.lineEditPath.text(), item)
                
                pathGranule = os.path.join(inSAFE, 'GRANULE')
                L1CPart = os.listdir(pathGranule)[0]
                pathData = os.path.join(pathGranule, L1CPart, 'IMG_DATA')
                listFileData = os.listdir(pathData)
                for image in listFileData : 
                    if image.split('_')[-1] == "TCI.jp2":
                        TCIPath = os.path.join(pathData, image)
                        if os.path.getsize(TCIPath) > 50*10**6 : 

                            param = item.split('_')
                            date = param[2].split('T')
                            qDate = QtCore.QDate.fromString(date[0],"yyyyMMdd")
                            tile = param[5]
                            if tile == tileNumber and qDate > sDate and qDate < eDate : 
                                outIMG = inSAFE + tile + '_' + param[2] + '.img'
                                #subprocess.call(["launchConda.bat", inSAFE, outIMG, tempDir])
                                self.listObjSentinel.append(objSentinel(inSAFE,outIMG))
                        else :
                            #delete the SAFE sans traitement shutil.rmtree(path)
                            pass

        shutil.rmtree(tempDir)
        for obj in self.listObjSentinel :

            imgFile = gdal.Open(obj.pathIMG)
            b = imgFile.RasterCount
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
                    
                    elif val == 5 :
                        water += 1


                pClear = clear/maxVal
                pCloud = cloud/maxVal
                pShadow = shadow/maxVal
                pWater = water/maxVal

                countCloud[num] = (pCloud+pShadow)
                countClear[num] = (pClear+pWater)
            
            divFact = x*y
            pNull = null/divFact
            pTCloud = totalCloud/divFact
            pTClear = totalClear/divFact
            if pNull > pTClear + pTCloud :
                #Flag 2 Delete 
                pass
            else :
                #create object if pTCloud >= 0.6 mark as DELETE
                obj.clearPercent = countClear
                obj.cloudPercent = countCloud
            
            
        #Traitement des résultats
        #self.listObjSentinel.sort(reverse=True, key= lambda x : x.clearPercent)
        
        
        row_list =[] #[["pathSAFE", "clearPercent","cloudPercent"]]
        pathCSV = 'results.csv'
        for obj in self.listObjSentinel :
            row_list.append([str(obj.pathSAFE)])#, str(obj.clearPercent), str(obj.cloudPercent)])
        
        with open(pathCSV, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(row_list)

        self.showResultWindow = resultWindow()
        
        self.showResultWindow.readCSV(pathCSV)


        """for obj in self.listObjSentinel :
            self.showResultWindow.addPictureFrame(obj.pathSAFE)

        self.showResultWindow.show()
        r=QtCore.QRectF(0,0,1600,1384)
        self.showResultWindow.ui.graphicsView.fitInView(r, QtCore.Qt.KeepAspectRatio)"""


         
#Matrice de Pourcentage
#Need to be delete
#IsTOP5 somewhere + place?
#Marquer les zones qui sont 95% et + dans la tuile
class objSentinel : 
    def __init__(self, pathSAFE='', nameIMG='', cloudPercent=[0]*16, clearPercent=[0]*16) :
            self.pathSAFE = pathSAFE
            self.nameIMG = nameIMG
            self.cloudPercent = cloudPercent
            self.clearPercent = clearPercent


#Lancer le bat avec des arguments -- Ajouter temp folder dans l'exécutable
#Offrir les résultats -- liste avec hyperlien

app = QtWidgets.QApplication(sys.argv)
a = searchWindow()
a.show()
sys.exit(app.exec_())