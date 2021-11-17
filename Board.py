from _typeshed import Self
from enum import Enum
class CellState(Enum):
    UNKNOWN = 2
    VOID = 0
    FILLED = 1



class Cell:

    def __init__(self, state, rowNumber, columnNumber):
        self.rowNumber = rowNumber
        self.columnNumber = columnNumber
        self.state = CellState(state)

    def setState(self, value):
        if(value != self.state):
            self.state = value

    def getState(self):
        return self.state

class LineRule:
    
    def __init__(self, Rules, LineLength, FilledCells, VoidCells, MinSpace, isEmpty, OuterRules, InnerRules):
        self.Rules = Rules
        self.LineLength = 5
        self.FilledCells = sum(Rules)
        self.VoidCells = LineLength - FilledCells
        self.MinSpace = FilledCells + (len(Rules)-1)
        self.OuterRules = 1
        if(len(Rules) >= 3):
            self.OuterRules = 2
        self.InnerRules = len(Rules) - OuterRules
        self.isEmpty = False
        if(len(Rules) <= 0):
            self.isEmpty = True
    
    def isLegal(self):
        return self.MinSpace <= self.LineLength
    
    def isTrivial(self):
        return self.isEmpty or (self.isLegal() and self.MinSpace >= self.LineLength)
    
    

class Line:

    def __init__(self, Cells):
        self.Cells = Cells
        self.Length = Cells.length

    def fillGap(self, gapSize):
        cells = []

        for i in range(0, gapSize):
            cells.append(Cell(0))
        
        return cells
    
    def fillBlock(self, blockSize):
        cells = []

        for i in range(0, blockSize):
            cells.append(Cell(1))

        return cells

    def computeBlocks(self):

        lineBlocks = []

        nextBlock = 0
        blockActive = False

        for i in range(0, self.Length):

            if(self.Cells[i].getState() == 1):

                if blockActive:
                    lineBlocks[nextBlock - 1] += 1

                else:
                    lineBlocks.append(1)
                    nextBlock += 1
                    blockActive = True
            





