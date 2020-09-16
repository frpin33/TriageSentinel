# Form implementation generated from reading ui file 'resultTestWindow.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

#import PyQt5
#import PyQt5.QtWidgets as QtWidgets

#Fonction de sort 


from PyQt5 import QtGui, QtWidgets, QtCore
import sys, gdal, qimage2ndarray, os, csv, pickle
import numpy as np
from PIL import Image


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(911, 809)
        self.graphicsView = QtWidgets.QGraphicsView(Dialog)
        self.graphicsView.setGeometry(QtCore.QRect(10, 10, 891, 771))
        self.graphicsView.setObjectName("graphicsView")
        #b = scene.itemAt(-125,-125, QtGui.QTransform())

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))


class resultWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(resultWindow,self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.currentX = 10
        self.currentY = 0
        self.scene = QtWidgets.QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)

    def addPictureFrame(self, pathSAFE) : 

        pathGranule = os.path.join(pathSAFE, 'GRANULE')
        L1CPart = os.listdir(pathGranule)[0]
        pathData = os.path.join(pathGranule, L1CPart, 'QI_DATA')
        listFileData = os.listdir(pathData)
        picturePath = ""
        for item in listFileData : 
            if item.split('.')[-1] == "jp2":
                picturePath = item
                break
        
        if picturePath :
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
            self.scene.addItem(pixItem)

            self.scene.addRect(self.currentX, self.currentY, 363, 383)
            
            textItem= QtWidgets.QGraphicsTextItem("")
            textItem.setOpenExternalLinks(True)
            textItem.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
            name = pathSAFE.split('\\')[-1].split('_')[2]
            newSAFEPath = pathSAFE.replace("\\","/")
            htmlText = "<a href=\"" + newSAFEPath + "\">" + name + "</a>"
            textItem.setHtml(htmlText)
            textItem.setPos(self.currentX+10, self.currentY+353)
            font = QtGui.QFont()
            font.setPointSize(14)
            textItem.setFont(font)
            self.scene.addItem(textItem)
            
            if self.currentX >= 1200 :
                self.currentX = 10
                self.currentY += 400
            else : 
                self.currentX += 400

    def readCSV(self):

        path = "U:\\Mosaique_Sentinel\\test\\2018\\Information\\T18TUT.txt"
        #path = "C:/Users/Frederick/Desktop/Work_Git/mosaique/Sentinel_T18TUT/2018/Information/T18TUT.txt"
        listObj = pickle.load(open(path,'rb'))
        for row in listObj:
            self.addPictureFrame(row.pathSAFE)
        
        self.show()
        r=QtCore.QRectF(0,0,1600,1384)
        self.ui.graphicsView.fitInView(r, QtCore.Qt.KeepAspectRatio)
                

class objSentinel : 
    def __init__(self, pathSAFE='', nameIMG='', totalClearPercent=0.0, clearPercent=[0]*16, isTopFile=[False]*16, under60=True) :
            self.pathSAFE = pathSAFE
            self.nameIMG = nameIMG
            self.totalClearPercent = totalClearPercent
            self.clearPercent = clearPercent
            self.isTopFile = isTopFile
            self.under60 = under60

app = QtWidgets.QApplication(sys.argv)

showResultWindow = resultWindow()
        
showResultWindow.readCSV()


sys.exit(app.exec_())


