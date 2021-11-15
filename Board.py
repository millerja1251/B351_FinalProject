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
        self.isEmpty = False
        self.OuterRules = 1
        if(len(Rules) >= 3):
            self.OuterRules = 2
        self.InnerRules = len(Rules) - OuterRules
     

