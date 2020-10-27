from PyQt5 import QtCore, QtGui, QtWidgets
import sys, gdal, qimage2ndarray, os, csv, pickle
import numpy as np
from PIL import Image
import ressource
from ui_menuRecherche import Ui_Dialog
from fileProcessing import dataLocation


class resultWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(resultWindow,self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.currentX = 10
        self.currentY = 0
        self.scene = QtWidgets.QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)
        self.ui.pushButtonLaunch.pressed.connect(self.startSearch)
        self.ui.groupBoxDate.clicked.connect(self.groupDateChange)

    def groupDateChange(self, val):
        self.ui.label.setEnabled(True)
        self.ui.label_2.setEnabled(True)
        if val :  
            self.ui.endDateEdit.setEnabled(False)
            self.ui.startDateEdit.setEnabled(False)
        else : 
            self.ui.endDateEdit.setEnabled(True)
            self.ui.startDateEdit.setEnabled(True)

    
    def getZoneFilter(self):
        zoneSTR = self.ui.lineEditZone.text()
        splitZone = zoneSTR.split(',')
        listIntZone = []
        listSTRZone = []
        errorInFormat = False
        for zone in splitZone :
            try : 
                listIntZone.append(int(zone))
                listSTRZone.append(zone)
            except : 
                errorInFormat = True
        if errorInFormat : 
            correctZone = '-'.join(listSTRZone)
            strResult = 'Attention au format des zones. Le résultat attendu pourrait être éronné \nLes zones d\'intérêts sont : ' + correctZone 
        else :
            correctZone = '-'.join(listSTRZone)
            strResult = 'Les zones d\'intérêts sont : ' + correctZone 
        
        self.ui.plainTextEdit.setPlainText(strResult)
        return listIntZone


    
    def startSearch(self) :
        self.scene = QtWidgets.QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)
        tileNumber = self.ui.lineEditNumero.text()
        tileName = tileNumber + ".txt"
        tilePath = os.path.join(dataLocation, 'Information', tileName)
        if os.path.exists(tilePath) :
            listObj = pickle.load(open(tilePath,'rb'))
        
            if self.ui.groupBoxDate.isChecked() :
                self.currentListSAFE = listObj
            
            else :
                newList = [] 
                startDate = self.ui.startDateEdit.date()
                endDate = self.ui.endDateEdit.date()
                for obj in listObj :
                    dirName = obj.pathSAFE
                    param = dirName.split('_')
                    date = param[2].split('T')
                    qDate = QtCore.QDate.fromString(date[0],"yyyyMMdd")
                    if qDate > startDate and qDate < endDate :
                        newList.append(obj)
                self.currentListSAFE = newList
        
            nbObj = len(self.currentListSAFE)
            zoneFilter = self.getZoneFilter()
            if zoneFilter :
                listTuple = []
                divFac = len(zoneFilter)
                
                for obj in self.currentListSAFE : 
                    pCloud = 0
                    for num in zoneFilter :
                        val = obj.clearPercent[num-1]
                        pCloud += val
                    pCloud = pCloud/divFac
                    listTuple.append((obj,pCloud))
                listTuple.sort(reverse=True, key = lambda tup: tup[1])
                newOrder = []
                for tup in listTuple : 
                    newOrder.append(tup[0])
                self.currentListSAFE = newOrder

            strPlainText = 'Récupération des ' + str(nbObj) + ' tuiles trouvées'
            self.ui.plainTextEdit.setPlainText(strPlainText)
            self.currentListIndex = 0
            path2Use = self.currentListSAFE[self.currentListIndex].pathSAFE
            self.currentThread = threadAffichage(path2Use, 0, 0)
            self.currentThread.finished.connect(self.addPictureOnFrame)
            self.currentThread.start()
            
        
        else : 
            strResult = 'Aucune tuile de la base de donnée possède le numéro demandé' 
            self.ui.plainTextEdit.setPlainText(strResult)
    
    def addPictureOnFrame(self):
        
        self.currentListIndex += 1
        
        if self.currentThread.reject == False :
            self.scene.addItem(self.currentThread.hyperTextItem)
            self.scene.addRect(self.currentThread.shapeRect)
            self.scene.addItem(self.currentThread.pixmapItem)

            r=QtCore.QRectF(0,0,1600,1384)
            self.ui.graphicsView.fitInView(r, QtCore.Qt.KeepAspectRatio)
            
            if self.currentThread.currentX >= 1200 :
                self.currentThread.currentX = 10
                self.currentThread.currentY += 400
            else : 
                self.currentThread.currentX += 400
            
        X2Use = self.currentThread.currentX
        Y2Use = self.currentThread.currentY
        try : 
            path2Use = self.currentListSAFE[self.currentListIndex].pathSAFE
            self.currentThread = threadAffichage(path2Use, X2Use, Y2Use)
            self.currentThread.finished.connect(self.addPictureOnFrame)
            self.currentThread.start()
        except:
            strResult = 'Chargement terminé'
            self.ui.plainTextEdit.setPlainText(strResult)  


class objSentinel : 
    def __init__(self, pathSAFE='', nameIMG='', totalClearPercent=0.0, clearPercent=[0]*16, isTopFile=[False]*16, under60=True) :
        self.pathSAFE = pathSAFE
        self.nameIMG = nameIMG
        self.totalClearPercent = totalClearPercent
        self.clearPercent = clearPercent
        self.isTopFile = isTopFile
        self.under60 = under60


class threadAffichage(QtCore.QThread):
    def __init__(self, path2SAFE, currentX, currentY) :
        QtCore.QThread.__init__(self)
        self.path2SAFE = path2SAFE
        self.currentX = currentX
        self.currentY = currentY
        self.pixmapItem = None
        self.hyperTextItem = None
        self.shapeRect = None
        self.reject= False
    
    def run(self):
        
        pathGranule = os.path.join(self.path2SAFE, 'GRANULE')
        L1CPart = os.listdir(pathGranule)[0]
        pathData = os.path.join(pathGranule, L1CPart, 'QI_DATA')
        listFileData = os.listdir(pathData)
        picturePath = ""
        for item in listFileData : 
            if item.split('.')[-1] == "jp2":
                picturePath = item
                break
        
        if picturePath :
            self.reject= False
            try :
                pathJP2 = os.path.join(pathData, picturePath)
                
                raster = gdal.Open(pathJP2)
                rArray = raster.GetRasterBand(1).ReadAsArray()
                gArray = raster.GetRasterBand(2).ReadAsArray()
                bArray = raster.GetRasterBand(3).ReadAsArray()

                array = np.dstack((rArray,gArray, bArray))
                image = qimage2ndarray.array2qimage(array)

                pixMap = QtGui.QPixmap().fromImage(image)
                pixItem = QtWidgets.QGraphicsPixmapItem(pixMap)
                pixItem.setOffset(self.currentX+10, self.currentY+10)
                self.pixmapItem = pixItem

                self.shapeRect = QtCore.QRectF(self.currentX, self.currentY, 363, 383)
                textItem= QtWidgets.QGraphicsTextItem("")
                textItem.setOpenExternalLinks(True)
                textItem.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
                name = self.path2SAFE.split('\\')[-1].split('_')[2]
                newSAFEPath = self.path2SAFE.replace("\\","/")
                htmlText = "<a href=\"" + newSAFEPath + "\">" + name + "</a>"
                textItem.setHtml(htmlText)
                textItem.setPos(self.currentX+10, self.currentY+353)
                font = QtGui.QFont()
                font.setPointSize(14)
                textItem.setFont(font)
                self.hyperTextItem = textItem
            except:
                self.reject= True
            


app = QtWidgets.QApplication(sys.argv)
showResultWindow = resultWindow()
showResultWindow.show()
sys.exit(app.exec_())