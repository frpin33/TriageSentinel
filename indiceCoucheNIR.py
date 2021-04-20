import gdal, time, osr
import numpy as np

pathNir = 'U:/Mosaique_Sentinel/test/T19UDT_20200614T154819_NIR_Cut.tif'
pathNBR = 'U:/Mosaique_Sentinel/test/T19UDT_NBR.tif'
pathNDVI = 'U:/Mosaique_Sentinel/test/T19UDT_NDVI.tif'


nir = gdal.Open(pathNir)

swirBand = nir.GetRasterBand(1)
nirBand = nir.GetRasterBand(2)
redBand = nir.GetRasterBand(3)
sizeX = nir.RasterXSize
sizeY = nir.RasterYSize
proj = nir.GetProjection()
georef = nir.GetGeoTransform()
src = osr.SpatialReference(proj)



arrSwir = swirBand.ReadAsArray()
arrSwir.astype(float)[arrSwir ==0] = np.nan
arrNir = nirBand.ReadAsArray()
arrNir.astype(float)[arrNir ==0] = np.nan
arrRed = redBand.ReadAsArray()
arrRed.astype(float)[arrRed ==0] = np.nan

topNBR = (arrNir - arrSwir).astype(float) 
botNBR = (arrNir + arrSwir).astype(float) 
botNBR[botNBR==0] = np.nan
NBRArray = np.divide(topNBR,botNBR, where= ((botNBR!=np.nan) | (topNBR!=np.nan)) )*1000
np.nan_to_num(NBRArray,False, nan=-32768, posinf=32767, neginf=-32767)

topNDVI = (arrNir - arrRed).astype(float) 
botNDVI = (arrNir + arrRed).astype(float) 
botNDVI[botNDVI==0] = np.nan
NDVIArray = np.divide(topNDVI,botNDVI, where= ((botNDVI!=np.nan) | (topNDVI!=np.nan)) )*1000
np.nan_to_num(NDVIArray,False, nan=-32768, posinf=32767, neginf=-32767)


tab = []
for i in range(1,9):
    tab.append(2**i)
driver = gdal.GetDriverByName("GTiff")

fileout = driver.Create(pathNDVI,sizeX,sizeY, 1, gdal.GDT_Int16, ["COMPRESS=LZW"])
fileout.GetRasterBand(1).WriteArray(NDVIArray)
fileout.GetRasterBand(1).SetNoDataValue(-32768)
fileout.SetProjection(src.ExportToWkt())
fileout.SetSpatialRef(src)
fileout.SetGeoTransform(georef)
fileout.BuildOverviews('AVERAGE', tab)
fileout.FlushCache()
fileout = None

#print(np.min(i[np.nonzero(i)]))
#print(i.min())
#print(i.max())


#for x in range(sizeX):
#    for y in range(sizeY) :
#        pass

print(time.time())