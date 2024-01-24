# Importations
from Cell2Fire.Stats import *
from Cell2Fire.Heuristics import *
import numpy as np
import os

# Basic Operational Environment
class Cell2FireEnv_Operational:
    def __init__(self, env):
        """
        constructor
        """
        # Time step reset
        self._nepisode = -1
        self._global_tstep = 0
        self._tstep = 0
        self.env = env

    def reset(self):
        """
        reset environment and outputs the initial state
        """
        # Reset
        state = self.env.InitSim()
        self._nepisode += 1
        
        # Update steps, plot, and grid (if needed)
        self.env.PlotStateGlobal(self._nepisode)
        self.env.outputGrid(self._nepisode)
        self._tstep = 1
        self._global_tstep += 1
        
        return state
        
    
    def step(self, action):
        """
        takes one operational step for the environment outputs reward, state
        and wether the episode is done or not
        """
        # Step
        obs, reward, done = self.env.OperationalStep(action)
        
        # Update steps
        self._global_tstep += 1
        self._tstep += 1
        
        # Plot and grid
        if done == 0:
            self.env.PlotStateGlobal(self._nepisode, done)
            self.env.outputGrid(self._nepisode, done)
        
        return obs, reward, done
    
    def statistics(self):
        """
        Postprocessing such as generate statistics
        """
        # MultiFire Plot
        self.env.MultiFire()
  
        # Stats object
        StatsPrinter = Statistics(OutFolder=self.env._OutFolder,
                                 StatsFolder=os.path.join(self.env._OutFolder, "Stats"),
                                 MessagesPath=self.env._MessagesPath,
                                 Rows=self.env._Rows,
                                 Cols=self.env._Cols,
                                 NCells=self.env._NCells,
                                 boxPlot=True,
                                 CSVs=True,
                                 statsGeneral=True, 
                                 statsHour=True,
                                 histograms=True,
                                 BurntProb=True,
                                 nSims=self.env._TotalSims,
                                 verbose=self.env._verbose)

        # Hourly Stats
        print("Hourly stats...")
        StatsPrinter.HourlyStats()

        # General Stats
        print("General stats...")
        StatsPrinter.GeneralStats()

        # Fire Spread Graphs
        print("Generating global fire spread evolution...")
        for v in tqdm(range(4)):
            StatsPrinter.GlobalFireSpreadEvo(self.env.getCoords, 
                                             onlyGraph=True,
                                             version=v)

        # Fire Spread Graphs (individual)
        print("Generating individual Fire Spread plots...")
        for n in tqdm(range(1, self.env._TotalSims + 1)):
            StatsPrinter.SimFireSpreadEvo(n, self.env.getCoords, 
                                          self.env.getColorsDict, 
                                          H=None, version=0,
                                          print_graph=True, 
                                          analysis_degree=False,
                                          onlyGraph=False)

            StatsPrinter.SimFireSpreadEvoV2(n, self.env.getCoords,
                                            self.env.getColorsDict, 
                                            H=None, version=0, 
                                            onlyGraph=True)

               
    
    def init_heuristic(self, args, runHeur=False):
        """
        Heuristic object and application
        """
        if runHeur is False:
            # Values
            self._FPVGrids = True
            self._onlyGraphs = False
            self._GenSel = False
            self._GreedySel = True 

            HOutFolder = self.env._OutFolder
            MessagePath = self.env._MessagesPath
        
        else:
            # Values
            self._FPVGrids = False
            self._onlyGraphs = False
            self._GenSel = self.env._GASelection
            self._GreedySel = not self.env._GASelection
            
            HOutFolder = self.env._OutFolder #os.path.join(self.env._OutFolder[:-1] + "_Heuristic/")
            MessagePath = self.env._msgHeur
                
        # Heuristic parameters
        self._Demand = np.full(self.env._TotalYears, 20)                      # To be read from csv or cmd line
        self._CellUtility = np.full(shape=(self.env._NCells), fill_value=10)  # Same as demand
                
        # Heur object
        self._HeurObject = Heuristic(version=self.env._heuristic,       # Heuristic ID
                                     MessagePath=MessagePath,           # Path to the messages (FPV and graphs)
                                     InFolder=self.env._InFolder,       # Instance Folder path
                                     OutFolder=self.env._OutFolder,     # Output Folder path (for heuristic solution)
                                     AvailCells=set(),                  # AvailCells
                                     BurntCells=set(),                  # BurntCells
                                     HarvestedCells=set(),              # Harvested Cells
                                     AdjCells=self.env.getAdj,          # Adjacent cells info
                                     NCells=self.env._NCells,           # Number of cells inside the forest
                                     Cols=self.env._Cols,               # Number of columns inside the forest 
                                     Rows=self.env._Rows,               # Number of rows inside the forest
                                     Year=self.env.getYear,             # Current year
                                     Demand=self._Demand,               # Demand array (per year)
                                     FPVGrids=self._FPVGrids,           # Boolean flag: Generate FPV grids/Heatmaps
                                     GeneticSelection=self._GenSel,     # Gen alg for selecting the best connected patch (adjacency)
                                     GreedySelection=self._GreedySel,   # Greedy selection (top to bottom) for adjacency constraints
                                     verbose=self.env._verbose)         # Verbosity level (False = minimum)

        if not os.listdir(MessagePath) and self.env._heuristic >= 6:
            print("No message files: FPV heuristics cannot be used")
            
        else:    
            # Init Graph (FPV)
            self._HeurObject.initGraph_FPV(self.env.getVol, 
                                           args.ngen,
                                           args.npop,
                                           args.tsize,
                                           args.cxpb,
                                           args.mutpb,
                                           args.indpb)
       
        if self.env._heuristic < 6:
            # Init Graph (BP) - CP: checking best way to split logics
            self._HeurObject.initGraph_BP()
                        
    
    def getAction(self):
        
        #print("FPeriod:", self.env.getFirePeriod, "\nAction")
        # Tactical actions
        if self.env.getFirePeriod == 0:
            
            # Run Heuristics
            action = list(self._HeurObject.runHeur(self.env.getAvailCells, 
                                                   self.env.getAdj, 
                                                   self.env.getVol, 
                                                   self._Demand, 
                                                   self._CellUtility, 
                                                   self.env.getYear))
            
        # If not the beginning of the fire season, no actions 
        else:
            action = [-1]

        # Info
        if self.env._verbose:
            print("Action (Heuristic):", action)
        
        return action

            
            
            
    
    def FPV_Plot(self, IndPlot=False, GlobalPlot=False):
        # Plot
        if GlobalPlot:
            self._HeurObject.Global_FPVPlot(normalized=True)        
            
    

# Basic Tactical Environment
class Cell2FireEnv_Tactical:
    def __init__(self, env):
        # Time step reset
        self._nepisode = -1
        self._global_tstep = 0
        self._tstep = 0
        self.env = env

    def reset(self):
        """
        reset environment and outputs the initial state
        """
        # Reset
        self.env.InitSim()
        self._nepisode += 1
        self._nyear = 1
        
        # Process state and plot if needed
        self.env.PlotStateGlobal(self._nepisode)
        self._tstep = 1
        self._global_tstep += 1
        
        return self.state

    def process_state(self):
        """
        get forest and coordinates np arrays from env and output the flatten
        state
        """
        self.state = [self.env.getState]
        
    def step(self, action):
        """
        takes one tactical step for the environment outputs reward, state
        and wether the episode is done or not
        """
        obs, rewards, dones = self.env.TacticalStep()
        
        self._global_tstep += 1
        self._tstep += 1
        
        return obs, rewards, dones
