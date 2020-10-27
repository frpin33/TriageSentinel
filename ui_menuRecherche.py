# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui-searchMenu.ui'
#
# Created by: PyQt5 UI code generator 5.12.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
import sys, gdal, qimage2ndarray, os, csv, pickle
import numpy as np
from PIL import Image
import ressource

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(1174, 789)
        self.graphicsView = QtWidgets.QGraphicsView(Dialog)
        self.graphicsView.setGeometry(QtCore.QRect(270, 10, 891, 771))
        self.graphicsView.setObjectName("graphicsView")
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setGeometry(QtCore.QRect(5, 290, 141, 16))
        self.label_4.setObjectName("label_4")
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setGeometry(QtCore.QRect(10, 40, 81, 16))
        self.label_3.setObjectName("label_3")
        self.lineEditNumero = upperLineEdit(Dialog)
        self.lineEditNumero.setGeometry(QtCore.QRect(110, 40, 151, 20))
        self.lineEditNumero.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEditNumero.setObjectName("lineEditNumero")
        self.frame = QtWidgets.QFrame(Dialog)
        self.frame.setGeometry(QtCore.QRect(60, 360, 151, 151))
        self.frame.setStyleSheet("background-color: rgba(255, 255, 255, 0);\n"
"image: url(:/Image/ExempleZone.PNG);")
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.label_6 = QtWidgets.QLabel(Dialog)
        self.label_6.setGeometry(QtCore.QRect(20, 60, 81, 16))
        self.label_6.setObjectName("label_6")
        self.lineEditZone = QtWidgets.QLineEdit(Dialog)
        self.lineEditZone.setGeometry(QtCore.QRect(145, 290, 121, 20))
        self.lineEditZone.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEditZone.setObjectName("lineEditZone")
        self.pushButtonLaunch = QtWidgets.QPushButton(Dialog)
        self.pushButtonLaunch.setGeometry(QtCore.QRect(75, 560, 111, 23))
        self.pushButtonLaunch.setObjectName("pushButtonLaunch")
        self.label_5 = QtWidgets.QLabel(Dialog)
        self.label_5.setGeometry(QtCore.QRect(70, 320, 151, 16))
        self.label_5.setObjectName("label_5")
        self.groupBoxDate = QtWidgets.QGroupBox(Dialog)
        self.groupBoxDate.setGeometry(QtCore.QRect(10, 100, 251, 151))
        self.groupBoxDate.setCheckable(True)
        self.groupBoxDate.setObjectName("groupBoxDate")
        self.label = QtWidgets.QLabel(self.groupBoxDate)
        self.label.setGeometry(QtCore.QRect(10, 40, 81, 16))
        self.label.setObjectName("label")
        self.startDateEdit = QtWidgets.QDateEdit(self.groupBoxDate)
        self.startDateEdit.setEnabled(False)
        self.startDateEdit.setGeometry(QtCore.QRect(90, 40, 151, 20))
        self.startDateEdit.setDateTime(QtCore.QDateTime(QtCore.QDate(2020, 1, 1), QtCore.QTime(0, 0, 0)))
        self.startDateEdit.setCalendarPopup(True)
        self.startDateEdit.setObjectName("startDateEdit")
        self.endDateEdit = QtWidgets.QDateEdit(self.groupBoxDate)
        self.endDateEdit.setEnabled(False)
        self.endDateEdit.setGeometry(QtCore.QRect(90, 90, 151, 20))
        self.endDateEdit.setDateTime(QtCore.QDateTime(QtCore.QDate(2020, 1, 1), QtCore.QTime(0, 0, 0)))
        self.endDateEdit.setCalendarPopup(True)
        self.endDateEdit.setObjectName("endDateEdit")
        self.label_2 = QtWidgets.QLabel(self.groupBoxDate)
        self.label_2.setGeometry(QtCore.QRect(24, 90, 71, 16))
        self.label_2.setObjectName("label_2")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(Dialog)
        self.plainTextEdit.setGeometry(QtCore.QRect(10, 600, 251, 131))
        self.plainTextEdit.setObjectName("plainTextEdit")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_4.setText(_translate("Dialog", "Zones prioritères (facultatif):"))
        self.label_3.setText(_translate("Dialog", "Numéro de tuile : "))
        self.label_6.setText(_translate("Dialog", "Ex : T18TUT"))
        self.pushButtonLaunch.setText(_translate("Dialog", "Lancer la recherche"))
        self.label_5.setText(_translate("Dialog", "Exemple de format : 1,5,9,13 "))
        self.groupBoxDate.setTitle(_translate("Dialog", "Toutes les périodes possibles"))
        self.label.setText(_translate("Dialog", "Date de début : "))
        self.label_2.setText(_translate("Dialog", "Date de fin :"))


class upperLineEdit(QtWidgets.QLineEdit):

    def __init__(self,parent=None):
        super(upperLineEdit, self).__init__(parent)


    def keyPressEvent(self, event):
        QtWidgets.QLineEdit.keyPressEvent(self, event)
        pretext = self.text()
        self.setText(pretext.__str__().upper())




