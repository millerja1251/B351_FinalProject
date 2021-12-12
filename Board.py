import time
from enum import Enum
import enum
import copy

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
        return self.filledCells() + self.minGaps()

    def outerRules(self):
        if(len(self.Rules) == 1):
            return 1
        else:
            return 2
    
    def innerRules(self):
        return len(self.Rules) - self.outerRules()

    def minGaps(self):
        if(len(self.Rules) == 1):
            if(self.filledCells() == self.LineLength):
                return 0
            else:
                return 1
        else:
            return self.innerRules() + 1
    
    def innerGaps(self):
        if(len(self.Rules) == 1):
            return 0
        else:
            return self.innerRules() + 1
    
    def maxGaps(self):
        if(self.minSpace() < self.LineLength):
            return self.minGaps() + min(self.LineLength - self.minSpace(), self.outerRules)
        else:
            return self.minGaps()
    
    def isEmpty(self):
        if(len(self.Rules) <= 0 or self.Rules[0] == 0):
            return True
        else:
            return False
    
    def isLegal(self):
        return self.minSpace() <= self.LineLength
    
    def isTrivial(self):
        return self.isEmpty() or (self.isLegal() and (self.minGaps() == self.maxGaps))
    
    def getTrivialSolution(self):

        if (not self.isTrivial()):
                return None

        if(self.isEmpty()):
            cells = [Cell(CellState.VOID) for i in range(self.LineLength)]
            return Line(1, cells, None)

        solution = [Cell(CellState.UNKNOWN) for i in range(self.LineLength)]
        lineIndex = 0
        for blockIndex in range(len(self.Rules)):
            for fillingIndex in range(self.Rules[blockIndex]):

                solution[lineIndex] = Cell(CellState.FILLED)
                lineIndex += 1
            
            if (blockIndex < len(self.Rules) - 1):
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
                if(lineBlocks[i] > self.Rules[i]):
                    temp = False
                    break
            return temp
    
    def checkSolution(self, line):
        if(self.isEmpty()):
            for i in range(len(line.Cells)):
                if(line.Cells[i].getState() != CellState.VOID):
                    return False
            return True
        
        lineBlocks = line.computeBlocks()
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
        if(self.isTrivial()):
            temp = [self.getTrivialSolution()]
            return temp
        gapRules = self.GetGapRules()
        generatedGaps = self.GenerateGapStructures(gapRules, self.voidCells())
        return self.GenerateLinesFromGapStructures(generatedGaps)

    def GetGapRules(self):
        voidsToAllocate = self.LineLength - self.filledCells() - self.innerGaps()
        gapRules = []
        
        newTuple1 = (0, voidsToAllocate)
        gapRules.append(newTuple1)

        for i in range(self.innerGaps()):
            newTuple2 = (1, 1 + voidsToAllocate)
            gapRules.append(newTuple2)

        newTuple3 = (0, voidsToAllocate)
        gapRules.append(newTuple3)

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

        #if it is a list of cells
        if determiningNumber == 1:
            self.Cells = inputOne

        #if it is a length with a cellstate
        elif determiningNumber == 2:
            cellList = []

            for i in range(0, inputOne):
                cellList.append(Cell(inputTwo))
        
            self.Cells = cellList

        #If we want to copy
        elif determiningNumber == 5:
            for i in range(0, inputOne.Length()):
                state = inputOne.Cells[i].getState()
                self.Cells.append(Cell(state))

        #Rules is input one, gap is input two
        elif determiningNumber == 6:
            if len(inputTwo) != len(inputOne) + 1:
                raise ValueError("Gap length must be greater than blocksRule by 1")

            cellList = []
            
            for i in range(0, len(inputOne)):
                cellList.extend(self.fillGap(inputTwo[i]))
                cellList.extend(self.fillBlock(inputOne[i]))

            cellList.extend(self.fillGap(inputTwo[len(inputTwo) - 1]))

            self.Cells = cellList

    def Length(self):
        return len(self.Cells)

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

        for lineIndex in range(0, len(self.Cells)):

            if(self.Cells[lineIndex].getState() == CellState.FILLED):

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
        if(activeLine.Length() != self.Length()):
            raise Exception("Bruh")

        temp = True
        for i in range(0, activeLine.Length()):
            if activeLine.Cells[i].getState() != CellState.UNKNOWN:
                if activeLine.Cells[i].getState() == self.Cells[i].getState():
                    temp = True
                else:
                    temp = False
                    break
        return temp
        


    def And(self, otherLine):
        if self.Length() != otherLine.Length():
            raise Exception("The Lines don't have same length")
        
        for i in range(0, self.Length()):
            localState = self.Cells[i].getState()
            otherState = otherLine.Cells[i].getState()
            if localState == otherState:
                self.Cells[i].setState(localState)
            else:
                self.Cells[i].setState(CellState.UNKNOWN)
    
    def Print(self):
        lineString = ""
        for cells in self.Cells:
            if cells.getState() == CellState.UNKNOWN:
                lineString += " ?"
            elif cells.getState() == CellState.VOID:
                lineString += "  "
            elif cells.getState() == CellState.FILLED:
                lineString += " ■"
            else:
                lineString += " X"
            
        lineString + "\n"
        print(lineString)


class LineType(Enum):
    COLUMN = 0
    ROW = 1

class ActiveLine(Line):
    def __init__(self, Cells, Rules, Type, Index, CopySource):
        if(CopySource == None):
            self.Type = Type
            self.Index = Index
            self.Rules = Rules
            self.CandidateSolutions = Rules.GenerateCandidates()
            self.skipReview = False
            self.Cells = Cells
            self.ReviewCandidates()
        
            if(not self.skipReview):
                self.ReviewCandidates()
        else:
            self.Type = CopySource.Type
            self.Index = CopySource.Index
            self.Rules = CopySource.Rules
            self.CandidateSolutions = CopySource.CandidateSolutions
            self.skipReview = False
            self.Cells = Cells

            if(not self.skipReview):
                self.ReviewCandidates()
    
    def Length(self):
        return len(self.Cells)
    
    def CandidateCount(self):
        return len(self.CandidateSolutions)

    def isValid(self):
        if len(self.CandidateSolutions) > 0:
            return True
        else:
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
            if(i.isCandidateSolutionFor(self) == True):
                temp.append(i)
        
        self.CandidateSolutions = temp       

    def GetDeterminableCells(self):
        if (not self.isValid()):
            return Line(2, self.Length(), CellState.UNKNOWN)

        determinableCells = Line(5, self.CandidateSolutions[0], None)
        for candidateSolution in self.CandidateSolutions[1:]:
            determinableCells.And(candidateSolution)

        return determinableCells
    
    def ApplyLine(self, line):
        if(line.Length() != self.Length()):
            raise ValueError("Lines must be of the same length")

        self.skipReview = True
        for i in range(0, self.Length()):
            newState = line.Cells[i].getState()
            if(newState != CellState.UNKNOWN):
                self.Cells[i].setState(newState)
        self.skipReview = False
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
            self.RowCount = self.Puzzle.RowCount
            self.ColumnCount = self.Puzzle.ColumnCount

            self.Matrix = [[] for i in range(self.RowCount)]
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
            self.RowCount = self.Puzzle.RowCount
            self.ColumnCount = self.Puzzle.ColumnCount
            self.Matrix = [[] for i in range(self.RowCount)]
            for rowIndex in range(self.RowCount):
                for columnIndex in range(self.ColumnCount):
                    otherCell = copySource.Matrix[rowIndex][columnIndex]
                    self.Matrix[rowIndex].append(Cell(otherCell.getState()))
                    self.Matrix[rowIndex][columnIndex].row = rowIndex
                    self.Matrix[rowIndex][columnIndex].column = columnIndex
            
            self.Columns = self.CopyColumns(copySource)
            self.Rows = self.CopyRows(copySource)
            self.ActiveLines = []

            for i in self.Columns:
                self.ActiveLines.append(i)
            for i in self.Rows:
                self.ActiveLines.append(i)

    def Copy(self, source):
        if(self.Puzzle != source.board.Puzzle):
            raise Exception("Oh Hell nah!")

        for rowIndex in range(self.RowCount):
            for columnIndex in range(self.ColumnCount):
                otherCell = source.board.Matrix[rowIndex][columnIndex]
                self.Matrix[rowIndex][columnIndex].setState(otherCell.getState())

    def GatherColumns(self):
        columns = []

        for columnIndex in range(self.ColumnCount):
            columnCells = []
            for rowIndex in range(self.RowCount):
                columnCells.append(self.Matrix[rowIndex][columnIndex])
            
            columnRule = LineRule(self.Puzzle.ColumnRules[columnIndex], self.RowCount)
            
            columns.append(ActiveLine(columnCells, columnRule, LineType.COLUMN, columnIndex, None))
        
        return columns

    def GatherRows(self):
        rows = []

        for rowIndex in range(self.RowCount):
            rowCells = []
            for columnIndex in range(self.ColumnCount):
                rowCells.append(self.Matrix[rowIndex][columnIndex])
            
            rowRule = LineRule(self.Puzzle.RowRules[rowIndex], self.ColumnCount)

            rows.append(ActiveLine(rowCells, rowRule, LineType.ROW, rowIndex, None))
        
        return rows

    def CopyColumns(self, copySource):
        columns = []
        for columnIndex in range(self.ColumnCount):
            columnCells = []
            for rowIndex in range(self.RowCount):
                columnCells.append(self.Matrix[rowIndex][columnIndex])
            
            columns.append(ActiveLine(columnCells, None, None, None, copySource.Columns[columnIndex]))
        
        return columns
    
    def CopyRows(self, copySource):
        rows = []
        for rowIndex in range(self.RowCount):
            rowCells = []
            for columnIndex in range(self.ColumnCount):
                rowCells.append(self.Matrix[rowIndex][columnIndex])
            
            rows.append(ActiveLine(rowCells, None, None, None, copySource.Rows[rowIndex]))
        
        return rows

    def SetLineSolution(self, lineType, lineIndex, candidateToSet):
        targetSet = self.Columns
        if(lineType == LineType.ROW):
            targetSet = self.Rows
        
        target = targetSet[0]
        for i in targetSet:
            if i.Index == lineIndex:
                target = i
                break
        
        target.ApplyLine(candidateToSet)


class SpeculativeCallContext:
    global depth
    global optionIndex
    global optionsCount

class VerboseLevel(Enum):
    SILENT = 0
    STARTDECLARATION = 1
    STEPBYSTEP = 2

class BoardLogic(BoardStructure):

    def __init__(self, board):
        self.board = board

    def IsValid(self):
        for i in self.board.ActiveLines:
            if i.isValid() == False:
                return False
        return True
    
    def IsSet(self):
        for i in self.board.ActiveLines:
            if i.isSet() == False:
                return False
        return True
    
    def IsSolved(self):
        for i in self.board.ActiveLines:
            if i.isSolved() == False:
                return False
        return True
        
    def Solve(self, verboseLevel, context):
        if(not self.IsValid()):
            if(verboseLevel != VerboseLevel.SILENT):
                return
        
        if(context == None):
            self.SetDeterminableCells()

        self.CandidateExlclusionSolve(verboseLevel)

        if(self.IsValid() and not self.IsSolved()):         
            undeterminedLines = []
            for i in self.board.ActiveLines:
                if i.isSet() == False:
                    undeterminedLines.append(i)

            speculationTarget = undeterminedLines[0]  
            for i in undeterminedLines:
                if speculationTarget.CandidateCount() >  i.CandidateCount():
                    speculationTarget = i    

            candidateSolutions = speculationTarget.CandidateSolutions
            candidatesCount = len(candidateSolutions)

            for i in range(candidatesCount):
                speculativeBoard = BoardLogic(BoardStructure(None, self.board))
                speculativeBoard.board.SetLineSolution(speculationTarget.Type, speculationTarget.Index, candidateSolutions[i])

                speculativeContext = SpeculativeCallContext()
                if(context == None):
                    context = speculativeContext
                    speculativeContext.depth = 1
                elif(context.depth != None):
                    speculativeContext.depth = context.depth + 1
                speculativeContext.optionIndex = i
                speculativeContext.optionsCount = candidatesCount
                
                speculativeBoard.Solve(verboseLevel, speculativeContext)
                if(speculativeBoard.IsValid() and speculativeBoard.IsSolved()):
                    self.board.Copy(speculativeBoard)
                    return
        
    def SetDeterminableCells(self):
        for i in self.board.ActiveLines:
            i.ApplyLine(i.GetDeterminableCells())

    def CandidateExlclusionSolve(self, verboseLevel):
        solvableLines = []
        for i in self.board.ActiveLines:
            if(not i.isSet() and len(i.CandidateSolutions) == 1):
                solvableLines.append(i)
        while(len(solvableLines) > 0 and self.IsValid()):
            selectedLine = solvableLines[0]
            selectedLine.ApplyLine(selectedLine.CandidateSolutions[0])
            solvableLines.pop(0)

    
    def Print(self):
        for row in self.board.Rows:
            row.Print()

    def ourAlgorithm(self):

        if(self.IsSolved):
            return self.board
    
        else:

            for activeLines in self.board.Columns:

                rules = activeLines.Rules.Rules
                addedRule = 0

                for rule in rules:
                    addedRule += rule + 1
            
                addedRule -= 1

                difference = self.board.RowCount - addedRule

                candidateRules = []

                for rule in rules:
                    if rule > difference:
                        candidateRules.append(rule)


                if rules[0] == activeLines.Length:
                    for cells in activeLines.Cells:
                        cells.setState(CellState.FILLED)

                if len(rules) == 0:
                    for cells in activeLines.Cells:
                        cells.setState(CellState.VOID)

                cellIndex = -1

                blankBoard = True

                for cells in activeLines.Cells:
                    if cells.getState == CellState.VOID or cells.getState() == CellState.FILLED:
                        blankBoard = False
                        break
                
                if blankBoard == True:

                    for rule in rules:

                        if rule in candidateRules:
                            fillAmount = rule - difference
                        
                            cellIndex += rule

                            cellIndexFilledTo = cellIndex - fillAmount
                        
                            for i in range(cellIndex, cellIndexFilledTo, -1):
                                activeLines.Cells[i].setState(CellState.FILLED)

                            cellIndex += 1
                        else:
                            cellIndex += rule + 1
                else:
                    
                    filledSpaces = 0
                    unknownSpaces = 0

                    for cells in activeLines.Cells:
                        if cells.getState() == CellState.FILLED:
                            filledSpaces += 1
                        else:
                            unknownSpaces += 1
                    
                    summedRule = 0

                    for i in rules:
                        summedRule += i

                    solvableSpaces = summedRule - filledSpaces

                    if solvableSpaces == unknownSpaces:
                        for cells in activeLines.Cells:
                            if cells.getState() == CellState.UNKNOWN:
                                cells.setState(CellState.FILLED)


            for activeLines in self.board.Rows:

                rules = activeLines.Rules.Rules
                addedRule = 0

                for rule in rules:
                    addedRule += rule + 1
            
                addedRule -= 1

                difference = self.board.ColumnCount - addedRule

                candidateRules = []

                for rule in rules:
                    if rule > difference:
                        candidateRules.append(rule)
            
                if rules[0] == activeLines.Length:
                    for cells in activeLines.Cells:
                        cells.setState(CellState.FILLED)

                if len(rules) == 0:
                    for cells in activeLines.Cells:
                        cells.setState(CellState.VOID)

                filledCount = 0

                for cells in activeLines.Cells:
                    if cells.getState() == CellState.FILLED:
                        filledCount += 1

                cellIndex = -1

                blankBoard = True

                for cells in activeLines.Cells:
                    if cells.getState == CellState.VOID or cells.getState() == CellState.FILLED:
                        blankBoard = False
                        break
                
                if blankBoard == True:

                    for rule in rules:

                        if rule in candidateRules:
                        
                            fillAmount = rule - difference

                            cellIndex += rule

                            cellIndexFilledTo = cellIndex - fillAmount
                        
                            for i in range(cellIndex, cellIndexFilledTo, -1):
                                activeLines.Cells[i].setState(CellState.FILLED)

                            cellIndex += 1
                        else:
                            cellIndex += rule + 1
                else:

                    filledSpaces = 0
                    unknownSpaces = 0

                    for cells in activeLines.Cells:
                        if cells.getState() == CellState.FILLED:
                            filledSpaces += 1
                        else:
                            unknownSpaces += 1
                    
                    summedRule = 0

                    for i in rules:
                        summedRule += i

                    solvableSpaces = summedRule - filledSpaces

                    if solvableSpaces == unknownSpaces:
                        for cells in activeLines.Cells:
                            if cells.getState() == CellState.UNKNOWN:
                                cells.setState(CellState.FILLED)
                    
                    break


            for activeLines in self.board.Columns:
                
                fillAmount = 0

                for cells in activeLines.Cells:
                    if cells.getState() == CellState.FILLED:
                        fillAmount += 1
                
                addedRule = 0

                for rule in activeLines.Rules.Rules:
                    addedRule += rule
                
                if fillAmount == addedRule:
                    for cell in range(0, activeLines.Length):
                        if activeLines.Cells[cell].getState() == CellState.UNKNOWN:
                            activeLines.Cells[cell].setState(CellState.VOID)
            
            for activeLines in self.board.Rows:
                
                fillAmount = 0

                for cells in activeLines.Cells:
                    if cells.getState() == CellState.FILLED:
                        fillAmount += 1
                
                addedRule = 0

                for rule in activeLines.Rules.Rules:
                    addedRule += rule
                
                if fillAmount == addedRule:
                    for cell in range(0, activeLines.Length):
                        if activeLines.Cells[cell].getState() == CellState.UNKNOWN:
                            activeLines.Cells[cell].setState(CellState.VOID)

            self.Print()
            return self.ourAlgorithm()

if __name__ == "__main__":
    puzzle = BoardPuzzle()
    columnRules1 = [[1],[1,1],[1,1,1],[1,3],[4]]
    rowRules1 = [[2],[1,1],[3],[1,2],[4]]
    columnRules2 = [[],[3],[3],[3],[]]
    rowRules2 = [[],[3],[3],[3],[]]
    columnRules3 = [[1,1],[1,3],[1],[3],[1,2]]
    rowRules3 = [[2,2],[1],[5],[1,1],[1]]
    columnRules4 = [[0],[1,2],[2],[2],[4]]
    rowRules4 = [[1,1],[1,1],[2,1],[1,2],[1]]
    columnRules5 = [[2],[1,1],[1,1],[3,1],[1]]
    rowRules5 = [[1,1],[4],[1],[1,1],[1,1]]
    columnRules6 = [[3],[1],[3],[1],[3,1]]
    rowRules6 = [[3],[2,1],[1,1,1],[1],[1,1]]
    columnRules7 = [[1,1],[1,1],[3],[2],[1,2]]
    rowRules7 = [[1],[2],[3],[1,1,1],[2,1]]
    columnRules8 = [[4],[],[2,2],[1,1],[1,3]]
    rowRules8 = [[1,1,1],[1,2],[1,1],[1,3],[1,1]]
    columnRules9 = [[1,1,1],[1,1],[1,1,1],[3],[1]]
    rowRules9 = [[4],[2],[4],[],[1,1]]
    columnRules10 = [[2,1],[1,1],[3],[2],[1,1]]
    rowRules10 = [[2],[2,1],[1,1,1],[1],[3]]

    puzzle.setColumns(columnRules1)
    puzzle.setRows(rowRules1)
    board = BoardStructure(puzzle, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    print(t1-t0)
    boardSolver.Print()

    
    puzzle.setColumns(columnRules2)
    puzzle.setRows(rowRules2)
    board = BoardStructure(puzzle, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    print(t1-t0)
    boardSolver.Print()

    puzzle.setColumns(columnRules3)
    puzzle.setRows(rowRules3)
    board = BoardStructure(puzzle, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    print(t1-t0)
    boardSolver.Print()

    puzzle.setColumns(columnRules4)
    puzzle.setRows(rowRules4)
    board = BoardStructure(puzzle, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    print(t1-t0)
    boardSolver.Print()

    puzzle.setColumns(columnRules5)
    puzzle.setRows(rowRules5)
    board = BoardStructure(puzzle, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    print(t1-t0)
    boardSolver.Print()

    puzzle.setColumns(columnRules6)
    puzzle.setRows(rowRules6)
    board = BoardStructure(puzzle, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    print(t1-t0)
    boardSolver.Print()
    
    puzzle.setColumns(columnRules7)
    puzzle.setRows(rowRules7)
    board = BoardStructure(puzzle, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    print(t1-t0)
    boardSolver.Print()

    puzzle.setColumns(columnRules8)
    puzzle.setRows(rowRules8)
    board = BoardStructure(puzzle, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    print(t1-t0)
    boardSolver.Print()

    puzzle.setColumns(columnRules9)
    puzzle.setRows(rowRules9)
    board = BoardStructure(puzzle, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    print(t1-t0)
    boardSolver.Print()

    puzzle.setColumns(columnRules10)
    puzzle.setRows(rowRules10)
    board = BoardStructure(puzzle, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    print(t1-t0)
    boardSolver.Print()
    