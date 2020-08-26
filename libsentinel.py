#!/usr/bin/python3-64
# -*- coding: utf-8 -*-

"""
	Module écrit par Jean-François Bourdon
	Direction des inventaires forestiers
	Ministère des Forêts, de la Faune et des Parcs
	jean-francois.bourdon@mffp.gouv.qc.ca
	
	Dernière mise à jour: 2019-01-04
"""

"""
	###########################
	Génère les masques de nuages à partir
	des bandes 4, 5, 9 et 10 de Sentinel-2
	###########################
"""

from osgeo import gdal
from scipy import ndimage, stats
import pandas as pd
import xml.etree.ElementTree as ET
import numpy as np
import os, subprocess, sys, datetime, shutil


def load_raster(path, filetype):
	# Permet simplement de charger un fichier raster, JP2, GTiff ou JPEG.
	# Fichier à bande unique seulement!
	
	driver = gdal.GetDriverByName(filetype)
	file = gdal.Open(path)
	band = file.GetRasterBand(1)
	array = band.ReadAsArray()
	proj = file.GetProjection()
	georef = file.GetGeoTransform()
	sizeX = file.RasterXSize
	sizeY = file.RasterYSize
	return([array, proj, georef, sizeX, sizeY])


def majority_filter(array):
	# Très lent, à voir si je peux améliorer
	# a = np.random.randint(9, size=(10,10))
	# x = np.array([4,4,5,5,6,7,7,1,2,9,5])
	
	#https://github.com/scipy/scipy/issues/8916
	#https://ilovesymposia.com/2017/03/15/prettier-lowlevelcallables-with-numba-jit-and-decorators/
	#https://ilovesymposia.com/2016/12/20/numba-in-the-real-world/
	#https://ilovesymposia.com/2017/03/12/scipys-new-lowlevelcallable-is-a-game-changer/
	#https://ilovesymposia.com/2014/06/24/a-clever-use-of-scipys-ndimage-generic_filter-for-n-dimensional-image-processing/
	#https://realpython.com/primer-on-python-decorators/
	#https://www.ebooks.com/95838978/elegant-scipy/nunez-iglesias-juan-walt-stefan-van-der-dashnow-ha/
	
	
	def myfunc(x):
		# À noter que s'il y a deux valeurs avec la même fréquence, la valeur la plus petite est retenue.
		# Il y aurait moyen d'avoir un arbre de décision plus élaboré avec np.unique(x, return_counts=True)
		# et un peu de gossage supplémentaire
		val = stats.mode(x)[0][0]
		return val
	
	# En fait, au lieu de calculer un mode, je suis peut-être aussi bien de calculer un min() qui éliminerait
	# encore plus agressivement les pixels isolés. Réduire par contre à ce moment la fenêtre à 3. 
	filtered = ndimage.generic_filter(array, myfunc, size=5)
	return(filtered)


def create_mask(indir, outdir):
	# Crée un masque de nuages à partir des bandes 9 et 10. Les seuils sont présentement fixes
	# et certainement pas optimaux. Un buffer de 10 pixels est ajouté
	# Éventuellement, l'azimuth solaire pourrait aussi être pris en compte afin de retirer
	# encore plus de pixels (les ombres). En fait, éventuellement, il faudrait qu'une autre méthode soit utilisée
	# afin d'exclure les nuages, celles-ci étant très brute. Ça fera la job pour le moment...
	# Je devrais également créer une autre fonction pour évaluer le degré d'homogénéité des tuiles, c'est-à-dire
	# à quel point les zones sans nuages sont fragmentées dans la tuile. Je pourrais l'évaluer en passant
	# un filtre haut sur le masque de nuages et ensuite en calculant la quantités de pixels de transition (en
	# gros le périmètre de tous les nuages par rapport à la superficie de zone sans nuages)
	
	ls_files = [file for file in os.listdir(indir) if os.path.isfile(os.path.join(indir, file)) and file.endswith(".jp2")]
	ls_files.sort()
	
	# Importation de la bande 9
	path_JP2 = os.path.join(indir, ls_files[8])
	band09 = load_raster(path_JP2, "JPEG2000")
	
	# Importation de la bande 10
	path_JP2 = os.path.join(indir, ls_files[9])
	band10 = load_raster(path_JP2, "JPEG2000")
	
	# Faire en plus un ratio bande 4 / 5, car généralement:
	# Au-dessus d'un nuage: bande 5 légèrement plus élevée que bande 4
	# Au-dessus de l'eau:   bande 4 légèrement plus élevée que bande 5
	# Au-dessus chemin:     bande 5 légèrement plus élevée que bande 4
	# Au-dessus forêt:      bande 5 deux à trois fois plus élevée que bande 4
	band_shape = band09[0].shape
	
	# Rescale de la bande 04 à 60m avec interpolation bilineaire
	path_JP2 = os.path.join(indir, ls_files[3])
	outpath = os.path.join(outdir, ls_files[3][:-4] + "_60m.tif")
	subprocess.run(" ".join(["gdal_translate -tr 60 60 -r bilinear", path_JP2, outpath]))
	band04 = load_raster(outpath, "GTiff")
	
	# Rescale de la bande 05 à 60m avec interpolation bilineaire
	path_JP2 = os.path.join(indir, ls_files[4])
	outpath = os.path.join(outdir, ls_files[4][:-4] + "_60m.tif")
	subprocess.run(" ".join(["gdal_translate -tr 60 60 -r bilinear", path_JP2, outpath]))
	band05 = load_raster(outpath, "GTiff")
	
	# Faire ratio de 04/05 et si entre 0.85 et 1, dire que c'est potentiellement un nuage
	# Des avertissements de division par zéro seront émis, mais peuvent être ignorés
	ratio0405 = band04[0] / band05[0]
	ar_stack = np.zeros(shape=(band_shape[0], band_shape[1], 2), dtype=np.bool)
	ar_stack[..., 0] = ratio0405 >= 0.85
	ar_stack[..., 1] = ratio0405 < 1
	mask0405 = np.all(ar_stack, 2)
	
	# Faire une passe de filter majoritaire sur mask0405
	# Étape plutôt lente, à voir si je peux accélérer la chose
	mask0405 = majority_filter(mask0405)
	#mask0405 = ndimage.generic_filter(mask0405, min, size=3)
	
	# Création du masque combiné 09*10
	prod0910 = band09[0] * band10[0]
	mask0910 = prod0910 >= 20000
	
	# Faire une passe de filter majoritaire sur mask0910
	# Autre étape lente à cause du filter
	mask0910 = majority_filter(mask0910)
	#mask0910 = ndimage.generic_filter(mask0910, min, size=3)
	
	# Applique la condition que les deux couches doivent être True pour affirmer qu'il y a un nuage
	ar_stack = np.zeros(shape=(band_shape[0], band_shape[1], 2), dtype=np.bool)
	ar_stack[0:band_shape[0], 0:band_shape[1], 0] = mask0405
	ar_stack[0:band_shape[0], 0:band_shape[1], 1] = mask0910
	cloud_mask = np.all(ar_stack, 2)
	
	
	# Rafinement du masque de nuages en retirant des pixels esseulés et en ajoutant un buffer autour des
	# pixels de nuages restants
	
	# Faire une passe de filtre majoritaire sur cloud_mask pour éliminer les pixels esseulés
	#cloud_mask = majority_filter(cloud_mask)
	
	# Faire une passe de filtre minimal sur cloud_mask pour éliminer les pixels esseulés
	#cloud_mask = ndimage.generic_filter(cloud_mask, min, size=3) à voir si l'utilisation de grey_erosion est vraiment plus rapide
	cloud_mask = ndimage.morphology.grey_erosion(cloud_mask, size=3)
	
	# Ajout d'un buffer d'environ 10 pixels au masque
	#strel = np.zeros((21, 21))
	#rr, cc = draw.circle(10, 10, 10) #plus un peu d'ajustement
	#strel[rr, cc] = 1
	
	strel = np.array([[0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0],
					  [0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
					  [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0],
					  [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
					  [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
					  [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
					  [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
					  [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
					  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
					  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
					  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
					  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
					  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
					  [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
					  [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
					  [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
					  [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
					  [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
					  [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0],
					  [0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
					  [0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0]])
	
	cloud_mask_expanded = ndimage.morphology.binary_dilation(cloud_mask, structure=strel)
	
	# Exportation bien simple du fichier de masque pour visualisation
	outpath_60m = os.path.join(outdir, ls_files[0][:-7] + "mask_60m.tif")
	driver = gdal.GetDriverByName("GTiff")
	fileout = driver.Create(outpath_60m, band_shape[0], band_shape[1], 1, gdal.GDT_Byte, options=["COMPRESS=LZW"])
	fileout.GetRasterBand(1).WriteArray(cloud_mask_expanded)
	fileout.SetProjection(band09[1])
	fileout.SetGeoTransform(band09[2])
	fileout.FlushCache()
	fileout = None
	
	#subprocess.run(" ".join(["gdal_translate -tr 20 20 -r nearest", outpath_60m, outpath_60m[:-7] + "20m.tif"]))
	#subprocess.run(" ".join(["gdal_translate -tr 10 10 -r nearest", outpath_60m, outpath_60m[:-7] + "10m.tif"]))
	
	# Éventuellement, faire un calcul pour déterminer l'homogénéïté spatial des nuages
	# afin de prioriser plus loin les tuiles qui ont des nuages concentrés (et le moins possible)
	# Ça devrait se retrouver dans une fonction séparée
	# https://stackoverflow.com/questions/6094957/high-pass-filter-for-image-processing-in-python-by-using-scipy-numpy
	
	# Pour la priorisation des couches. À la suggestion d'Antoine, je pourrais utiliser les lacs pour déterminer s'il y a présence
	# ou non de voile atmosphérique. De mi-juin à septembre, les lacs devraient être stables. À voir quelles bandes sont utilisables
	# afin d'éviter des problèmes liés au scientillement causé par les vagues parfois
	
	#return(cloud_mask_expanded)


def refine_mask(inpath, str_datetime, outdir):
	"""
		Permet de rafiner le masque de nuage issu du processus de correction
		atmosphérique Sen2Cor
		
		inpath: chemin d'accès au masque de nuages brut
		outdir: chemin d'accès au répertoire où sera exporter le masque final
	"""
	
	mask_raw = load_raster(inpath, "JPEG2000")
	mask_shape = mask_raw[0].shape
	
	#Faire une reclassification
	mask_refine = mask_raw[0] >= 3
	
	#Faire des filtres
	mask_refine = majority_filter(mask_refine)
	
	# Faire une passe de filtre minimal sur cloud_mask pour éliminer les pixels esseulés
	#cloud_mask = ndimage.generic_filter(cloud_mask, min, size=3) à voir si l'utilisation de grey_erosion est vraiment plus rapide
	#cloud_mask = ndimage.morphology.grey_erosion(cloud_mask, size=3)
	
	# Ajout d'un buffer d'environ 10 pixels au masque
	#strel = np.zeros((21, 21))
	#rr, cc = draw.circle(10, 10, 10) #plus un peu d'ajustement
	#strel[rr, cc] = 1
	
	strel = np.array([[0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0],
					  [0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
					  [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0],
					  [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
					  [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
					  [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
					  [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
					  [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
					  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
					  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
					  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
					  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
					  [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
					  [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
					  [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0],
					  [0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0],
					  [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
					  [0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0],
					  [0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0],
					  [0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0],
					  [0,0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0]])
	
	cloud_mask_expanded = ndimage.morphology.binary_dilation(mask_refine, structure=strel)
	
	# Ajouter une translation au masque afin de considérer l'ombre
	# Extraction de l'heure UTC de l'acquisition
	# Idéalement, il faudrait que j'aille chercher l'info dans les métadonnées, mais ça ne
	# semble pas être présent
	utc_time = datetime.datetime.strptime(str_datetime, "%Y%m%dT%H%M%S")
	
	# Identification de la coordonnées centrale de l'image
	resolution = mask_raw[2][1]
	x1 = mask_raw[2][0] + resolution * mask_shape[0] / 2 # À valider que mask_shape[1] est bien sur l'axe X
	y1 = mask_raw[2][3] - resolution * mask_shape[1] / 2 # À valider que mask_shape[1] est bien sur l'axe Y
	
	# Reprojection de la coordonnée centrale en EPSG 4326
	import pyproj, math
	epsg = mask_raw[1].split(",")[-1][1:-3]
	inProj  = pyproj.Proj("+init=EPSG:"+epsg, preserve_units=True)
	outProj = pyproj.Proj("+init=EPSG:4326")
	lon, lat = pyproj.transform(inProj, outProj, x1, y1)
	alt, azi = get_sun_alt_azi(utc_time, lon, lat)
	
	# Évaluation de la translation nécessaire pour couvrir les ombres
	buffer = 17 # Taille du déplacement en nombre de pixels
	translation_unit = buffer * resolution
	theta = azi - math.pi / 2
	delta_x = translation_unit * math.sin(theta) #Valider que mes X et Y sont dans le bon ordre
	delta_y = translation_unit * math.cos(theta) #Valider que mes X et Y sont dans le bon ordre
	
	delta_x_px = math.ceil(delta_x / resolution) #Valider que mes X et Y sont dans le bon ordre
	delta_y_px = math.ceil(delta_y / resolution) #Valider que mes X et Y sont dans le bon ordre
	
	# Incorporation du masque de nuages avec le masque d'ombres
	false_mask = np.zeros(shape=(mask_shape[0],mask_shape[1],2), dtype=np.bool_)
	false_mask[...,0] = cloud_mask_expanded
	false_mask[:-delta_x_px, :-delta_y_px, 1] = cloud_mask_expanded[delta_x_px:, delta_y_px:] #Valider que mes X et Y sont dans le bon ordre
	
	full_mask = np.any(false_mask, axis=2)
	
	
	# Exportation bien simple du fichier de masque pour visualisation
	outpath_60m = os.path.join(outdir, str_datetime + "_mask_60m.tif")
	driver = gdal.GetDriverByName("GTiff")
	fileout = driver.Create(outpath_60m, mask_shape[0], mask_shape[1], 1, gdal.GDT_Byte, options=["COMPRESS=LZW"])
	fileout.GetRasterBand(1).WriteArray(full_mask)
	fileout.SetProjection(mask_raw[1])
	fileout.SetGeoTransform(mask_raw[2])
	fileout.FlushCache()
	fileout = None
	
	subprocess.run(" ".join(["gdal_translate -tr 20 20 -r nearest", outpath_60m, outpath_60m[:-7] + "20m.tif"]))
	subprocess.run(" ".join(["gdal_translate -tr 10 10 -r nearest", outpath_60m, outpath_60m[:-7] + "10m.tif"]))


def get_sun_alt_azi(utc_time, lon, lat):
	from pyorbital import astronomy
	import datetime, math
	
	alt, azi = astronomy.get_alt_az(utc_time, lon, lat)
	
	alt_deg = alt * 180 / math.pi      # à 19h UTC =>  15.65°   à 12h UTC =>  -5.03°
	
	if azi < 0:
		azi += 2 * math.pi
	
	azi_deg = azi * 180 / math.pi   # à 19h UTC => 210.50°   à 12h UTC => 116.82°
	
	return(alt, azi)



def apply_mask(path_ori, path_mask):
	# Charge en mémoire le masque de nuages et l'applique sur la bande chargée
	# La fonction n'écrit rien sur le disque et ne fait que renvoyer l'array modifié de la bande
	
	band = load_raster(path_ori, "JPEG2000")
	cloud_mask = load_raster(path_mask, "GTiff")
	
	import tempfile
	path_temp = os.path.join(tempfile.gettempdir(), os.path.basename(path_mask)[:-4] + "_resized")
	# Je semble obligé d'exporter un fichier... j'en ferai un fichier bidon dans le répertoire temporaire pour l'instant
	# Je devrais éventuellement utiliser une approche par VRT qui éviterait en partie le problème à moins que je réussisse
	# à conserver en interne le fichier.
	ds2 = gdal.Translate(path_temp, path_mask, xRes=band[2][1], yRes=-band[2][5], resampleAlg="nearest")
	mask = ds2.GetRasterBand(1)
	cloud_mask_resized = mask.ReadAsArray()
	
	# Mise à None des pixels sous le masque de nuages
	band[0][np.where(cloud_mask_resized == 1)] = 0
	
	return(band)


def rewrite_band(band, outpath, nodata=None):
	# Exportation bien simple du fichier de la bande modifiée pour visualisation
	driver = gdal.GetDriverByName("GTiff")
	fileout = driver.Create(outpath, band[0].shape[0], band[0].shape[1], 1, gdal.GDT_UInt16, options=["COMPRESS=LZW"])
	fileout.GetRasterBand(1).WriteArray(band[0])
	fileout.GetRasterBand(1).SetNoDataValue(nodata) if nodata is not None else None
	fileout.SetProjection(band[1])
	fileout.SetGeoTransform(band[2])
	fileout.FlushCache()
	fileout = None





"""
	###########################
	Produit les couches liées au
	50e percentille
	###########################
"""
def list_doy_pref(ls_order_doy, date_pref):
	"""
		Permet de créer la liste d'ordre nécessaire en intrant pour la fonction perc50_raster
		Particulièrement utile pour obtenir l'ordre des images en souhaitant utiliser
		préférentiellement les images les plus près possible d'une certaine date.
		
		Le double np.argsort() permet d'obtenir une liste me disant que le i élément de la liste
		devrait être à la position ls_order[i] de l'array non classé ls_order_doy.
	"""
	
	arr_order_doy = np.array(ls_order_doy).astype('int16')
	arr_order = np.argsort(np.argsort(abs(arr_order_doy - date_pref)).astype('uint16'))
	ls_order = arr_order.tolist()
	return(ls_order)


def list_order_doy(ls_files):
	"""
		Permet pour le moment de trouver la date (DOY) des tuiles à importer avec list_rasterfiles().
		Éventuellement, ce ne sera pas nécessaire puisque les valeur seront directement extraites
		du fichier CSV. Cette fonction est vraiment seulement pour la phase de tests.
	"""
	from datetime import datetime
	
	ls_order_value = []
	for file in ls_files:
		str_date = os.path.basename(file)[7:15]
		int_doy = datetime.strptime(str_date, "%Y%m%d").timetuple().tm_yday
		ls_order_value.append(int_doy)
	
	return(ls_order_value)


def list_rasterfiles(indir, extension, path):
	"""
		Permet la création d'une liste de chemin d'accès à des images matricielles pour le calcul de percentile.
		Dans le cas présent, la liste est également classée en ordre aphabétique afin d'assurer une constance lors
		du calcul de ls_order.
		Éventuellement, il faudrait plutôt une fonction aller lire le CSV du catalogue d'images et retourner
		les chemins d'accès complet.
	"""
	
	if extension == ".jp2":
		drivername = "JPEG2000"
	elif extension == ".tif":
		drivername = "GTIFF"
	
	# Identification des tuiles à charger
	if path == "short":
		ls_files = [file for file in os.listdir(indir) if os.path.isfile(os.path.join(indir, file)) and file.endswith(extension)]
	elif path == "full":
		ls_files = [os.path.join(indir, file) for file in os.listdir(indir) if os.path.isfile(os.path.join(indir, file)) and file.endswith(extension)]
	
	return(sorted(ls_files))


def list_rasterfiles2(indir, extension, path):
	"""
		Permet la création d'une liste de chemin d'accès à des images matricielles pour le calcul de percentile.
		Dans le cas présent, la liste est également classée en ordre aphabétique afin d'assurer une constance lors
		du calcul de ls_order.
		Éventuellement, il faudrait plutôt une fonction aller lire le CSV du catalogue d'images et retourner
		les chemins d'accès complet.
	"""
	
	if extension == ".jp2":
		drivername = "JPEG2000"
	elif extension == ".tif":
		drivername = "GTIFF"
	
	# Identification des tuiles à charger
	if path == "short":
		ls_files = [file for file in os.listdir(indir) if os.path.isfile(os.path.join(indir, file)) and file.endswith(extension)]
	elif path == "full":
		ls_files = [os.path.join(indir, file) for file in os.listdir(indir) if os.path.isfile(os.path.join(indir, file)) and file.endswith(extension)]
	
	return(sorted(ls_files))


def _zvalue_from_index(arr, ind):
	"""
		private helper function to work around the limitation of np.choose() by employing np.take()
		See: http://stackoverflow.com/a/32091712/4169585
		This is faster and more memory efficient than using the ogrid based solution with fancy indexing.
		
		arr: has to be a 3D array
		ind: has to be a 2D array containing values for z-indicies to take from arr
	"""
	
	# get number of rows and columns
	_,nR,nC = arr.shape
	
	# get linear indices and extract elements with np.take()
	idx = nC*nR*ind + nC*np.arange(nR)[:,None] + np.arange(nC)
	return np.take(arr, idx)


def p50_raster(ls_files, outdir, prefix, nodata_ori, ls_order_pref, ls_order_doy, obs_min=1):
	"""
		Permet la création d'une image matricielle contenant le 50e percentille d'une série d'images.
		Il est à noter que ls_files doit contenir des images dont les nuages ont été masqués (le plus possible).
		Une bonne partie code à propos de la sélection du 50e percentille vient du site suivant:
		https://krstn.eu/np.nanpercentile()-there-has-to-be-a-faster-way/
		
		ls_files:      liste des chemins d'accès aux images à charger
		outdir:        chemin d'accès au répertoire où seront exportés les fichiers de résultat 
		nodata_ori:    valeur originale de NoData qui sera convertie en 65535
		ls_order_pref: liste comprenant l'ordre de priorité d'utilisation des fichiers en entrée (liste d'entiers positifs)
		ls_order_doy:  liste comprenant les valeurs associées à l'élément correspondant de ls_order_pref (liste d'entiers positifs)
		obs_min:       nombre minimal d'observations valides pour conserver une valeur de p50 en sortie
	"""
	os.makedirs(outdir) if not os.path.exists(outdir) else None
	
	# Établissement et conversion de certaines valeurs de base
	nodata_new = 65535
	
	if max(ls_order_pref) == 0:
		# Remplacement des valeurs d'ordre de préférence pour les valeurs de dates
		# afin de les extraire plus facilement lors du calcul de la médiane sans préférence
		arr_order_pref = np.array(ls_order_doy).astype('uint16')
	else:
		arr_order_pref = np.array(ls_order_pref).astype('uint16')
		arr_argsort = np.argsort(arr_order_pref).astype('uint16')
		arr_order_doy = np.take(np.array(ls_order_doy).astype('uint16'), arr_argsort)
	
	# Validation que la longueur de ls_files est la même que ls_order_pref
	nb_files = len(ls_files)
	if nb_files != len(ls_order_pref) and ls_order is not None:
		sys.exit("Le nombre de fichiers en entrée ne correspond pas au nombre d'éléments dans la liste d'ordre.")
	
	# Extraction des informations de base de la première image (résolution, projection et géoréférencement)
	file = gdal.Open(ls_files[0])
	proj = file.GetProjection()
	georef = file.GetGeoTransform()
	sizeX = file.RasterXSize
	sizeY = file.RasterYSize
	resolution = int(georef[1])
	
	# Création préalable du stack en fonction du nombre d'images en entrée
	# À noter que la correspondance des axes de arr_stack est la suivante:
	#	axe 0: chaque position correspond à une image distincte
	#	axe 1: correspond à la rangée dans l'image (Y)
	#	axe 2: correspond à la colonne dans l'image (X)
	#	axe 3: position 0 -> valeur de pixel
	#		   position 1 -> ordre de classement selon la différence avec la date de préférence
	arr_stack = np.full(shape=(nb_files, sizeY, sizeX, 2), fill_value=nodata_new, dtype=np.uint16)
	
	# Remplissage du stack avec les images dont les nuages ont été masqués
	counter = 0
	for filepath in ls_files:
		file = gdal.Open(filepath)
		proj = file.GetProjection()
		georef = file.GetGeoTransform()
		band = file.GetRasterBand(1)
		arr_stack[counter,...,0] = band.ReadAsArray() # pas très beau... ce n'est certainement pas la façon de faire...
		arr_stack[counter,...,0][arr_stack[counter,...,0] == nodata_ori] = nodata_new # pas très beau, je devrais peut-être gérer différemment
		arr_stack[counter,...,1][arr_stack[counter,...,0] < nodata_new] = arr_order_pref[counter] # ajout de l'ordre sauf aux endroits de NoData
		counter += 1
	
	# Établissement du nombre de valeurs valides selon l'axe 0
	# S'il n'y a que 2 pixels valides sur une possibilité de 10, il est fort probable que la valeur retenue
	# ne soit pas la meilleure. Je devrais exporter la couche avant la ligne valid_obs[valid_obs == 0] = 1
	# afin de ne pas fausser les choses (il y aurait sinon des endroits NoData avec 1 valeur valide)
	valid_obs = np.sum(arr_stack != nodata_new, axis=0)[...,0]
	valid_obs_true = np.copy(valid_obs)
	
	# Indique une observation valide même lorsqu'il n'y en a pas, afin de permettre à une valeur de NoData d'être transférée
	valid_obs[valid_obs == 0] = 1
	
	# Tri selon l'axe 0 afin de déplacer les valeurs de NoData au bout du stack
	# tout en conservant la correspondance à travers l'axe 3
	# https://stackoverflow.com/questions/52953076/sorting-4d-numpy-array-but-keeping-one-axis-tied-together
	idx = np.argsort(arr_stack[...,0], axis=0).astype(np.uint16)
	arr_stack2 = np.take_along_axis(arr_stack, idx[...,None], axis=0)
	
	# Détermination de la position du quantile désiré (ici 50e percentile)
	quant = 50
	k_arr = (valid_obs - 1) * (quant / 100)
	f_arr = np.floor(k_arr).astype(np.uint16)
	c_arr = np.ceil(k_arr).astype(np.uint16)
	fc_equal_k_mask = f_arr == c_arr
	
	# Extraction et calcul de la valeur au 50e percentile
	floor_val = _zvalue_from_index(arr_stack2[...,0], f_arr) * (c_arr - k_arr)
	ceil_val = _zvalue_from_index(arr_stack2[...,0], c_arr) * (k_arr - f_arr)
	quant_arr = floor_val + ceil_val
	
	# Si floor == ceiling prendre la valeur de floor
	quant_arr[fc_equal_k_mask] = _zvalue_from_index(arr_stack2[...,0], k_arr.astype(np.int32))[fc_equal_k_mask]
	
	if max(ls_order_pref) == 0:
		date_arr = _zvalue_from_index(arr_stack2[...,1], f_arr)
		date_arr[date_arr == nodata_new] = 0
		quant_arr[quant_arr == nodata_new] = 0
		ls_export = [quant_arr.astype(np.uint16), date_arr, valid_obs_true]
	else:
		# Détermination des bornes supérieures et inférieures acceptables
		# Plage acceptable en absolu des valeurs de réflectance autour du p50. Sentinel-2 est en 12-bit, donc valeurs possibles de 0 à 4095
		p_span = 205 #environ 5%
		p_span = 150 #environ 4%
		quant_arr_min = quant_arr - p_span
		quant_arr_max = quant_arr + p_span
		
		# Mettre à nodata_new les quantiles dépassant les bornes
		# L'utilisation de bornes fait en sorte que s'il n'y a que deux observations valides, mais que leur
		# valeur est plus éloignée que 2 fois p_span aucune des deux observations ne sera finalement retenue
		arr_stack2[arr_stack2[...,0] < quant_arr_min] = nodata_new
		arr_stack2[arr_stack2[...,0] > quant_arr_max] = nodata_new
		
		# Tri selon l'axe 0 afin de mettre au premier rang les valeurs valides selon l'ordre de préférence
		idx = np.argsort(arr_stack2[...,1], axis=0).astype(np.uint16)
		arr_stack3 = np.take_along_axis(arr_stack2, idx[...,None], axis=0)
		
		# Mise à NoData des pixels où il y a une nombre d'observations valides inférieur au seuil établi
		if obs_min > 1:
			arr_stack3[0,...,0][valid_obs == obs_min] = 0
		
		# Remplacement des valeurs de NoData 65535 pour 0 afin d'éviter de faire planter np.take avec une valeur d'index invalide
		# puis remplacement des valeurs d'ordre par les valeurs de date correspondantes
		arr_stack3[0,...][arr_stack3[0,...,1] == nodata_new] = 0
		arr_stack4 = np.take(arr_order_doy, arr_stack3[0,...,1])
		
		ls_export = [arr_stack3[0,...,0], arr_stack4, valid_obs_true]
	
	# Exportation en GeoTIFF des résultats
	for ii, filename in [0, prefix+"_p50.tif"], [1, prefix+"_order_doy_"+str(resolution)+"m.tif"], [2, prefix+"_valid_obs.tif"]:
		driver = gdal.GetDriverByName("GTiff")
		fileout = driver.Create(os.path.join(outdir, filename), sizeX, sizeY, 1, gdal.GDT_UInt16, options=["COMPRESS=LZW"])
		fileout.GetRasterBand(1).WriteArray(ls_export[ii])
		fileout.GetRasterBand(1).SetNoDataValue(0) # Crée une certaine confusion avec valid_obs.tif où une valeur de 0 veut vraiment dire 0
		fileout.SetProjection(proj)
		fileout.SetGeoTransform(georef)
		fileout.FlushCache()
		fileout = None
	
	return(ls_export[1])


def id2raster(ls_files, outdir, prefix, ls_order_doy, arr_order_doy_fullraster):
	"""
		Script ne faisant que récupérer une couche d'ordre et une liste de fichiers
		puis sort un raster avec les pixels correspondant.
		
		ls_order_doy doit être de la même longueur que ls_files et doit être bien associées
		élément à élément (ls_order_doy[0] doit bien être lié à ls_files[0])
		Cette fonction assume que la valeur de NoData des fichiers est 0
	"""
	arr_order_doy = np.array(ls_order_doy).astype('uint16')
	
	# Extraction des informations de base de la première image (résolution, projection et géoréférencement)
	file = gdal.Open(ls_files[0])
	proj = file.GetProjection()
	georef = file.GetGeoTransform()
	sizeX = file.RasterXSize
	sizeY = file.RasterYSize
	
	# Création préalable du stack en fonction du nombre d'images en entrée
	nb_files = len(ls_files)
	arr_stack1 = np.zeros(shape=(nb_files, sizeY, sizeX, 2), dtype=np.uint16)
	
	# Remplissage du stack avec les images dont les nuages ont été masqués
	counter = 0
	for filepath in ls_files:
		file = gdal.Open(filepath)
		proj = file.GetProjection()
		georef = file.GetGeoTransform()
		band = file.GetRasterBand(1)
		arr_stack1[counter,...,0] = band.ReadAsArray()
		arr_stack1[counter,...,1] = arr_order_doy[counter]
		counter += 1
	
	# Différence entre les dates du stack et les dates sélectionnées
	arr_stack1[...,1] = arr_stack1[...,1] - arr_order_doy_fullraster
	
	# Tri des valeurs selon l'axe 0 afin de mettre au premier rang les valeurs correspondant aux dates sélectionnées
	idx = np.argsort(arr_stack1[...,1], axis=0).astype(np.uint16)
	arr_stack2 = np.take_along_axis(arr_stack1, idx[...,None], axis=0)
	
	# Exportation en GeoTIFF des valeurs retenues
	driver = gdal.GetDriverByName("GTiff")
	fileout = driver.Create(os.path.join(outdir, prefix+".tif"), sizeX, sizeY, 1, gdal.GDT_UInt16, options=["COMPRESS=LZW"])
	fileout.GetRasterBand(1).WriteArray(arr_stack2[0,...,0])
	fileout.GetRasterBand(1).SetNoDataValue(0)
	fileout.SetProjection(proj)
	fileout.SetGeoTransform(georef)
	fileout.FlushCache()
	fileout = None


def cloud_dispersion_index(inpath):
	"""
		Calcul d'un indice de dispersion des nuages à partir d'un masque de nuages épuré avec buffer
		
		Encore développement alpha
	"""
	inpath = r"F:\Tests_Sen2Cor\Multiproc_sen2cor\20180524T160231_mask_60m.tif"
	outpath = r"F:\Tests_Sen2Cor\Multiproc_sen2cor\20180524T160231_high_pass.tif"
	mask = load_raster(inpath, "GTiff")
	
	strel = np.array([[-1,-1,-1],
					  [-1, 8,-1],
					  [-1,-1,-1]])
	
	high_pass_mask = ndimage.filters.convolve(mask[0], strel)
	high_pass_mask[high_pass_mask > 5] = 0
	high_pass_mask[high_pass_mask > 0] = 1
	
	sum_cloud_fill = mask[0].sum()
	sum_cloud_edge = high_pass_mask.sum()
	
	dispersion_index = sum_cloud_edge/sum_cloud_fill
	
	# Exportation en GeoTIFF
	# Seulement pour la phase de tests, ce n'est pas pertinent d'exporter une couche
	driver = gdal.GetDriverByName("GTiff")
	fileout = driver.Create(outpath, high_pass_mask.shape[0], high_pass_mask.shape[1], 1, gdal.GDT_Byte, options=["COMPRESS=LZW"])
	fileout.GetRasterBand(1).WriteArray(high_pass_mask)
	fileout.GetRasterBand(1).SetNoDataValue(0)
	fileout.SetProjection(mask[1])
	fileout.SetGeoTransform(mask[2])
	fileout.FlushCache()
	fileout = None
	
	return(dispersion_index)



"""
	Fonctions wrapper
"""

def makemaskedbands(indir, outdir, date_start, date_end):
	"""
		Permet de créer les bandes masquées par les nuages.
		Des sécurités devraient être mises en place afin d'éviter
		de refaire le calcul pour une tuile déjà calculée (ajouter
		un paramètre overwrite)
		
		indir:      chemin d'accès au répertoire contenant les tuiles dont on veut masquer les nuages
		outdir:     chemin d'accès au répertoire de sortie pour les bandes masquées
		date_start: date début des images à masquer au format "YYYY-MM-DD"
		date_end:   date de fin des images à masquer au format "YYYY-MM-DD"
	"""
	
	#Lecture du CSV
	csv_path = os.path.join(indir, "db_sentinel2.csv")
	df = pd.read_csv(csv_path, parse_dates=["acquisition_date"], date_parser=lambda x: pd.to_datetime(x, format="%Y-%m-%d"))
	
	# Sélection des entrées comprises entre les deux dates
	# Possibilité d'ajouter une autre condition pour n'avoir qu'un des deux satellites à cause des problèmes de décalage spatial
	# ainsi que pour restreindre la sélection des images avec un pourcentage maximal de nuages estimés
	timestamp_start = pd.to_datetime(date_start, format="%Y-%m-%d")
	timestamp_end = pd.to_datetime(date_end, format="%Y-%m-%d")
	df_subset = df.loc[(df["acquisition_date"] >= timestamp_start) & (df["acquisition_date"] <= timestamp_end)]
	
	ls_filename = df_subset["filename"].tolist()
	
	for filename in ls_filename:
		dir_main = os.path.join(indir, filename + ".SAFE")	
		path_XML = os.path.join(dir_main, "MTD_MSIL1C.xml")
		str_path = ET.parse(path_XML).getroot()[0][0][11][0][0][0].text[:-27]
		full_path = os.path.join(dir_main, str_path)
		
		outdir_filename = os.path.join(outdir, filename)
		os.makedirs(outdir_filename) if not os.path.exists(outdir_filename) else None
		outdir_intermediate = os.path.join(outdir_filename, "Intermediate")
		os.makedirs(outdir_intermediate) if not os.path.exists(outdir_intermediate) else None
		
		create_mask(full_path, outdir_intermediate)
		prefix_mask = filename[38:45] + filename[11:26]
		
		for str_band in ["B02", "B03", "B04", "B08"]:
			band = apply_mask(os.path.join(full_path, prefix_mask + "_" + str_band + ".jp2"), os.path.join(outdir_intermediate, prefix_mask + "_mask_10m.tif"))
			rewrite_band(band, os.path.join(outdir_filename, prefix_mask + "_" + str_band + "_masked.tif"), 0)
		
		for str_band in ["B05", "B06", "B07", "B8A", "B11", "B12"]:
			band = apply_mask(os.path.join(full_path, prefix_mask + "_" + str_band + ".jp2"), os.path.join(outdir_intermediate, prefix_mask + "_mask_20m.tif"))
			rewrite_band(band, os.path.join(outdir_filename, prefix_mask + "_" + str_band + "_masked.tif"), 0)


def makep50(indir, outdir, tileid, doy_pref, nodata_ori=0):
	"""
		Produit la matrice du 50e percentille à partir d'une série d'images msaquées
		Éventuellement, je devrais demander de nouveau une sélection de dates et de tuiles
		afin de rendre cette fonction complètement indépendante de makemaskedbands().
		J'utiliserais alors un fichier CSV pour lire les informations pertinentes.
		
		indir:      chemin d'accès au répertoire contenant les tuiles dont les nuages sont masqués
		outdir:     chemin d'accès au répertoire de sortie pour les TIF liés au p50
		tileid:     ID de la tuile à traiter au format "T18TUT". Paramètre qui pourrait être retiré,
		            car je peux l'extraire des noms de dossier
		doy_pref:   jour de l'année correspondant à la journée de préférence
		nodata_ori: valeur de NoData originale (devrait être 0)
	"""
	
	band_p50 = "B05" #Pour le moment, le calcul se fera toujours avec la bande 5
	customid = "pref_" + str(doy_pref)
	prefix_p50 = tileid + "_" + customid + "_" + band_p50
	ls_folders = [folder for folder in os.listdir(indir) if not os.path.isfile(os.path.join(indir, folder))]
	
	ls_files = []
	for folder in ls_folders:
		# Chemin d'accès complet pour la bande 5 qui servira aux comparaisons inter-scènes
		full_path = os.path.join(indir, folder, tileid + "_" + folder[11:26] + "_" + band_p50 + "_masked.tif")
		ls_files.append(full_path)
	
	# Création de la liste des dates (DOY) à partir des noms de fichiers
	ls_order_doy = list_order_doy(ls_files)
	
	if doy_pref == 0:
		# Permet de n'avoir aucune préférence de date, la valeur la plus près du p50 est simplement prise.
		# S'il y a un nombre pair de valeurs valides, la valeur inférieure est sélectionnée.
		ls_order_pref = [0 for order in ls_order_doy]
	else:
		ls_order_pref = list_doy_pref(ls_order_doy, doy_pref)
	
	p50_raster(ls_files, outdir, prefix_p50, nodata_ori, ls_order_pref, ls_order_doy)
	
	# Production du raster de dates à une résolution de 10m
	path_order_doy_20m = os.path.join(outdir, prefix_p50 + "_order_doy_20m.tif")
	path_order_doy_10m = os.path.join(outdir, prefix_p50 + "_order_doy_10m.tif")
	subprocess.run(" ".join(["gdal_translate -tr 10 10 -r nearest", path_order_doy_20m, path_order_doy_10m]))
	
	# Production des p50 des autres bandes à 10m et 20m
	arr_order = load_raster(path_order_doy_10m, "GTiff")[0]
	for band_p50 in ["B02","B03","B04","B08"]:
		prefix_p50 = prefix_p50[:-3] + band_p50
		ls_files = [file.replace(file[-14:], band_p50 + "_masked.tif") for file in ls_files]
		id2raster(ls_files, outdir, prefix_p50 + "_p50", ls_order_doy, arr_order)
	
	arr_order = load_raster(path_order_doy_20m, "GTiff")[0]
	for band_p50 in ["B06","B07","B8A","B11","B12"]:
		prefix_p50 = prefix_p50[:-3] + band_p50
		ls_files = [file.replace(file[-14:], band_p50 + "_masked.tif") for file in ls_files]
		id2raster(ls_files, outdir, prefix_p50 + "_p50", ls_order_doy, arr_order)


def sen2cor(safe, outdir=None):
	sen2cor_path = r"C:\Mrnmicro\Applic\Sen2Cor-02.05.05-win64\L2A_Process.bat"
	subprocess.run(sen2cor_path + " " + safe)
	
	if outdir is not None:
		shutil.move(safe, os.path.join(outdir, os.path.basename(safe)))


def mp_sen2cor(ls_safe, outdir=None):
	import multiprocessing as mp
	from functools import partial
	nb_cores = 4
	
	pool = mp.Pool(nb_cores)
	sen2cor_partial = partial(sen2cor, outdir=outdir)
	pool.map_async(sen2cor_partial, ls_safe)
	pool.close()


def create_vrt(dir_gdal, outdir, indir, basename, level, resolution, ls_bands):
	# Création d'un VRT dans le répertoire racine pour l'instant
	
	str_resolution = ""
	if level == "L2A":
		indir = indir[:-3] + str(resolution) + "m"
		str_resolution = "_" + str(resolution) + "m"
	
	str_bands = "-".join(ls_bands)
	path_vrt = os.path.join(outdir, basename + "_" + str_bands + "_" + level + ".vrt")
	
	ls_path_files = [os.path.join(indir, basename + "_B" + band + str_resolution + ".jp2") for band in ls_bands]
	str_path_files = " ".join(ls_path_files)
	
	subprocess.run(" ".join([os.path.join(dir_gdal, "gdalbuildvrt.exe"), "-separate --config GDAL_DATA", gdal_data, path_vrt, str_path_files]))


def extract_jp2_relativerootpath(indir):
	# Permet d'extraire le chemin d'accès au répertoire où se trouve les JP2 à l'intérieur d'un .SAFE en lisant le XML
	# La sortie est composée d'une liste à deux éléments, soit le nom du JP2 sans l'extention et le chemin
	# d'accès au répertoire de ce JP2.
	from lxml import etree, html
	import os
	
	xml_file = [file for file in os.listdir(indir) if file.startswith("MTD")][0]
	
	tree = etree.parse(os.path.join(indir, xml_file))
	internal_path = tree.getroot()[0][0][11][0][0][0]
	str_temp = etree.tostring(internal_path).decode("utf-8")
	start = str_temp.find(">") + 1
	end = str_temp.find("<", start)
	ls_terms = str_temp[start:end].split("/")
	end_basename = ls_terms[-1:][0].find("_B0")
	relativerootpath = [xml_file[7:-4], ls_terms[-1:][0][:end_basename], os.path.join(*ls_terms[:-1])]
	
	return(relativerootpath)