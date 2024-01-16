

__version__ = 0.03

# Importations
import ctypes
import pandas as pd
import numpy.random as npr
from itertools import repeat
import FBP2PY
import SpottingFBP
import numpy as np
import ellipses as el

global PromTuning
PromTuning = {"c1": {"FFactor":0.8931, "HFactor":0.91098, "BFactor":3.58792, "EFactor":1.0},
              "c2": {"FFactor":0.9281, "HFactor":0.97068, "BFactor":0.99623, "EFactor":1.06962},
              "c3": {"FFactor":0.8664, "HFactor":0.9333, "BFactor":3.58792, "EFactor":0.99153},
              "c4": {"FFactor":0.97756, "HFactor":1.0, "BFactor":1.0, "EFactor":1.0},
              "c5": {"FFactor":2.11274, "HFactor":2.94553, "BFactor":21.7273, "EFactor":2.01723},
              "c6": {"FFactor":0.97812, "HFactor":0.99959, "BFactor":3.60114, "EFactor":0.99959},
              "c7": {"FFactor":1.16421, "HFactor":8.24102, "BFactor":0.58547, "EFactor":6.22679},
              "d1": {"FFactor":1.22071, "HFactor":0.98826, "BFactor":1.43501, "EFactor":1.0},
              "d2": {"FFactor":1.62494, "HFactor":1.20127, "BFactor":1.9885, "EFactor":0.98406},
              "m1": {"FFactor":1.1577, "HFactor":7.74904, "BFactor":18.61587, "EFactor":16.70639},
              "m2": {"FFactor":0.99221, "HFactor":0.6201, "BFactor":1.19015, "EFactor":9.32454},
              "m3": {"FFactor":2.58868, "HFactor":1.00106, "BFactor":1.0, "EFactor":1.0},
              "m4": {"FFactor":1.70025, "HFactor":2.43285, "BFactor":2.41831, "EFactor":13.13039},
              "o1a": {"FFactor":1.07092, "HFactor":9.6896, "BFactor":18.55275, "EFactor":12.6258},
              "o1b": {"FFactor":1.38534, "HFactor":2.51217, "BFactor":1.08151, "EFactor":1.76923},
              "s1": {"FFactor":0.99125, "HFactor":0.80619, "BFactor":0.67432, "EFactor":0.99453},
              "s2": {"FFactor":1.19038, "HFactor":2.06655, "BFactor":0.50119, "EFactor":1.39225},
              "s3": {"FFactor":0.35157, "HFactor":0.86095, "BFactor":14.79993, "EFactor":5.29027}
             }

# Cells Class: Detailed information about each forest's cell, including the send/receive 
# messages functions (fire spread modcellel) and all the math involved when determining a new Fire    
class Cells:
    # Basic parameters
    StatusD = {0: "Available", 1: "Burning", 2: "Burnt", 3: "Harvested", 4:"Non Fuel"}
    #TerrainD = {0: "Soft", 1: "Medium", 2: "Hard"}   Not being used
    FTypeD = {0:"NonBurnable", 1: "Normal", 2: "Burnable"}
    FTypeD2 = {"M1":0, "M2":1,"M3":2,"M4":3,
               "C1":4,"C2":5,"C3":6,"C4":7,"C5":8,"C6":9,"C7":10,
               "D1":11,"S1":12,"S2":13,"S3":14,"O1a":15,"O1b":16,"D2":17}
    
    '''
    Constructor
    
    Inputs:
    ID           int
    Area         double
    Coord        double array (2D)
    Age          double
    FType        string
    FType2       integer
    Terrain      integer (not used)
    Vol          double
    Perimeter    double
    Status       int
    Adjacents    Dictionary {string: [int array]}
    Color        string
    RealID       int
    OutputGrid   boolean
    '''
    def __init__(self, ID, Area, Coord, Age, FType, FType2,
                 Vol, Perimeter, Status, Adjacents,
                 Color, RealID, OutputGrid):
        #Constructor
        self.ID = ID
        self.Area = Area
        self.Coord = Coord
        self.Age = Age
        self.FType = FType
        self.FType2 = FType2
        #self.Terrain = Terrain
        self.Vol = Vol
        self.Perimeter = Perimeter
        self.Status = Status
        self.Adjacents = Adjacents
        self.Color = Color
        self.RealID = RealID
        self._ctr2ctrdist = np.sqrt(self.Area) # assume a square
        
        if np.abs(4 * self._ctr2ctrdist - self.Perimeter) > 0.01 * self.Perimeter:
            print( "Cell ID=", self.ID, "Area=", self.Area, "Perimeter=", self.Perimeter)
            raise RuntimeError("Cell does not seem to be square based on area vs. perimeter")
        
        '''
        OutputGrid is Being modified
        '''
        # If grid is generated after simulation
        if OutputGrid:
            #self.GMsgList = [[] for i in repeat(None,12*7*24)]                      
            #self.FSCell = [[] for i in repeat(None,12*7*24)]    # Being modified  
            #self.FICell = [[] for i in repeat(None,12*7*24)]    # Being modified
            self.GMsgList = {}
            self.FSCell = {}     # Dict{CelliID (int): [period (int), CelljID (int)]}
            self.FICell = {}     # Dict{CelliID (int): period (int)}
            self.HPeriod = None
            
        self.Firestarts = 0
        self.Harveststarts = 0
        self.FireStartsSeason = 0
        self.FSCell = {}     # Dict{CelliID (int): [period (int), CelljID (int)]}
        
        # Total number of years/periods = 4 by default (hard coded)
        self.TYears = 4
        #self.GMsgListSeason = [[] for i in repeat(None,self.TYears)]
        self.GMsgListSeason = {}
        
        '''
        CP April 2018: Monetary values will be populated from the heuristic class, not needed NOW!
        '''
        #self.CH = [5 for i in range(0,self.TYears)]
        #self.CHVar = [5 for i in range(0,self.TYears)]
        #self.Value = None
        #self.Productivity = [10 for i in range(0,self.TYears)]
        '''
        heuristic class will use this info for determining the harvesting plan
        '''
        
        # Fire dynamic dictionaries
        self.FireProgress = {}  # dynamic; meters from the center on the axis
        self.AngleDict = {}     # static; indexed by neighbors contains angle
        self.ROSAngleDir = {}   # dynamic; indexed by active angles; contains current ROS
        self.DistToCenter = {}  # static; distance in meters
        self.angle_to_nb = {}   # static map

        self.TriedToSpot = False # one try to spot

    '''
    CP October 2017
    New function: populate angles, distances, and initialize ROS per axis
    Modified by dlw to use cell area to compute distances in meters.
    ASSUME square fire cells.
    
    Returns        void
    
    Inputs:
    CoorCells      array of 2D int arrays
    AvailSet       int set
    '''
    def InitializeFireFields(self, CoordCells, AvailSet):
        # Loop over neighbors
        for nb in self.Adjacents.values():
            if nb != None: 
                a = -CoordCells[nb[0]-1][0] + CoordCells[self.ID-1][0]
                b = -CoordCells[nb[0]-1][1] + CoordCells[self.ID-1][1]
                if a == 0:
                    if b>=0:
                        angle = 270
                    else:
                        angle = 90
                                        
                if b == 0:
                    if a >= 0:
                        angle = 180
                    else:                    
                        angle = 0
                                        
                if a!=0 and b!=0:
                    if a>0 and b >0:
                        angle = np.degrees(np.arctan(b/a))+180.0
                    if a>0 and b <0:
                        angle = np.degrees(-np.abs(np.arctan(b/a)))+180.0
                    if a<0 and b >0:
                        angle = np.degrees(-np.abs(np.arctan(b/a)))+360.0
                    if a<0 and b <0:
                        angle = np.degrees(np.arctan(b/a))
                            
                self.AngleDict[nb[0]] = angle
                if nb[0] in AvailSet:
                    self.ROSAngleDir[angle] = None
                self.angle_to_nb[angle] = nb[0]
                self.FireProgress[nb[0]] = 0.0
                self.DistToCenter[nb[0]] = np.sqrt(a*a + b*b) * self._ctr2ctrdist
    
    '''
    Returns       void
    
    Inputs:
    thetafire     double
    forward       double
    flank         double
    back          double
    offset        double
    base          double
    '''
    #New functions for calculating the ROS based on the fire angles
    def ros_distr(self, thetafire, forward, flank, back, EFactor):
        """
        CP May 2018: New Ellipse logic for distribution
        """
        
        '''
        Returns      double
        
        Inputs:
        offset       double
        base         double
        ros1         double
        ros2         double
        '''
        # Ellipse parameters
        #a = (forward + back) / 2
        #b = flank
        #c = (forward - back) / 2
        
        # Rho vector magnitude with respect to the focus of the ellipse (burning cell)
        def rhoTheta(theta, a, b):
            c2 = a**2 - b**2
            e = np.sqrt(c2) / a

            r1 = a * (1 - e ** 2)
            r2 = 1 - e * np.cos(theta*np.pi / 180.0)
            r = r1 / r2 

            return r
    
        # x and y points for fitting
        a = (forward + back) / 2
        x = [0.0, back, back, (forward + back) / 2, (forward + back) / 2, (forward + back)]
        y = [0.0, flank ** 2 / a, - (flank ** 2 / a), flank, -flank, 0.0]
        data = [x,y]
    
        # Fit the ellipse
        lsqe = el.LSqEllipse()
        lsqe.fit(data)
        center, a, b, phi = lsqe.parameters()
        
        # Ros allocation for each angle inside the dictionary
        for angle in self.ROSAngleDir:
            offset = angle - thetafire
            if offset < 0:
                offset += 360
            if offset >= 360:
                offset -= 360
            
            self.ROSAngleDir[angle] = rhoTheta(offset, a, b) * EFactor
    
     
    '''
    Returns           list[integers]   Important: we are sending a True sometimes, pick a special value -x for replacing it
    
    Inputs:
    period            int
    AvailSet          int set
    verbose           boolean
    df                Data frame
    coef              pointer
    spotting          boolean
    SpottingParams    Data frame
    CoordCells        array of 2D doubles arrays
    Cells_Obj         dictionary of cells objects
    '''
    def manageFire(self, period, AvailSet, verbose, df, coef, spotting,
                   SpottingParams, CoordCells, Cells_Obj, args):
        """
        some inputs:
            args: we just read a lot of options straight from the args
        """
        # Access to global dictionary
        global PromTuning
        
        # Aux variable for looping until fire reaches another cell 
        Repeat = "False"
        msg_list_aux = []
        
        # Create an empty message list
        msg_list = []

        # Check spotting option (true if flag)
        if spotting and not self.TriedToSpot:
            self.TriedToSpot = True
            
            # Output spotting parameters
            if verbose:
                print("SPOTANGLE:", SpottingParams["SPOTANGLE"])
                print("SPOT0PROB:", SpottingParams["SPOT0PROB"])
                print("SPOT10TIME:",SpottingParams["SPOT10TIME"])
                
            #xxx get the wind speed and direction from the df xxxx
            spot_list = SpottingFBP.SpottingFBP(Cells_Obj, CoordCells, AvailSet,
                                                df.iloc["WD"][0],
                                                df.iloc["WS"][0],
                                                SpottingParams, verbose)
            print ("debug: spot_list=", spot_list)
            
            # Populate the msg list
            for si in spot_list:
                msg_list.append(si)

        # Compute main angle and ROSs: forward, flanks and back
        mainstruct, headstruct, flankstruct, backstruct = FBP2PY.CalculateOne(df,coef,self.ID,verbose)
        
        # Stochastic ROS (standard deviation)
        ROSCV = args.ROS_CV
        if ROSCV == 0:
            ROSRV = 0
        else:
            ROSRV = npr.randn()

        # Cartesian Angle debug
        cartesianAngle =  270 - mainstruct.raz
        if cartesianAngle < 0:
            cartesianAngle += 360
        
        # Display if verbose True (FBP ROSs, Main angle, and ROS std (if included))
        if verbose == True:
                print("Main Angle:", mainstruct.raz)
                print("Cartesian Angle:", cartesianAngle)
                print("FBP Front ROS Value:", headstruct.ros * args.HFactor)
                print("FBP Flanks ROS Value:", flankstruct.ros * args.FFactor)
                print("FBP Rear ROS Value:", backstruct.ros * args.BFactor)
                print("Std Normal RV for Stochastic ROS CV:", ROSRV)

                
        # Jan 2018: if cell cannot send, then it will be burned out in the main loop
        HROS =  (1 + ROSCV*ROSRV) * headstruct.ros * args.HFactor
        if verbose == True:
            print("Sending message conditions")
            print("HROS:", HROS, " Threshold:", args.ROS_Threshold)
            print("HeadStruct FI:", headstruct.fi, " Threshold:", args.HFI_Threshold)
            
        if HROS > args.ROS_Threshold and headstruct.fi > args.HFI_Threshold:
            Repeat = "True"  #xxxxxxxx DLW: think about this a little more (feb 2018)
            '''
            CP April 2018: Need to modify this logic for better performance... WIP
            CP October 2017: Repeat = True allows us to indicate to the sim that the fire in this cell
            is "alive" and we need to take into account that maybe there is no message 
            sent in the current period, but maybe in the next one....

            major change in the original loop logic of the simulator....

            Workaround: add this new variable and use it as a new condition for moving to the 
            next year...
                '''
            if verbose == True:
                print("Repeat condition: ", Repeat)
                print("Cell can send messages")

            # Delete adjacent cells that are not available 
            for angle in self.angle_to_nb:
                nb = self.angle_to_nb[angle]

                if nb not in AvailSet and angle in self.ROSAngleDir:
                    self.ROSAngleDir.pop(angle)

            # ROS distribution method
            #self.ros_distr(mainstruct.raz, headstruct.ros * args.HFactor, flankstruct.ros * args.FFactor, 
             #              backstruct.ros * args.BFactor)
            if args.PromTuning == False:
                self.ros_distr(cartesianAngle, headstruct.ros * args.HFactor, flankstruct.ros * args.FFactor, 
                               backstruct.ros * args.BFactor, args.EFactor)
            # Prometheus tuned
            else:
                auxType = df.iloc[self.ID-1:self.ID].fueltype.values[0]
                #print("Debugging aux type variable for prometheus tuning:", auxType)
                self.ros_distr(cartesianAngle, 
                               headstruct.ros * PromTuning[auxType]["HFactor"] * args.HFactor, 
                               flankstruct.ros * PromTuning[auxType]["FFactor"] * args.FFactor,
                               backstruct.ros * PromTuning[auxType]["BFactor"] * args.BFactor,
                               PromTuning[auxType]["EFactor"] * args.EFactor)
            
                
            if verbose == True:
                print ("ROSAngleDir Cell", self.ID,":",self.ROSAngleDir)
                print ("Fire Progress before this update", self.ID, ":", self.FireProgress)

            '''
            Fire progress using ROS from burning cell, not the neighbors
            '''
            # Update Fireprogress 
            for angle in list(self.ROSAngleDir):
                nb = self.angle_to_nb[angle]
                ros = (1 + ROSCV*ROSRV) * self.ROSAngleDir[angle]
                if verbose:
                    print ("    angle, realized ros in m/min",angle, ros)
                self.FireProgress[nb] += ros * args.input_PeriodLen # fire periodlen

                # If the message arrives to the adjacent cell's center, send a message
                if self.FireProgress[nb] >= self.DistToCenter[nb]:
                    
                    # New info for heuristics: FSCell[Cellj] = [hitPeriod, hitROS]
                    self.FSCell[nb] = [period * args.input_PeriodLen, self.ROSAngleDir[angle]] 
                    
                    # Messages list and angle dir pop
                    msg_list.append(nb)
                    self.ROSAngleDir.pop(angle) 

                    if verbose == True:
                        print ("Fire reaches the center of the cell", nb, 
                               "Distance to cell (in meters) was", self.DistToCenter[nb])
                        msg_list.sort()
                        print("MSG list:", msg_list)
                        print("Cell", nb, "popped out from the ROSAngleDir")
                        print("ROSAngleDir Cell", self.ID,":",self.ROSAngleDir)

                '''
                    If we have not reached the center of an adjacent cell but the fire is still "alive",
                    send a True value to the msg_list for using it as a flag in the main code
                '''

                if self.FireProgress[nb] < self.DistToCenter[nb] and Repeat == "True" and "True" not in msg_list_aux:
                    if verbose == True:
                        print("A Repeat = TRUE flag is sent in order to continue with the current fire.....")
                        print("Main workaround of the new sim logic.....")
                    msg_list_aux.append(Repeat)

                '''
                    Workaround....
                '''
                        
        # If original is empty (no messages but fire is alive if aux_list is not empty)
        if len(msg_list) == 0:
            if len(msg_list_aux) > 0:
                msg_list = msg_list_aux
            else:
                self.Status = 2   # we are done sending messages, call us burned
                
                        
        '''
        DLW notes Jan 2018: the status is not perfect, but close. Also, the logic in this routine should
        be revamped now that we know how we want fires to work within a cell.
        '''        
                        
        if verbose == True:
            print( " ----------------- End of new manageFire function -----------------")
        return msg_list
    
    
    
    
    
    
    '''
    Returns     boolean  
    
    Inputs:
    period      int
    NMsg        int
    Season      int
    verbose     boolean
    df          Data frame
    coef        pointer
    ROSThresh   double
    
    TODO CP 2018: the ROS for the threshold should be the ROS that is coming from the sender cell, not its own
    '''
    
    # Get burned new logic: Checks if the ROS on its side is above a threshold for burning
    def get_burned(self, period,NMsg,Season,verbose,df,coef, args):
        """
        returns true of the cell is fully burned (I think: dlw jan 2018)
        Maybe this needs to move to the manageFire function.
        """
        if verbose == True:
            print("\nROS Threshold get_burned method")
            print("ROSThresh:", args.ROS_Threshold)
            
        # Compute main angle and ROSs: forward, flanks and back
        mainstruct, headstruct, flankstruct, backstruct = FBP2PY.CalculateOne(df,coef,self.ID)
        
        # Cartesian Angle debug
        cartesianAngle =  270 - mainstruct.raz#  360 - mainstruct.raz 
        if cartesianAngle < 0:
            cartesianAngle += 360
            
        # Display if verbose True
        if verbose == True:
            print("Main Angle:", mainstruct.raz )
            print("Cartesian Angle:", cartesianAngle )
            print("Front ROS Value:", headstruct.ros * args.HFactor)
            print("Flanks ROS Value:", flankstruct.ros * args.FFactor)
            print("Rear ROS Value:", backstruct.ros * args.BFactor)
            print("Head ROS value:", headstruct.ros * args.HFactor)
        
        # Check a threshold for the ROS
        if headstruct.ros * args.HFactor > args.ROS_Threshold: 
            
            # Update status
            self.Status = 1 # burning
            self.Firestarts = period
            self.FireStartsSeason = Season
            self.BurntP = period
            
            return True
        
        # Not burned
        else:
            return False
            
    '''
    End new functions
    '''
    
    
    
    
    
    
    
    # Old functions
    '''
    Returns            void
    
    Inputs:  
    AdjacentCells      dictionary{string:[array integers]}
    '''
    def set_Adj(self,AdjacentCells):
        # Set (if needed) adjacent cells again
        self.Adjacents = AdjacentCells

    '''
    Returns            void
    
    Inputs:  
    Status_int         int
    '''
    def set_Status(self,Status_int):
        # Change the status of the cell: 0 available, 1 burning, 2 harvested, 3 burnt
        self.Status = Status_int

    '''
    Returns            string
    
    Inputs:  
    '''
    def get_Status(self):
        # Returns cell status
        return self.StatusD[self.Status]
            
   
    
    '''
    Returns           boolean
    
    Inputs:
    period            int
    Season            int
    IgnitionPoints    array of int
    df                Data frame
    coef              pointer
    ROSThresh         double
    HFIThreshold      double
    '''
    def ignition(self, period, Year, IgnitionPoints, df, coef, args):
        #Determines if a cell ignites, based on the period, cell characteristics and poisson strike distribution
        # dlw jan 2018: does the FBP have an ignition function xxxx ??
	verbose = args.verbose_input        
        # If we have ignition points
        if IgnitionPoints != "":
            self.Status = 1
            self.Firestarts = period
            self.FireStartsSeason = Year
            self.BurntP = period
            
            '''
            CP Apr 2018: FI = Firestarts, can be eliminated
            '''
            if hasattr(self, "FICell"):
                self.FICell[period-1] = 1 
            return True
            
        
        # ignite if implied head ros is high enough
        else:
            mainstruct, headstruct, flankstruct, backstruct = FBP2PY.CalculateOne(df,coef,self.ID)
                        
            # Cartesian Angle debug
            cartesianAngle =  270 - mainstruct.raz 
            if cartesianAngle < 0:
                cartesianAngle += 360    
            
            # Display if verbose True
            if verbose == True:
                    print("In ignition function")
                    print( "Main Angle:", mainstruct.raz)
                    print( "Cartesian Angle:", cartesianAngle )
                    print( "Front ROS Value:", headstruct.ros)
                    print( "Flanks ROS Value:", flankstruct.ros)
                    print( "Rear ROS Value:", backstruct.ros)
             
            
            # Check a threshold for the ROS
            if headstruct.ros * args.HFactor > args.ROS_Threshold and headstruct.fi > args.HFI_Threshold:
                if verbose == True:
                    print("Head (ROS, FI) values of", headstruct.ros * args.HFactor, 
                          headstruct.fi, " are enough for ignition")
                
                self.Status = 1
                self.Firestarts = period
                self.FireStartsSeason = Year
                self.BurntP = period
                
                '''
                CP Apr 2018: Idem as before...
                '''
                if hasattr(self, "FICell"):
                    self.FICell[period-1] = 1 
                return True
            else:
                return False        
            
    
    
    '''
    CP Apr 2018: NOT NEEDED NOW!!! DO NOT TRANSLATE TO C
    Returns     list of integers
    
    Inputs:
    period      int
    MsgLists    array of arrays (int)
    Season      int
    verbose     boolean
    '''
    def got_burnt_from_mem(self,period,MsgLists,Season,verbose):
        #Compute FS parameter
        # dlw feb 2018: only called if OutputGrid
        counter=1
        auxlist = []
        for sublist in MsgLists:
            
            if self.ID in sublist:
                auxlist.append(counter)
                counter+=1
            else:
                counter+=1
        
        self.GMsgList[period-1] = auxlist
        
        if len(self.GMsgList[period-1]) > 0:
            self.GMsgListSeason[Season].append(self.GMsgList[period-1])
        
        if verbose == True:
            print("Cell", self.ID, "got messages from the following cells in this fire period (hour):",
                   self.GMsgList[period-1])
    
        return self.GMsgList
    
    '''
    CP Apr 2018: NOT NEEDED NOW!!! DO NOT TRANSLATE TO C
    Returns     void
    
    Inputs:
    '''
    def FS_definition(self):
        #Determines if FS (fire start) is one or not for any period,
        # indicating the sender cell's ID.
        # dlw feb 2018: only called if OutputGrid
        self.FSCell[self.Firestarts-1] = self.GMsgList[self.Firestarts-1]
        
        for y in range(0,self.TYears):
                        
            if (self.FireStartsSeason-1) == y and len(self.GMsgListSeason[y])>= 1:
                self.FSCell[self.Firestarts-1] = self.GMsgListSeason[y][(len(self.GMsgListSeason[y])-1)]
                
       
    
    
    '''
    Returns      void
    Inputs
    ID           int
    period       int
    '''
    def harvested(self,ID,period):
        # Cell is harvested
        self.Status = 3
        self.Harveststarts = period
              
            
    
    
    '''
    Returns      void
    '''
    def print_info(self):
        #Print Cell information
        print ("Cell Information" + "\n" +" ID = " + str(self.ID) , 
               "\nStatus = "+ str(self.StatusD[self.Status]),
               "\nCoordinates = " +str(self.Coord),
               "\nArea = "+str(self.Area),
               "\nVol = "+str(self.Vol),
               "\nAge = "+ str(self.Age),
               "\nFTypes = "+ str(self.FTypeD[self.FType]),
               #"\nTerrain: "+str(self.TerrainD[self.Tmaerrain]),
               "\nAdjacents = "+str(self.Adjacents))
        
        
        

        


# Fuel Coeff class: defines the structure of the fuel coefficients (using ctypes)
class fuel_coeffs(ctypes.Structure):
    _fields_ = [('fueltype', ctypes.c_char*4), 
                ('q', ctypes.c_float),
                ('bui0', ctypes.c_float),
                ('cbh', ctypes.c_float),
                ('cfl', ctypes.c_float),
                ('a', ctypes.c_double),
                ('b', ctypes.c_double),
                ('c', ctypes.c_double)]

