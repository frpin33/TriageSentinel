# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui-menuRecherche.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtGui, QtWidgets, QtCore
import ressource, sys
from os.path import isdir

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(403, 552)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(106, 130, 81, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(120, 180, 71, 16))
        self.label_2.setObjectName("label_2")
        self.groupBoxPath = dropedit(self.centralwidget)
        self.groupBoxPath.setGeometry(QtCore.QRect(20, 29, 361, 71))
        self.groupBoxPath.setObjectName("groupBoxPath")
        self.lineEditPath = QtWidgets.QLineEdit(self.groupBoxPath)
        self.lineEditPath.setGeometry(QtCore.QRect(30, 30, 281, 20))
        self.lineEditPath.setReadOnly(True)
        self.lineEditPath.setObjectName("lineEditPath")
        self.toolButtonPath = QtWidgets.QToolButton(self.groupBoxPath)
        self.toolButtonPath.setGeometry(QtCore.QRect(310, 30, 25, 19))
        self.toolButtonPath.setObjectName("toolButtonPath")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(100, 230, 81, 16))
        self.label_3.setObjectName("label_3")
        self.lineEditNumero = upperLineEdit(self.centralwidget)
        self.lineEditNumero.setGeometry(QtCore.QRect(200, 230, 151, 20))
        self.lineEditNumero.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEditNumero.setObjectName("lineEditNumero")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(40, 290, 151, 16))
        self.label_4.setObjectName("label_4")
        self.lineEditZone = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEditZone.setGeometry(QtCore.QRect(200, 290, 151, 20))
        self.lineEditZone.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEditZone.setObjectName("lineEditZone")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(37, 320, 151, 16))
        self.label_5.setObjectName("label_5")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(30, 340, 151, 151))
        self.frame.setStyleSheet("background-color: rgba(255, 255, 255, 0);\n"
"image: url(:/Image/ExempleZone.PNG);")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.pushButtonLaunch = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonLaunch.setGeometry(QtCore.QRect(240, 360, 111, 23))
        self.pushButtonLaunch.setObjectName("pushButtonLaunch")
        self.startDateEdit = QtWidgets.QDateEdit(self.centralwidget)
        self.startDateEdit.setGeometry(QtCore.QRect(200, 130, 151, 20))
        self.startDateEdit.setDateTime(QtCore.QDateTime(QtCore.QDate(2020, 1, 1), QtCore.QTime(0, 0, 0)))
        self.startDateEdit.setCalendarPopup(True)
        self.startDateEdit.setObjectName("startDateEdit")
        self.endDateEdit = QtWidgets.QDateEdit(self.centralwidget)
        self.endDateEdit.setGeometry(QtCore.QRect(200, 180, 151, 20))
        self.endDateEdit.setDateTime(QtCore.QDateTime(QtCore.QDate(2020, 1, 1), QtCore.QTime(0, 0, 0)))
        self.endDateEdit.setCalendarPopup(True)
        self.endDateEdit.setObjectName("endDateEdit")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(110, 250, 81, 16))
        self.label_6.setObjectName("label_6")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 403, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Outil de recherche de tuile"))
        self.label.setText(_translate("MainWindow", "Date de début : "))
        self.label_2.setText(_translate("MainWindow", "Date de fin :"))
        self.groupBoxPath.setTitle(_translate("MainWindow", "Chemin des dossiers"))
        self.toolButtonPath.setText(_translate("MainWindow", "..."))
        self.label_3.setText(_translate("MainWindow", "Numéro de tuile : "))
        self.label_4.setText(_translate("MainWindow", "Zones prioritères (facultatif):"))
        self.label_5.setText(_translate("MainWindow", "Exemple de format : 1,5,9,13 "))
        self.pushButtonLaunch.setText(_translate("MainWindow", "Lancer la recherche"))
        self.label_6.setText(_translate("MainWindow", "Ex : T18TUT"))


class dropedit(QtWidgets.QGroupBox):   

    def __init__(self, parent=None):
        super(dropedit, self).__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        event.accept()
        
    def dropEvent(self, event):
        fileURL = event.mimeData().urls()[0].toString()
        try :
            fileName = fileURL.split('file:///')[1]
        except :
            fileName = fileURL.split('file:')[1]
        
        if isdir(fileName):
            for child in self.children(): 
                if child.metaObject().className() == "QLineEdit":
                    child.setText(fileName)



class upperLineEdit(QtWidgets.QLineEdit):

    def __init__(self,parent=None):
        super(upperLineEdit, self).__init__(parent)


    def keyPressEvent(self, event):
        QtWidgets.QLineEdit.keyPressEvent(self, event)
        pretext = self.text()
        self.setText(pretext.__str__().upper())
        
        