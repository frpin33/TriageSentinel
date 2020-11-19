
import gdal, osr, pickle

class objSentinel : 
    def __init__(self, pathSAFE='', nameIMG='', totalClearPercent=0.0, clearPercent=[0]*16, isTopFile=[False]*16, under60=True) :
        self.pathSAFE = pathSAFE
        self.nameIMG = nameIMG
        self.totalClearPercent = totalClearPercent
        self.clearPercent = clearPercent
        self.isTopFile = isTopFile
        self.under60 = under60

tilePath = "I:/TeleDiff/Commun/a-Images-Satellites/SENTINEL/Information/T19UEP.txt"

listObj = pickle.load(open(tilePath,'rb'))
print('a')


