#delete all NIR cut rgb cut pour 2017

#le traitement de ce soir devrait créer tous les fichiers

path = '\\\\Sef1271a\\f1271i\\TeleDiff\\Commun\\a-Images-Satellites\\SENTINEL\\2017'

listname = ['_RGB.tif','_NIR.tif']
#print(dic)
name2del = {'_RGB.tif':'_RGB_Cut.tif', '_NIR.tif': '_NIR_Cut.tif'}
import os, json
from PIL import Image

Image.MAX_IMAGE_PIXELS = 1000000000 

i = os.listdir(path) 
dic = []
''' '''
for safe in os.listdir(path) :
    #f = os.path.join(path, 'S2A_MSIL1C_20171009T161341_N0205_R140_T18UUU_20171009T161342.SAFE')
    filePath = os.path.join(path,safe)
    dirName = os.path.basename(filePath) 
    paramOfName = dirName.split('_')
    count = 0
    for item in listname :
        picname = paramOfName[-2] + '_' + paramOfName[-5] + item
        fullpath = os.path.join(filePath,picname)
        if os.path.exists(fullpath) :

            img = Image.open(fullpath)
            try : 
                img.seek(2)
                histo = img.histogram()
            except: 
                if filePath not in dic : dic.append(filePath)
    


with open('U:\\JSONPath.json', 'w') as f : 
    json.dump(dic, f)
''' '''
with open('U:\JSONPath.json') as f : 
    dictParam = json.load(f)

#print(dic)
#name2del = {'_RGB.tif':'_RGB_Cut.tif', '_NIR.tif': '_NIR_Cut.tif'}

for item in dictParam :
    dirName = os.path.basename(item) 
    paramOfName = dirName.split('_')
    for name, cut in name2del.items() :
        picname = paramOfName[-2] + '_' + paramOfName[-5] + name
        fullpath = os.path.join(item,picname)
        if os.path.exists(fullpath) :
            try : 
                os.remove(fullpath)
                cutname = paramOfName[-2] + '_' + paramOfName[-5] + cut
                cutpath = os.path.join(item,cutname)
                if os.path.exists(cutpath) : os.remove(cutpath)

            except : print(name)
