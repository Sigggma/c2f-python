
# coding: utf-8


# General importations
import os
import shutil
import numpy as np
from argparse import ArgumentParser
from numpy import random as npr


# Classes importations
import ReadDataPrometheus
import Plot
import WeatherFBP
import Forest


# In[3]:


'''
Returns       args object (containing command line arguments)

Inputs:
'''
def ParseInputs():
    parser = ArgumentParser()

    parser.add_argument("--input-forest",
                        help="The name of the csv file that contains the forest grid data",
                        dest="input_forest",
                        type=str,
                        default=None)                

    parser.add_argument("--input-fpblookup",
                        help="The name of the csv file that contains the forest grid data",
                        dest="input_fbplookup",
                        type=str,
                        default=None) 

    parser.add_argument("--input-instance-folder",
                        help="The path to the folder contains all the files for the simulation",
                        dest="input_folder",
                        type=str,
                        default=None)                

    parser.add_argument("--output-folder",
                        help="The path to the folder for simulation output files",
                        dest="output_folder",
                        type=str,
                        default=None)                

    parser.add_argument("--seed",
                        help="Seed for random numbers (default is None, which randomizes)",
                        dest="seed",
                        type=int,
                        default=None)        

    parser.add_argument("--weather",
                        help="The 'type' of weather: constant, random, rows (default rows)",
                        dest="input_weather",
                        type=str,
                        default="rows")

    parser.add_argument("--spotting-parameter-data-file-name",
                        help="Spotting parameter data file name (default None)\n  As of Feb 2018 a JSON file and the dictionary should have 'SPTANGLE', 'SPOT0PROB', and 'SPOT10TIME'",
                        dest="spotting_parameter_data_file_name",
                        type=str,
                        default=None)                

    parser.add_argument("--plot",
                        help="Plots are created after the simulation",
                        dest="input_plottrue",
                        default=False,
                        action='store_true') 
    
    parser.add_argument("--finalplot",
                        help="Final plot (only) is created after the simulation",
                        dest="input_fplot",
                        default=False,
                        action='store_true') 
    
    parser.add_argument("--plot-time",
                        help="Plots are generated in multiples of this factor",
                        dest="plot_time",
                        type=int,
                        default=-1) 

    parser.add_argument("--plot-hour",
                        help="Plots are generated per hour",
                        dest="plotHour",
                        default=False,
                        action='store_true') 

    parser.add_argument("--grid-hour",
                        help="Grids are generated per hour",
                        dest="gridHour",
                        default=False,
                        action='store_true') 

    parser.add_argument("--verbose",
                        help="Output all the simulation log",
                        dest="verbose_input",
                        default=False,
                        action='store_true')

    parser.add_argument("--ignition-point",
                        help="The name of the csv file that contains the ignition data",
                        dest="input_ignitions",
                        type=str,
                        default="")        

    parser.add_argument("--ignitions",
                        help="Activates the predefined ignition points when using the folder execution",
                        dest="act_ignitions",
                        default=False,
                        action="store_true")    

    parser.add_argument("--sim-years",
                        help="Number of years per simulation (default 1)",
                        dest="sim_years",
                        type=int,
                        default=1)    

    parser.add_argument("--nsims",
                        help="Total number of simulations (replications)",
                        dest="input_nsims",
                        type=int,
                        default=1)    

    parser.add_argument("--Fire-Period-Length",
                        help="Fire Period length in minutes (needed for ROS computations). Default 60",
                        dest="input_PeriodLen",
                        type=float,
                        default=60)                    

    parser.add_argument("--Weather-Period-Length",
                        help="Weather Period length in minutes (needed weather update). Default 60",
                        dest="weather_period_len",
                        type=float,
                        default=60)                    

    parser.add_argument("--ROS-Threshold",
                        help="A fire will not start or continue to burn in a cell if the head ros is not above this value (m/min) default 0.1.",
                        dest="ROS_Threshold",
                        type=float,
                        default=0.1)                    

    parser.add_argument("--HFI-Threshold",
                        help="A fire will not start or continue to burn in a cell if the HFI is not above this value (Kw/m) default is 10.",
                        dest="HFI_Threshold",
                        type=float,
                        default=10.0)                    

    parser.add_argument("--ROS-CV",
                        help="Coefficient of Variation for normal random ROS (e.g. 0.13), but default is 0 (deteriministic)",
                        dest="ROS_CV",
                        type=float,
                        default=0.0)                    

    parser.add_argument("--heuristic",
                        help="Harvesting heuristic/plan used (number)",
                        dest="input_heur",
                        type=int,
                        default=0)        

    parser.add_argument("--statistics",
                        help="Excel file with statistics is created at the end of the simulation",
                        dest="input_excel",
                        default=False,
                        action="store_true")    

    parser.add_argument("--combine",
                        help="Combine fire evolution diagrams with the forest background",
                        dest="input_combine",
                        default=False,
                        action="store_true")                    

    parser.add_argument("--save-memory",
                        help="Activates memory monitoring version (useful for very large instances)",
                        dest="input_save",
                        default=False,
                        action="store_true")                

    parser.add_argument("--scenarios-out",
                        help="Activates scenario output files; requires --output-grid",
                        dest="input_scenario",
                        default=False,
                        action="store_true")        

    parser.add_argument("--no-output",
                        help="Activates no-output mode ",
                        dest="no_output",
                        default=False,
                        action="store_true")        

    parser.add_argument("--output-grid",
                        help="Activates forest grid's output mode (TEMPORARILY DISABLED by DLW)",
                        dest="output_grid",
                        default=False,
                        action="store_true")        

    parser.add_argument("--FBP-tester-cell",
                        help="If not 0, Causes special output, then termination after one ROS calculation for the cell number given (default 0)",
                        dest="FBP_tester_cell",
                        type=int,
                        default=0)        

    parser.add_argument("--max-fire-periods",
                        help="Maximum fire periods per year (default 100000)",
                        dest="max_fire_periods",
                        type=int,
                        default=100000) 
    
    parser.add_argument("--gen-data",
                        help="Generates the Data.dat file before the simulation",
                        dest="input_gendata",
                        default=False,
                        action="store_true")
    
    parser.add_argument("--output-messages",
                        help="Generates a file with messages per cell, hit period, and hit ROS",
                        dest="input_messages",
                        default=False,
                        action='store_true') 
    
    parser.add_argument("--HFactor",
                        help="Adjustement factor: HROS",
                        dest="HFactor",
                        type=float,
                        default=1.0)
    
    parser.add_argument("--FFactor",
                        help="Adjustement factor: FROS",
                        dest="FFactor",
                        type=float,
                        default=1.0)
    
    parser.add_argument("--BFactor",
                        help="Adjustement factor: BROS",
                        dest="BFactor",
                        type=float,
                        default=1.0)
    
    parser.add_argument("--EFactor",
                        help="Adjustement ellipse factor",
                        dest="EFactor",
                        type=float,
                        default=1.0)
    
    parser.add_argument("--BurningLen",
                        help="Burning length period (periods a cell is burning)",
                        dest="BurningLen",
                        type=float,
                        default=-1.0)
    
    parser.add_argument("--Prometheus-tuned",
                        help="Activates the predefined tuning parameters based on Prometheus",
                        dest="PromTuning",
                        default=False,
                        action="store_true") 

    parser.add_argument("--HarvestedCells",
                        help="File with initial harvested cells (csv with number of cells: e.g 1,2,3,4,10)",
                        dest="HCells",
                        type=str,
                        default=None)
    
    parser.add_argument("--IgnitionRadius",
                        help="Adjacents degree for defining an ignition area (around ignition point)",
                        dest="IgRadius",
                        type=int,
                        default=0) 
   
    args = parser.parse_args()
        
    return args
    
    
    
    
    


# In[61]:


'''
Returns          dict {int:int}, Weather class object, Plot class object, dataframe

Inputs:
Ignitions        string
WeatherOpt       list of strings
DF               DataFrame
args             args object
verbose          boolean
nooutput         boolean
'''
def Init(Ignitions, WeatherOpt, plottrue, OutFolder, DF, args, verbose, nooutput):
    # Check for ignition points       
    if Ignitions != "":
        Ignitions = ReadDataPrometheus.IgnitionPoints(Ignitions)
        if nooutput == False:
            print("We have specific ignition points")
            print("Ignitions:", Ignitions)
    if Ignitions == "" and nooutput == False:
        print( "No ignition points")

    # Weather options
    wchoices = ['constant', 'random', 'rows']
    if WeatherOpt not in wchoices:
        print( "Valid weather choices are:",str(wchoices))
        raise RuntimeError ("invalid choice for --weather") 

    if nooutput==False:
        print("Reading weather file")
    weatherperiod = 0
    if WeatherOpt == 'random':
    	I = range(0,360)
    	i = str(np.random.choice(I))
    	print "Weather i", i
     	Weather_Obj = WeatherFBP.Weather(os.path.join(args.input_folder, "WeatherFolder/Weather"+i+".csv"))
    else:
    	Weather_Obj = WeatherFBP.Weather(os.path.join(args.input_folder, "Weather.csv"))
    if WeatherOpt != 'constant':
        DF = Weather_Obj.update_Weather_FBP(DF, WeatherOpt, weatherperiod)

    # Weather: printing info, if verbose
    if verbose == True:
        print("DF", DF[["ws","waz","ps", "saz"]])
        Weather_Obj.print_info(weatherperiod)

    #Initializing plot object and plot the initial forest
    if plottrue == True or args.plotHour == True:
        PlotPath = os.path.join(OutFolder, "Plots")
        if not os.path.exists(PlotPath):
            print("creating", PlotPath)
            os.makedirs(PlotPath)
        Plotter = Plot.Plot()

    else:
        Plotter = None
    
    if args.gridHour == True:
        GridPath = os.path.join(OutFolder, "Grids")
        if not os.path.exists(GridPath):
            print("creating", GridPath)
            os.makedirs(GridPath)
        
    return Ignitions, Weather_Obj, Plotter, DF


# In[49]:


'''
Returns          int array, int array, int array, array of 4D doubles tuples [(d1,d2,d3,d4),...,(d1n,d2n,d3n,d4n)]  

Inputs:
Ignitions        string
WeatherOpt       list of strings
DF               DataFrame
args             args object
verbose          boolean
nooutput         boolean
'''
def InitCells(NCells, FTypes2, ColorsDict, CellsGrid4, CellsGrid3):   
    FTypeCells = np.zeros(NCells).astype(int)   #[]
    StatusCells = np.zeros(NCells).astype(int)  #[]
    RealCells = np.zeros(NCells).astype(int)    #[]
    Colors = []
    cellcounter=1

    # Populate Status, FType, IDs, and Color of the cells
    for i in range(NCells):
        if str.lower(CellsGrid4[i]) not in FTypes2.keys():
            #FTypeCells[i] = 0 #0.append(0)
            StatusCells[i] = 4 #.append(4)
            CellsGrid4[i] = "s1"
            #RealCells[i] = 0 #append(0)
        else:
            FTypeCells[i] = 2 #.append(2)
            #StatusCells[i] = 0 #.append(0)
            RealCells[i] = cellcounter #.append(cellcounter)
            cellcounter+=1

        if str(CellsGrid3[i]) not in ColorsDict.keys():
            Colors.append((1.0,1.0,1.0,1.0))

        if str(CellsGrid3[i]) in ColorsDict.keys():
            Colors.append(ColorsDict[str(CellsGrid3[i])])

    return FTypeCells, StatusCells, RealCells, Colors


# In[53]:


'''
Returns          Forest object

Inputs:
FID              int
FLocation        string
FCoor            2D double array [d1,d2]
FArea            double
FVol             double
FAVGAge          double
FPerimeter       double
FFTypes          dict {string:int}
verbose          boolean
'''
def InitForest(FID, FLocation, FCoord, FNCells, FArea, FVol, FAVGAge, FPerimeter, FFTypes, verbose):
    Forest1 = Forest.Forest(FID, FLocation, FCoord, FNCells, FArea, FVol, FAVGAge, FPerimeter, FFTypes)
    
    if verbose == True:
        print("\n------------------------ Forests lists ------------------------")
        Forest1.print_info()
            
    return Forest1


