# Template para clase Heuristics
# Authors: Jaime Carrasco, Cristobal Pais
import math
import WeatherFBP
import CellsFBP
import pandas as pd
import numpy as np

import ReadDataPrometheus
from matplotlib.pylab import *
from coord_xy import *
import networkx as nx




# Reads the csv file "ForestDetails.csv" with prices and volume associated to each cell per period, based on growth model
def ReadForest(Folder, Year):
    aux = 1
    # Folder =  Folder + "ForestDatails4x4.csv"
    Folder1 = Folder + "/ForestDetails.csv"
    file = open(Folder1, "r")

    Utility = {}
    Volume = {}
    DemandArray = ReadDemand(Folder)
    # Read file and return the Utility and Volume per cells, for the selected Year
    for line in file:
        if aux > 1:
            aux += 1
            line = line.replace("\n", "")
            line = line.split(",")

            if int(line[6]) == Year:
                Utility[int(line[0])] = float(line[4])
                Volume[int(line[0])] = float(line[6])

        if aux == 1:
            aux += 1
    return Utility, Volume, DemandArray


# Reads Demand.csv file and creates an array with them
def ReadDemand(Folder):
    Folder = Folder + '/Demand.csv'
    aux = 1
    file = open(Folder, "r")
    demand = {}
    for line in file:
        if aux > 1:
            line = line.replace("\n", "")
            line = line.split(",")
            demand[int(line[0])] = int(line[1])
        if aux == 1:
            aux += 1
    return demand


def Heuristics(typeheur, AvailSet, BurntSet, HarvestedCells, Year, Folder, AdjCells, NCells, Utility, Volume,
               DemandArray, Cells_Obj, Weather_Obj, G):
    print 'AvailSet in the year ' + str(Year) + ' = ', AvailSet
    HarvestedCells_previous = HarvestedCells
    del HarvestedCells

    if AvailSet == {}:
        HarvestedCells = set()
        TotalDemand = 0
        TotalUtility = 0
        return HarvestedCells, TotalDemand, TotalUtility
    setDir = ['S', 'SE', 'E', 'NE', 'N', 'NW', 'W', 'SW']
    aux = set([])
    # Hay que definir como leer DemandArray
    DemandYear = DemandArray[Year]
    Adjacents = {}
    for k in range(0, NCells):
        aux = set([])
        for i in setDir:
            if AdjCells[k][i] != None:
                aux = aux | set(AdjCells[k][i])
        Adjacents[k + 1] = aux & AvailSet

    HarvestedCells = set()
    HCs = []
    TotalDemand = 0
    TotalUtility = 0
    aux_util = dict()
    # Folder1 = '/Users/jaime/Google Drive/Dogrib/NewStochSim_vsAugust_2017/Simulator/CurrentVersionPython2.7/16CellsHom/ForestDetails.csv'
    # Utility, Volume = ReadForest(Folder1,Period)

    if typeheur == 1:  # This Heuristic, harvest the most beneficial cells
        # print 'AvailSet', AvailSet
        # print 'Utility', Utility
        for i in AvailSet:
            aux_util[i] = Utility[i]
        index = sorted(aux_util, key=aux_util.__getitem__, reverse=True)
        j = 0
        while TotalDemand < DemandYear:
            HarvestedCells.add(index[j])
            TotalDemand += Volume[index[j]]
            TotalUtility += Utility[index[j]]
            j = j + 1

    if typeheur == 2:  # This Heuristic, harvest the most beneficial adjacent cells of years previous
        for i in AvailSet:
            aux_util[i] = Utility[i]
        idxorder = sorted(aux_util, key=aux_util.__getitem__, reverse=True)

        if HarvestedCells_previous != set([]):
            AdjacentsToHarvested = set()
            for i in HarvestedCells_previous:
                AdjacentsToHarvested = AdjacentsToHarvested | set(Adjacents[i])
            HarvestedCells = HarvestedCells_previous
        else:
            TotalDemand += Volume[idxorder[0]]
            TotalUtility += aux_util[idxorder[0]]
            HarvestedCells.add(idxorder[0])
            AdjacentsToHarvested = Adjacents[idxorder[0]]

        del idxorder

        while TotalDemand < DemandYear:
            util = dict()
            adj_set = AdjacentsToHarvested
            # print 'adj_set = ', adj_set
            if adj_set != set([]):
                for i in adj_set:
                    util[i] = aux_util[i]
                idx_aux = sorted(util, key=util.__getitem__, reverse=True)
                print 'idx_aux = ', idx_aux
                HarvestedCells.add(idx_aux[0])
                AdjacentsToHarvested = AdjacentsToHarvested.union(Adjacents[idx_aux[0]]) - HarvestedCells
                # print 'AdjacentsToHarvested = ', AdjacentsToHarvested
                TotalUtility += Utility[idx_aux[0]]
                TotalDemand += Volume[idx_aux[0]]
                del util
            # del idx_aux
            else:
                aux = AvailSet - (AdjacentsToHarvested | HarvestedCells)
                for i in aux:
                    util[i] = aux_util[i]
                idx_aux = sorted(util, key=util.__getitem__, reverse=True)
                HarvestedCells.add(idx_aux[0])
                AdjacentsToHarvested = AdjacentsToHarvested.union(Adjacents[idx_aux[0]]) - HarvestedCells
                TotalUtility += Utility[idx_aux[0]]
                TotalDemand += Volume[idx_aux[0]]
                del util

    if typeheur == 3:  # This Heuristic, harvest the most beneficial adjacent cells (no respeta adyacencia del periodo previo)
        for i in AvailSet:
            aux_util[i] = Utility[i]
        index = sorted(aux_util, key=aux_util.__getitem__, reverse=True)

        HCs = HCs + [index[0]]
        HarvestedCells = set([index[0]])
        AdjHarvested = Adjacents[index[0]]
        TotalDemand += Volume[index[0]]
        TotalUtility += Utility[index[0]]
        j = 1
        # del index[0]
        while TotalDemand < DemandYear:
            if index[j] in AdjHarvested:
                HarvestedCells.add(index[j])
                HCs += [index[j]]
                AdjHarvested = AdjHarvested.union(Adjacents[index[j]]) - HarvestedCells
                TotalDemand += Volume[index[j]]
                TotalUtility += Utility[index[j]]
            # del index[j]
            # j = 0
            else:
                if j + 1 < len(index):
                    j = j + 1
                else:
                    break

    if typeheur == 4:  # Heuristica que respeta adjacencia (Idea AW)
        if Year == 1:
            for i in AvailSet:
                aux_util[i] = Utility[i]
            idxorder = sorted(aux_util, key=aux_util.__getitem__, reverse=True)
            TotalDemand += Volume[idxorder[0]]
            TotalUtility += aux_util[idxorder[0]]
            HarvestedCells.add(idxorder[0])
            AdjacentsToHarvested = Adjacents[idxorder[0]]
            j = 1
            while TotalDemand < DemandYear:
                if idxorder[j] in AdjacentsToHarvested:
                    HarvestedCells.add(idxorder[j])
                    AdjacentsToHarvested = AdjacentsToHarvested.union(Adjacents[idxorder[j]]) - HarvestedCells
                    TotalDemand += Volume[idxorder[j]]
                    TotalUtility += Utility[idxorder[j]]
                else:
                    if j + 1 < len(idxorder):
                        j = j + 1
                    else:
                        return HarvestedCells, TotalDemand, TotalUtility
        else:
            AdjacentsToHarvested = set()
            for i in HarvestedCells_previous:
                AdjacentsToHarvested = AdjacentsToHarvested | set(Adjacents[i])
            HarvestedCells = HarvestedCells_previous

            NoAdjacentsCells = AvailSet - (AdjacentsToHarvested | HarvestedCells)
            if NoAdjacentsCells != set([]):
                for i in NoAdjacentsCells:
                    aux_util[i] = Utility[i]
                idxorder = sorted(aux_util, key=aux_util.__getitem__, reverse=True)
                TotalDemand += Volume[idxorder[0]]
                TotalUtility += aux_util[idxorder[0]]
                HarvestedCells.add(idxorder[0])
                AdjacentsToHarvested = Adjacents[idxorder[0]]
                j = 1
                while TotalDemand < DemandYear:
                    if idxorder[j] in AdjacentsToHarvested:
                        HarvestedCells.add(idxorder[j])
                        AdjacentsToHarvested = AdjacentsToHarvested.union(Adjacents[idxorder[j]]) - HarvestedCells
                        TotalDemand += Volume[idxorder[j]]
                        TotalUtility += Utility[idxorder[j]]
                    else:
                        if j + 1 < len(idxorder):
                            j = j + 1
                        else:
                            break
            else:
                HarvestedCells = {}
                TotalDemand = 0
                TotalDemand = 0
    if typeheur == 5:  # Heuristica de Cris

        maxvalue = 0
        indexvalue = 0
        auxfeasible = 0
        # HarvestedCells = set()
        verbose = False
        Beta = [0.25 for i in range(0, 5)]
        # Price = 10
        Delta = 0.5
        CellValue = [[] for i in range(0, NCells)]
        #print 'largo Cells_Obj ', len(Cells_Obj)
        for c in range(0, NCells):
            # Cells_Obj[c].print_info()
            Price = Utility[c + 1]
            CellValue[c] = CellVal(Cells_Obj[c], Cells_Obj, AvailSet, Weather_Obj.get_Weather(), Year, NCells, Beta,
                                   Price, Delta)
            Cells_Obj[c].Value = CellValue[c]
            #print("Cell", c + 1, "value:", CellValue[c])

        while TotalDemand < DemandYear:
            maxvalue = max(CellValue)
            if verbose == True:
                print("")
                print("Availcells_set:", AvailSet, "Max cells value:", maxvalue)
            # Once the maximum value is found, we harvest that cell and update sets and its value
            for i in AvailSet:
                if CellValue[i - 1] == maxvalue:  # and CellValue[i-1] > 0.0:
                    indexvalue = i

                    if verbose == True:
                        print("Cell with max value", indexvalue)
                    CellValue[i - 1] = 0
                    Cells_Obj[i - 1].Value = 0

                    Cells_Obj[i - 1].set_Status(3)
                    Cells_Obj[i - 1].Harveststarts = Year

                    # TotalDemand += Cells_Obj[i - 1].Area * Cells_Obj[i - 1].Productivity[Year - 1]
                    # TotalUtility += Cells_Obj[i - 1].Area * Cells_Obj[i - 1].Productivity[Year - 1] * Price

                    TotalDemand += Volume[indexvalue]
                    TotalUtility += Utility[indexvalue]
                    NewHID = indexvalue
                    Aux_set = set([NewHID])
                    HarvestedCells = HarvestedCells.union(Aux_set)
                    AvailSet = AvailSet.difference(HarvestedCells)

                    if verbose == True:
                        print("Harvested Cells:", HarvestedCells, ", Harvested Amount: ", TotalDemand)
                        print("AvailCells_Set:", AvailSet)
                    break
    if typeheur == 6: # new FPV heuristic
                   
        fpv_av = dict(G.nodes(data='fpv'))

        for i in AvailSet:
            aux_util[i] = fpv_av[i]
        index = sorted(aux_util, key = aux_util.__getitem__, reverse=True)

        HCs = HCs + [index[0]]
        HarvestedCells = set([index[0]])
        AdjHarvested = Adjacents[index[0]]
        TotalDemand += Volume[index[0]]
        TotalUtility += Utility[index[0]]
        j = 1
        # del index[0]
        while TotalDemand < DemandYear:
            if index[j] in AdjHarvested:
                HarvestedCells.add(index[j])
                HCs += [index[j]]
                AdjHarvested = AdjHarvested.union(Adjacents[index[j]]) - HarvestedCells
                TotalDemand += Volume[index[j]]
                TotalUtility += Utility[index[j]]
            # del index[j]
            # j = 0
            else:
                if j + 1 < len(index):
                    j = j + 1
                else:
                    break

    if typeheur == 7: # Heuristic, Palma et al. approach

        fpv_bc = nx.betweenness_centrality(G, normalized=False, weight='time')

        for i in AvailSet:
            aux_util[i] = fpv_bc[i]
        index = sorted(aux_util, key = aux_util.__getitem__, reverse=True)

        HCs = HCs + [index[0]]
        HarvestedCells = set([index[0]])
        AdjHarvested = Adjacents[index[0]]
        TotalDemand += Volume[index[0]]
        TotalUtility += Utility[index[0]]
        j = 1
        # del index[0]
        while TotalDemand < DemandYear:
            if index[j] in AdjHarvested:
                HarvestedCells.add(index[j])
                HCs += [index[j]]
                AdjHarvested = AdjHarvested.union(Adjacents[index[j]]) - HarvestedCells
                TotalDemand += Volume[index[j]]
                TotalUtility += Utility[index[j]]
            # del index[j]
            # j = 0
            else:
                if j + 1 < len(index):
                    j = j + 1
                else:
                    break
    
    if typeheur == 8: # Burn Probability
	
	freq_burn = dict(G.nodes(data='freq_burn'))
	
	for i in AvailSet:
            aux_util[i] = freq_burn[i]

        index = sorted(aux_util, key = aux_util.__getitem__, reverse=True)

        HCs = HCs + [index[0]]
        HarvestedCells = set([index[0]])
        AdjHarvested = Adjacents[index[0]]
        TotalDemand += Volume[index[0]]
        TotalUtility += Utility[index[0]]
        j = 1
        # del index[0]
        while TotalDemand < DemandYear:
            if index[j] in AdjHarvested:
                HarvestedCells.add(index[j])
                HCs += [index[j]]
                AdjHarvested = AdjHarvested.union(Adjacents[index[j]]) - HarvestedCells
                TotalDemand += Volume[index[j]]
                TotalUtility += Utility[index[j]]
            # del index[j]
            # j = 0
            else:
                if j + 1 < len(index):
                    j = j + 1
                else:
                    break
	
    return HarvestedCells, TotalDemand, TotalUtility


def CellVal(Cells_Obj, Cells_Objs, AvailCells_Set, Weather, period, NCells, Beta, Price, Delta):
    # Cells value function
    #print 'Estoy en CellVal'
    #print 'largo Cells_Objs = ', len(Cells_Objs)
    # Initializing variables
    maxPrice = 0.0
    minPrice = 999999.0
    minArea = 1.0
    maxArea = 1.0
    minProductivity = 1.0
    maxProductivity = 1.0
    minCH = 0.0
    maxCH = 0.0
    minCHVar = 0.0
    maxCHVar = 0.0

    Marker1 = 0
    Marker2 = 0
    Marker3 = 0
    Marker4 = 0

    # Normalizing (max min)
    # Normalizing Area
    # print 'Largo de Cells_Objs: ', Cells_Objs
    for c in range(0, len(Cells_Objs)):
        # print 'Cells_Objs[c].Area = ', Cells_Objs[c].Area, 'c =', c
        if Cells_Objs[c].Area > maxArea:
            maxArea = Cells_Objs[c].Area
        if Cells_Objs[c].Area < minArea:
            minArea = Cells_Objs[c].Area
    #maxArea = 100
    #minArea = 100
    #
    if maxArea != minArea:
        for c in range(0, len(Cells_Objs)):
    #    print "Area normalizada celda",c,":", (Cells_Objs[c].Area - minArea)/(maxArea-minArea)
             Cells_Objs[c].NArea = (Cells_Objs[c].Area - minArea) / (maxArea - minArea)
             if Cells_Obj.ID == (c + 1):
                 Cells_Obj.NArea = Cells_Objs[c].NArea
    #
    # #    print "Cells NArea",c,":",Cells_Objs[c].NArea
    if maxArea == minArea:
        for c in range(0, len(Cells_Objs)):
    #         #print "Area normalizada2 celda", c, ":", 1.0
             Cells_Objs[c].NArea = 1.0
             if Cells_Obj.ID == (c + 1):
                 Cells_Obj.NArea = Cells_Objs[c].NArea
    # #    print "Cells NArea",c,":",Cells_Objs[c].NArea
    #
    # # Normalizing Productivity
    for c in range(0, len(Cells_Objs)):
        if Cells_Objs[c].Productivity[period - 1] > maxProductivity:
             maxProductivity = Cells_Objs[c].Productivity[period - 1]
        if Cells_Objs[c].Productivity[period - 1] < minProductivity:
             minProductivity = Cells_Objs[c].Productivity[period - 1]
    #
    if maxProductivity != minProductivity:
        for c in range(0, len(Cells_Objs)):
    #         #    print "Area normalizada celda",c,":", (Cells_Objs[c].Area - minArea)/(maxArea-minArea)
             Cells_Objs[c].NProductivity[period - 1] = (Cells_Objs[c].Productivity[period - 1] - minProductivity)/(maxProductivity - minProductivity)
             if Cells_Obj.ID == (c + 1):
                 Cells_Obj.NProductivity[period - 1] = Cells_Objs[c].NProductivity[period - 1]
    # #    print "Cells NArea",c,":",Cells_Objs[c].NArea
    if maxProductivity == minProductivity:
        for c in range(0, len(Cells_Objs)):
    #         #    print "Area normalizada2 celda",c,":", 1.0
             Cells_Objs[c].NProductivity[period - 1] = 1.0
             if Cells_Obj.ID == (c + 1):
                 Cells_Obj.NProductivity[period - 1] = Cells_Objs[c].NProductivity[period - 1]
    # #    print "Cells NArea",c,":",Cells_Objs[c].NArea
    #
    # # Normalizing CH
    for c in range(0, len(Cells_Objs)):
        if Cells_Objs[c].CH[period - 1] > maxCH:
             maxCH = Cells_Objs[c].CH[period - 1]
        if Cells_Objs[c].CH[period - 1] < minCH:
             minCH = Cells_Objs[c].CH[period - 1]
    #
    if maxCH != minCH:
        for c in range(0, len(Cells_Objs)):
    #         #    print "Area normalizada celda",c,":", (Cells_Objs[c].CH[period-1] - minCH)/(maxCH-minCH)
           Cells_Objs[c].NCH[period - 1] = (Cells_Objs[c].CH[period - 1] - minCH) / (maxCH - minCH)
           if Cells_Obj.ID == (c + 1):
              Cells_Obj.NCH[period - 1] = Cells_Objs[c].NCH[period - 1]
    # #    print "Cells NCH",c,":",Cells_Objs[c].NCH[period-1]
    if maxCH == minCH:
        for c in range(0, len(Cells_Objs)):
    #         #    print "Area normalizada2 celda",c,":", 1.0
            Cells_Objs[c].NCH[period - 1] = 0.0
            if Cells_Obj.ID == (c + 1):
                Cells_Obj.NCH[period - 1] = Cells_Objs[c].NCH[period - 1]
    # #    print "Cells NCH",c,":",Cells_Objs[c].NCH[period-1]
    #
    # # Normalizing CHVar
    for c in range(0, len(Cells_Objs)):
        if Cells_Objs[c].CHVar[period - 1] > maxCHVar:
            maxCHVar = Cells_Objs[c].CHVar[period - 1]
        if Cells_Objs[c].CHVar[period - 1] < minCHVar:
            minCHVar = Cells_Objs[c].CHVar[period - 1]
    #
    if maxCHVar != minCHVar:
        for c in range(0, len(Cells_Objs)):
    #         #    print "Area normalizada celda",c,":", (Cells_Objs[c].CHVar[period-1] - minCHVar)/(maxCHVar-minCHVar)
           Cells_Objs[c].NCHVar[period - 1] = (Cells_Objs[c].CHVar[period - 1] - minCHVar) / (maxCHVar - minCHVar)
           if Cells_Obj.ID == (c + 1):
                Cells_Obj.NCHVar[period - 1] = Cells_Objs[c].NCHVar[period - 1]
    # #    print "Cells NCHVar",c,":",Cells_Objs[c].NCHVar[period-1]
    if maxCHVar == minCHVar:
        for c in range(0, len(Cells_Objs)):
    #         #    print "Area normalizada2 celda",c,":", 1.0
            Cells_Objs[c].NCHVar[period - 1] = 0.0
            if Cells_Obj.ID == (c + 1):
                Cells_Obj.NCHVar[period - 1] = Cells_Objs[c].NCHVar[period - 1]
    # #    print "Cells NCHVar",c,":",Cells_Objs[c].NCHVar[period-1]
    #
    # # Min and Max for each parameter
    difArea = maxArea - minArea
    if difArea <= 0:
         Marker1 = 1
    #
    difProductivity = maxProductivity - minProductivity
    if difProductivity <= 0:
         Marker2 = 1
    #
    difCH = maxCH - minCH
    if difCH <= 0:
         Marker3 = 1
    #
    difCHVar = maxCHVar - minCHVar
    if difCHVar <= 0:
         Marker4 = 1

    # Main function
    if Cells_Obj.ID in AvailCells_Set:
        # Ignition
        Part0 = Beta[0] * ProbIgnition(Cells_Obj, Weather, period)
        # print "Part 0:",Part0
        # Spread From
        Part1 = Beta[1] * ProbSpreadFrom(Cells_Obj, Cells_Objs, AvailCells_Set, Weather, period) * AvailAdjAgainst(
            Cells_Obj, AvailCells_Set, Weather) / Adjacents(Cells_Obj)
        # print "Part 1:",Part1
        # Spread To
        Part2 = Beta[2] * ProbSpreadTo(Cells_Obj, Cells_Objs, Weather, period) * AvailAdjPro(Cells_Obj, AvailCells_Set,
                                                                                             Weather) / Adjacents(
            Cells_Obj)
        # print "Part 2:",Part2
        # AdjAvailCells and TotalAdjacents
        Part3 = Beta[3] * AvailAdj(Cells_Obj, AvailCells_Set) / Adjacents(Cells_Obj)
        # print "Part 3:",Part3
        # Half normalized
        Part4 = Beta[4] * ((Price / (Price * math.pow(1 + Delta, period))) * (
                    (Cells_Obj.Productivity[period - 1]) / max(difProductivity, Cells_Obj.Productivity[period - 1])) * (
                                       (Cells_Obj.Area) / max(difArea, Cells_Obj.Area)) - (
                                       (Cells_Obj.CH[period - 1]) / max(difCH, Cells_Obj.CH[period - 1])) - (
                                       (Cells_Obj.CHVar[period - 1]) / max(difCHVar, Cells_Obj.CHVar[period - 1]) * (
                                           (Cells_Obj.Area) / max(difArea, Cells_Obj.Area))))
        # print "Part 4:",Part4
        # Only Price is normalized
        Part42 = Beta[4] * ((Price / (Price * math.pow(1 + Delta, period))) * (
                    Cells_Obj.Productivity[period - 1] * Cells_Obj.Area) - (
                                        Cells_Obj.CH[period - 1] + (Cells_Obj.CHVar[period - 1] * Cells_Obj.Area)))
        # print "Part 42:",Part42
        # Not Normalized
        Part43 = Beta[4] * (
                    (Price / math.pow((1 + Delta), period)) * (Cells_Obj.Productivity[period - 1] * Cells_Obj.Area) - (
                        Cells_Obj.CH[period - 1] + (Cells_Obj.CHVar[period - 1] * Cells_Obj.Area)))
        # print "Part 43:",Part43
        # Totally normalized
        Part44 = Beta[4] * (
                    (1.0 / math.pow((1 + Delta), period)) * (Cells_Obj.NProductivity[period - 1] * Cells_Obj.NArea) - (
                        Cells_Obj.NCH[period - 1] + (Cells_Obj.NCHVar[period - 1] * Cells_Obj.NArea))) + 100
        # print "Part 44:",Part44

        return Part0 + Part1 * (Adjacents(Cells_Obj) / 8.0) + Part2 * (
                    Adjacents(Cells_Obj) / 8.0) + Part3 + Part44  # Part43
    else:
        return 0.0


def ProbIgnition(Cells_Obj, Weather, period):
    # Computing Ignition Probability per cell per period

    # Burnt conditions
    # Check Wind Speed, Temperature, Precipitation, Age and Dew Point thresholds plus initial ignition probability
    WST = 15
    TMT = 20
    PRT = 40
    AGT = 1
    DPT = 0
    ProbIgnition = 0.6

    # If the object is normal, ignition probability is 0
    if Cells_Obj.FTypeD[Cells_Obj.FType] == "Normal" or Cells_Obj.Age < AGT:
        ProbIgnition *= 0.1

    if (Weather["Wind_Speed"] >= WST and Weather["Temperature"] >= TMT and Weather["Rain"] <= PRT and Weather[
        "DPoint"] >= DPT and (Cells_Obj.FTypeD[Cells_Obj.FType] == "Burnable" or Cells_Obj.FTypeD[
        Cells_Obj.FType] == "Medium") and Cells_Obj.Age >= AGT):
        # Updating ignition probability
        # FType = Medium, then less ignition probability
        if Cells_Obj.FTypeD[Cells_Obj.FType] == "Medium":
            ProbIgnition *= 0.5

        # Age adjustement
        ageEps = (float(Cells_Obj.Age) - float(AGT)) / (float(Cells_Obj.Age))
        factorAge = 4
        ProbIgnition *= (1 + pow(ageEps, factorAge))

        # Temp adjustement
        tempEps = (float(Weather["Temperature"]) - float(TMT)) / (float(Weather["Temperature"]))
        factorTemp = 3
        ProbIgnition *= (1 + pow(tempEps, factorTemp))

        #  Terrain adjustement
        HardFactor = 0.05
        MediumFactor = 0.03
        SoftFactor = 0.0

        if Cells_Obj.TerrainD[Cells_Obj.Terrain] == "Hard":
            ProbIgnition *= (1 + HardFactor)
        elif Cells_Obj.TerrainD[Cells_Obj.Terrain] == "Medium":
            ProbIgnition *= (1 + MediumFactor)
        elif Cells_Obj.TerrainD[Cells_Obj.Terrain] == "Soft":
            ProbIgnition *= (1 + SoftFactor)

        if verbose == True:
            print("Ignition Probability Cell", Cells_Obj.ID, ":", ProbIgnition)

    return ProbIgnition


def ProbSpreadTo(Cells_Obj, Cells_Objs, Weather, period):
    # Computes probability of burning adjacent cells
    verbose = False
    probWindSpeed = 0.95
    probTemp = 0.90
    probNoRain = 0.95

    # Probability of sending a message (to any adjacent cell)
    probSendMsg = probWindSpeed * probTemp * probNoRain

    # Spread to probability (to any adjacent cell)
    probSpreadTo = ProbIgnition(Cells_Obj, Weather, period) * probSendMsg
    if verbose == True:
        print("Spread to probability Cell", Cells_Obj.ID, ":", probSpreadTo)

    return probSpreadTo


def ProbSpreadFrom(Cells_Obj, Cells_Objs, AvailCells_Set, Weather, period):
    # Computes probability of getting burnt by adjacents
    probSpreadFrom = 0.0

    # Components of spread probability
    probWindDirection = 0.25
    probWindSpeed = 0.95
    probTemp = 0.90
    probNoRain = 0.95

    # Determining the adjacent cells (available)
    AdjacentsCellsSet = AdjacentSets(Cells_Obj, AvailCells_Set)
    probSendMsg = [1.0 for a in range(0, len(AdjacentsCellsSet))]

    # Computing "spread" probabilities from adjacent cells
    posaux = 0
    for a in AdjacentsCellsSet:
        probSendMsg[posaux] = probWindDirection * probWindSpeed * probTemp * probNoRain
        posaux += 1

    # Computing the SpreadFrom probability
    posaux = 0
    for a in AdjacentsCellsSet:
        probSpreadFrom += ProbIgnition(Cells_Obj, Weather, period) * ProbIgnition(Cells_Objs[a - 1], Weather, period) * \
                          probSendMsg[posaux]
        posaux += 1
    # if verbose == True:
    #	print("Spread From probability Cell", Cells_Obj.ID, ":", probSpreadFrom)

    return probSpreadFrom


def AdjacentSets(Cells_Obj, AvailCells_Set):
    # Initializing parameters and variables for adjacent cells
    Adjacents_Cells = []
    Avail_Adjacent_Cells = []
    Adjacents_Cells_Aux = []
    AvailAdjSet = ()

    # Adjacent cells in a list of lists
    for i in list(Cells_Obj.Adjacents.values()):
        if i != None:
            Adjacents_Cells_Aux.append(i)

    # Flat adjacent cells list
    aux = 0
    for i in Adjacents_Cells_Aux:
        if isinstance(i, int) == False:
            for n in range(0, len(i)):
                baux = Adjacents_Cells_Aux[aux]
                Adjacents_Cells.append(baux[n])
        else:
            Adjacents_Cells.append(i)
        aux += 1

    # Adjacents set without non available
    AdjSet = set(Adjacents_Cells)
    AdjacentsCellsSet = set(Adjacents_Cells)

    for i in AdjacentsCellsSet:
        if i not in AvailCells_Set:
            AuxSet = set([i])
            AdjacentsCellsSet = AdjacentsCellsSet - AuxSet

    return AdjacentsCellsSet


def Adjacents(Cells_Obj):
    # Initializing parameters and variables
    Adjacents_Cells = []
    Avail_Adjacent_Cells = []
    Adjacents_Cells_Aux = []

    # Adjacent cells in a list of lists
    for i in list(Cells_Obj.Adjacents.values()):
        if i != None:
            Adjacents_Cells_Aux.append(i)

    # Flat adjacent cells list
    aux = 0
    for i in Adjacents_Cells_Aux:
        if isinstance(i, int) == False:
            for n in range(0, len(i)):
                baux = Adjacents_Cells_Aux[aux]
                Adjacents_Cells.append(baux[n])
        else:
            Adjacents_Cells.append(i)
        aux += 1

    # print "Cell",Cells_Obj.ID," total adjacents:",len(Adjacents_Cells)

    return len(Adjacents_Cells)


def AvailAdj(Cells_Obj, AvailCells_Set):
    # Initializing parameters and variables
    Adjacents_Cells = []
    Avail_Adjacent_Cells = []
    Adjacents_Cells_Aux = []
    AvailAdjSet = ()

    # Adjacent cells in a list of lists
    for i in list(Cells_Obj.Adjacents.values()):
        if i != None:
            Adjacents_Cells_Aux.append(i)

    # Flat adjacent cells list
    aux = 0
    for i in Adjacents_Cells_Aux:
        if isinstance(i, int) == False:
            for n in range(0, len(i)):
                baux = Adjacents_Cells_Aux[aux]
                Adjacents_Cells.append(baux[n])
        else:
            Adjacents_Cells.append(i)
        aux += 1

    # Adjacents set without non available
    AdjSet = set(Adjacents_Cells)
    AvailAdjSet = set(Adjacents_Cells)

    for i in AvailAdjSet:
        if i not in AvailCells_Set:
            AuxSet = set([i])
            # print "AuxSet: ",AuxSet
            AvailAdjSet = AvailAdjSet - AuxSet

    # print "AvailCells_Set", AvailCells_Set
    # print "Avail Adj Cells: ",AvailAdjSet
    # print "Cell",Cells_Obj.ID," total AvailAdjacents:",len(AvailAdjSet)

    # Return the number of total available adjacents
    return len(AvailAdjSet)


def AvailAdjAgainst(Cells_Obj, AvailCells_Set, Weather):
    # Number of available adjacent cells against the wind direction

    # Initializing parameters and variables
    Adjacents_Cells = []
    Avail_Adjacent_Cells = []
    Adjacents_Cells_Aux = []

    if (Weather["Wind_Direction"] >= 45 and Weather["Wind_Direction"] <= 135):
        AgainstSection = "S"

    elif (Weather["Wind_Direction"] >= 225 and Weather["Wind_Direction"] <= 315):
        AgainstSection = "N"

    elif (Weather["Wind_Direction"] >= 135 and Weather["Wind_Direction"] <= 225):
        AgainstSection = "E"

    elif (Weather["Wind_Direction"] >= 0 and Weather["Wind_Direction"] <= 45) or (
            Weather["Wind_Direction"] >= 315 and Weather["Wind_Direction"] <= 360):
        AgainstSection = "W"

    # Adjacent cells in a list of lists
    # print "AgainstSection:",AgainstSection
    if Cells_Obj.Adjacents[AgainstSection] != None:
        for i in Cells_Obj.Adjacents[AgainstSection]:
            if i != None:
                Adjacents_Cells_Aux.append(i)

        # Flat adjacent cells list
        aux = 0
        for i in Adjacents_Cells_Aux:
            if isinstance(i, int) == False:
                for n in range(0, len(i)):
                    baux = Adjacents_Cells_Aux[aux]
                    Adjacents_Cells.append(baux[n])
            else:
                Adjacents_Cells.append(i)
            aux += 1

        # Adjacents set without non available
        AdjSet = set(Adjacents_Cells)
        AgainstAvailAdjSet = set(Adjacents_Cells)

        for i in AdjSet:
            if i not in AvailCells_Set:
                # print "i previo adjacent set:",i
                AuxSet = set([i])
                AgainstAvailAdjSet = AgainstAvailAdjSet.difference(AuxSet)

        # print "Cell",Cells_Obj.ID," total AgaintsAvailAdjacents:",len(AgainstAvailAdjSet)

        # Return the number of total available adjacents
        return len(AgainstAvailAdjSet)

    else:
        return 0


def AvailAdjPro(Cells_Obj, AvailCells_Set, Weather):
    # Number of available adjacent cells in favor in the wind direction

    # Initializing parameters and variables
    Adjacents_Cells = []
    Avail_Adjacent_Cells = []
    Adjacents_Cells_Aux = []

    if (Weather["Wind_Direction"] >= 45 and Weather["Wind_Direction"] <= 135):
        Section = "N"

    elif (Weather["Wind_Direction"] >= 225 and Weather["Wind_Direction"] <= 315):
        Section = "S"

    elif (Weather["Wind_Direction"] >= 135 and Weather["Wind_Direction"] <= 225):
        Section = "W"

    elif (Weather["Wind_Direction"] >= 0 and Weather["Wind_Direction"] <= 45) or (
            Weather["Wind_Direction"] >= 315 and Weather["Wind_Direction"] <= 360):
        Section = "E"

    # Adjacent cells in a list of lists
    # print "ProSection:",Section
    if Cells_Obj.Adjacents[Section] != None:
        for i in Cells_Obj.Adjacents[Section]:
            if i != None:
                Adjacents_Cells_Aux.append(i)

        # Flat adjacent cells list
        aux = 0
        for i in Adjacents_Cells_Aux:
            if isinstance(i, int) == False:
                for n in range(0, len(i)):
                    baux = Adjacents_Cells_Aux[aux]
                    Adjacents_Cells.append(baux[n])
            else:
                Adjacents_Cells.append(i)
            aux += 1

        # Adjacents set without non available
        AdjSet = set(Adjacents_Cells)
        ProAvailAdjSet = set(Adjacents_Cells)

        for i in AdjSet:
            if i not in AvailCells_Set:
                AuxSet = set([i])
                ProAvailAdjSet = ProAvailAdjSet.difference(AuxSet)

        # print "Cell",Cells_Obj.ID," total ProAvailAdjacents:",len(ProAvailAdjSet)

        # Return the number of total available adjacents
        return len(ProAvailAdjSet)

    else:
        return 0


def AvailAdjPro(Cells_Obj, AvailCells_Set, Weather):
    # Number of available adjacent cells in favor in the wind direction

    # Initializing parameters and variables
    Adjacents_Cells = []
    Avail_Adjacent_Cells = []
    Adjacents_Cells_Aux = []

    if (Weather["Wind_Direction"] >= 45 and Weather["Wind_Direction"] <= 135):
        Section = "N"

    elif (Weather["Wind_Direction"] >= 225 and Weather["Wind_Direction"] <= 315):
        Section = "S"

    elif (Weather["Wind_Direction"] >= 135 and Weather["Wind_Direction"] <= 225):
        Section = "W"

    elif (Weather["Wind_Direction"] >= 0 and Weather["Wind_Direction"] <= 45) or (
            Weather["Wind_Direction"] >= 315 and Weather["Wind_Direction"] <= 360):
        Section = "E"

    # Adjacent cells in a list of lists
    # print "ProSection:",Section
    if Cells_Obj.Adjacents[Section] != None:
        for i in Cells_Obj.Adjacents[Section]:
            if i != None:
                Adjacents_Cells_Aux.append(i)

        # Flat adjacent cells list
        aux = 0
        for i in Adjacents_Cells_Aux:
            if isinstance(i, int) == False:
                for n in range(0, len(i)):
                    baux = Adjacents_Cells_Aux[aux]
                    Adjacents_Cells.append(baux[n])
            else:
                Adjacents_Cells.append(i)
            aux += 1

        # Adjacents set without non available
        AdjSet = set(Adjacents_Cells)
        ProAvailAdjSet = set(Adjacents_Cells)

        for i in AdjSet:
            if i not in AvailCells_Set:
                AuxSet = set([i])
                ProAvailAdjSet = ProAvailAdjSet.difference(AuxSet)

        # print "Cell",Cells_Obj.ID," total ProAvailAdjacents:",len(ProAvailAdjSet)

        # Return the number of total available adjacents
        return len(ProAvailAdjSet)

    else:
        return 0
