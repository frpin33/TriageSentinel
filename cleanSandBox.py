
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

#listObj = pickle.load(open(tilePath,'rb'))

src = osr.SpatialReference()
src.ImportFromEPSG(32198)
c = src.ExportToXML()
src = osr.SpatialReference()
src.ImportFromEPSG(32618)
d = src.ExportToXML()
e = [d,c]
#print(c)
pickle.dump(e,open("test.txt","wb"))
'''print(src.ExportToWkt())
src.ImportFromEPSG(32620)
print(src.ExportToWkt())
src.ImportFromEPSG(32621)
print(src.ExportToWkt())
src.ImportFromEPSG(32198)
print(src.ExportToWkt())'''

