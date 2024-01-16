
# coding: utf-8

# In[28]:


import numpy as np
import pandas as pd
import os
pd.options.mode.chained_assignment = None


# In[14]:


# Reads fbp_lookup_table.csv and creates dictionaries for the fuel types and cells' colors
def Dictionary(filename):
    aux = 1
    file = open(filename, "r") 
    row = {}
    colors = {} 
    all = {}
    
    # Read file and save colors and ftypes dictionaries
    for line in file: 
        if aux > 1:
            aux +=1
            line = line.replace("-","")
            line = line.replace("\n","")
            line = line.replace("No","NF")
            line = line.split(",")
            
            if line[3][0:3] in ["O1a", "O1b"]:
                row[line[0]] = line[3][0:3]
            else:
                row[line[0]] = line[3][0:2]
            colors[line[0]] = (float(line[4]) / 255.0, 
                               float(line[5]) / 255.0,
                               float(line[6]) / 255.0,
                               1.0)
            all[line[0]] = line
    
        if aux == 1:
            aux +=1
            
    return row, colors


# In[4]:


# Reads the ASCII file with the forest grid structure and returns an array with all the cells and grid dimensions nxm
# Modified Feb 2018 by DLW to read the forest params (e.g. cell size) as well
def ForestGrid(filename, Dictionary):
    with open(filename, "r") as f:
        filelines = f.readlines()

    line = filelines[4].replace("\n","")
    parts = line.split()
    
    if parts[0] != "cellsize":
        print ("line=",line)
        raise RuntimeError("Expected cellsize on line 5 of "+ filename)
    cellsize = float(parts[1])
    
    cells = 0
    row = 1
    trows = 0 
    tcols = 0
    gridcell1 = []
    gridcell2 = []
    gridcell3 = []
    gridcell4 = []
    grid = []
    grid2 = []
    
    # Read the ASCII file with the grid structure
    for row in range(6, len(filelines)):
        line = filelines[row]
        line = line.replace("\n","")
        line = ' '.join(line.split())
        line = line.split(" ")
        #print(line)
        
        
        for c in line: #range(0,len(line)-1):
            if c not in Dictionary.keys():
                gridcell1.append("NData")
                gridcell2.append("NData")
                gridcell3.append("NData")
                gridcell4.append("NData")
            else:
                gridcell1.append(c)
                gridcell2.append(Dictionary[c])
                gridcell3.append(int(c))
                gridcell4.append(Dictionary[c])
            tcols = np.max([tcols,len(line)])

        grid.append(gridcell1)
        grid2.append(gridcell2)
        gridcell1 = []
        gridcell2 = []
    
    # Adjacent list of dictionaries and Cells coordinates
    CoordCells = np.empty([len(grid)*(tcols), 2]).astype(int)
    n = 1
    tcols += 1
    
    return gridcell3, gridcell4, len(grid), tcols-1, cellsize


# In[5]:


# Reads the ASCII files with forest data elevation, saz, slope, and (future) curing degree and returns arrays
# with values
def DataGrids(InFolder, NCells):
    filenames = ["elevation.asc", "saz.asc", "slope.asc", "cur.asc"]
    Elevation =  np.full(NCells, np.nan)
    SAZ = np.full(NCells, np.nan)
    PS = np.full(NCells, np.nan)
    Curing = np.full(NCells, np.nan)
    
    for name in filenames:
        ff = os.path.join(InFolder, name)
        if os.path.isfile(ff) == True:
            aux = 0
            with open(ff, "r") as f:
                filelines = f.readlines()

                line = filelines[4].replace("\n","")
                parts = line.split()

                if parts[0] != "cellsize":
                    print ("line=",line)
                    raise RuntimeError("Expected cellsize on line 5 of "+ ff)
                cellsize = float(parts[1])

                row = 1

                # Read the ASCII file with the grid structure
                for row in range(6, len(filelines)):
                    line = filelines[row]
                    line = line.replace("\n","")
                    line = ' '.join(line.split())
                    line = line.split(" ")
                    #print(line)


                    for c in line: 
                        if name == "elevation.asc":
                            Elevation[aux] = float(c)
                            aux += 1
                        if name == "saz.asc":
                            SAZ[aux] = float(c)
                            aux += 1
                        if name == "slope.asc":
                            PS[aux] = float(c)
                            aux += 1
                        if name == "curing.asc":
                            Curing[aux] = float(c)
                            aux += 1

        else:
            print("   No", name, "file, filling with NaN")
            
    return Elevation, SAZ, PS, Curing


# In[26]:


# Generates the Data.dat file (csv) from all data files (ready for the simulator)
def GenerateDat(GFuelType, Elevation, PS, SAZ, Curing, InFolder):
    # DF columns
    Columns = ["fueltype", "mon", "jd", "m", "jd_min", 
               "lat", "lon", "elev", "ffmc", "ws", "waz", 
               "bui", "ps", "saz", "pc", "pdf", "gfl", 
               "cur", "time"]
    
    # GFL dictionary
    GFLD = {"c1": 0.75, "c2": 0.8, "c3": 1.15, "c4": 1.2, "c5":1.2, "c6":1.2, "c7":1.2, 
            "d1": np.nan, "d2": np.nan, 
            "s1":np.nan, "s2": np.nan, "s3": np.nan, 
            "o1a":0.35, "o1b":0.35, 
            "m1": np.nan, "m2": np.nan, "m3":np.nan, "m4":np.nan, "nf":np.nan,
            "m1_5": 0.1, "m1_10": 0.2,  "m1_15": 0.3, "m1_20": 0.4, "m1_25": 0.5, "m1_30": 0.6, 
            "m1_35": 0.7, "m1_40": 0.8, "m1_45": 0.8, "m1_50": 0.8, "m1_55": 0.8, "m1_60": 0.8, 
            "m1_65": 1.0, "m1_70": 1.0, "m1_75": 1.0, "m1_80": 1.0, "m1_85": 1.0, "m1_90": 1.0, "m1_95": 1.0}
    
    # PDF dictionary
    PDFD ={"m3_5": 5,"m3_10": 10,"m3_15": 15,"m3_20": 20,"m3_25": 25,"m3_30": 30,"m3_35": 35,"m3_40": 40,"m3_45": 45,"m3_50": 50,
           "m3_55": 55,"m3_60": 60,"m3_65": 65,"m3_70": 70,"m3_75": 75,"m3_80": 80,"m3_85": 85,"m3_90": 90,"m3_95": 95,"m4_5": 5,
           "m4_10": 10,"m4_15": 15,"m4_20": 20,"m4_25": 25,"m4_30": 30,"m4_35": 35,"m4_40": 40,"m4_45": 45,"m4_50": 50,"m4_55": 55,
           "m4_60": 60,"m4_65": 65,"m4_70": 70,"m4_75": 75,"m4_80": 80,"m4_85": 85,"m4_90": 90,"m4_95": 95,"m3m4_5": 5,"m3m4_10": 10,
           "m3m4_15": 15,"m3m4_20": 20,"m3m4_25": 25,"m3m4_30": 30,"m3m4_35": 35,"m3m4_40": 40,"m3m4_45": 45,"m3m4_50": 50,"m3m4_55": 55,
           "m3m4_60": 60,"m3m4_65": 65,"m3m4_70": 70,"m3m4_75": 75,"m3m4_80": 80,"m3m4_85": 85,"m3m4_90": 90,"m3m4_95": 95}
    
    # PCD dictionary
    PCD = {"m1_5":5,"m1_10":10,"m1_15":15,"m1_20":20,"m1_25":25,"m1_30":30,"m1_35":35,"m1_40":40,"m1_45":45,
           "m1_50":50,"m1_55":55,"m1_60":60,"m1_65":65,"m1_70":70,"m1_75":75,"m1_80":80,"m1_85":85,"m1_90":90,
           "m1_95":95,"m2_5":5,"m2_10":10,"m2_15":15,"m2_20":20,"m2_25":25,"m2_30":30,"m2_35":35,"m2_40":40,
           "m2_45":45,"m2_50":50,"m2_55":55,"m2_60":60,"m2_65":65,"m2_70":70,"m2_75":75,"m2_80":80,"m2_85":85,
           "m2_90":90,"m2_95":95,"m1m2_5":5,"m1m2_10":10,"m1m2_15":15,"m1m2_20":20,"m1m2_25":25,"m1m2_30":30,
           "m1m2_35":35,"m1m2_40":40,"m1m2_45":45,"m1m2_50":50,"m1m2_55":55,"m1m2_60":60,"m1m2_65":65,"m1m2_70":70,
           "m1m2_75":75,"m1m2_80":80,"m1m2_85":85,"m1m2_90":90,"m1m2_95":95}
    
    DF = pd.DataFrame(columns=Columns)
    DF["fueltype"] = [x.lower() for x in GFuelType]
    DF["elev"] = Elevation
    DF["ps"] = PS
    DF["saz"] = SAZ
    DF["time"] = np.zeros(len(GFuelType)).astype(int) + 20
    DF["lat"] = np.zeros(len(GFuelType)) + 51.621244
    DF["lon"] = np.zeros(len(GFuelType)).astype(int) - 115.608378
    
    # If no Curing file (or all NaN) check special cases for grass type O1 (default cur = 60)
    if np.sum(np.isnan(Curing)) == len(Curing):
        DF["cur"][DF.fueltype == "o1a"] = 60.0
        DF["cur"][DF.fueltype == "o1b"] = 60.0
        
    # Populate gfl
    for i in GFLD.keys():
        DF["gfl"][DF.fueltype == i] = GFLD[i]
        
    # Populate pdf
    for i in PDFD.keys():
        DF["pdf"][DF.fueltype == i] = PDFD[i]
    
    # Populate pc
    for i in PCD.keys():
        DF["pc"][DF.fueltype == i] = PCD[i]
    
    
    filename = os.path.join(InFolder, "Data.dat")
    print(filename)
    DF.to_csv(path_or_buf=filename, index=False, index_label=False, header=False)
    
    return DF

    


# In[21]:


def GenDataFile(InFolder):
    FBPlookup = os.path.join(InFolder, "fbp_lookup_table.csv")
    FBPDict, ColorsDict =  Dictionary(FBPlookup)
    
    FGrid = os.path.join(InFolder, "Forest.asc")
    GFuelTypeN, GFuelType, Rows, Cols, CellSide = ForestGrid(FGrid, FBPDict)
    
    NCells = len(GFuelType)
    Elevation, SAZ, PS, Curing = DataGrids(InFolder, NCells)
    GenerateDat(GFuelType, Elevation, PS, SAZ, Curing, InFolder)


