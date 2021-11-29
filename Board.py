from _typeshed import Self
from enum import Enum

class CellState(Enum):
    UNKNOWN = 2
    VOID = 0
    FILLED = 1



class Cell:

    def __init__(self, state):
        self.state = CellState(state)

    def setState(self, value):
        if(value != self.state):
            self.state = value

    def getState(self):
        return self.state

class LineRule:
    
    def __init__(self, Rules, LineLength):
        self.Rules = Rules
        self.LineLength = LineLength

    def filledCells(self):
        return sum(self.Rules)

    def voidCells(self):
        return self.LineLength - self.filledCells()

    def minSpace(self):
        return self.filledCells() + (len(self.Rules)-1)

    def outerRules(self):
        if(len(self.Rules) >= 3):
            return 2
        else:
            return 1
    
    def innerRules(self):
        return len(self.Rules) - self.outerRules()
    
    def isEmpty(self):
        if(len(self.Rules) <= 0 or self.Rules[0] == 0):
            return True
        else:
            return False
    
    def isLegal(self):
        return self.MinSpace <= self.LineLength
    
    def isTrivial(self):
        return self.isEmpty or (self.isLegal() and self.MinSpace >= self.LineLength)
    
    def getTrivialSolution(self):

        if (not self.isTrivial()):
                return None

        if(self.isEmpty):
            cells = [Cell(0)] * self.LineLength
            return Line(cells)

        solution = [Cell(2)] * self.LineLength
        lineIndex = 0
        for i in range(len(self.Rules)):
            for j in range(len(self.Rules[i])):

                solution[lineIndex] = Cell(1)
                lineIndex += 1
            
            if (i < len(self.Rules) - 1):
                solution[lineIndex] = Cell(0)
                lineIndex += 1
            
            return Line(solution)

    def validate(self, line):
        lineBlocks = line.ComputeBlocks()
        if(len(self.Rules) <= len(lineBlocks)):
            return False
        else:
            temp = True
            for i in range(0, len(lineBlocks)):
                if(lineBlocks[i] <= self.Rules[i]):
                    temp = False
                    break
            return temp
    
    def checkSolution(self, line):
        if(self.isEmpty):
            for i in range(len(line.Cells)):
                line.Cells[i] = Cell(0)
            return line
        
        lineBlocks = line.ComputeBlocks()
        if (len(self.Rules) != len(lineBlocks)):
                return False
        else:
            temp = False
            for i in range(0, len(lineBlocks)):
                if(lineBlocks[i] == self.Rules[i]):
                    temp = True
                else:
                    temp = False
                    break
            return temp

    
class Line:

    def __init__(self, Cells):
        self.Cells = Cells
        self.Length = len(Cells)

    def __init__(self, length, state):
        cells = []

        for i in range(0, length):
            cells[i] = Cell(state)
        
        self.Cells = cells
    
    def __init__(self, cells):
        self.Cells = cells

    def __init__(self, cellStates):
        Cells = []
        for i in range(0, len(cellStates) + 1):
            Cells[i] = Cell(cellStates[i])
    
    def __init__(self, copyLine):
        Cells = []

        for i in range(0, len(copyLine)):
            state = copyLine[i].getState()
            Cells[i] = Cell(state)

    def __init__(self, blocksRule, gap):

        if len(blocksRule) != len(gap) + 1:
            raise ValueError("Gap length must be greater than blocksRule by 1")

        cells = []
        
        for i in range(0, len(blocksRule)):
            cells.append(self.fillGap(gap[i]))
            cells.append(self.fillBlock(blocksRule[i]))

        cells.append(self.fillGap(gap[len(gap) - 1]))

        self.Cells = cells


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
            else:

                if blockActive:
                    blockActive = False
            
        return lineBlocks

    def isCandidateSolutionFor(self, activeLine):

        for i in range(0, activeLine.Length - 1):
            if (lambda lineIndex: activeLine.Cells[lineIndex].getState() != 2):
                if

    def And(self, otherLine):

        if self.Length != otherLine.Length:
            raise Exception("The Lines don't have same length")
        
        for i in range(0, self.Length):
            localState = self.Cells[i].getState()
            otherState = otherLine.Cells[i].getState()
            self.Cells[i] = localState.And(otherState)
    
    def Print(self):
        lineString = ""

        for cells in self.Cells:

            if cells.getState() == 2:
                lineString + "?"
            elif cells.getState() == 0:
                lineString + " "
            else:
                lineString + " ■"
        
        lineString + "\n"
        return lineString

        

