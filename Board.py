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
        return self.minSpace() <= self.LineLength
    
    def isTrivial(self):
        return self.isEmpty or (self.isLegal() and self.minSpace() >= self.LineLength)
    
    def getTrivialSolution(self):

        if (not self.isTrivial()):
                return None

        if(self.isEmpty):
            cells = [Cell(CellState.VOID)] * self.LineLength
            return Line(cells)

        solution = [Cell(CellState.UNKNOWN)] * self.LineLength
        lineIndex = 0
        for i in range(len(self.Rules)):
            for j in range(len(self.Rules[i])):

                solution[lineIndex] = Cell(CellState.FILLED)
                lineIndex += 1
            
            if (i < len(self.Rules) - 1):
                solution[lineIndex] = Cell(CellState.VOID)
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
                line.Cells[i] = Cell(CellState.VOID)
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
    
    def GenerateCandidates(self):
        if (self.isTrivial()):
            return self.getTrivialSolution()
        gapRules = self.GetGapRules()
        generatedGaps = self.GenerateGapStructures(gapRules, self.voidCells())
        return self.GenerateLinesFromGapStructures(generatedGaps)

    def GetGapRules(self):
        voidsToAllocate = self.LineLength - self.filledCells() - (self.innerRules() + 1)
        gapRules = []
        
        #Left outer gap
        newTuple = (0, voidsToAllocate)
        gapRules.append(newTuple)

        #Inner gapStructures
        for i in range((self.innerRules() + 1)):
            newTuple = (1, 1 + voidsToAllocate)
            gapRules.append(newTuple)

        #Right outer gap
        newTuple = (0, voidsToAllocate)
        gapRules.append(newTuple)

        return gapRules

    def GenerateGapStructures(self, gapRules, gapsToBeAllocated):
        sum = 0
        for i in gapRules:
            sum += i[1]
        if sum < gapsToBeAllocated:
            return None

        gapStructures = []
        headRule = gapRules[0]
        headValues = range(headRule[0], (headRule[1] - headRule[0]) + 2)

        for headValue in headValues:
        
            innerGapRules = gapRules[1:]
            nextGapsToBeAllocated = gapsToBeAllocated - headValue
            if (nextGapsToBeAllocated >= 0):
                if (len(innerGapRules) == 1):
                    gapStructure = [headValue, nextGapsToBeAllocated]
                    gapStructures.append(gapStructure)
                
                else:
                    innerGaps = self.GenerateGapStructures(innerGapRules, nextGapsToBeAllocated)
                    if (innerGaps != None):
                        for innerGap in innerGaps:
                            gapStructure = [headValue]
                            gapStructure.extend(innerGap)
                            gapStructures.append(gapStructure)
        return gapStructures
    
    def GenerateLinesFromGapStructures(self, gapStructures):
        lines = []
        for gapStructure in gapStructures:
            lines.append(Line(self.Rules, gapStructure))
        
        return lines
    
class Line:

    def __init__(self, Cells):
        self.Cells = Cells
        self.Length = len(Cells)

    def fillGap(self, gapSize):
        cells = []

        for i in range(0, gapSize):
            cells.append(Cell(CellState.VOID))
        
        return cells
    
    def fillBlock(self, blockSize):
        cells = []

        for i in range(0, blockSize):
            cells.append(Cell(CellState.FILLED))

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

        return None

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

class LineConstuctor:

    def __init__(self, length, state):

        cells = []

        for i in range(0, length):
            cells[i] = Cell(state)
        

