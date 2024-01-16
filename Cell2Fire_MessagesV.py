# coding: utf-8

__version__ = 0.05

# Importationslp
import os
import shutil
import numpy.random as npr
import numpy as np
from itertools import repeat
import time
import ctypes
from ParseInputs import ParseInputs, Init, InitCells, InitForest

# Class importations
import WeatherFBP
import CellsFBP
import Forest
import Lightning
import Plot
import FBP2PY
import ReadDataPrometheus
import SpottingFBP
import Output_Grid
import DataGenerator

from Heuristic import *
# Shared library .so (CP: Careful with Windows vs UNIX)
soname = "FBPfunc5NODEBUG.so"
try:
    lib = ctypes.cdll.LoadLibrary(soname)
except:
    raise RuntimeError("Could not load the library=" + soname)

'''
A little "local" report writer for debugging
Used for quick analysis of output and for regression tests.
Writes a self-documenting csv file

Return        void

Inputs:
args           arguments from command line object
Sim            int
AreaCells      double
NCells         int
Fire_Period    int
ASet           int set
BSet           int set
NSet           int set
HSet           int set
'''


def CSVGrid(rows, cols, AvailCells, NonBurnableCells, plotnumber, GridPath):
    status = np.ones(rows * cols).astype(int)
    status[list(AvailCells) - np.ones(len(AvailCells)).astype(int)] = 0
    if len(NonBurnableCells) > 0:
        status[list(NonBurnableCells) - np.ones(len(NonBurnableCells)).astype(int)] = 0
    fileName = GridPath + "/ForestGrid" + str(plotnumber) + ".txt"
    np.savetxt(fileName, status.reshape(rows, cols).astype(int), delimiter=',', fmt='%i')


def special_report(args, Sim, AreaCells, NCells, Fire_Period, ASet, BSet, NSet, HSet=None):
    def writeone(appfile, name, val):
        appfile.write(", " + name + ", " + str(val))

        fname = os.path.join(args.output_folder, "SimReport.csv")

        with open(fname, "a") as appfile:
            appfile.write("infolder, " + args.input_folder)
            writeone(appfile, "ReplicateNum", Sim)
            writeone(appfile, "seed", args.seed)
            writeone(appfile, "ROSCV", args.ROS_CV)
            writeone(appfile, "CellArea", AreaCells)
            writeone(appfile, "NCells", NCells)
            writeone(appfile, "Burntcells", len(BSet))
            writeone(appfile, "NonBurnable", len(NSet))
            writeone(appfile, "StillAvailableCells", len(ASet))
            if HSet is not None:
                writeone(appfile, "HarvestedCells", len(HSet))
            writeone(appfile, "SimYears", args.sim_years)

            for fi in range(len(Fire_Period)):
                writeone(appfile, "fireperiods" + str(fi + 1), Fire_Period[fi])
            appfile.write("\n")


# Main class with all the simulation scheme
class Main:
    ######################################################################################################################################
    #
    #        Simulator: All the simulation scheme is developed here
    #
    ######################################################################################################################################

    # Step -1: FBP
    ##########################################################################################################
    #                                    FBP Coefficients and types
    ##########################################################################################################
    # FType coefficients and data from FBP library
    listlen = 18
    ListOfCoefs = listlen * CellsFBP.fuel_coeffs
    coef_ptr = ListOfCoefs()
    lib.setup_const(coef_ptr)
    FTypes2 = {"m1": 0, "m2": 1, "m3": 2, "m4": 3,
               "c1": 4, "c2": 5, "c3": 6, "c4": 7, "c5": 8, "c6": 9, "c7": 10,
               "d1": 11, "s1": 12, "s2": 13, "s3": 14, "o1a": 15, "o1b": 16, "d2": 17}

    # Forest Data (read table using c functions in class ReadData)

    ##########################################################################################################
    #                                           Read input values
    ##########################################################################################################
    # Read inputs from command line
    args = ParseInputs()

    # Initialize parameters
    InFolder = args.input_folder
    OutFolder = args.output_folder
    OutMessages = args.input_messages
    SaveMem = args.input_save
    scenarios = args.input_scenario
    nooutput = args.no_output
    OutputGrid = args.output_grid
    MinutesPerWP = args.weather_period_len
    cellID = args.FBP_tester_cell
    verbose = args.verbose_input
    plottrue = args.input_plottrue
    Max_Fire_Periods = args.max_fire_periods
    TotalYears = args.sim_years
    TotalSims = args.input_nsims
    FirePeriodLen = args.input_PeriodLen
    ForestFile = args.input_forest
    FBPlookup = args.input_fbplookup
    Ignitions = args.input_ignitions
    WeatherOpt = str.lower(args.input_weather)
    spotting = args.spotting_parameter_data_file_name is not None
    exceltrue = args.input_excel
    heuristic = args.input_heur
    combine = args.input_combine
    GenData = args.input_gendata
    FinalPlot = args.input_fplot
    PlotInterval = args.plot_time
    Thresholds = {}
    toPrint = True

    # Debug mode    
    if args.FBP_tester_cell > 0:
        cellID = args.FBP_tester_cell
        print("Entering FBP_tester; trying cell=", cellID)
        mainstruct, headstruct, flankstruct, backstruct = FBP2PY.CalculateOne(DF, coef_ptr, cellID, verbose=True)
        quit()

    # Generate Data.dat if needed
    if GenData == True:
        print("Generating Data.dat File")
        if InFolder != None:
            DataGenerator.GenDataFile(InFolder)
        else:
            DataGenerator.GenDataFile("")

    # Filename
    if scenarios and not OutputGrid:
        raise RuntimeError("--scenarios requires --output-grid")
    if InFolder != None:
        filename = os.path.join(InFolder, "Data.dat")
        if os.path.isfile(filename) == False:
            print("Data.dat file does not exists, generating it from files inside", InFolder)
            DataGenerator.GenDataFile(InFolder)

    else:
        filename = "Data.dat"
        if os.path.isfile(filename) == False:
            print("Data.dat file does not exists, generating it from files inside current directory")
            DataGenerator.GenDataFile("")

    # Folder existence
    if os.path.exists(OutFolder):
        print("Creating a new, empty folder =", OutFolder)
        shutil.rmtree(OutFolder)
    os.makedirs(OutFolder)

    # No output dominates verbose
    if nooutput == True:
        verbose = False

    # Random seed
    if verbose:
        print("Setting initial pseudo-random number stream seed to ", str(args.seed))
    if args.seed is not None:
        npr.seed(int(args.seed))

    # If we have a folder with an instance read files
    if InFolder != None:
        ForestFile = os.path.join(InFolder, "Forest.asc")
        FBPlookup = os.path.join(InFolder, "fbp_lookup_table.csv")
        Ign = args.act_ignitions

        if Ign == True:
            Ignitions = os.path.join(InFolder, "IgnitionPoints.csv")

        if args.spotting_parameter_data_file_name is not None:
            SpottingFile = os.path.join(InFolder, args.spotting_parameter_data_file_name)
            SpottingParams = ReadDataPrometheus.ReadSpotting(SpottingFile, nooutput)

        else:
            SpottingParams = None

    # Fire Period length
    FirePeriodLen = args.input_PeriodLen
    print("-----------------------------------------------------------------------------------")
    if FirePeriodLen > MinutesPerWP:
        print("Fire Period Length > Weather Period: setting Fire Period Length = Weather Period")
        FirePeriodLen = MinutesPerWP
    print("Fire Period Length for ROS computations [min]: ", FirePeriodLen)
    # Burning period length
    if args.BurningLen > 0:
        print("Cells maximum burning periods is set to", args.BurningLen)

    print("-----------------------------------------------------------------------------------")
    ##########################################################################################################

    ##########################################################################################################
    #                                    Read Data Frame & Fuel types
    ##########################################################################################################
    # Read DataFrame
    DF = FBP2PY.inputData(filename)
    if GenData == False:
        Elevation, SAZ, PS = ReadDataPrometheus.DataGrids(InFolder, len(DF))
        DF["elev"] = Elevation
        DF["saz"] = SAZ
        DF["ps"] = PS
        DF["time"] = np.zeros(DF.shape[0]) + 20
    if verbose == True:
        print("DF:", DF)

    # Getting FType for each cell from data 
    FTypeCells2 = np.array(DF['fueltype'], dtype=object)

    # Periods and Initialize simulation number
    max_weeks = 12  # weeks
    Sim = 1
    ##########################################################################################################
    #                                           
    ##########################################################################################################

    ##########################################################################################################
    #                                          Global Forest Data
    ##########################################################################################################
    # Read Forest
    if nooutput == False:
        print("\n----------------- Forest Data -----------------")

    # Obtain FBP and Color dictionaries from FBP file, read the ForestGrid file
    FBPDict, ColorsDict = ReadDataPrometheus.Dictionary(FBPlookup)
    GForestN, GForestType, Rows, Cols, AdjCells, CoordCells, CellSide = ReadDataPrometheus.ForestGrid(ForestFile,
                                                                                                      FBPDict)

    # Number of cells
    NCells = Rows * Cols

    # Initialize main cells inputs
    FTypeCells, StatusCells, RealCells, Colors = InitCells(NCells, FTypes2, ColorsDict,
                                                           GForestType, GForestN)

    ###################################################################
    # Print information for debug
    # if verbose == True:
    #    print("\nCoord Cells:", CoordCells)
    #    print("\nCells GForestType:", GForestType)
    #    print("\nFTypeCells:", FTypeCells)
    #    print("\nFTypeCells2:", FTypeCells2)
    #    print("\nlist of coef:", ListOfCoefs)
    #    print("\nRealCells:", RealCells)
    #    print("\nStatus Cells:", StatusCells)
    #    print("\nColors:", Colors)
    #    print("\nCells GForestN:", GForestN)
    #    print("\nCoef pointer:", coef_ptr)
    #    print("\nlen DF fueltype:", DF['fueltype'].shape[0])
    #    print("\nFBPDict:", FBPDict)
    #    print("\nColorsDict:",ColorsDict)
    #    print("\nAdj cells:",AdjCells)
    #    print("\nCell side:", CellSide)
    ###################################################################

    # Releasing memory
    del GForestN
    del ColorsDict

    # Cell instance data (explicit for the moment, final version may read it from a source file)
    VolCells, AgeCells = ReadDataPrometheus.CellsInfo(ForestFile)
    AreaCells = CellSide * CellSide
    PerimeterCells = CellSide * 4

    # Init Forest object
    ForestObj = InitForest(1, "My Mind", [1, 1], NCells, NCells * AreaCells,
                           NCells * VolCells, 0.0, 2 * CellSide * (Rows + Cols),
                           FTypeCells2, verbose)
    # FTypes = {0: "NonBurnable", 1: "Normal", 2: "Burnable"}

    if nooutput == False:
        print("Rows:", Rows, "Cols:", Cols, "NCells:", NCells)
        print("------------ End read forest data -------------")

    ##########################################################################################################
    #                               Ignition, Weather, Plot, Lightning Options/Data
    ##########################################################################################################    
    weatherperiod = 0
    Ignitions, Weather_Obj, Plotter, DF = Init(Ignitions, WeatherOpt, plottrue, OutFolder, DF,
                                               args, verbose, nooutput)

    # DF_Orig = DF.copy()
    if heuristic != 0:
        # Utility[i] : demanda de la celda i
        # Volume[i] : volumen de la celda i
        # Demanda[Year] : Demanda del anio Year
        Utility, Volume, DemandArray = ReadForest(InFolder, 1)

    ##########################################################################################################
    #                              Simulation loop (Sim: 1 to TotalSims replications)
    ##########################################################################################################
    while Sim <= TotalSims:

        # DF = DF_Orig.copy()

        ##########################################################################################################
        #                 Step 0: Initializing Instances, classes, global parameters, sets, etc.
        ##########################################################################################################
        print("------------------------------------------------- Simulation Number ", Sim,
              "-------------------------------------------------")

        # Global Parameters (reseting)
        week_number = 1
        Year = 1
        weatherperiod = 0
        NoIgnition = None
        MessagesSent = None
        plotnumber = 1

        '''
        Check it! Logic of the grid
        '''
        if OutputGrid:
            FI = {}
            HPeriod = [0]

        # Reset DF if not initial sim
        if Sim != 1:
            DF = Weather_Obj.update_Weather_FBP(DF, WeatherOpt, weatherperiod)

        # Current fire period in a year (also records last fire period)
        Fire_Period = np.zeros(TotalYears).astype(int)

        # BurntP is an array (by period) of the array of cells burned in the period (migrating to dict)
        BurntP = {}  # BurntP = [[] for i in repeat(None, Max_Fire_Periods)]

        # Record current clock for measuring running time (including data reading)
        Initial_Time = time.clock()

        ##########################################################################################################
        #                               Ignition, Weather, Plot, Lightning Options/Data
        ##########################################################################################################    

        # Plots
        if (plottrue == True and toPrint == True) or FinalPlot == True or args.plotHour == True:
            emptylist = dict.fromkeys([i for i in range(1, NCells + 1)], [])
            PlotPath = os.path.join(OutFolder, "Plots")
            if os.path.isfile(os.path.join(OutFolder, "ForestInitial.png")) == True:
                if nooutput == False:
                    print("Forest already exists")
            else:
                Plotter.PlotForestOnly(Colors, CoordCells, plotnumber, 0, Year, False, Rows, Cols, OutFolder)

        # Generate grids folders
        if args.gridHour == True:
            GridPath = os.path.join(OutFolder, "Grids/Grids" + str(Sim))
            if not os.path.exists(GridPath):
                os.makedirs(GridPath)

        # Generate messages folders 
        if OutMessages == True:
            MessagesPath = os.path.join(OutFolder, "Messages/Messages" + str(Sim))
            if not os.path.exists(MessagesPath):
                os.makedirs(MessagesPath)

            # Maximum fire periods validity
        if WeatherOpt == "rows":
            MaxFP = int(MinutesPerWP / FirePeriodLen) * (Weather_Obj.rows)
            if Max_Fire_Periods > MaxFP:
                Max_Fire_Periods = MaxFP - 1
                if verbose == True:
                    print("Maximum fire periods are set to:", Max_Fire_Periods,
                          "based on the weather file, Fire Period Length, and Minutes per WP")
            else:
                print("Maximum fire periods:", Max_Fire_Periods)

        # Number of years and Ignitions
        if Ignitions != "":
            IgYears = len(Ignitions.keys())
            if TotalYears > IgYears:
                print("Total Years set to", IgYears, "based on Ignitions points provided")
                TotalYears = IgYears

        # Initializing Lambda Instance (random lightning)
        Lambda_Strike = Lightning.Lightning()

        ##########################################################################################################
        #                                   Cells Obj Dictionary and Main Sets
        ##########################################################################################################    
        # Cells Dictionary: Will have active cells (burnin/burnt and potentially active ones - getting messages)
        Cells_Obj = {}

        # Sets (Available cells, burning cells, burnt cells and harvest cells: starting from array and cast later)
        AvailCells_Set = set(np.where(StatusCells != 4)[0] + 1)
        NonBurnableCells_Set = set(np.where(StatusCells == 4)[0] + 1)
        BurningCells_Set = set()
        BurntCells_Set = set()
        HarvestCells_Set = set()

        TotalDemand = [0] * TotalYears
        TotalUtility = [0] * TotalYears
        HarvestedCells = set()
        # Printing info about the cells' status
        if verbose == True:
            print("\nSet information period (week", week_number, ")")
            print("Available Cells:", AvailCells_Set)
            print("Non Burnable Cells:", NonBurnableCells_Set)
            print("Burning Cells:", BurningCells_Set)
            print("Burnt Cells:", BurntCells_Set)
            print("Harvest Cells:", HarvestCells_Set)

        ##########################################################################################################
        #                                   Years' loop (Periods = 4 by default) 
        ##########################################################################################################    
        while Year <= TotalYears:
            if verbose == True:
                print("\nSimulating Year", Year, "\n")

            ##########################################################################################################
            #                   Step 0: Harvested Heuristic
            ##########################################################################################################
            if heuristic != 0:
                print("---------------------- Step 0: Harvest Heuristic ----------------------")
                HarvestedCells, TotalDemand[Year - 1], TotalUtility[Year - 1] = Heuristics(heuristic,
                                                                                           AvailCells_Set,
                                                                                           BurntCells_Set,
                                                                                           HarvestedCells,
                                                                                           Year,
                                                                                           InFolder,
                                                                                           AdjCells,
                                                                                           NCells,
                                                                                           Utility,
                                                                                           Volume,
                                                                                           DemandArray,
                                                                                           Cells_Obj,
                                                                                           Weather_Obj)
                HarvestCells_Set = HarvestCells_Set.union(HarvestedCells)
                print 'HarvestedCells_Set', HarvestCells_Set
                AvailCells_Set = AvailCells_Set.difference(HarvestCells_Set)
                if heuristic != 0:
                    print("Benefit year", Year, ":", TotalUtility[Year - 1])
                    print('HarvestCells_Set', Year, ':', HarvestCells_Set)

                # inicializar las cosechas
                for c in HarvestCells_Set:
                    if (c - 1) not in Cells_Obj.keys():
                        print 'Cosechamos la celda', c
                        Cells_Obj[c - 1] = CellsFBP.Cells((c),
                                                          AreaCells,
                                                          CoordCells[c-1],
                                                          AgeCells,
                                                          FTypeCells[c-1],
                                                          coef_ptr[FTypes2[str.lower(GForestType[c-1])]],
                                                          #TerrainCells,
                                                          VolCells,
                                                          PerimeterCells,
                                                          StatusCells[c-1],
                                                          AdjCells[c-1],
                                                          Colors[c-1],
                                                          RealCells[c-1],
                                                          OutputGrid)
                    Cells_Obj[c-1].Status = 3

            ##########################################################################################################
            #                   Step 1: Lightning/Ignition loop in order to find the first week with fire
            ##########################################################################################################    
            # Loop for finding next fire week
            # Printing information if verbose is true
            if verbose == True:
                print(
                "\n------------------------------------ Current Year:", Year, " ------------------------------------")
                print("---------------------- Step 1: Ignition ----------------------")

            # Save Memory mode: Burnt cells are deleted from Cells_Obj dictionary (Inactive)
            if SaveMem == True:
                if verbose == True:
                    print("Deleting burnt cells from Cells_Obj dict...")
                for c in BurntCells_Set:
                    thrash = Cells_Obj.pop(c - 1, None)
                    if verbose == True and thrash != None:
                        print("Deleted:", c)

            # Parameters and variables
            aux = 0
            loops = 0
            NoIgnition = False

            # Starting fire week 
            if Ignitions == "":
                while week_number <= max_weeks:
                    # If a lightning occurs in a week, we select that week
                    if Lambda_Strike.Lambda_NH(week_number, verbose) == True:
                        Sel_Week = week_number
                        if verbose == True:
                            print("Selected Week: " + str(Sel_Week))
                        break
                    else:
                        week_number += 1
                        weatherperiod += 1

            else:
                week_number = 1
                weatherperiod = 0
                Sel_Week = 1

            # Go to that period/week
            print("Selected Week (Ignition) =", Sel_Week)

            if verbose == True:
                print("\nCurrent Period (Week):", week_number)
                print("Current Fire Period (Hour):", Fire_Period[Year - 1])

            ##########################################################################################################
            #                                      Ignite the cell (or not)
            ##########################################################################################################    
            aux = 0
            loops = 0
            NoIgnition = False

            # Select the "burning" cell
            # If no ignition points, take one cell at random
            if Ignitions == "":
                while True:
                    aux = int(npr.uniform(0, 1) * NCells)

                    print("aux:", aux)
                    print("RealCells[aux]:", RealCells[aux])

                    # If cell is available (global properties)
                    if StatusCells[aux] != 4 and (aux + 1) not in BurntCells_Set:

                        # Initialize cell if needed
                        if aux not in Cells_Obj.keys():
                            Cells_Obj[aux] = CellsFBP.Cells((aux + 1), AreaCells, CoordCells[aux],
                                                            AgeCells, FTypeCells[aux],
                                                            coef_ptr[FTypes2[str.lower(GForestType[aux])]],
                                                            VolCells, PerimeterCells,
                                                            StatusCells[aux], AdjCells[aux], Colors[aux],
                                                            RealCells[aux], OutputGrid)

                            # Avail set modification for initialization
                            Cells_Obj[aux].InitializeFireFields(CoordCells, AvailCells_Set)

                        # If the cell is available and burnable (from object properties)
                        if Cells_Obj[aux].get_Status() == "Available" and Cells_Obj[aux].FType != 0:
                            if Cells_Obj[aux].ignition(Fire_Period[Year - 1], Year, Ignitions, DF, coef_ptr,
                                                       args):

                                # If we have an ignition, change the status of the forest
                                if OutputGrid:
                                    FI[Fire_Period[Year - 1] - 1] = Cells_Obj[aux].ID
                                    BurntP[Fire_Period[Year - 1] - 1] = Cells_Obj[aux].ID

                                '''
                                Check if we need to keep it this way or with a dict
                                for i in range(Fire_Period[Year-1], Max_Fire_Periods):
                                    BurntP[i] = Cells_Obj[aux].ID
                                '''

                                # Printing info about ignitions        
                                if verbose == True:
                                    print("Cell ", Cells_Obj[aux].ID, " Ignites")
                                    print("Cell ", Cells_Obj[aux].ID, " Status: ", Cells_Obj[aux].get_Status())

                                # Plot and SaveMemory flags: Active cells plot
                                if plottrue == True and SaveMem == True and FinalPlot == False and toPrint == True:
                                    Plotter.forest_plotV3_FreeMem(Cells_Obj, emptylist, plotnumber,
                                                                  Fire_Period[Year - 1], Year, False, Rows,
                                                                  Cols, PlotPath, CoordCells, BurntCells_Set, Sim)
                                    plotnumber += 1

                                # Otherwise, we print the whole forest
                                if plottrue == True and SaveMem != True and FinalPlot == False and toPrint == True:
                                    Plotter.forest_plotV3(Cells_Obj, emptylist, plotnumber, Fire_Period[Year - 1], Year,
                                                          False, Rows, Cols, PlotPath, Sim)
                                    plotnumber += 1

                                break

                    # Updating parameters inside the loop
                    loops += 1

                    # Maximum number of iterations
                    if loops > NCells:
                        NoIgnition = True
                        break

            # IF we have specific ignitions
            if Ignitions != "":
                # Check ignition points are not already burnt and the cell is burnable
                if Ignitions[Year] not in BurntCells_Set and StatusCells[Ignitions[Year] - 1] != 4:

                    # Initialize it if needed
                    if (Ignitions[Year] - 1) not in Cells_Obj.keys():
                        Cells_Obj[Ignitions[Year] - 1] = CellsFBP.Cells((Ignitions[Year]), AreaCells,
                                                                        CoordCells[Ignitions[Year] - 1], AgeCells,
                                                                        FTypeCells[Ignitions[Year] - 1],
                                                                        coef_ptr[FTypes2[str.lower(
                                                                            GForestType[Ignitions[Year] - 1])]],
                                                                        VolCells, PerimeterCells,
                                                                        StatusCells[Ignitions[Year] - 1],
                                                                        AdjCells[Ignitions[Year] - 1],
                                                                        Colors[Ignitions[Year] - 1],
                                                                        RealCells[Ignitions[Year] - 1], OutputGrid)

                        # Initialize fire fields 
                        Cells_Obj[Ignitions[Year] - 1].InitializeFireFields(CoordCells, AvailCells_Set)

                    # If not available, no ignition
                    if Cells_Obj[Ignitions[Year] - 1].get_Status() != "Available" or Cells_Obj[
                        Ignitions[Year] - 1].FType == 0:
                        NoIgnition = True

                    # If available, ignites
                    if Cells_Obj[Ignitions[Year] - 1].get_Status() == "Available" and Cells_Obj[
                        Ignitions[Year] - 1].FType != 0:
                        if Cells_Obj[Ignitions[Year] - 1].ignition(Fire_Period[Year - 1], Year, Ignitions, DF,
                                                                   coef_ptr, args):

                            if OutputGrid:
                                FI[Fire_Period[Year - 1] - 1] = Cells_Obj[Ignitions[Year] - 1].ID
                                BurntP[Fire_Period[Year - 1] - 1] = Cells_Obj[Ignitions[Year] - 1].ID
                            '''
                            Check if needed
                            for i in range(Fire_Period[Year-1],Max_Fire_Periods):
                                BurntP[i] = Cells_Obj[Ignitions[Year]-1].ID
                            '''

                            # Printing info about ignitions        
                            if verbose == True:
                                print("Cell", Cells_Obj[Ignitions[Year] - 1].ID, "Ignites")
                                print("Cell", Cells_Obj[Ignitions[Year] - 1].ID, "Status:",
                                      Cells_Obj[Ignitions[Year] - 1].get_Status())

                            # Plot and save memory
                            if plottrue == True and SaveMem == True and FinalPlot == False and toPrint == True:
                                Plotter.forest_plotV3_FreeMem(Cells_Obj, emptylist, plotnumber, Fire_Period[Year - 1],
                                                              Year, False, Rows, Cols, PlotPath, CoordCells,
                                                              BurntCells_Set, Sim)
                                plotnumber += 1

                            # Plot no save memory
                            if plottrue == True and SaveMem != True and FinalPlot == False and toPrint == True:
                                Plotter.forest_plotV3(Cells_Obj, emptylist, plotnumber, Fire_Period[Year - 1], Year,
                                                      False,
                                                      Rows, Cols, PlotPath, Sim)
                                plotnumber += 1

                                # Otherwise, no ignitions (already burnt or non burnable)
                else:
                    NoIgnition = True
                    if nooutput == False:
                        print("No ignition during year", Year,
                              ", cell", Ignitions[Year], "is already burnt or non-burnable type")

            # If ignition occurs, we update the forest status
            if NoIgnition == False:

                # Updating AvailCells and BurningCells sets    
                if Ignitions == "":
                    NewID = Cells_Obj[aux].ID
                    Aux_set = set([NewID])
                    BurningCells_Set = BurningCells_Set.union(Aux_set)
                    AvailCells_Set = AvailCells_Set.difference(BurningCells_Set)

                else:
                    NewID = Cells_Obj[Ignitions[Year] - 1].ID
                    Aux_set = set([Ignitions[Year]])
                    BurningCells_Set = BurningCells_Set.union(Aux_set)
                    AvailCells_Set = AvailCells_Set.difference(BurningCells_Set)
                    BurntCells_Set = BurntCells_Set.union(Aux_set)

            # Printing information about the forest
            if verbose == True:
                print("Available cells:", AvailCells_Set)
                print("Non Burnable Cells:", NonBurnableCells_Set)
                print("Burning cells:", BurningCells_Set)
                print("Harvest cells:", HarvestCells_Set)
                print("Burnt cells (including burning):", BurntCells_Set)

            ##########################################################################################################
            #                                      Next period t+1
            ##########################################################################################################    
            # Update Weather: Needs to be modified such that a weather period is coherent with the fire period
            # Fire_Period[Year-1] += 1
            toPrint = True

            if PlotInterval != -1 and Fire_Period[Year - 1] % PlotInterval != 0:
                if verbose == True:
                    print("A plot is generated in this period due to Plot Interval option")
                toPrint = False

            if verbose == True:
                print("debug Fire_Period[Year-1]", Fire_Period[Year - 1])

            if WeatherOpt != 'constant' and Fire_Period[Year - 1] * FirePeriodLen / MinutesPerWP > weatherperiod + 1:
                weatherperiod += 1
                DF = Weather_Obj.update_Weather_FBP(DF, WeatherOpt, weatherperiod)
                if args.plotHour == True:
                    Plotter.forest_plotV3(Cells_Obj, emptylist, plotnumber, Fire_Period[Year - 1], Year, False, Rows,
                                          Cols, PlotPath, Sim)
                    plotnumber += 1
                if args.gridHour == True:
                    CSVGrid(Rows, Cols, AvailCells_Set, NonBurnableCells_Set, weatherperiod, GridPath)

            if verbose == True:
                print("Current Week:", week_number)
                print("Fire Period Starts:", Fire_Period[Year - 1], "\n")
                Weather_Obj.print_info(weatherperiod)
                print("DF:", DF[["fueltype", "ws", "waz", "ffmc", "bui", "saz", "elev", "ps"]])

                if WeatherOpt == 'constant':
                    print("(NOTE: current weather is not used for ROS with constant option)")

                # End of the ignition step
                print("\nNext Fire Period:", Fire_Period[Year - 1])

            # Ending condition for the year (week/fire period)
            if week_number == 12 or Fire_Period[Year - 1] == 2016:
                print("-------------------------------------------------------------------------\n",
                      "End of the fire year", Year,
                      "-------------------------------------------------------------------------")

            # If no ignition occurs, go to next year (no multiple ignitions per year, only one)
            if NoIgnition == True:
                if verbose == True:
                    print("No ignition in year", Year)
                # Next year, reset the week
                Year += 1
                week_number = 1

            ##########################################################################################################
            #                                      Step 2,3: Send/Receive messages
            ##########################################################################################################    
            # If an ignition happened, enter in fire dynamic loop
            if NoIgnition == False:

                # Loop until max number of fire periods
                while Fire_Period[Year - 1] < Max_Fire_Periods:
                    # Ending condition and message to user
                    if Fire_Period[Year - 1] == Max_Fire_Periods - 1:
                        print("\n **** WARNING!!!! About to hit Max_Fire_Periods=", Max_Fire_Periods, " ***\n\n")

                    ##################################################################################################
                    #                                      Step 2: Send messages
                    ##################################################################################################    
                    # Initial Parameters
                    MessagesSent = False
                    SendMessageList = {}  # Testing dictionary instead of list
                    # SendMessageList = [[] for i in repeat(None, NCells)]

                    # Printing info before sending messages
                    if verbose == True:
                        print("\n---------------------- Step 2: Sending Messages from Ignition ----------------------")
                        print("Current Week:", week_number)
                        print("Current Fire Period:", Fire_Period[Year - 1])
                        print("Burning Cells:", BurningCells_Set)
                        print("Burnt Cells (should include burning):", BurntCells_Set)
                        print(" -------------------- NEW CLEANING STEP ------------------------")

                    '''
                    Cleaning ROSAngleDir dictionaries based on the current burning cells
                    '''

                    # For all the cells already initialized (SIMPLE Embarrasingly Parallel) we clean
                    # angles if nb cells are not available
                    for cell in Cells_Obj.keys():
                        # Check those cells with at least one possible neighbor to send fire
                        if len(Cells_Obj[cell].ROSAngleDir) > 0:

                            # Delete adjacent cells that are not available 
                            for angle in Cells_Obj[cell].angle_to_nb:
                                nb = Cells_Obj[cell].angle_to_nb[angle]

                                if nb not in AvailCells_Set and angle in Cells_Obj[cell].ROSAngleDir:
                                    if verbose == True:
                                        print("Cell", cell + 1, ": clearing ROSAngleDir")

                                    Cells_Obj[cell].ROSAngleDir.pop(angle)

                    if verbose == True:
                        print("----------------------------------------------------------------")

                    ##################################################################################################
                    #                             Core: Sending messages (to be parallelized)
                    ##################################################################################################    

                    # RepeatFire
                    RepeatFire = False
                    BurnedOutList = []

                    ##################################################################################################
                    #                                         Parallel Zone
                    ##################################################################################################    

                    # Burning cells loop: sending messages (Embarrasingly parallel?: CP: should be)
                    # Each burning cell updates its fire progress and (if needed) populates their message
                    # dictionary {ID:[list with int]}
                    for cell in BurningCells_Set:
                        # Info of fire fields
                        if verbose == True:
                            print("\nCell object new fields")
                            print("ID:", Cells_Obj[cell - 1].ID)
                            print("FireProgress:", Cells_Obj[cell - 1].FireProgress)
                            print("AngleDict:", Cells_Obj[cell - 1].AngleDict)
                            print("ROSAngleDir:", Cells_Obj[cell - 1].ROSAngleDir)
                            print("DistToCenter:", Cells_Obj[cell - 1].DistToCenter)
                            print("angle_to_nb:", Cells_Obj[cell - 1].angle_to_nb)

                        # Check if the burning cell can send more messages or not (based on ROSAngleDir)
                        # If no angle is available, no more messages
                        # print("DEBUG NEW BURNINGLEN:  FIREPERIOD=", Fire_Period[Year-1],
                        #     "  FIRESTARTS=", Cells_Obj[cell-1].Firestarts,
                        #    "  BurningLen=", args.BurningLen)
                        ContinueBurning = 1
                        if Fire_Period[Year - 1] - Cells_Obj[
                            cell - 1].Firestarts > args.BurningLen and args.BurningLen > 0:
                            ContinueBurning = -1
                            print("DEBUG: Cell", Cells_Obj[cell - 1].ID + 1,
                                  "is no longer burning due to Burning Length Period")

                        if len(Cells_Obj[cell - 1].ROSAngleDir) > 0 and ContinueBurning == 1:
                            # Cell can still send messages (info to user) based on nb conditions
                            if verbose == True:
                                print("Cell", cell, "can still send messages to neighbors\n")

                            Aux_List = Cells_Obj[cell - 1].manageFire(Fire_Period[Year - 1], AvailCells_Set,
                                                                      verbose, DF, coef_ptr,
                                                                      spotting, SpottingParams,
                                                                      CoordCells, Cells_Obj, args)

                        # No more neighbors to send messages (empty list)
                        else:
                            if verbose == True:
                                print("\nCell", cell, "does not have any neighbor available for receiving messages")
                            Aux_List = []

                        # Print for Debugf
                        if verbose == True:
                            print("\nAux list:", Aux_List)

                        # Cases
                        # 1) If messages and not empty, populate message list
                        if len(Aux_List) > 0 and Aux_List[0] != "True":
                            if verbose == True:
                                print("\nList is not empty")
                            MessagesSent = True
                            SendMessageList[Cells_Obj[cell - 1].ID] = Aux_List
                            if verbose == True:
                                print("\nSendMessageList: ", SendMessageList)

                        # 2) If message is True, then we update and repeat the fire
                        if len(Aux_List) > 0 and Aux_List[0] == "True":
                            if verbose == True:
                                print("\nFire is still alive and we may repeat if no other messages......")
                            RepeatFire = True

                        # 3) If empty list, cell is burnt and no messages are added
                        if len(Aux_List) == 0:
                            BurnedOutList.append(Cells_Obj[cell - 1].ID)
                            if verbose == True:
                                print("\nMessage and Aux Lists are empty; adding to BurnedOutList")
                    # End burn loop (parallel zone)

                    ##################################################################################################
                    #                              
                    ##################################################################################################    

                    # Update burning cells
                    BurningCells_Set.difference(set(BurnedOutList))

                    # Check the conditions for repeating, stopping, etc. 
                    # Global message list
                    Global_Message_Aux = [val for sublist in SendMessageList.values() for val in sublist]
                    if verbose == True:
                        print("Global_Message_Aux:", Global_Message_Aux)
                        print("RepeatFire:", RepeatFire)

                    # If we have at least one cell that needs repetition and no other messages exists
                    # We repeat
                    if RepeatFire == True and len(Global_Message_Aux) == 0:
                        # Update fire period 
                        # print("\nFires are still alive and no message has been generated during this period")
                        # print("Current Fire period:", Fire_Period[Year-1])
                        Fire_Period[Year - 1] += 1
                        # print("New Fire period: ", Fire_Period[Year-1],"\n")

                        # Update weather if needed based on Period lengths
                        if WeatherOpt != 'constant' and Fire_Period[
                            Year - 1] * FirePeriodLen / MinutesPerWP > weatherperiod + 1:
                            weatherperiod += 1
                            DF = Weather_Obj.update_Weather_FBP(DF, WeatherOpt, weatherperiod)
                            if args.plotHour == True:
                                Plotter.forest_plotV3(Cells_Obj, emptylist, plotnumber, Fire_Period[Year - 1], Year,
                                                      False, Rows, Cols, PlotPath, Sim)
                                plotnumber += 1
                            if args.gridHour == True:
                                CSVGrid(Rows, Cols, AvailCells_Set, NonBurnableCells_Set, weatherperiod, GridPath)
                            if verbose == True:
                                print("Weather has been updated!, weather period", weatherperiod)
                                print("DF:", DF[["fueltype", "ws", "waz", "ffmc", "bui", "saz", "elev", "ps"]])

                    # If repetition and messages are sent, send them!
                    if RepeatFire == True and len(Global_Message_Aux) > 0:
                        # print("Messages have been sent, next step",
                        #     "Current Fire period:", Fire_Period[Year-1])
                        RepeatFire = False

                        # Checking if the list is empty and no repeat flag, then if it is empty,
                    # end of the actual fire dynamic period, go to next year
                    if MessagesSent == False and RepeatFire == False:
                        if verbose == True:
                            print("\nNo messages during the fire period, end of year", Year)

                        # Next year, reset weeks, weather period, and update burnt cells from burning cells
                        Year += 1
                        week_number = 1
                        weatherperiod = 0

                        # Burning cells are labeled as Burnt cells (no more messages), then
                        # if save memory flag is True, we delete the cells objects saving memory...
                        BurntCells_Set = BurntCells_Set.union(BurningCells_Set)
                        BurningCells_Set = set()

                        # if no savemem flag, keep the cell object and update status
                        if SaveMem != True:
                            for br in BurntCells_Set:
                                Cells_Obj[br - 1].Status = 2

                        # Otherwise, delete the inactive (burnt cells)
                        if SaveMem == True:
                            for c in BurntCells_Set:
                                if (c - 1) in Cells_Obj.keys():
                                    if verbose == True:
                                        print("Deleting burnt cells from dictionary...")
                                        print("Deleted:", c)
                                    del Cells_Obj[c - 1]

                        break

                    ##################################################################################################
                    #                                      Step 3: Receive messages
                    ##################################################################################################    
                    # Otherwise, go to next fire period and receiving messages loop
                    if MessagesSent == True and RepeatFire == False:
                        # Global list with messages (all messages)
                        Global_Message_List = [val for sublist in SendMessageList.values() for val in sublist]
                        Global_Message_List.sort()

                        if verbose == True:
                            print("Lists of messages per Cell:", SendMessageList)
                            print("Global Message Lists:", Global_Message_List)
                            print("We have at least one message:", MessagesSent)

                        ##################################################################################################
                        #                                         Parallel Zone
                        ##################################################################################################    
                        # Initialize cell (getting a message) if needed
                        for bc in set(Global_Message_List):
                            if (bc - 1) not in Cells_Obj.keys() and bc not in BurntCells_Set:
                                Cells_Obj[bc - 1] = CellsFBP.Cells((bc), AreaCells, CoordCells[bc - 1], AgeCells,
                                                                   FTypeCells[bc - 1],
                                                                   coef_ptr[FTypes2[str.lower(GForestType[bc - 1])]],
                                                                   VolCells, PerimeterCells,
                                                                   StatusCells[bc - 1], AdjCells[bc - 1],
                                                                   Colors[bc - 1], RealCells[bc - 1],
                                                                   OutputGrid)

                                Cells_Obj[bc - 1].InitializeFireFields(CoordCells, AvailCells_Set)
                        ##################################################################################################
                        #                                         
                        ##################################################################################################    

                        #  Only active cells are being plotted (SaveMem mode)
                        if plottrue == True and SaveMem == True and FinalPlot == False and toPrint == True:
                            Plotter.forest_plotV3_FreeMem(Cells_Obj, SendMessageList, plotnumber,
                                                          Fire_Period[Year - 1], Year, False, Rows, Cols,
                                                          PlotPath, CoordCells, BurntCells_Set, Sim)
                            plotnumber += 1

                        # Otherwise, plot everything
                        if plottrue == True and SaveMem != True and FinalPlot == False and toPrint == True:
                            Plotter.forest_plotV3(Cells_Obj, SendMessageList, plotnumber,
                                                  Fire_Period[Year - 1], Year, False, Rows, Cols,
                                                  PlotPath, Sim)
                            plotnumber += 1

                        # Grid and FS/FI definitions: To be modified
                        # if OutputGrid:
                        #    for c in Cells_Obj.keys():
                        #        Cells_Obj[c].got_burnt_from_mem(Fire_Period[Year-1],
                        #                                        SendMessageList, Year-1,
                        #                                        verbose)

                        # Releasing Memory 
                        del SendMessageList

                        ##################################################################################################
                        #                                      Receive messages dynamic
                        ##################################################################################################    
                        # Printing information
                        if verbose == True:
                            print(
                                "\n---------------------- Step 3: Receiving and processing messages from Ignition ----------------------")

                        # Initializing Parameters
                        BurntList = []
                        # NMessages = [0]*NCells migrating to dictionary
                        NMessages = {}
                        GotMsg_Set = set(Global_Message_List)

                        # Check which cells got messages and how many of them
                        if verbose == True:
                            print("Cells receiving messages: " + str(GotMsg_Set))

                        # Number of messages by each cell 
                        # for i in range(1, NCells+1):  migrating to GotMsg_Set
                        for i in GotMsg_Set:
                            NMessages[i - 1] = Global_Message_List.count(i)
                            if verbose == True:
                                print("Cell", i, "receives", NMessages[i - 1], "messages")

                        # Releasing Memory 
                        del Global_Message_List

                        if verbose == True:
                            print("\nCells status")

                        ##################################################################################################
                        #                                         Parallel Zone
                        ##################################################################################################    
                        # Initialize cells getting messages (if needed)
                        for bc in GotMsg_Set:
                            if bc not in BurntCells_Set:
                                if (bc - 1) not in Cells_Obj.keys():
                                    Cells_Obj[bc - 1] = CellsFBP.Cells((bc), AreaCells, CoordCells[bc - 1], AgeCells,
                                                                       FTypeCells[bc - 1],
                                                                       coef_ptr[
                                                                           FTypes2[str.lower(GForestType[bc - 1])]],
                                                                       TerrainCells, VolCells, PerimeterCells,
                                                                       StatusCells[bc - 1], AdjCells[bc - 1],
                                                                       Colors[bc - 1], RealCells[bc - 1])

                                    print("-------- Initializing new cell ", bc, "--------")
                                    Cells_Obj[bc - 1].InitializeFireFields(CoordCells, AvailCells_Set)
                                    print("-----------------------------------------------")

                                # Check if cell is burnt or not (since it gets a message)
                                if Cells_Obj[bc - 1].FType != 0:
                                    Check_Burnt = Cells_Obj[bc - 1].get_burned(Fire_Period[Year - 1], NMessages[bc - 1],
                                                                               Year, verbose, DF, coef_ptr,
                                                                               args)

                                # Else, not burnt
                                else:
                                    Check_Burnt = False

                                # Print out info w.r.t. status
                                if verbose == True:
                                    print("Cell", Cells_Obj[bc - 1].ID, "got burnt:", Check_Burnt)

                                # If burnt, update Burnlist
                                if Check_Burnt == True:
                                    BurntList.append(Cells_Obj[bc - 1].ID)

                        ##################################################################################################
                        #
                        ##################################################################################################         

                        if verbose == True:
                            print("\nResults")
                            print("Newly Burnt (and/or burning) List:", BurntList)

                        # Update cells status (burnt or not burnt), Update AvailCells and BurntCells sets
                        Aux_set = set(BurntList)  # newly burning
                        BurntCells_Set = BurntCells_Set.union(Aux_set)
                        BurntCells_Set = BurntCells_Set.union(set(BurnedOutList))
                        BurningCells_Set = BurningCells_Set.union(Aux_set)
                        AvailCells_Set = AvailCells_Set.difference(Aux_set)

                        # Releasing Memory 
                        del Aux_set

                        # Check current status
                        if verbose == True:
                            print("Available cells:", AvailCells_Set)
                            print("Non Burnable Cells:", NonBurnableCells_Set)
                            print("Burning cells:", BurningCells_Set)
                            print("Harvest cells:", HarvestCells_Set)
                            print("Burnt and Burning cells:", BurntCells_Set)

                        '''
                        Check if we need to keep it or use a dict
                        for t in range(Fire_Period[Year-1],Max_Fire_Periods+1):
                            BurntP[t-1]=list(BurningCells_Set)
                        '''

                        # Plot
                        if plottrue == True and FinalPlot == False and toPrint == True:
                            if SaveMem == True:
                                Plotter.forest_plotV3_FreeMem(Cells_Obj, emptylist, plotnumber,
                                                              Fire_Period[Year - 1], Year, False, Rows, Cols,
                                                              PlotPath, CoordCells, BurntCells_Set, Sim)
                                plotnumber += 1

                            if SaveMem != True:
                                Plotter.forest_plotV3(Cells_Obj, emptylist, plotnumber, Fire_Period[Year - 1],
                                                      Year, False, Rows, Cols, PlotPath, Sim)
                                plotnumber += 1

                        ##################################################################################################
                        #                                       Next period t+1
                        ##################################################################################################         

                        # Next Period: t=t+1. Update Weather
                        Fire_Period[Year - 1] += 1
                        toPrint = True

                        # New plot interval logic
                        if PlotInterval != -1 and Fire_Period[Year - 1] % PlotInterval != 0:
                            toPrint = False

                        if WeatherOpt != 'constant' and Fire_Period[
                            Year - 1] * FirePeriodLen / MinutesPerWP > weatherperiod + 1:
                            weatherperiod += 1
                            DF = Weather_Obj.update_Weather_FBP(DF, WeatherOpt, weatherperiod=weatherperiod)
                            if args.plotHour == True:
                                Plotter.forest_plotV3(Cells_Obj, emptylist, plotnumber, Fire_Period[Year - 1], Year,
                                                      False, Rows, Cols, PlotPath, Sim)
                                plotnumber += 1
                            if args.gridHour == True:
                                CSVGrid(Rows, Cols, AvailCells_Set, NonBurnableCells_Set, weatherperiod, GridPath)
                            if verbose:
                                print("Weather has been updated, weather period:", weatherperiod)

                        # Info about weather
                        if verbose == True:
                            Weather_Obj.print_info(weatherperiod)

                            if WeatherOpt == 'constant':
                                print("\n(NOTE: current weather is not used for ROS with constant option)")
                                print("\nCurrent week:", week_number)
                                print("Current Fire Period:", Fire_Period[Year - 1])

                        '''
                        CP Apr 2018: Check later if this is useful
                        '''
                        # Equivalence between fire periods and weeks (hours for the moment)
                        # 168 hours per week
                        if Fire_Period[Year - 1] >= 168 * 60 / FirePeriodLen:
                            week_number += 1

                # Extra breaking condition: Max fire periods then go to next year
                print("Next year...")
                Year += 1
                week_number = 1
                weatherperiod = 0

        ##################################################################################################
        #                                       Step 4: Results
        ##################################################################################################         
        # End of the code for one sim, output files with statistics and plots (if asked)
        for br in BurntCells_Set:
            if (br - 1) in Cells_Obj.keys():
                Cells_Obj[br - 1].Status = 2
        for bn in BurningCells_Set:
            if (bn - 1) in Cells_Obj.keys():
                Cells_Obj[bn - 1].Status = 2

        if nooutput == False:
            print("\n----------------------------- Results -----------------------------")

            # General results
            print("--------------------------- Solution without Heuristic --------------------------")
            print("Total Available Cells:    ", len(AvailCells_Set), "- % of the Forest: ",
                  np.round(len(AvailCells_Set) / NCells * 100.0, 3), "%")
            print("Total Burnt Cells:        ", len(BurntCells_Set), "- % of the Forest: ",
                  np.round(len(BurntCells_Set) / NCells * 100.0, 3), "%")
            print("Total Non-Burnable Cells: ", len(NonBurnableCells_Set), "- % of the Forest: ",
                  np.round(len(NonBurnableCells_Set) / NCells * 100.0, 3), "%")
            print("Total Harvested Cells:", len(HarvestCells_Set), ", % of the Forest: ",
                  np.round(len(HarvestCells_Set) / float(NCells) * 100.0, 2), "%")



            '''
            CP Apr 2018: Check special report
            '''
            special_report(args, Sim, AreaCells, NCells, Fire_Period, AvailCells_Set,
                           BurntCells_Set, NonBurnableCells_Set)

            # Statistics: Cells' status, Fire periods, start, end.
            if SaveMem != True:
                print("\n" + "Cells status")
                for i in Cells_Obj.keys():
                    if Cells_Obj[i].get_Status() == "Burnt":
                        print("Cell", i + 1, "status:", Cells_Obj[i].get_Status(), "Year:",
                              Cells_Obj[i].FireStartsSeason, ", Fire starts (fire period):", Cells_Obj[i].Firestarts)

            if SaveMem == True:
                for br in BurntCells_Set:
                    print("Cell", br, "status: Burnt")
                if verbose == True:
                    for av in AvailCells_Set:
                        print("Cell", av, "status: Available")

            # Total simulation time
            Final_Time = time.clock()
            print("\nFinal Time:", np.round(Final_Time, 3), "[s]")
            print("Total simulation time:", np.round(Final_Time - Initial_Time, 3), " [s]")

        # Plots
        if plottrue == True or args.plotHour == True:
            if SaveMem == True:
                Plotter.forest_plotV3_FreeMem(Cells_Obj, emptylist, plotnumber, 1,
                                              Year, False, Rows, Cols, PlotPath, CoordCells,
                                              BurntCells_Set, Sim)
                plotnumber += 1

            if SaveMem != True:
                Plotter.forest_plotV3(Cells_Obj, emptylist, plotnumber, 1, Year,
                                      False, Rows, Cols, PlotPath, Sim)
                plotnumber += 1

            # Check combine flag: if true, plots are combined with background
            if combine == True:
                for i in range(1, plotnumber):
                    Plotter.Mix(OutFolder, i, Sim)

        # if args.gridHour == True:
        #   CSVGrid(Rows, Cols, AvailCells_Set, NonBurnableCells_Set, weatherperiod+1, GridPath)

        # Scenarios and Excel
        # Excel
        if exceltrue == True and SaveMem != True:
            # Call the function
            Output_Grid.ExcelOutput(Cells_Obj, Sim, OutFolder, heuristic, TotalSims, TotalYears,
                                    NCells, BurntCells_Set, AvailCells_Set)

            print("Excel file has been successfully created ")

        # fScenarios
        # If we are not in the save-memory version, check all the initialized cells and print scenarios.dat
        if SaveMem != True and scenarios == True:
            for cell in BurntCells_Set:
                Cells_Obj[cell - 1].FS_definition()

            # Printing forest's data to a txt file
            Output_Grid.ScenarioOutput(TotalYears, Cells_Obj, NCells,
                                       BurntCells_Set, OutFolder, Sim,
                                       spotting, verbose)

            if nooutput == False:
                print("Scenarios have been successfully created")

            if SaveMem == True and scenarios == True and nooutput == False:
                print("\nScenarios cannot be output in Save Memory mode")

            if SaveMem == True and exceltrue == True and nooutput == False:
                print("\nStatistics cannot be output in Save Memory mode")

        # TBD, DLW? what do you do about weather in a new year?
        # CP Apr 2018: Can we take the same weather file from the beginning with a std value?

        # Forest Grid
        if OutputGrid == True:
            Output_Grid.OutputGrid(OutFolder, Rows, Cols, BurntCells_Set,
                                   Sim, spotting, verbose, AreaCells)
            if nooutput == False:
                print("Forest Grid has been created")

        # Messages
        if OutMessages == True:
            if verbose == True:
                print("\n--------------- Cell[i], Cell[j], hitPeriod, hitROS -------------")

            file = open(MessagesPath + "/MessagesFile.txt", "w")
            # file.write("Cell[i]  Cell[j]  hitPeriod[min]  hitROS[m/min]\n")
            for c in Cells_Obj.keys():
                for nb in Cells_Obj[c].FSCell.keys():
                    file.write(str(c + 1) + " " + str(nb) + " " + str(Cells_Obj[c].FSCell[nb][0]) + " " + str(
                        Cells_Obj[c].FSCell[nb][1]) + "\n")
                    if verbose == True:
                        print(c + 1, nb, Cells_Obj[c].FSCell[nb][0], Cells_Obj[c].FSCell[nb][1])
            file.close()

        Sim += 1

    # Final simulation time (all replications)
    if nooutput == True:
        Final_Time = time.clock()
        print("\nFinal Time:", np.round(Final_Time - Initial_Time, 3), "[s]")
