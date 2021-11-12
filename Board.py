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

    def changeState(self, value):
        if(value != self.state):
            self.state = value


