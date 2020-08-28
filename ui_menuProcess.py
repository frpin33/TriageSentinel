# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui-menuProcess.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(299, 295)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(26, 30, 81, 16))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(40, 80, 71, 16))
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(20, 130, 81, 16))
        self.label_3.setObjectName("label_3")
        self.lineEditNumero = upperLineEdit(self.centralwidget)
        self.lineEditNumero.setGeometry(QtCore.QRect(120, 130, 151, 20))
        self.lineEditNumero.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.lineEditNumero.setObjectName("lineEditNumero")
        self.pushButtonLaunch = QtWidgets.QPushButton(self.centralwidget)
        self.pushButtonLaunch.setGeometry(QtCore.QRect(160, 190, 111, 23))
        self.pushButtonLaunch.setObjectName("pushButtonLaunch")
        self.startDateEdit = QtWidgets.QDateEdit(self.centralwidget)
        self.startDateEdit.setGeometry(QtCore.QRect(120, 30, 151, 20))
        self.startDateEdit.setDateTime(QtCore.QDateTime(QtCore.QDate(2020, 1, 1), QtCore.QTime(0, 0, 0)))
        self.startDateEdit.setCalendarPopup(True)
        self.startDateEdit.setObjectName("startDateEdit")
        self.endDateEdit = QtWidgets.QDateEdit(self.centralwidget)
        self.endDateEdit.setGeometry(QtCore.QRect(120, 80, 151, 20))
        self.endDateEdit.setDateTime(QtCore.QDateTime(QtCore.QDate(2020, 1, 1), QtCore.QTime(0, 0, 0)))
        self.endDateEdit.setCalendarPopup(True)
        self.endDateEdit.setObjectName("endDateEdit")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(30, 150, 81, 16))
        self.label_6.setObjectName("label_6")
        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(20, 190, 118, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.labelNombreTuile = QtWidgets.QLabel(self.centralwidget)
        self.labelNombreTuile.setGeometry(QtCore.QRect(20, 230, 251, 16))
        self.labelNombreTuile.setObjectName("labelNombreTuile")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 299, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Interface de traitement"))
        self.label.setText(_translate("MainWindow", "Date de début : "))
        self.label_2.setText(_translate("MainWindow", "Date de fin :"))
        self.label_3.setText(_translate("MainWindow", "Numéro de tuile : "))
        self.pushButtonLaunch.setText(_translate("MainWindow", "Lancer le traitement"))
        self.label_6.setText(_translate("MainWindow", "Ex : T18TUT"))
        self.labelNombreTuile.setText(_translate("MainWindow", "Nombre de tuile à traiter : Aucune"))


class upperLineEdit(QtWidgets.QLineEdit):

    def __init__(self,parent=None):
        super(upperLineEdit, self).__init__(parent)


    def keyPressEvent(self, event):
        QtWidgets.QLineEdit.keyPressEvent(self, event)
        pretext = self.text()
        self.setText(pretext.__str__().upper())
