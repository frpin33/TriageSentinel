
import gdal, osr
osr.SpatialReference
filetype = 'JPEG2000'
path = "U:/Mosaique_Sentinel/Sentinel_T18TUT/S2A_MSIL1C_20180514T155911_N0206_R097_T18TUT_20180514T194414.SAFE/GRANULE/L1C_T18TUT_A015109_20180514T160535/IMG_DATA/T18TUT_20180514T155911_B04.jp2"
driver = gdal.GetDriverByName(filetype)
file = gdal.Open(path)
band = file.GetRasterBand(1)
array = band.ReadAsArray()
proj = file.GetProjection()
georef = file.GetGeoTransform()
sizeX = file.RasterXSize
sizeY = file.RasterYSize
meta = file.GetMetadata()
gcp = file.GetGCPProjection()
src = osr.SpatialReference(proj)
dst = osr.SpatialReference()
dst.ImportFromEPSG(32198)
ct = osr.CoordinateTransformation(src,dst)
result = ct.TransformPoint(georef[0], georef[3])
print(dst.GetAttrValue('PROJCS'))
#print(dst.GetAttrValue('AUTHORITY'))
a = georef[0] + georef[1]*sizeX
b = georef[3] + georef[5]*sizeY


lamb = '//ulysse/LIDAR/Developpement/Programmation/FP/Pic2Map/Exemples_photos/SRTM_nord.tif'
prof = '//ulysse/LIDAR/Developpement/Programmation/FP/Pic2Map/Exemples_photos/DIF_2661/SRTM_2661.tif'
d = gdal.GetDriverByName('GTiff')
f = gdal.Open(lamb)
p = f.GetProjection()
d2 = gdal.GetDriverByName('GTiff')
f2 = gdal.Open(prof)
p2 = f2.GetProjection()

if p == p2 :
    print('YEAH') 

print(sizeY)



