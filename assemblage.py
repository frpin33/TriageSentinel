
dataLocation = "\\\\Sef1271a\\f1271i\\TeleDiff\\Commun\\a-Images-Satellites\\SENTINEL"

def recherche():

    if os.path.exists(tilePath) :
    tileName = tileNumber + ".txt"
    tilePath = os.path.join(dataLocation, 'Information', tileName)
    
    
    listObj = pickle.load(open(tilePath,'rb'))
    
    newList = [] 
    startDate = startDate
    endDate = endDate

    for obj in listObj :
        dirName = obj.pathSAFE
        param = dirName.split('_')
        date = param[2].split('T')


        qDate = QtCore.QDate.fromString(date[0],"yyyyMMdd")

        if qDate > startDate and qDate < endDate :
            newList.append(obj)
    
        
    if newList :

        nbObj = len(newList)
        
        zoneFilter = zoneFilter
        if zoneFilter :
            listTuple = []

            divFac = len(zoneFilter)
        
            for obj in newList : 
                pCloud = 0
                for num in zoneFilter :
                    val = obj.clearPercent[num-1]
                    pCloud += val
                pCloud = pCloud/divFac
            listTuple.append((obj,pCloud))

            listTuple.sort(reverse=True, key = lambda tup: tup[1])
            newOrder = []
            for tup in listTuple : 
                newOrder.append(tup[0])
            newList = newOrder
        
        

def getBestTileGroup(listTile, startDate, endDate) :
    #Pour chaque tuile de la liste, trouver les dates,
    #Est ce que la même date est présente au moins 80%? 90%? si oui = Faucher
    #parmis les fauchers il faut trouver la meilleure
    for tile in listTile : 

