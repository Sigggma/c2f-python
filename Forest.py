
# coding: utf-8

'''
# Forest Class: defining the main parameters of the instance including 
# ID (int), Location (String), Coordinates (Lat & Long, double list), 
# NCells (int), Area (double), Vol (double), Age (double), Perimeter (double)
# types of trees (dictionary)

Inputs:
ID        int
Location  string
Coord     double 2D array
NCells    int
Area      int
Vol       double
Age       double
Perimeter double
FTypes    dictionary / list  (any of them)
'''
class Forest:
    def __init__(self, ID, Location, Coord, NCells, Area, Vol, Age, Perimeter, FTypes):
        #Constructor
        self.ID = ID
        self.Location = Location
        self.Coord = Coord
        self.NCells = NCells
        self.Area = Area
        self.Vol = Vol
        self.Age = Age
        self.FTypes = FTypes

        self.CellsDistance = {}
        self.AvailCells = []
        self.AvailCells.append(list(range(1,self.NCells + 1)))
        self.BurntCells = list()
        
        
    '''
    Returns          list
    Inputs:
    period           int
    AvailCells_set   int set
    '''
    #AvailCells list takes the value from the actual AvailCells set (global set)
    def set_AvailCells(period,AvailCells_set):
        self.AvailCells[period] = AvailCells.insert((period) ,list(AvailCells_set))
        return AvailCells
        
    
    '''
    Returns          list
    Inputs:
    period           int
    BurntCells_set   int set
    '''
    #BurntCells list takes the value from the actual BurntCells set (global set)
    def set_BurntCells(period,BurntCells_set):
        self.BurntCells[period] = BurntCells.insert((period), list(BurntCells_set))
        return BurntCells
        
    
    '''
    Returns          void
    Inputs:
    '''
    # Prints-out info forest's info
    def print_info(self):
        print("Forest Information", 
              "\n ID = " + str(self.ID), 
              "\n Location = "+ str(self.Location),
              "\n Coordinates = " + str(self.Coord), 
              "\n NCells = " + str(self.NCells),
              "\n Area = " + str(self.Area),
              "\n Vol = " + str(self.Vol), 
              "\n Age = " + str(self.Age),
              "\n FTypes = "+ str(self.FTypes))