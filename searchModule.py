'''
L'entièreté du code a été réalisé par Frédérick Pineault (frederick.pineault@mffp.gouv.qc.ca)

Ce fichier contient une classe de type QMainWindow qui permet la recherche de tuiles Sentinel en fonction
du numéro de tuile et des dates sélectionnées

Il est possible de faire une recherche en fonction de certaines zones spécifiques pour priorisés certains résultats
Il est possible d'enregistrer un assemblage de bande sur une tuile spécifique. L'utilisateur doit choisir les
bandes qu'il désire manuellement.

L'application peut seulement fonctionner si l'ordinateur a accès au serveur F1271I (\\SEF1271A) du MFFP
Pour chaque numéro de tuile, un document txt est utilisé pour lire l'information. Pour chaque tuile, un objet de 
la classe objSentinel est enregistré avec la librairie pickle. Il est donc seulement possible de lire le fichier texte
avec un script Python

Problème avec T19UDT, T18UXB -- Réglé -- Dossier vide (y a-t-il une raison)
Il serait intéressant de trouver si d'autres ont des problèmes (loop on each TXT)
3 fichiers ont des dossiers 10-20-60m plutôt que la norme, donc il ne fonctionne pas
2016 toujours pas programmé
Empêcher de crash avec un try si il n'est pas possible d'ouvrir TCI et/ou os.listDir crash
'''

from PyQt5 import QtCore, QtGui, QtWidgets
import sys, gdal, qimage2ndarray, os, csv, pickle, osr
import numpy as np
from PIL import Image
import ressource, tifCreation, fileProcessing
from ui_menuRecherche import Ui_searchMenu
#from fileProcessing import dataLocation
dataLocation = "\\\\Sef1271a\\f1271i\\TeleDiff\\Commun\\a-Images-Satellites\\SENTINEL"



class resultWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(resultWindow,self).__init__()
        self.ui = Ui_searchMenu()
        self.ui.setupUi(self)
        self.currentX = 10
        self.currentY = 0
        self.scene = QtWidgets.QGraphicsScene()
        self.ui.graphicsView.setScene(self.scene)
        self.ui.pushButtonLaunch.pressed.connect(self.startSearch)
        self.ui.groupBoxDate.clicked.connect(self.groupDateChange)
        self.ui.pushButtonSaveBand.clicked.connect(self.saveBandCombinaison)
        self.ui.pushButtonRefresh.clicked.connect(self.refreshSAFEStoreFile)
        self.currentRect = None
        self.pastRect = None
        self.lineItemList = []


        ####add connect ici
    #Active/Désactive les QDateEdit selon la checkbox
    #Les QDateEdit permettent de sélectionner des dates spécifique pour la recherche de tuile
    def groupDateChange(self, val):
        self.ui.label.setEnabled(True)
        self.ui.label_2.setEnabled(True)
        if val :  
            self.ui.endDateEdit.setEnabled(False)
            self.ui.startDateEdit.setEnabled(False)
        else : 
            self.ui.endDateEdit.setEnabled(True)
            self.ui.startDateEdit.setEnabled(True)

    #Détermine les zones d'intérêts en fonction du format standard (virgule entre les zones)
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


    #Lance le processus de recherche
    #Trouve le fichier texte correspondant à la tuile demandée et récupère la liste des tuiles
    #Si des dates sont spécifiées, la liste est parcourue pour retirer les tuiles non concernées
    #Si des zones spécifiques sont demandées, la liste est classée en fonction des zones importantes
    #Lancement du thread pour l'affichage de la première tuile à la position initiale
    def startSearch(self) :
        self.scene = QtWidgets.QGraphicsScene()
        self.currentRect = None
        self.ui.graphicsView.mousePressEvent = self.clicOnQraphicsView
        try : self.ui.checkBoxShowZone.stateChanged.disconnect()
        except : pass
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
                if newList :
                    self.currentListSAFE = newList
                else : 
                    strResult = 'Aucune tuile disponible pour la période demandée' 
                    self.ui.plainTextEdit.setPlainText(strResult)
                    return

        
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
    
    #Ajoute les objets de l'image en cours sur la scene 
    #Détermine la position de la prochaine image 
    #Si il reste des images à afficher, le thread d'affichage est relancée avec la position détemrinée
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
            if self.ui.checkBoxShowZone.isChecked() :
                self.newCommandZoneLine(2)
            self.ui.checkBoxShowZone.stateChanged.connect(self.newCommandZoneLine)  

    #Trace des lignes pour chacune des images pour permettre l'identification des 16 zones
    def newCommandZoneLine(self, state):

        if state == 2 : 
            itemList = self.scene.items()
            pen = QtGui.QPen(QtCore.Qt.yellow, 4)
            self.lineItemList = []
            for item in itemList :
                if isinstance(item, QtWidgets.QGraphicsPixmapItem) :
                    geo = item.boundingRect()
                    distX = int(geo.width()/4)
                    distY = int(geo.height()/4)
                    for i in range(1,4) :
                        lineX =self.scene.addLine(geo.x()+distX*i, geo.y(), geo.x()+distX*i, geo.y()+geo.height(), pen)
                        lineX.setZValue(3) 
                        lineY =self.scene.addLine(geo.x(),geo.y()+distY*i, geo.x()+geo.width(), geo.y()+distY*i, pen)
                        lineY.setZValue(3)
                        self.lineItemList.append(lineX)
                        self.lineItemList.append(lineY)


        elif state == 0 :
            if self.lineItemList :
                for line in self.lineItemList:
                    self.scene.removeItem(line)

    #Permet de rafraîchir la liste des tuiles disponibles sur le serveur
    def refreshSAFEStoreFile(self) :
        fileProcessing.mainProcess()

    #Récupère le nom pour chacune des bandes a utiliés pour l'enregistrement
    #Prépare les noms des fichiers à enregistrer
    #Vérifie que  les images JP2 existent
    #Lance le thread d'enregistrement pour la nouvelle image
    def saveBandCombinaison(self) : 

        try :
            self.cutVersion = self.ui.checkBoxCutVersion.isChecked()
            nameBand1 = self.ui.comboBoxBand1.currentText() + '.jp2'
            nameBand2 = self.ui.comboBoxBand2.currentText() + '.jp2'
            nameBand3 = self.ui.comboBoxBand3.currentText() + '.jp2'
            pixelSize = self.ui.comboBoxPixelSize.currentText()

            saveName = self.ui.lineEditSaveTile.text()
            if saveName :
                newSaveName = saveName +'.tif'
                cutSaveName = saveName + '_Cut.tif'

            else : 
                newSaveName = self.customName +'.tif'
                cutSaveName = self.customName + '_Cut.tif'

            newFullPath = os.path.join(self.customPath, newSaveName)
            if os.path.exists(newFullPath):os.remove(newFullPath)
            
            if self.cutVersion : 
                cutFullPath = os.path.join(self.customPath, cutSaveName)
                imgPath = self.imgSelectPath 
                if os.path.exists(cutFullPath) :os.remove(cutFullPath)
            else : 
                cutFullPath = ''
                imgPath = ''

            pathGranule = os.path.join(self.customPath, 'GRANULE')
            L1CPart = os.listdir(pathGranule)[0]
            pathData = os.path.join(pathGranule, L1CPart, 'IMG_DATA')
            listFileData = os.listdir(pathData)
            
            band1 = ''
            band2 = ''
            band3 = ''

            for image in listFileData : 

                if image.split('_')[-1] == nameBand1:
                    band1 = os.path.join(pathData, image)
                
                if image.split('_')[-1] == nameBand2:
                    band2 = os.path.join(pathData, image)

                if image.split('_')[-1] == nameBand3:
                    band3 = os.path.join(pathData, image)

            if band1 and band2 and band3 :
                
                currentNumber = self.ui.lineEditNumero.text()
                proj = currentNumber[1:3]

                self.saveThread = threadSaveCustomBand(band1,band2,band3, proj,pixelSize, newFullPath, cutFullPath, imgPath)
                self.saveThread.finished.connect(self.checkSaveResult)
                strResult = 'Début de l\'enregistrement'
                self.ui.plainTextEdit.setPlainText(strResult)
                self.ui.pushButtonSaveBand.setEnabled(False)
                self.saveThread.start()
        except : 
            strResult = 'Enregistrement impossible, il n\'est pas possible de récupérer toutes les bandes demandées'
            self.ui.plainTextEdit.setPlainText(strResult)

    #Affiche à l'utilisateur comment l'enregistrement s'est déroulé
    def checkSaveResult(self) :
        if self.saveThread.result :
            if self.isCutPossible and self.cutVersion :
                strResult = 'Enregistrement terminé pour les 2 images'
                self.ui.plainTextEdit.setPlainText(strResult)
            elif self.cutVersion and not self.isCutPossible :
                strResult = 'Enregistrement seulement possible pour l\'image sans découpage, le masque n\'existe pas.'
                self.ui.plainTextEdit.setPlainText(strResult)
            else :
                strResult = 'Enregistrement terminé'
                self.ui.plainTextEdit.setPlainText(strResult)
            
        else :
            strResult = 'Échec de l\'enregistrement'
            self.ui.plainTextEdit.setPlainText(strResult)
        self.ui.pushButtonSaveBand.setEnabled(True)

    #Action activé par un click sur le QGraphicsView
    #Détermine sur quel objet le click a eu lieu
    #Si le click est sur une image, le chemin est recupéré pour l'enregistrement
    #L'image devient la tuile sélectionnée dans l'application
    #Si le click est sur le nom de l'image, le dossier de l'image s'ouvre dans l'explorateur Windows
    #Change la couleur du rectangle pour souligner la sélection en cours
    def clicOnQraphicsView(self, mouseEvent) : 
        mousePosition = mouseEvent.pos()
        items = self.ui.graphicsView.items(mousePosition)
        isSelection = False
        for item in items :
            if isinstance(item, (QtWidgets.QGraphicsPixmapItem, QtWidgets.QGraphicsTextItem)):
                dirName = os.path.basename(item.fileLocation) 
                paramOfName = dirName.split('_')
                nameOfPicture = paramOfName[-5]

                self.customName = paramOfName[-2] + '_' + paramOfName[-5] + '_customBand'
                imgName = paramOfName[-2] + '_' + paramOfName[-5] + '.img'
                self.customPath = item.fileLocation

                imgPath = os.path.join(self.customPath, imgName)
                if os.path.exists(imgPath) :
                    self.isCutPossible = True
                    self.imgSelectPath = imgPath
                else :
                    self.isCutPossible = False
                    self.imgSelectPath = ''

                self.ui.lineEditSelectTile.setText(nameOfPicture)
                self.ui.lineEditSaveTile.setText(self.customName)
                self.ui.pushButtonSaveBand.setEnabled(True)
                isSelection= True


            if isinstance(item,QtWidgets.QGraphicsTextItem):
                os.startfile(item.fileLocation)

        if isSelection:
            #self.ui.checkBoxShowZone.setCheckState(0) non nécessaire
            for item in items:
                if isinstance(item, QtWidgets.QGraphicsRectItem):
                    try : 
                        if self.currentRect :
                            self.scene.removeItem(self.currentRect)
                        self.scene.removeItem(item)
                    except : pass

                    if self.pastRect :
                        self.scene.addRect(self.pastRect)
                    
                    brush = QtGui.QBrush(QtCore.Qt.gray)
                    a = item.boundingRect()
                    newRect = QtCore.QRectF(a.x(),a.y(),a.width(), a.height())
                    
                    self.currentRect = self.scene.addRect(newRect,QtCore.Qt.gray,QtCore.Qt.gray)
                    self.pastRect = newRect
                    self.ui.graphicsView.update()

#Class qui contient les informations enregistrer pour chaque tuile
class objSentinel : 
    def __init__(self, pathSAFE='', nameIMG='', totalClearPercent=0.0, clearPercent=[0]*16, isTopFile=[False]*16, under60=True) :
        self.pathSAFE = pathSAFE
        self.nameIMG = nameIMG
        self.totalClearPercent = totalClearPercent
        self.clearPercent = clearPercent
        self.isTopFile = isTopFile
        self.under60 = under60

#Thread qui prépare les objets qui seront affichés sur le QGraphicsViews pour chaque tuile
#L'application n'est donc pas ralenti par le chargement de l'image en mémoire
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
                pixItem.setZValue(2)
                self.pixmapItem = pixItem
                self.pixmapItem.fileLocation = self.path2SAFE

                self.shapeRect = QtCore.QRectF(self.currentX, self.currentY, 363, 383)
                self.shapeRect.fileLocation = self.path2SAFE
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
                textItem.setZValue(2)
                self.hyperTextItem = textItem
                self.hyperTextItem.fileLocation = self.path2SAFE
            except:
                self.reject= True
            
#Thread qui lance l'enregistrement de l'image personnalisée
class threadSaveCustomBand(QtCore.QThread):
    def __init__(self, band1, band2, band3, proj,pixelSize, savePath, cutPath='', imgPath='') :
        QtCore.QThread.__init__(self)
        self.band1 = band1
        self.band2 = band2
        self.band3 = band3
        self.proj =proj
        self.pixelSize = pixelSize
        self.savePath = savePath
        self.cutPath = cutPath
        self.imgPath = imgPath
        self.result = False
    
    def run(self):
        self.result = tifCreation.createTIFfromBand(self.band1, self.band2, self.band3, self.proj, self.pixelSize, self.savePath, self.cutPath, self.imgPath)


if __name__ == "__main__":
     
    app = QtWidgets.QApplication(sys.argv)
    showResultWindow = resultWindow()
    showResultWindow.show()
    sys.exit(app.exec_())