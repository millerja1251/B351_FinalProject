#from _typeshed import Self
from enum import Enum
import enum

class CellState(Enum):
    UNKNOWN = 2
    VOID = 0
    FILLED = 1

class Cell:

    def __init__(self, state):
        self.state = CellState(state)
        self.row = 0
        self.column = 0

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
            return Line(1, cells, None)

        solution = [Cell(CellState.UNKNOWN)] * self.LineLength
        lineIndex = 0
        for i in range(len(self.Rules)):
            for j in range(len(self.Rules[i])):

                solution[lineIndex] = Cell(CellState.FILLED)
                lineIndex += 1
            
            if (i < len(self.Rules) - 1):
                solution[lineIndex] = Cell(CellState.VOID)
                lineIndex += 1
            
        return Line(1, solution, None)

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
        return Line(solution)
    
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
        
        newTuple = (0, voidsToAllocate)
        gapRules.append(newTuple)

        for i in range((self.innerRules() + 1)):
            newTuple = (1, 1 + voidsToAllocate)
            gapRules.append(newTuple)

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
            lines.append(Line(6, self.Rules, gapStructure))
        
        return lines
    
class Line:

    def __init__(self, determiningNumber, inputOne, inputTwo):

        self.Cells = []
        self.Length = len(self.Cells)

        if determiningNumber == 1:
            self.Cells = inputOne
            self.Length = len(inputOne)

        elif determiningNumber == 2:
            cellList = []

            for i in range(0, inputOne):
                cellList.append(Cell(inputTwo))
        
            self.Cells = cellList

        elif determiningNumber == 3:
            self.Cells = inputOne

        elif determiningNumber == 4:
            for i in range(0, len(inputOne) + 1):
                self.Cells[i] = Cell(inputOne[i])

        elif determiningNumber == 5:
            for i in range(0, len(inputOne)):
                state = inputOne[i].getState()
                self.Cells[i] = Cell(state)

        elif determiningNumber == 6:

            if len(inputOne) != len(inputTwo) + 1:
                raise ValueError("Gap length must be greater than blocksRule by 1")

            cellList = []
            
            for i in range(0, len(inputOne)):
                cellList.append(self.fillGap(inputTwo[i]))
                cellList.append(self.fillBlock(inputOne[i]))

            cellList.append(self.fillGap(inputTwo[len(inputTwo) - 1]))

            self.Cells = cellList


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

        trueList = []

        for i in range(0, activeLine.Length - 1):
            if activeLine.Cells[i] == CellState.UNKNOWN:
                return False
            if self.Cells[i].getState() == activeLine.Cells[i].getState():
                trueList.append(True)
        
        if all(trueList):
            return True


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


class LineType(Enum):
    COLUMN = 0
    ROW = 1

class ActiveLine(Line):
    def __init__(self, Cells, Rules, Type, Index):
        self.Type = Type
        self.Index = Index
        self.Rules = Rules
        self.Cells = Cells
        self.CandidateSolutions = Rules.GenerateCandidates()
        self.Length = len(Cells)
    
    def isValid(self):
        if self.CandidateSolutions.Length > 0:
            return True
        return False

    def isSet(self):
        for cell in self.Cells:
            if(cell.getState() == CellState.UNKNOWN):
                return False
        return True

    def isSolved(self):
        return self.Rules.checkSolution(self)
    
    def ReviewCandidates(self):
        temp = []
        for i in self.CandidateSolutions:
            x = lambda a : a.IsCandidateSolutionFor(self)
            if(x == True):
                temp.append(i)
        
        self.CandidateSolutions = temp           

    def GetDeterminableCells(self):
        if (self.isValid()):
            return Line(2, len(self.Cells), CellState.UNKNOWN)

        determinableCells = Line(5, self.CandidateSolutions[0])
        for candidateSolution in self.CandidateSolutions[1:]:
            determinableCells.And(candidateSolution)

            return determinableCells
    
    def ApplyLine(self, line):
        # if(line.Length != self.Length):
        #     raise ValueError("Lines must be of the same length")

        for i in range(0, self.Length):
            newState = line.Cells[i].getState()
            if(newState != CellState.UNKNOWN):
                self.Cells[i] = newState
        
        self.ReviewCandidates()

class BoardPuzzle:

    def __init__(self):
        self.ColumnCount = 5
        self.RowCount = 5        
        self.ColumnRules = [[] for i in range(5)]
        self.RowRules = [[] for i in range(5)]

    def setColumns(self, list):
        self.ColumnRules = list

    def setRows(self, list):
        self.RowRules = list

    def getRows(self):
        return self.RowRules

    def getColumns(self):
        return self.ColumnRules      
        

class BoardStructure:

    def __init__(self, puzzle, copySource):
        if(puzzle != None):
            self.Puzzle = puzzle
            self.RowCount = puzzle.RowCount
            self.ColumnCount = puzzle.ColumnCount

            self.Matrix = [[] for i in range(self.RowCount + 1)]
            for rowIndex in range(self.RowCount):
                for columnIndex in range(self.ColumnCount):
                    self.Matrix[rowIndex].append(Cell(CellState.UNKNOWN))
                    self.Matrix[rowIndex][columnIndex].row = rowIndex
                    self.Matrix[rowIndex][columnIndex].column = columnIndex
            
            self.Columns = self.GatherColumns()
            self.Rows = self.GatherRows()
            self.ActiveLines = []

            for i in self.Columns:
                self.ActiveLines.append(i)
            for i in self.Rows:
                self.ActiveLines.append(i)
        
        if(copySource != None):
            self.Puzzle = copySource.Puzzle
            self.RowCount = copySource.RowCount
            self.ColumnCount = copySource.ColumnCount

            self.Matrix = [[] for i in range(self.RowCount)]
            for rowIndex in range(self.RowCount):
                for columnIndex in range(self.ColumnCount):
                    otherCell = copySource.Matrix[rowIndex][columnIndex]
                    self.Matrix[rowIndex][columnIndex] = Cell(otherCell.getState())
                    self.Matrix[rowIndex][columnIndex].row = rowIndex
                    self.Matrix[rowIndex][columnIndex].column = columnIndex
            
            self.Columns = self.CopyColumns(copySource)
            self.Rows = self.CopyRows(copySource)
            self.ActiveLines = []

            for i in self.Columns:
                self.ActiveLines.append(i)
            for i in self.Rows:
                self.ActiveLines.append(i)
    
    def GatherColumns(self):
        columns = []

        for columnIndex in range(self.ColumnCount):
            columnCells = []
            for rowIndex in range(self.RowCount):
                columnCells.append(self.Matrix[rowIndex][columnIndex])
            
            columnRule = LineRule(self.Puzzle.ColumnRules[columnIndex], self.RowCount)
            
            columns.append(ActiveLine(columnCells, columnRule, LineType.COLUMN, columnIndex))
        
        return columns

    def GatherRows(self):
        rows = []

        for rowIndex in range(self.RowCount):
            rowCells = []
            for columnIndex in range(self.ColumnCount):
                rowCells.append(self.Matrix[rowIndex][columnIndex])
            
            rowRule = LineRule(self.Puzzle.RowRules[rowIndex], self.ColumnCount)

            rows.append(ActiveLine(rowCells, rowRule, LineType.ROW, rowIndex))
        
        return rows

    def CopyColumns(self, copySource):
        columns = []
        for columnIndex in range(self.ColumnCount):
            columnCells = []
            for rowIndex in range(self.RowCount):
                columnCells.append(self.Matrix[rowIndex][columnIndex])
            
            columns.append(ActiveLine(columnCells, copySource.Columns[columnIndex]))
        
        return columns
    
    def CopyRows(self, copySource):
        rows = []
        for rowIndex in range(self.RowCount):
            rowCells = []
            for columnIndex in range(self.ColumnCount):
                rowCells.append(self.Matrix[rowIndex][columnIndex])
            
            rows.append(ActiveLine(rowCells, copySource.Rows[rowIndex]))
        
        return rows

    def SetLineSolution(self, lineType, lineIndex, candidateToSet):
        targetSet = self.Columns
        if(lineType == LineType.ROW):
            targetSet = self.Rows
        
        target = None
        for i in targetSet:
            if i.Index == lineIndex:
                target = i
                break
        
        target.ApplyLine(candidateToSet)


class SpeculativeCallContext:
    global depth
    global optionIndex
    global optionsCount



class BoardLogic(BoardStructure):

    def __init__(self, board):
        self.board = board
        self.IsValid = True
        for i in board.ActiveLines:
            if i.isValid() == False:
                self.IsValid = False
                break
        self.IsSet = True
        for i in board.ActiveLines:
            if i.isSet() == False:
                self.IsSet = False
                break

        self.IsSolved = True
        for i in board.ActiveLines:
            if i.isSolved() == False:
                self.IsSolved = False
                break
    
    def Solve(self, context = None):
        if(context == None):
            self.SetDeterminableCells()
        
        if(self.IsValid and not self.IsSolved):
            undeterminedLines = []
            for i in self.board.ActiveLines:
                if i.IsSet == False:
                    undeterminedLines.append(i)
        
        speculationTarget = self.board.ActiveLines[0]
        counter = len(self.board.ActiveLines[0].candidateSolutions)
        for i in self.board.ActiveLines[1:]:
            if len(i.candidateSolutions) < counter:
                speculationTarget = i
                counter = len(i.candidateSolutions)

        candidateSolutions = speculationTarget.CandidateSolutions
        candidatesCount = len(candidateSolutions)

        for i in range(candidatesCount):
            speculativeBoard = BoardLogic(self)
            speculativeBoard.SetLineSolution(speculationTarget.Type, speculationTarget.Index, candidateSolutions[i])

            speculativeContext = SpeculativeCallContext()
            if(context == None or context.depth == None):
                speculativeContext.depth = 1
            else:
                speculativeContext.depth = context.depth + 1
            speculativeContext.optionIndex = i
            speculativeContext.optionsCount = candidatesCount

            speculativeBoard.Solve(speculativeContext)
            if(speculativeBoard.IsValid and speculativeBoard.IsSolved):
                return speculativeBoard
        
    def SetDeterminableCells(self):
        for i in self.board.ActiveLines:
            i.ApplyLine(i.GetDeterminableCells())
    
    def Print(self):
        for row in self.board.Rows:
            row.Print()
    
    

    def ourAlgorithm(self, board):

        if(board.IsSolved):
            return board
    
        else:

            for activeLines in board.getColumns():

                rules = activeLines.getRule()
                addedRule = 0

                for rule in rules:
                    addedRule += rule
                    addedRule + 1
            
                addedRule - 1

                difference = board.getRowCount() - addedRule

                candidateRules = []

                for rule in rules:
                    if rule > difference:
                        candidateRules.append(rule)

                if rules[0] == len(activeLines):
                    for cells in activeLines.Cells:
                        cells.setState(CellState.FILLED)

                if len(rules) == 0:
                    for cells in activeLines.Cells:
                        cells.setState(CellState.VOID)

                filledCount = 0

                for cells in activeLines:
                    if cells.getState() == CellState.FILLED:
                        filledCount += 1
            
                ruleSum = 0

                for i in rules:
                    ruleSum += i

                if ruleSum == filledCount:
                    for cells in activeLines.Cells:
                        cells.setState(CellState.VOID)

                cellIndex = 0

                for rule in rules:

                    if rules in candidateRules:
                        fillAmount = rule - difference
                    
                        if rule == rules[0]:
                            cellIndex += rule - 1
                        else:
                            cellIndex += rule

                        cellIndexFilledTo = cellIndex - fillAmount
                    
                        for i in range(cellIndex, cellIndexFilledTo):
                            activeLines.Cells[i].setState(CellState.FILLED)

                        cellIndex += 1
                    else:
                        cellIndex += rule + 1

                if len(rules) == len(candidateRules):
                    for cells in activeLines:
                        if activeLines.Cells[cells].getState() == CellState.UNKNOWN:
                            activeLines.Cells[cells].setState(CellState.VOID)


            for activeLines in board.getRows():

                rules = activeLines.getRule()
                addedRule = 0

                for rule in rules:
                    addedRule += rule
                    addedRule + 1
            
                addedRule - 1

                difference = board.getColumnCount() - addedRule

                candidateRules = []

                for rule in rules:
                    if rule > difference:
                        candidateRules.append(rule)
            
                if rules[0] == len(activeLines):
                    for cells in activeLines.Cells:
                        cells.setState(CellState.FILLED)

                if len(rules) == 0:
                    for cells in activeLines.Cells:
                        cells.setState(CellState.VOID)

                filledCount = 0

                for cells in activeLines:
                    if cells.getState() == CellState.FILLED:
                        filledCount += 1
            
                ruleSum = 0

                for i in rules:
                    ruleSum += i

                if ruleSum == filledCount:
                    for cells in activeLines.Cells:
                        cells.setState(CellState.VOID)

                cellIndex = 0

                for rule in rules:

                    if rules in candidateRules:
                    
                        fillAmount = rule - difference
                    
                        if rule == rules[0]:
                            cellIndex += rule - 1
                        else:
                            cellIndex += rule

                        cellIndexFilledTo = cellIndex - fillAmount
                    
                        for i in range(cellIndex, cellIndexFilledTo):
                            activeLines.Cells[i].setState(CellState.FILLED)

                        cellIndex += 1
                    else:
                        cellIndex += rule + 1
                
                if len(rules) == len(candidateRules):
                    for cells in activeLines:
                        if activeLines.Cells[cells].getState() == CellState.UNKNOWN:
                            activeLines.Cells[cells].setState(CellState.VOID)

            return self.ourAlgorithm(board)



if __name__ == "__main__":
    puzzle1 = BoardPuzzle()
    columnRules1 = [[1],[1,1],[1,1,1],[1,3],[4]]
    rowRules1 = [[2],[1,1],[3],[1,2],[4]]
    puzzle1.setColumns(columnRules1)
    puzzle1.setRows(rowRules1)

    board1 = BoardStructure(puzzle1, None)
    boardSolver1 = BoardLogic(board1)
    boardSolver1.Solve()
    boardSolver1.Print()

