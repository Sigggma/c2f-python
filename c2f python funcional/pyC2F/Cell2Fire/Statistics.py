# Importations
import pandas as pd
import numpy as np

# Matplotlib and Seaborn
import matplotlib
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib import rcParams
import matplotlib.pyplot as plt
from matplotlib.pylab import *
import matplotlib as mpl
import matplotlib.cm as cm
import matplotlib.patches as patches
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

# Classes
from Cell2Fire.coord_xy import *
import ReadDataPrometheus

# Extra importations
import os 
import itertools
from operator import itemgetter
from tqdm import tqdm

# Statistics Class
class StatisticsObj(object):
    # Initializer
    def __init__(self,
                 OutFolder="",
                 StatsFolder="",
                 MessagesPath="",
                 Rows=0,
                 Cols=0,
                 NCells=0,
                 boxPlot=True,
                 CSVs=True,
                 statsGeneral=True, 
                 statsHour=True,
                 histograms=True,
                 BurntProb=True,
                 nSims=1,
                 verbose=False):
    
        self._OutFolder = OutFolder
        self._MessagesPath = MessagesPath
        self._Rows = Rows
        self._Cols = Cols
        self._NCells = NCells
        self._boxPlot = boxPlot
        self._CSVs = CSVs
        self._statsGeneral = statsGeneral
        self._statsHour = statsHour
        self._histograms = histograms
        self._BurntProb = BurntProb
        self._nSims = nSims
        self._verbose = verbose

        # Create Stats path (if needed)
        if StatsFolder != "":
            self._StatsFolder = StatsFolder
        else:
            self._StatsFolder = os.path.join(OutFolder, "Stats")
        if not os.path.exists(self._StatsFolder):
            if self._verbose:
                print("creating", self._StatsFolder)
            os.makedirs(self._StatsFolder)

            
    ####################################
    #                                  #
    #            Methods               #
    #                                  #
    ####################################
    # Boxplot function
    def BoxPlot(self, Data, xx="Hour", yy="Burned", xlab="Hours", ylab="# Burned Cells", 
                pal="Reds", title="Burned Cells Evolution", Path=None, namePlot="BoxPlot",
                swarm=True):
        
        # Figure
        plt.figure(figsize = (15, 9)) 

        # Font sizes
        plt.rcParams['font.size'] = 16
        plt.rcParams['axes.labelsize'] = 16
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['xtick.labelsize'] = 16
        plt.rcParams['ytick.labelsize'] = 16
        plt.rcParams['legend.fontsize'] = 16
        plt.rcParams['figure.titlesize'] = 18

        # axes
        ax = plt.subplot(111)                    
        ax.spines["top"].set_visible(False)  
        ax.spines["right"].set_visible(False)
        ax.get_xaxis().tick_bottom()  
        ax.get_yaxis().tick_left() 

        # Title and labels
        plt.title(title)

        #sns.set(style="darkgrid", font_scale=1.5)
        ax = sns.boxplot(x=xx, y=yy, data=Data, linewidth=2.5, palette=pal).set(xlabel=xlab,ylabel=ylab)    
        if swarm == True:
            ax = sns.swarmplot(x=xx, y=yy, data=Data, linewidth=2.5, palette=pal).set(xlabel=xlab,ylabel=ylab)   

        # Save it
        if Path == None:
            Path = os.getcwd() + "/Stats/"
            if not os.path.exists(Path):
                os.makedirs(Path)

        plt.savefig(os.path.join(Path, namePlot + ".png"), dpi=200, bbox_inches='tight')
        plt.close("all")
        
    
    # Histograms
    def plotHistogram(self, df, NonBurned=False, xx="Hour", xmax=6, KDE=True, title="Histogram: Burned Cells",
                      Path=None, namePlot="Histogram"):
        
        # Modify rc parameters (Matplotlib/Seaborn)
        rcParams['patch.force_edgecolor'] = True
        rcParams['patch.facecolor'] = 'b'

        # Figure Size
        plt.figure(figsize = (15, 9)) 

        # Font sizes
        plt.rcParams['font.size'] = 16
        plt.rcParams['axes.labelsize'] = 16
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['xtick.labelsize'] = 16
        plt.rcParams['ytick.labelsize'] = 16
        plt.rcParams['legend.fontsize'] = 16
        plt.rcParams['figure.titlesize'] = 18

        # axes
        ax = plt.subplot(111)                    
        ax.spines["top"].set_visible(False)  
        ax.spines["right"].set_visible(False)
        ax.get_xaxis().tick_bottom()  
        ax.get_yaxis().tick_left() 

        # Title and labels
        plt.title(title)

        # Make default histogram of sepal length
        if KDE == True:
            g = sns.distplot(df[df[xx] == xmax]["Burned"], bins=10, kde=KDE, rug=False).set(xlabel="Number of Cells", ylabel="Density")
            if NonBurned == True: 
                g += sns.distplot(df[df[xx] == xmax]["NonBurned"], bins=10, kde=KDE, rug=False).set(xlabel="Number of Cells", ylabel="Density")
        else:
            g = sns.distplot(df[df[xx] == xmax]["Burned"], bins=10,  kde=KDE, rug=False).set(xlabel="Number of Cells", ylabel="Frequency")
            if NonBurned == True:
                g += sns.distplot(df[df[xx] == xmax]["NonBurned"], bins=10, kde=KDE, rug=False).set(xlabel="Number of Cells", ylabel="Frequency")

        # Save it
        if Path == None:
            Path = os.getcwd() + "/Stats/"
            if not os.path.exists(Path):
                os.makedirs(Path)

        plt.savefig(os.path.join(Path, namePlot + ".png"), dpi=200, bbox_inches='tight')
        plt.close("all")

    # Burnt Probability Heatmap
    def BPHeatmap(self, WeightedScar, Path=None, nscen=10, sq=False, namePlot="BP_HeatMap"):
        # Figure size
        plt.figure(figsize = (15, 9)) 

        # Font sizes
        plt.rcParams['font.size'] = 16
        plt.rcParams['axes.labelsize'] = 16
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['xtick.labelsize'] = 16
        plt.rcParams['ytick.labelsize'] = 16
        plt.rcParams['legend.fontsize'] = 16
        plt.rcParams['figure.titlesize'] = 18

        # axes
        ax = plt.subplot(111)                    
        ax.spines["top"].set_visible(False)  
        ax.spines["right"].set_visible(False)
        ax.get_xaxis().tick_bottom()  
        ax.get_yaxis().tick_left() 

        # Title and labels
        plt.title("Fire Probability Heatmap (nscen="+str(nscen)+")")

        # Modify existing map to have white values
        cmap = cm.get_cmap('RdBu_r')
        lower = plt.cm.seismic(np.ones(100)*0.50)
        upper = cmap(np.linspace(1 - 0.5, 1, 90))
        colors = np.vstack((lower, upper))
        tmap = matplotlib.colors.LinearSegmentedColormap.from_list('terrain_map_white', colors)

        # Create Heatmap
        ax = sns.heatmap(WeightedScar, center=0.0, xticklabels=5, yticklabels=5, 
                         square=sq, cmap=tmap, vmin=0, vmax=1, annot=False)    

        # Save it
        if Path == None:
            Path = os.getcwd() + "/Stats/"
            if not os.path.exists(Path):
                os.makedirs(Path)

        for _, spine in ax.spines.items():
            spine.set_visible(True)

        plt.savefig(os.path.join(Path, namePlot+".png"), dpi=200, bbox_inches='tight', 
                    pad_inches=0, transparent=False)
        
        plt.close("all")

    # Fire Spread evolution plot (global sims)
    def GlobalFireSpreadEvo(self, G, CoordCells, onlyGraph=True, version=0):
        # V0 Frequency
        coord_pos = dict() # Cartesian coordinates
        for i in G.nodes:
            coord_pos[i] = CoordCells[i-1] + 0.5
        
        # Font sizes
        plt.rcParams['font.size'] = 16
        plt.rcParams['axes.labelsize'] = 16
        plt.rcParams['axes.titlesize'] = 16
        plt.rcParams['xtick.labelsize'] = 16
        plt.rcParams['ytick.labelsize'] = 16
        plt.rcParams['legend.fontsize'] = 16
        plt.rcParams['figure.titlesize'] = 18

        # axes
        ax = plt.subplot(111)                    
        ax.get_xaxis().tick_bottom()  
        ax.get_yaxis().tick_left() 
        plt.ylim(bottom=0)

        # Print nodes
        if onlyGraph == False:
            nx.draw_networkx_nodes(G, pos = coord_pos,
                                   node_size = 5,
                                   nodelist = list(G.nodes),
                                   node_shape='s',
                                   node_color = Colors)

        edges = G.edges()
        weights = [G[u][v]['weight'] for u,v in edges]

        if version == 0:
            # Fixed edge color (red), different scaled width
            nx.draw_networkx_edges(G, pos = coord_pos, edge_color = 'r',
                                   width = weights/np.max(weights), arrowsize=3)

        if version == 1:
            # Edge = Frequency, width = frequency
            nx.draw_networkx_edges(G, pos = coord_pos, edge_color = weights, edge_cmap=plt.cm.Reds,
                                   width = weights/np.max(weights), arrowsize=3)

        if version == 2:
            # Edge = Frequency, width = frequency
            nx.draw_networkx_edges(G, pos = coord_pos, edge_color = weights/np.max(weights), edge_cmap=plt.cm.Reds,
                                  width = weights/np.max(weights), arrowsize=3)

        if version == 3:
            # Edge = frequency, fixed width
            nx.draw_networkx_edges(G, pos = coord_pos, edge_color = weights, edge_cmap=plt.cm.Reds,
                                  width = 1.0, arrowsize=3)

        #Title
        plt.title("Propagation Tree and Frequency")
        plt.axis('scaled')
        plt.savefig(os.path.join(self._StatsFolder, "SpreadTree_FreqGraph_V" + str(version) + ".png"), 
                    dpi=200, figsize=(200, 200), 
                    bbox_inches='tight', transparent=False)
        plt.close("all")
        
    
    # Fire Spread evolution plots (per sim)
    def SimFireSpreadEvo(self, nSim, CoordCells, Colors, G, H=None, version=0,
                         print_graph=True, analysis_degree=True, onlyGraph=False):
        # V1
        # If no graph, read it
        if H == None:
            H = nx.read_edgelist(path = os.path.join(self._MessagesPath, "MessagesFile" + str(nSim) + ".txt"),
                                 create_using = nx.DiGraph(),
                                 nodetype = int,
                                 data = [('time', float), ('ros', float)])
            
        # Cartesian positions
        coord_pos = dict() 

        for i in G.nodes:
            coord_pos[i] = CoordCells[i-1] + 0.5
        
        # We generate the plot
        if print_graph:

            # plt.figure(figsize = (15, 9)) 

            # Font sizes
            plt.rcParams['font.size'] = 16
            plt.rcParams['axes.labelsize'] = 16
            plt.rcParams['axes.titlesize'] = 16
            plt.rcParams['xtick.labelsize'] = 16
            plt.rcParams['ytick.labelsize'] = 16
            plt.rcParams['legend.fontsize'] = 16
            plt.rcParams['figure.titlesize'] = 18

            # axes
            ax = plt.subplot(111)                    
            ax.get_xaxis().tick_bottom()  
            ax.get_yaxis().tick_left() 

            # Dimensionamos el eje X e Y
            plt.axis([-1, self._Rows, -1, self._Cols])

            # Print graph and nodes
            if onlyGraph == False:
                nx.draw_networkx_nodes(G, pos = coord_pos,
                                       node_size = 5,
                                       nodelist = list(G.nodes),
                                       node_shape='s',
                                       node_color = Colors)

            nx.draw_networkx_edges(H, pos = coord_pos, edge_color = 'r', width = 0.5, arrowsize=4)

            #Title
            plt.title("Propagation Tree")
            plt.axis('scaled')

            # Save plot
            plt.savefig(os.path.join(self._OutFolder, "Plots", "Plots" + str(nSim), 
                                     "PropagationTree" + str(nSim) +".png"), 
                        dpi=200, figsize=(200, 200), 
                        bbox_inches='tight', transparent=False)

        # Hitting times and ROSs
        if analysis_degree == True:
            dg_ros_out = sorted(list(H.out_degree(weight = 'ros')), key = itemgetter(1), reverse = True)
            dg_time_out = sorted(list(H.out_degree(weight = 'time')), key = itemgetter(1))

            plt.figure(2)
            dg_ros = dict(H.degree(weight='ros'))
            plt.hist(dg_ros.values())
            plt.title('ROS hit Histogram')
            plt.savefig(os.path.join(self._OutFolder, "Plots", "Plots" + str(nSim), 'HitROS_Histogram.png'))
            
            plt.figure(3)
            dg_time = dict(H.degree(weight='time'))
            plt.hist(dg_time.values())
            plt.title('Time hit Histogram')
            plt.savefig(os.path.join(self._OutFolder, "Plots", "Plots" + str(nSim), 'HitTime_Histogram.png'))

        plt.close("all")
        
    
    # Fire Spread evolution plots (per sim, version 2)
    def SimFireSpreadEvoV2(self, nSim, CoordCells, Colors, G, H=None, version=0, onlyGraph=True):
        # V2
        # Scatter data
        c = self._Cols
        r = self._Rows
        x = np.linspace(0, c, c+1)
        y = np.linspace(0, r, r+1)
        pts = itertools.product(x, y)

        #Initializing figures
        figure()
        ax = gca()

        # If no graph H, read it
        if H == None:
            H = nx.read_edgelist(path = os.path.join(self._MessagesPath, "MessagesFile" + str(nSim) + ".txt"),
                                 create_using = nx.DiGraph(),
                                 nodetype = int,
                                 data = [('time', float), ('ros', float)])
            
        # Cartesian positions
        coord_pos = dict() 

        for i in G.nodes:
            coord_pos[i] = CoordCells[i-1] + 0.5
        
        #Rectangle
        edgecolor="None" #'k' if black borders are wanted
        lwidth=1.0

        rectangle = []

        # Fill figure
        for c in range(0, len(Colors)):
            rectangle.append(plt.Rectangle((CoordCells[c][0], CoordCells[c][1]), 1, 1, 
                                            fc="white", alpha=0.0, ec=edgecolor, linewidth=lwidth))
        for i in range(0, len(Colors)):
            ax.add_patch(rectangle[i])

        plt.title("Propagation Tree")#,color="white")
        plt.axis('scaled')

        # No nodes
        if onlyGraph == False:
            nx.draw_networkx_nodes(G, pos = coord_pos,
                                   node_size = 4,
                                   nodelist = list(G.nodes),
                                   node_shape='s',
                                   node_color = Colors)

        # Simple red
        if version == 0:
            nx.draw_networkx_edges(H, pos = coord_pos, edge_color = 'r', width = 0.5, 
                                   arrowsize=4, label="ROS messages")

        # Different plot versions
        elif version != 0 and H != None:
            edges = H.edges()
            weights = [H[u][v]['ros'] for u,v in edges]
            times = [H[u][v]['time'] for u,v in edges]

            # Edge color = Weights (freq)
            if version == 1:
                nx.draw_networkx_edges(H, pos = coord_pos, edge_color = weights, edge_cmap=plt.cm.Reds,
                                       width = 1.0, arrowsize=2)
            
            # Edge color = hit Times (normalized)
            if version == 2:
                nx.draw_networkx_edges(H, pos = coord_pos, edge_color = times/np.max(times), edge_cmap=plt.cm.Reds_r,
                                       width = 1.0, arrowsize=2)

            # Edge color = Weights (freq) and width = hit times (normalized)
            if version == 3:
                nx.draw_networkx_edges(H, pos = coord_pos, edge_color = weights/np.max(weights), edge_cmap=plt.cm.Reds,
                                       width = times / np.max(times), arrowsize=2)

        # Add legend and coordinates (if needed)
        plt.legend()
        XCoord = None
        YCoord = None

        plt.savefig(os.path.join(self._OutFolder, "Plots", "Plots" + str(nSim), 
                                 "FireSpreadTree_V2" + str(nSim) + ".png"),
                    dpi=200,  figsize=(200, 200), 
                    bbox_inches='tight', transparent=False)
        plt.close("all")
        
    
    # General Stats (end of the fire stats per scenario) 
    def GeneralStats(self):
        # If nSims = -1, read the output folder
        if self._nSims == -1:
            # Read folders with Grids (array with name of files) 
            Grids = glob.glob(self._OutFolder + 'Grids/')
            self._nSims = len(Grids)

        # Grids files (final scars)
        a = 0
        b = []
        statDict = {}
        statDF = pd.DataFrame(columns=[["ID", "NonBurned", "Burned", "Harvested"]])

        # Stats per simulation
        for i in range(self._nSims):
            GridPath = os.path.join(self._OutFolder, "Grids", "Grids"+str(i + 1))
            GridFiles = os.listdir(GridPath)
            #print(GridPath, GridFiles)
            if len(GridFiles) > 0: 
                a = pd.read_csv(GridPath +"/"+ GridFiles[-1], delimiter=',', header=None).values
                b.append(a)
                statDict[i] = {"ID": i+1,
                               "NonBurned": len(a[a == 0]),
                               "Burned": len(a[a == 1]), 
                               "Harvested": len(a[a == 2])}
            else:
                if i != 0:
                    a = np.zeros([a.shape[0], a.shape[1]]).astype(np.int64)
                    b.append(a)
                    statDict[i] = {"ID": i+1,
                                   "NonBurned": len(a[a == 0]),
                                   "Burned": len(a[a == 1]), 
                                   "Harvested": len(a[a == 2])}
                else:
                    a = np.zeros([self._Rows,self._Cols]).astype(np.int64)
                    b.append(a)
                    statDict[i] = {"ID": i+1,
                                   "NonBurned": len(a[a == 0]),
                                   "Burned": len(a[a == 1]), 
                                   "Harvested": len(a[a == 2])}
                                        
        # Generate CSV files
        if self._CSVs:
            # Dict to DataFrame
            A = pd.DataFrame(data=statDict, dtype=np.int32)
            A = A.T
            A = A[["ID", "NonBurned", "Burned", "Harvested"]]
            Aux = (A["NonBurned"] + A["Burned"] + A["Harvested"])
            A["%NonBurned"], A["%Burned"], A["%Harvested"] = A["NonBurned"] / Aux, A["Burned"] / Aux, A["Harvested"] / Aux
            A.to_csv(os.path.join(self._StatsFolder, "FinalStats.csv"), 
                     columns=A.columns, index=False, header=True, 
                     float_format='%.3f')
            if self._verbose:
                print("General Stats:\n", A)
                display(A[["Burned","Harvested"]].std())
            

            # General Summary
            SummaryDF = A.describe()
            SummaryDF.to_csv(os.path.join(self._StatsFolder, "General_Summary.csv"), header=True, 
                             index=True, columns=SummaryDF.columns, float_format='%.3f')
            if self._verbose:
                print("Summary DF:\n", SummaryDF)

        # Burnt Probability Heatmap
        if self._BurntProb:
            # Compute the global weighted Scar for heatmap
            #print("self._StatsFolder:", self._StatsFolder)
            WeightedScar = 0
            for i in range(len(b)):
                WeightedScar += b[i]
            WeightedScar =  WeightedScar / len(b)    
            
            # Set harvested to null prob
            WeightedScar[WeightedScar == 2] = 0
            
            if self._verbose:
                print("Weighted Scar:\n", WeightedScar)
            
            # Generate BPHeatmap
            self.BPHeatmap(WeightedScar, Path=self._StatsFolder, nscen=self._nSims, sq=True)
            
            # Save BP Matrix
            np.savetxt(os.path.join(self._StatsFolder, "BProb.csv"), WeightedScar, 
                       delimiter=" ", fmt="%.3f")

    # Hourly stats (comparison of each hour evolution per fire)
    def HourlyStats(self):
        # If nSims = -1, read the output folder
        if self._nSims == -1:
            # Read folders with Grids (array with name of files) 
            Grids = glob.glob(self._OutFolder + 'Grids/')
            self._nSims = len(Grids)

        # Grids files (per hour)  
        ah = 0
        bh = {}
        statDicth = {}
        statDFh = pd.DataFrame(columns=[["ID", "NonBurned", "Burned", "Harvested"]])
        for i in range(self._nSims):
            GridPath = os.path.join(self._OutFolder, "Grids", "Grids"+str(i+1))
            GridFiles = os.listdir(GridPath)
            if len(GridFiles) > 0:
                for j in range(len(GridFiles)):
                    ah = pd.read_csv(GridPath +"/"+ GridFiles[j], delimiter=',', header=None).values
                    bh[(i,j)] = ah
                    statDicth[(i,j)] = {"ID": i+1,
                                       "NonBurned": len(ah[ah == 0]),
                                       "Burned": len(ah[ah == 1]), 
                                       "Harvested": len(ah[ah == 2]),
                                       "Hour": j+1}
            else:
                if i != 0:
                    ah = np.zeros([ah.shape[0], ah.shape[1]]).astype(np.int64)
                    bh[(i,j)] = ah
                    statDicth[(i,j)] = {"ID": i+1,
                                        "NonBurned": len(ah[ah == 0]),
                                        "Burned": len(ah[ah == 1]), 
                                        "Harvested": len(ah[ah == 2]),
                                        "Hour": j+1}
                else:
                    ah = np.zeros([self._Rows,self.Cols]).astype(np.int64)
                    bh[(i,0)] = ah
                    statDicth[(i,0)] = {"ID": i+1,
                                        "NonBurned": len(ah[ah == 0]),
                                        "Burned": len(ah[ah == 1]), 
                                        "Harvested": len(ah[ah == 2]),
                                        "Hour": 0 + 1}
           
        # Generate CSV files
        if self._CSVs:
            # Dict to DataFrame   
            Ah = pd.DataFrame(data=statDicth, dtype=np.int32)
            Ah = Ah.T
            Ah[["Hour", "NonBurned", "Burned", "Harvested"]] = Ah[["Hour", "NonBurned", "Burned", "Harvested"]].astype(np.int32)
            Ah = Ah[["ID", "Hour", "NonBurned", "Burned", "Harvested"]]
            Aux = (Ah["NonBurned"] + Ah["Burned"] + Ah["Harvested"])
            Ah["%NonBurned"], Ah["%Burned"], Ah["%Harvested"] = Ah["NonBurned"] / Aux, Ah["Burned"] / Aux, Ah["Harvested"] / Aux
            Ah.to_csv(os.path.join(self._StatsFolder, "HourlyStats.csv"), columns=Ah.columns, index=False, 
                      header=True, float_format='%.3f')
            if self._verbose:
                print("Hourly Stats:\n",Ah)

            # Hourly Summary
            SummaryDF = Ah[["NonBurned", "Burned", "Harvested", "Hour"]].groupby('Hour')["NonBurned", "Burned", "Harvested"].mean()
            SummaryDF.rename(columns={"NonBurned":"AVGNonBurned", "Burned":"AVGBurned", "Harvested":"AVGHarvested"}, inplace=True)
            SummaryDF[["STDBurned", "STDHarvested"]] = Ah[["NonBurned", "Burned", "Harvested", "Hour"]].groupby('Hour')["Burned","Harvested"].std()[["Burned","Harvested"]]
            SummaryDF[["MaxNonBurned", "MaxBurned"]] = Ah[["NonBurned", "Burned", "Harvested", "Hour"]].groupby('Hour')["NonBurned", "Burned"].max()[["NonBurned", "Burned"]]
            SummaryDF[["MinNonBurned", "MinBurned"]] = Ah[["NonBurned", "Burned", "Harvested", "Hour"]].groupby('Hour')["NonBurned", "Burned"].min()[["NonBurned", "Burned"]]
            Aux = (SummaryDF["AVGNonBurned"] + SummaryDF["AVGBurned"] + SummaryDF["AVGHarvested"])
            SummaryDF["%AVGNonBurned"], SummaryDF["%AVGBurned"], SummaryDF["%AVGHarvested"] = SummaryDF["AVGNonBurned"] / Aux, SummaryDF["AVGBurned"] / Aux, SummaryDF["AVGHarvested"] / Aux
            SummaryDF.reset_index(inplace=True)
            SummaryDF.to_csv(os.path.join(self._StatsFolder, "HourlySummaryAVG.csv"), header=True, 
                             index=False, columns=SummaryDF.columns, float_format='%.3f')
            if self._verbose:
                print("Summary DF:\n", SummaryDF)

        # Hourly BoxPlots
        if self._boxPlot:
            self.BoxPlot(Ah, yy="Burned", ylab="# Burned Cells", pal="Reds", title="Burned Cells evolution", 
                         Path=self._StatsFolder, namePlot="BurnedCells_BoxPlot", swarm=False)
            self.BoxPlot(Ah, yy="NonBurned", ylab="# NonBurned Cells", pal="Greens", title="NonBurned Cells evolution", 
                         Path=self._StatsFolder, namePlot="NonBurnedCells_BoxPlot", swarm=False)
            self.BoxPlot(Ah, yy="Harvested", ylab="# Harvested Cells", pal="Blues", title="Harvested Cells evolution", 
                         Path=self._StatsFolder, namePlot="HarvestedCells_BoxPlot", swarm=False)
            
        # Hourly histograms
        if self._histograms is True and self._nSims > 1:
            self.plotHistogram(Ah, NonBurned=True, xx="Hour", xmax=6, KDE=True, 
                               title="Histogram: Burned and NonBurned Cells",
                               Path=self._StatsFolder, namePlot="Densities")