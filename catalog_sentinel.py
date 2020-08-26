#!/usr/bin/python3
# Nécessaire d'être en 64 bit


"""
	###########################
	Exécution du script complet
	de masque de nuages à partir
	de la lecture même du CSV
	des tuiles téléchargées et
	production des couches du
	50e percentille
	###########################
"""
import libsentinel as stl
from osgeo import gdal


# Variables pour le masquage des nuages
indir = r"F:\Sentinel_T18TUT"
outdir = r"F:\Sentinel_T18TUT_masked2"
date_start = "2018-07-15"
date_end = "2018-08-31"

# Variables pour le calcul du 50e percentile
tileid = "T18TUT"
nodata_ori = 0
doy_pref = 220  # Date préférentielle

stl.makemaskedbands(indir, outdir, date_start, date_end)
stl.makep50(outdir, r"F:\Sentinel_T18TUT_p50_220", tileid, doy_pref, nodata_ori)
stl.makep50(outdir, r"F:\Sentinel_T18TUT_p50_000", tileid, 0, nodata_ori)

# Performance
# Pour 11 tuiles, la fonction makemaskedbands prend environ 55 minutes (5 min / tuile)
# Pour 11 tuiles, la fonction makep50 prend environ 6 minutes. Ça ne devrait pas augmenter beaucoup avec plus de tuiles.


# Regarder ce qui cloche avec la tuile S2A_MSIL1C_20180706T160901_N0206_R140_T18TUT_20180706T195426
# qui ne semble pas passer dans le script (tester de nouveau quand même)



# Séquence pour générer des tuiles avec masques de nuages intégrés (bandes trouées)
# pour que Marie-Pierre puisse piger dans ces tuiles-là. Penser à générer un GTIFF
# composite d'aperçu à 20m.
safe = r"F:\Tests_Sen2Cor\Multiproc_sen2cor\S2A_MSIL2A_20180514T155911_N0206_R097_T18TUT_20180514T194414.SAFE"

#1 Téléchargement des images L1C


#2 Conversion en L2A
stl.sen2cor(safe, outdir_L2A)

safe_L2A = safe.replace("_MSIL1C_", "_MSIL2A_")
if outdir_L2A is not None:
	safe_L2A = os.path.join(outdir_L2A, os.path.basename(safe_L2A))

#3 Création du masque de nuages et inscription des métadonnées
relativerootpath = stl.extract_jp2_relativerootpath(safe_L2A)
subpath = relativerootpath[2]
cloudmask_path = os.path.join(safe_L2A, subpath[:-14], "QI_DATA", "MSK_CLDPRB_60m.jp2")
outdir_mask = os.path.join(safe_L2A, "DIF_mask")
os.makedirs(outdir_mask)
stl.refine_mask(cloudmask_path, relativerootpath[1][7:], outdir_mask)

#4 Trouer les bandes
outdir_bands = os.path.join(safe_L2A, "DIF_bands")
os.makedirs(outdir_bands)

for str_band in ["B02", "B03", "B04", "B08"]:
	band = stl.apply_mask(os.path.join(safe_L2A, relativerootpath[2][:-3] + "10m", relativerootpath[1] + "_" + str_band + "_10m.jp2"),
						  os.path.join(outdir_mask, relativerootpath[1][7:] + "_mask_10m.tif"))
	stl.rewrite_band(band, os.path.join(outdir_bands, relativerootpath[1] + "_" + str_band + "_10m_masked.tif"), 0)

for str_band in ["B05", "B06", "B07", "B8A", "B11", "B12"]:
	band = stl.apply_mask(os.path.join(safe_L2A, relativerootpath[2][:-3] + "20m", relativerootpath[1] + "_" + str_band + "_20m.jp2"),
						  os.path.join(outdir_mask, relativerootpath[1][7:] + "_mask_20m.tif"))
	stl.rewrite_band(band, os.path.join(outdir_bands, relativerootpath[1] + "_" + str_band + "_20m_masked.tif"), 0)

for str_band in ["B01", "B09"]:
	band = stl.apply_mask(os.path.join(safe_L2A, relativerootpath[2][:-3] + "60m", relativerootpath[1] + "_" + str_band + "_60m.jp2"),
						  os.path.join(outdir_mask, relativerootpath[1][7:] + "_mask_60m.tif"))
	stl.rewrite_band(band, os.path.join(outdir_bands, relativerootpath[1] + "_" + str_band + "_60m_masked.tif"), 0)

#5 Créer un composite d'aperçu
output_path = os.path.join(outdir_mask, relativerootpath[1][7:] + "_composite_080403.tif")


driver = gdal.GetDriverByName("GTiff")
fileout = driver.Create(outpath_path, resolutionX, resolutionY, 3, gdal.GDT_UInt16, options=["PHOTOMETRIC=RGB", "COMPRESS=LZW"])
fileout.GetRasterBand(1).WriteArray(B08)
fileout.GetRasterBand(2).WriteArray(B04)
fileout.GetRasterBand(3).WriteArray(B03)
fileout.GetRasterBand(1).SetNoDataValue(0)
fileout.SetProjection(mask[1])
fileout.SetGeoTransform(mask[2])
fileout.FlushCache()
fileout = None


"""
#6 Créer des raccourcis pour pointer vers les composites
# Nécessite le module pywin32
import os, pythoncom 
from win32com.client import Dispatch

# pythoncom.CoInitialize() # remove the '#' at the beginning of the line if running in a thread.
desktop = r'C:\Users\Public\Desktop' # path to where you want to put the .lnk
path = os.path.join(desktop, 'NameOfShortcut.lnk')
target = r'C:\path\to\target\file.exe'

shell = Dispatch("WScript.Shell")
shortcut = shell.CreateShortCut(path)
shortcut.Targetpath = target
shortcut.save()
"""



"""
	###########################
	Pour obtenir la position en colonne et en ligne
	d'un pixel à partir de la matrice projetée
	###########################
"""
#Coordonnées du centre du pixel au coin supérieur gauche du raster
coord_X =  300005
coord_Y = 5300035
resolution = 10

new_X =  318355
new_Y = 5284635
print("X: " + str(int(abs(new_X-coord_X)/resolution)), "\nY: " + str(int(abs(new_Y-coord_Y)/resolution)))


"""
	###########################
	Clip d'une petite zone pour
	réduire le temps de calcul
	###########################
"""
indir = r"F:\test_masque_nuages_sentinel\temp_clip"
outdir = r"F:\test_masque_nuages_sentinel\temp_clip\clip"
ls_files = [file for file in os.listdir(indir) if os.path.isfile(os.path.join(indir, file)) and file.endswith(".tif")]

for filename in ls_files:
	cmd = " ".join(["gdalwarp -of GTIFF -te 350730 5253021 372445 5262619 -co COMPRESS=LZW", filename, os.path.join(outdir, filename[:-4]+"_clip.tif")])
	subprocess.run(cmd, cwd=indir)



"""
	###########################
	Création d'un VRT
	###########################
"""
dir_out = r"F:\Sentinel_T18TUT"
ls_dir = []
for file in os.listdir(dir_out):
	if file.endswith(".SAFE"):
		ls_dir.append(file[:-5])

for dir in ls_dir:
	jp2_relativerootpath = extract_jp2_relativerootpath(dir_out, dir)
	
	# Création du composite VRT 04-03-02
	indir = os.path.join(dir_out, dir + ".SAFE", jp2_relativerootpath[1])
	create_vrt(dir_gdal, dir_out, indir, jp2_relativerootpath[0], ["04", "03", "02"])



"""
	###########################
	Tests pour réduire la taille du TCI et ainsi l'utiliser comme aperçu
	dans un éventuel catalogue Sentinel en HTML généré avec knitr
	###########################
"""
gdal_path = r"C:\Mrnmicro\Applic\gdal\2.2.3\gdal_translate.exe"
path_TCI = os.path.join(outpath, "T18TUT_20180608T155859_TCI.jp2")
path_resampled = os.path.join(outpath, "thumb.jpg")
cmd = " ".join([gdal_path, "-ot Byte -of JPEG -outsize 200 200", path_TCI, path_resampled])
subprocess.run(cmd)
os.remove(os.path.join(outpath, "thumb.jpg.aux.xml"))



"""
	###########################
	Test pour convertir un PIX en JP2
	###########################
"""
# Configuration de GDAL pour définir des variables d'enviromment temporaires https://trac.osgeo.org/gdal/wiki/ConfigOptions
# https://blog.hexagongeospatial.com/jpeg2000-quirks/
import os, subprocess
gdal_translate = r"C:\Mrnmicro\Applic\gdal\2.2.3\gdal_translate.exe"
gdal_data = r"C:\Mrnmicro\Applic\gdal\2.2.3\gdal-data"
inpath = r"E:\Test_Louise\mosa2018tot_clip_8bit.pix"
outpath = r"E:\Test_Louise\mosaique_quality050.jp2"
cmd = " ".join([gdal_translate, '-ot Byte -of JP2OpenJPEG --config GDAL_DATA', gdal_data, '-a_srs EPSG:32198 -co "QUALITY=5"', inpath, outpath])
subprocess.run(cmd)


# À partir de GDAL 2.3
#gdaladdo -ro --config COMPRESS_OVERVIEW JPEG --config PHOTOMETRIC_OVERVIEW YCBCR --config INTERLEAVE_OVERVIEW PIXEL myfile.jp2 2 4 8 16 32