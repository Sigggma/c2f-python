
# coding: utf-8


# This has code and structures to interface with FBP.
# Based on  FBP-LINE-newest.py
# Original Author (FBP-LINE-newest.py): David L. Woodruff, January 2017
# Modified by: Cristobal Pais, April 2018 
# CAUTION: Beware of DOS versus UNIX file formats for the input data.
# (Check the first string read by the panda for a strange leading char.)

# NOTE: the main FBP input structure
# in the calling code (often called df) is a panda data frame.

# Importations
import pandas as pd
from argparse import ArgumentParser
import pprint as pp
import ctypes

# Global Elements
soname = "FBPfunc5NODEBUG.so"
try:
    lib = ctypes.cdll.LoadLibrary(soname)
except:
    raise RuntimeError("Could not load the library=" + soname)

FieldsInFileOrder = [('fueltype', ctypes.c_char*4), 
                    ('mon', ctypes.c_int),
                    ('jd', ctypes.c_int),
                    ('m', ctypes.c_int),
                    ('jd_min', ctypes.c_int),
                    ('lat', ctypes.c_float),
                    ('lon', ctypes.c_float),
                    ('elev', ctypes.c_int),
                    ('ffmc', ctypes.c_float),
                    ('ws', ctypes.c_float),
                    ('waz', ctypes.c_int),
                    ('bui', ctypes.c_float),
                    ('ps', ctypes.c_int),
                    ('saz', ctypes.c_int),
                    ('pc', ctypes.c_int),
                    ('pdf', ctypes.c_int),
                    ('gfl', ctypes.c_float),
                    ('cur', ctypes.c_int),
                    ('time', ctypes.c_int)]
                    
month = [ 0,31,59,90,120,151,181,212,243,273,304,334]

# SubClasses and functions
class inputs(ctypes.Structure):
    _fields_ = [('fueltype', ctypes.c_char*4),
                ('ffmc', ctypes.c_float),
                ('ws', ctypes.c_float),
                ('gfl', ctypes.c_float),
                ('bui', ctypes.c_float),
                ('lat', ctypes.c_float),
                ('lon', ctypes.c_float),
                ('time', ctypes.c_int),
                ('pattern', ctypes.c_int),
                ('mon', ctypes.c_int),
                ('jd', ctypes.c_int),
                ('jd_min', ctypes.c_int),
                ('waz', ctypes.c_int),
                ('ps', ctypes.c_int),
                ('saz', ctypes.c_int),
                ('pc', ctypes.c_int),
                ('pdf', ctypes.c_int),
                ('cur', ctypes.c_int),
                ('elev', ctypes.c_int),
                ('hour', ctypes.c_int),
                ('hourly', ctypes.c_int)]

class fire_struc(ctypes.Structure):
    _fields_ = [('ros', ctypes.c_float),
                ('dist', ctypes.c_float),
                ('rost', ctypes.c_float),
                ('cfb', ctypes.c_float),
                ('fc', ctypes.c_float),
                ('cfc', ctypes.c_float),
                ('time', ctypes.c_float),
                ('rss', ctypes.c_float),
                ('isi', ctypes.c_float), 
                ('fd', ctypes.c_char),
                ('fi', ctypes.c_double)]

class main_outs(ctypes.Structure):
    _fields_ = [('hffmc', ctypes.c_float),
                ('sfc', ctypes.c_float),
                ('csi', ctypes.c_float),
                ('rso', ctypes.c_float),
                ('fmc', ctypes.c_float),
                ('sfi', ctypes.c_float),
                ('rss', ctypes.c_float),
                ('isi', ctypes.c_float),
                ('be', ctypes.c_float),
                ('sf', ctypes.c_float),
                ('raz', ctypes.c_float),
                ('wsv', ctypes.c_float),
                ('ff', ctypes.c_float), 
                ('jd_min', ctypes.c_int), 
                ('jd', ctypes.c_int), 
                ('covertype', ctypes.c_char)] 

class snd_outs(ctypes.Structure):
    _fields_ = [('lb', ctypes.c_float),
                ('area', ctypes.c_float),
                ('perm', ctypes.c_float),
                ('pgr', ctypes.c_float),
                ('lbt', ctypes.c_float)]

#==============================

'''
Prints-out info from the instance dataframe
Returns        void

Inputs:
inp            dataframe
'''
def inputs_pprint(inp):
    # print the input structure
    # Not really very pretty
    print("Dump of inputs structure")
    print('fueltype=', str(inp.fueltype))
    print('ffmc=', str(inp.ffmc))
    print('ws=', str(inp.ws))
    print('gfl=', str(inp.gfl))
    print('bui=', str(inp.bui))
    print('lat=', str(inp.lat))
    print('lon=', str(inp.lon))
    print('time=', str(inp.time))
    print('pattern=', str(inp.pattern))
    print('mon=', str(inp.mon))
    print('jd=', str(inp.jd))
    print('jd_min=', str(inp.jd_min))
    print('waz=', str(inp.waz))
    print('ps=', str(inp.ps))
    print('saz=', str(inp.saz))
    print('pc=', str(inp.pc))
    print('pdf=', str(inp.pdf))
    print('cur=', str(inp.cur))
    print('elev=', str(inp.elev))
    print('hour=', str(inp.hour))
    print('hourly=', str(inp.hourly))
    print("End of inputs structure")

'''
Prints-out info from the instance dataframe
Returns        void

Inputs:
main           dataframe
'''
def main_outs_pprint(main):
    print("Begin dump of main outputs")
    print('hffmc=', str(main.hffmc)),
    print('sfc=', str(main.sfc)),
    print('csi=', str(main.csi))
    print('rso=', str(main.rso))
    print('fmc=', str(main.fmc))
    print('sfi=', str(main.sfi))
    print('rss=', str(main.rss))
    print('isi=', str(main.isi))
    print('be=', str(main.be))
    print('sf=', str(main.sf))
    print('raz=', str(main.raz))
    print('wsv=', str(main.wsv))
    print('ff=', str(main.ff))
    print('jd_min', str(main.jd_min))
    print('jd=', str(main.jd))
    print('covertype=', str(main.covertype))
    print ("End dump of main outputs")

'''
Prints-out info from the instance dataframe
Returns        void

Inputs:
struct         dataframe
'''
def fire_outs_pprint(struct):
    print('ros=', str(struct.ros))
    print('dist=', str(struct.dist))
    print('rost=', str(struct.rost))
    print('cfb=', str(struct.cfb))
    print('fc=', str(struct.fc))
    print('cfc=', str(struct.cfc))
    print('time=', str(struct.time))
    print('rss=', str(struct.rss))
    print('isi=', str(struct.isi),)
    print('fd=', str(struct.fd))
    print('fi=', str(struct.fi))

'''
Prints-out info from the instance dataframe
Returns        void

Inputs:
sndstruct      dataframe
'''
def secondary_outs_pprint(sndstruct):
    print('lb=', str(sndstruct.lb))
    print('area=', str(sndstruct.area))
    print('perm=', str(sndstruct.perm))
    print('pgr=', str(sndstruct.pgr))
    print('lbt=', str(sndstruct.lbt))

#============================================

'''
Read csv filename and generates a dataframe
Returns        Dataframe

Inputs:
filename       string
'''
def inputData(filename):
    FieldsInFileOrder = [('fueltype', ctypes.c_char*4), 
                        ('mon', ctypes.c_int),
                        ('jd', ctypes.c_int),
                        ('m', ctypes.c_int),
                        ('jd_min', ctypes.c_int),
                        ('lat', ctypes.c_float),
                        ('lon', ctypes.c_float),
                        ('elev', ctypes.c_int),
                        ('ffmc', ctypes.c_float),
                        ('ws', ctypes.c_float),
                        ('waz', ctypes.c_int),
                        ('bui', ctypes.c_float),
                        ('ps', ctypes.c_int),
                        ('saz', ctypes.c_int),
                        ('pc', ctypes.c_int),
                        ('pdf', ctypes.c_int),
                        ('gfl', ctypes.c_float),
                        ('cur', ctypes.c_int),
                        ('time', ctypes.c_int)]
                    
    ColNames = []
    
    for i in FieldsInFileOrder:
        na, ty = i
        ColNames.append(na)
              
    if filename is None:
        raise RuntimeError("The --input-file-name option is required.")
    try:
        df = pd.read_csv(filename, index_col=False, header=None, names=ColNames, encoding='utf-8')
    except:
        raise RuntimeError("Could not read csv file="+filename)
        
    return df
    
    

    
    
'''
Specific row is copied to dataframe
Returns        Dataframe

Inputs:
index          int
row            int
'''
def CopyRowtoData(index, row):
    # Copy to the data struct (bad name) with modifictions.
    # Use LastOne to truncate the copy.
    global FieldsInFileOrder
    kwargs = {}
    for i in FieldsInFileOrder:
        na, ty = i
        val = row[na]
        if str(val) == "nan":
            val = 0
        if ty == ctypes.c_float: 
            val = float(val)
        elif ty == ctypes.c_int: 
            val = int(val)
        elif ty == ctypes.c_double: 
            val = double(val)
        else:
            val = val.strip()
            if len(val) == 2:
                val = val + ' '
            val = str.encode(str(val))
        kwargs[na] = val
    data = inputs(**kwargs)
    
    # modifications; comments are from the c code
    #  data.waz+=180;if(data.waz>=360)data.waz-=360;
    data.waz += 180
    if data.waz >= 360:
        data.waz -= 360
    # if(m!=0) data.jd=month[m-1]+d;
    # else data.jd=0;
    if data.m != 0:
        data.jd = month[data.m-1] + data.jd
    else:
        data.ja = 0
    # m=(int)(var[3]); d=(int)(var[4]);   /* this is minimum foliar moisture date*/
    # if(m>0) data.jd_min=month[m-1]+d;   /* only use it if it is EXPLICITLY specified*/
    if data.mon > 0:
        data.jd_min = month[data.m-1] + data.jd_min
    #   data.pattern=1;   /* point source ignition...so acceleration is included */
    data.pattern = 1
    return data
    
    

'''
Calculates 4 ROSs objects for all cells inside the forest, based on weather and forest characteristics
Returns    vector of dataframes/objects

Inputs:
df         dataframe
coef_ptr   pointer
'''
# Returns 4 objects for ROS for all cells
def CalculateAll(df, coef_ptr):
    testcase = 0  # for output
    for index, row in df.iterrows():
        testcase += 1
        datastruct = CopyRowtoData(index, row)
        
        # to be on the safe side, make new output receivers each time through
        mainstruct = main_outs()
        sndstruct = snd_outs()
        headstruct = fire_struc()
        backstruct = fire_struc()
        flankstruct = fire_struc()
        
        # byref seems like the opposite of what it is...
        dataptr = ctypes.byref(datastruct)
        mainptr = ctypes.byref(mainstruct)
        sndptr = ctypes.byref(sndstruct)
        headptr = ctypes.byref(headstruct)
        flankptr = ctypes.byref(flankstruct)
        backptr = ctypes.byref(backstruct)
        lib.calculate(dataptr,
                      coef_ptr,
                      mainptr,
                      sndptr,
                      headptr,
                      flankptr,
                      backptr);
        
        print("Test Case %d\n\n" % testcase)
        inputs_pprint(datastruct)    
        main_outs_pprint(mainstruct)
        
        # Modification October 2017: return all relevant objects
        return mainstruct, headstruct, flankstruct, backstruct

'''
Calculates 4 ROSs objects for a specific cell inside the forest, based on weather and cell characteristics
Returns    vector of dataframes/objects

Inputs:
df         dataframe
coef_ptr   pointer
'''
# Returns 4 objects for ROS for a specific cell
def CalculateOne(df,coef_ptr,ncel,verbose=False):
    df = df.iloc[ncel-1:ncel]
    for index, row in df.iterrows():
        datastruct = CopyRowtoData(index, row)
        
        # to be on the safe side, make new output receivers each time through
        mainstruct = main_outs()
        sndstruct = snd_outs()
        headstruct = fire_struc()
        backstruct = fire_struc()
        flankstruct = fire_struc()
        
        # byref seems like the opposite of what it is...
        dataptr = ctypes.byref(datastruct)
        mainptr = ctypes.byref(mainstruct)
        sndptr = ctypes.byref(sndstruct)
        headptr = ctypes.byref(headstruct)
        flankptr = ctypes.byref(flankstruct)
        backptr = ctypes.byref(backstruct)
        lib.calculate(dataptr,
                      coef_ptr,
                      mainptr,
                      sndptr,
                      headptr,
                      flankptr,
                      backptr);
        
        if verbose == True:
            print("Test Case %d\n\n" % ncel)
            inputs_pprint(datastruct)    
            main_outs_pprint(mainstruct)
            print("\nHead")
            fire_outs_pprint(headstruct)
            print("\nFlank")
            fire_outs_pprint(flankstruct)
            print("\nBack")
            fire_outs_pprint(backstruct)
            print("\n Secondary Outputs")
            secondary_outs_pprint(sndstruct)
        
        # All 4 objects needed for RAZ (mainstruct) and ROS (rest)
        return mainstruct, headstruct, flankstruct, backstruct

