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
    
    def getTrivialSolution(self):

        if (not self.isTrivial()):
                return None

        if(self.isEmpty):
            return PicrossLine(LineLength, PicrossCellState.Void)

        solution = []
        lineIndex = 0
        for i in range(len(self.Rules)):
            for j in range(len(self.Rules[i])):
                solution[lineIndex] = CellState(1)
                lineIndex += 1
            
            if (i < len(self.Rules) - 1):
                solution[lineIndex] = CellState(0)
                lineIndex += 1
            
            return PicrossLine(solution)
    
     


