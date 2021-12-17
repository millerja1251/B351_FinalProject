import time
from enum import Enum

#
# Here we create the state of each cell. Cells will initialize in an unknown state.
# Void Cells are ones where we know there will not be anything there
# Filled Cells are ones where we know there is something there 
#
class CellState(Enum):
    UNKNOWN = 2
    VOID = 0
    FILLED = 1

#
# Here we create the Cell objects. Each one contains its own CellState, as well as where it is in the board
# by giving it a row and column index. We then also make a getter and setter for later parts of the code
# to be a little simpler.
#
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

#
# Here we create the LineRule class. This creates objects which house the rules for each column and row.
# In this class we make multiple different methods which give us vital information about the lines.
# Then from those methods, we are able to generate candidate solutions for each line based on its rule.
# For instance, a line of length 5 and rules: [1,1] would generate 6 candidate solutions.
#
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
    
    # A line is Trivial if it's empty or if the sum of the rules and gaps is equal to the line length.
    def isTrivial(self):
        return self.isEmpty() or (self.isLegal() and (self.minGaps() == self.maxGaps))
    
    # Here is how we grab the solution to a line if it is a trivial line.
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
    
    # GenerateCandidates(), GetGapRules(), GenerateGapStructures(), and GenerateLineFromGapStructures() is how we get our candidate solutions.
    # These are all the lines which will be considered when being put into the backtracking algorithm for each line.

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
    
#
# Here is the Line class. This is where we create the Line objects that house each of the Cell objects for a specific Line.
#
class Line:

    def __init__(self, determiningNumber, inputOne, inputTwo):

        self.Cells = []

        #If it is a list of cells
        if determiningNumber == 1:
            self.Cells = inputOne

        #If it is a length with a cellstate
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

    # Creates a list of cells with VOID state with length equal to gapSize
    def fillGap(self, gapSize):
        cells = []

        for i in range(0, gapSize):
            cells.append(Cell(CellState.VOID))
        
        return cells
    
    # Creates a list of cells with FILLED state with length equal to blockSize
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

    # Sees whether or not the Line this is applied to is a solution for the ActiveLine that is passed into the method.
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
        

    # Sees if the line applied to and the line passed have the same cell states, otherwise sets current cell state at that position to unknown
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
    
    # How the Line is printed for showing the final board.
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

#
# LineType class to see if a line is a row or column
#
class LineType(Enum):
    COLUMN = 0
    ROW = 1

#
# ActiveLine objects combine everything we've previously set up. Takes in Cells which is a Line Object, takes in Rules which is a LineRule Object,
# Takes in Type which is a LineType object, and takes in an index to see where it is in the board.
# Also takes in CopySource, if it is meant to be copying another ActiveLine into a new ActiveLine object.
#
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
    
    # As said earlier, the candidate solutions start as all possible solutions to a line based on its rules
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
    
    # Reviews which candidates are potentially solutions for the given ActiveLine, and returns them while filtering out any that are not.
    def ReviewCandidates(self):
        temp = []
        for i in self.CandidateSolutions:
            if(i.isCandidateSolutionFor(self) == True):
                temp.append(i)
        
        self.CandidateSolutions = temp       

    # Returns a Line object that looks at each candidateSolution and sees which ones are determinable.
    def GetDeterminableCells(self):
        if (not self.isValid()):
            return Line(2, self.Length(), CellState.UNKNOWN)

        determinableCells = Line(5, self.CandidateSolutions[0], None)
        for candidateSolution in self.CandidateSolutions[1:]:
            determinableCells.And(candidateSolution)

        return determinableCells
    
    # Makes the line the method is applied to into the line which is being passed in, then reviews their candidates
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

#
# Most basic form of the structure for the full board. When called it will create an empty 5x5 board.
# We can then manually what is in the board using the set methods.
#
class BoardPuzzle:

    def __init__(self, multiple):
        self.ColumnCount = multiple
        self.RowCount = multiple        
        self.ColumnRules = [[] for i in range(multiple)]
        self.RowRules = [[] for i in range(multiple)]

    def setColumns(self, list):
        self.ColumnRules = list

    def setRows(self, list):
        self.RowRules = list

    def getRows(self):
        return self.RowRules

    def getColumns(self):
        return self.ColumnRules      
        
#
# The BoardStructure is where we pass in the BoardPuzzle object, and create the actual board.
# The BoardStructure object contains the amount of columns and rows, a matrix which contains all of the cell objects,
# and three different ActiveLine lists in order to properly manipulate each row and column individually.
# It also takes in a copy source for the use of the backtracking Solve()
#
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

    # GatherColumns(), GatherRows(), CopyColumns(), and CopyRows() are all meant to create lists of their respective ActiveLine types.

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

    # This method sets the line's solution, once it has been properly figured out by the algorithms.
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

#
# SpeculativeCallContext and VerboseLevel are both helper classes made for the backtracking algorithm.
# Each of these were included in Raphael's original usage, which he programed for an online game,
# and are still needed in order to make the program run properly.
#
class SpeculativeCallContext:
    global depth
    global optionIndex
    global optionsCount

class VerboseLevel(Enum):
    SILENT = 0
    STARTDECLARATION = 1
    STEPBYSTEP = 2

#
# The BoardLogic object takes in a BoardStructure object, and now makes it possible for us to use various methods on it.
# The big methods used on it are of course ourAlgorithm() and Solve() which represent our own method for solving, and
# the backtracking method for solving.
#
class BoardLogic(BoardStructure):

    def __init__(self, board):
        self.board = board

    # IsValid(), IsSet(), and IsSolved() run through all the rows and columns of the board to make sure that everything is correct.
    # These are mostly used for the backtracking algorithm as it needs them in order to see when to stop.
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

    # This is the backtracking algorithm that we are using.  
    def Solve(self, verboseLevel, context):
        if(not self.IsValid()):
            if(verboseLevel != VerboseLevel.SILENT):
                return
        
        # On the first run around, the Context will be None, therefore it will set whatever cells are possible to be said are filled or void
        if(context == None):
            self.SetDeterminableCells()

        # It will then see which lines only have 1 CandidateSolution, and set them equal to their CandidateSolution
        self.CandidateExlclusionSolve(verboseLevel)

        # Board must be valid and not solved in order for the algorithm to process everything it needs to.
        if(self.IsValid() and not self.IsSolved()):        

            #Grab all lines that have at least one UNKNOWN CellState 
            undeterminedLines = []
            for i in self.board.ActiveLines:
                if i.isSet() == False:
                    undeterminedLines.append(i)
            #Stops the solving if undeterminedLines doesn't have a length.
            if(len(undeterminedLines) == 0):
                return

            #Grab the undeterminedLine with the least number of CandidateSolutions
            speculationTarget = undeterminedLines[0]  
            for i in undeterminedLines:
                if speculationTarget.CandidateCount() >  i.CandidateCount():
                    speculationTarget = i    

            candidateSolutions = speculationTarget.CandidateSolutions
            candidatesCount = len(candidateSolutions)

            # Create a new board which will take in the old board and set the lines of the board based on the SpeculationTarget
            for i in range(candidatesCount):
                speculativeBoard = BoardLogic(BoardStructure(None, self.board))
                speculativeBoard.board.SetLineSolution(speculationTarget.Type, speculationTarget.Index, candidateSolutions[i])

                #Method to track how many times we have recursed through the board
                speculativeContext = SpeculativeCallContext()
                if(context == None):
                    context = speculativeContext
                    speculativeContext.depth = 1
                elif(context.depth != None):
                    speculativeContext.depth = context.depth + 1
                speculativeContext.optionIndex = i
                speculativeContext.optionsCount = candidatesCount
                
                #Recursive Call
                speculativeBoard.Solve(verboseLevel, speculativeContext)

                #Board is assumed to be correct if it can pass this if statement
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

    #Print out the board
    def Print(self):
        for row in self.board.Rows:
            row.Print()


    #Our Algorithm using the mathematical approach.
    def ourAlgorithm(self):
            for activeLines in self.board.Columns:
                #Start with columns, see if the line is Trivial, and if it is then set it to its trivial solution
                if(activeLines.Rules.isTrivial()):
                    activeLines.Cells = activeLines.Rules.getTrivialSolution().Cells

                #If not then run through the Mathematical Approach on the line
                else:    
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

                    cellIndex = -1

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

            for activeLines in self.board.Rows:
                #See if lines in the rows are trivial, if they are then set their trivial solution
                if(activeLines.Rules.isTrivial()):
                    activeLines.Cells = activeLines.Rules.getTrivialSolution().Cells
                #If not trivial then run through the mathemtaical approach on the line
                else:    
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

                    filledCount = 0

                    for cells in activeLines.Cells:
                        if cells.getState() == CellState.FILLED:
                            filledCount += 1

                    cellIndex = -1


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

            #After running through the mathematical approach on the rows and columns, it will see if there's any spaces in the rows
            #or columns that it can definitively say are going to be FILLED or VOID based on the rules.
            for activeLines in self.board.Columns:
                
                fillAmount = 0

                for cells in activeLines.Cells:
                    if cells.getState() == CellState.FILLED:
                        fillAmount += 1
                
                addedRule = 0

                for rule in activeLines.Rules.Rules:
                    addedRule += rule
                
                if fillAmount == addedRule:
                    for cell in activeLines.Cells:
                        if cell.getState() == CellState.UNKNOWN:
                            cell.setState(CellState.VOID)
            
            for activeLines in self.board.Rows:
                
                fillAmount = 0

                for cells in activeLines.Cells:
                    if cells.getState() == CellState.FILLED:
                        fillAmount += 1
                
                addedRule = 0

                for rule in activeLines.Rules.Rules:
                    addedRule += rule
                
                if fillAmount == addedRule:
                    for cell in activeLines.Cells:
                        if cell.getState() == CellState.UNKNOWN:
                            cell.setState(CellState.VOID)

#Main Function where we run the whole program.
if __name__ == "__main__":
    puzzle5 = BoardPuzzle(5)
    puzzle10 = BoardPuzzle(10)
    puzzle15 = BoardPuzzle(15)

    #Creation of all the rules that are pushed into the boards
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

    columnRules11 = [[1,1],[1,1],[2,2,2],[2,3,1],[2,1,3],[1,1,1,1],[3,1],[4,1],[1,1,1,1],[1,3]]
    rowRules11 = [[3,1],[5,2],[2],[4,2],[1,2,2],[1,1,1,2],[],[4,1],[1,1,1,3],[2,1]]
    columnRules12 = [[3,1,2],[1,1,2],[1,2,2,2],[2,1,1],[1,1,3],[2,1,1],[3,1],[1,2,1],[1,2,1,1],[1,3,1]]
    rowRules12 = [[2,1],[1,1],[1,1,2],[1,2,2,2],[1,2,3],[1,1,2,1],[2,1],[1,2,2],[3,1],[1,8]]
    columnRules13 = [[3,1,1],[2,2,2],[1,1,3],[7],[1,1,1],[3,1],[1,3],[1,1,1],[2,1],[2,1,1]]
    rowRules13 = [[1],[1,3],[3,2],[2,1,1,1],[3,1],[4,2],[1,1,1],[1,2,3],[3,1],[4,1,1]]
    columnRules14 = [[3],[1,2,2],[2,1,1],[1,2,1],[1,4,1],[2,1,1],[2,2,4],[1,1,2,1],[1,2],[2,3,1]]
    rowRules14 = [[1,1,2],[1,1,1],[2,1,3],[1,3,1,1],[1,3],[1,2,3],[1,4],[1,4,1],[2,2],[1,2,1]]
    columnRules15 = [[1,1,1],[2,1,3],[1,1,3],[1,1,4],[1,4,1],[1,2,2],[2,1,1],[1,2,4],[1,1,1],[3,1,2]]
    rowRules15 = [[1,1,1],[3,1,3],[1,1,1],[1,4,1],[2,1,2],[4,1],[5,1,1],[4,2],[1,2,1,1],[4]]
    columnRules16 = [[1,1,2],[1,1,1],[3,2,1],[1,1,1,1],[1,3,1],[1,1,3],[1,3,2],[1,3,1],[1,1,1],[1,2,1]]
    rowRules16 = [[1,1,1],[3],[1,4],[1,2,1,1],[1,5],[2,1,1],[1,1,5],[1,2,1],[2,3,1],[1,1]]
    columnRules17 = [[1,3,2],[3,2],[1,2,2],[4,1],[2,1,1],[1,2,1],[1,3,3],[1,2],[1,3,1,2],[6,1]]
    rowRules17 = [[1,1,3],[4,1],[1,1,2],[2,4,2],[4,5],[2,2,1],[2],[1,1,1],[7,2],[1,1,1]]
    columnRules18 = [[2,4,2],[1,3],[1,4],[1,1,1,1],[1,3,1],[7,1],[1,5],[2,1,1],[1,1,1,1],[6]]
    rowRules18 = [[1,2,2],[1,2,2],[1,1],[2,2,1],[1,4,1],[3,6],[3,2,1],[4,4],[1,1,2,1],[1,1,1]]
    columnRules19 = [[2,3,1],[1,2],[3,2],[2,2,1,1],[1,4,1],[2,2],[2,1,1],[1,3,1],[1,3,1],[3,2,1]]
    rowRules19 = [[1,1,1],[1,4,2],[2,1,1,1],[1],[5,2],[5,3],[1,1,5],[1,1,1,1],[1,1,1,1,1],[2,1]]
    columnRules20 = [[1,1,2,2,],[1,1,1,1],[1,1,1,1],[2,1],[2,3,1],[1,2,1],[1,2],[2,3],[3,1],[10]]
    rowRules20 = [[1,1,1,1],[1,2,2],[1,1,1,2],[1,3],[3,1,1],[1,2,1],[6,1],[1,1,2,1],[1,1,3],[2,1,1,1]]

    columnRules21 = [[1,1,1,2],[3,3,1,1,1],[1,2,6,1],[2,2,1,1],[1,1,2,1,3],[1,1,3,1],[1,4,1,1],[1,1,1,1,1,2],[3,2,2,2],[2,2,1,1],[1,1,2,1,1],[1,1,4,2,1],[2,3,1],[4,1,3,1],[1,2,3,4]]
    rowRules21 = [[2,3,1,1,1],[1,1,3,2],[3,1,1,2,1],[1,6,3],[2,1,2,1,1],[1,1,3,1,1],[6,1,1],[2,1,1,6],[2,2,1,5],[1,2,2,3],[2,2],[1,1,1,1,1,1],[1,3,2,1,1],[1,3,2,1,1],[1,1,2,1,2],[1,2,1,1]]
    columnRules22 = [[3,1,2,4],[4,1,3,1,1],[1,3,3,1],[1,2,4,1],[1,2,1,1,2,1],[2,1,1,3,1],[2,1,1,3],[4,1,1,2],[1,2,2,3],[1,2,2,3],[5,3,2],[7,3,2],[2,1,1,1],[2,4,3],[1,6,1,2]]
    rowRules22 = [[3,3,1,1],[2,1,3,2],[2,1,1,2,2],[1,5,3,2],[1,2,2,3,1],[2,1,7],[1,1,1,1,2],[2,3,4],[2,2,1],[5,6],[1,5,2,2],[4,2,5],[1,1,4,2],[2,1,5,1],[2,1,1,2]]
    columnRules23 = [[2,5,1,1],[2,1,2],[1,1,3,2,1],[1,1,2,1,1],[1,2,1],[4,2,1,1],[2,3,1,2],[5,1,1,1,2],[2,1,1,1,1],[1,2,2],[2,1,1,1,1,1],[1,3,1,2],[1,1,5,1],[3,2,1,1],[1,3,1,5,1]]
    rowRules23 = [[3,1,2,5],[2,1,2,1,1],[1,1,3,3],[2,8,1],[1,1,1,1,2],[1,2,1,1,1],[1,1,2,1,1],[3,2,1,1],[2,1,1,1,1,1],[1,2,3],[1,1,1,1],[1,2,2,1],[1,2,3,1],[1,2,1,1],[1,6,5]]
    columnRules24 = [[1,1,1,2,1],[3,1,1],[1,1,1,1],[2,1,4,1,1],[1,2,1,1,1],[2,3,2,1,2],[1,1,3,1,1,1],[4,7,2],[6,2,1],[1,2],[1,1,1,2,1,1],[1,2,1,1,1],[2,1,3,2],[1,3,1,3],[1,1]]
    rowRules24 = [[1,3,1,1],[2,3,1,1],[3,1,1,1],[1,4,2],[1,1,2,3],[1,1,2,1,1],[1,1,3,3],[1,6,1],[1,4,2],[4,1,1,2],[1,1,4,1,1],[1,1,2,1],[1,2,3,1],[1,1,1,3,2],[2,2,1,1]]
    columnRules25 = [[2,3,1],[1,1,3],[2,2,3],[1,1,4,2],[1,1,2,1,1,2,1],[1,4],[5,1,1,1],[4,2],[2,2,2,4],[1,2,1,2,1,1],[1,1,1,3],[1,1,3,2],[8,1,3],[1,1,1,1,4],[4,9]]
    rowRules25 = [[3,2,2],[2,1,1,1],[1,1,1,6],[1,2,1,1,1],[1,1,3,2],[3,3,2],[3,2,1,1],[2,1,3],[1,1,1,1,3,1],[1,3,1,1,1],[1,2,2,1,2,1],[1,1,2,2,1,2],[2,11],[1,1,1,5],[2,2,2,3]]
    columnRules26 = [[1,1,2,1],[4,1,6],[1,2,4,1],[4,1,2,1],[1,1,1,2,2],[1,3,2,1,1],[1,1,3,4],[1,1,1,1,1,3],[5,4,1],[1,1,3,1,1],[4,2],[1,2,2,2,1],[3,2,2,3],[3,5,1,1],[1,1,1,2,2]]
    rowRules26 = [[1,5,1,2],[2,4],[1,1,3,2],[1,3,2,1],[3,1,1,4],[3,4,4],[1,1,1,1,1,1],[2,1,3,3,2],[4,2,3],[2,1,1,2,1,1],[2,3,2,1],[2,1,1,2,1],[2,4,1,1],[4,2,1,1],[1,1,1,1,4]]
    columnRules27 = [[2,1,1,2],[5,3],[1,1,1,1,5],[1,1,1,1,3],[3,1,1],[2,2,4,2],[1,1,3,1],[2,1,2,1],[3,5,1],[1,2,1,2],[1,3,3],[1,2],[2,2,1,5],[1,1,5],[1,1,1,1]]
    rowRules27 = [[1,3,2,1],[1,2,1,1,1],[1,2,1,1,1],[2,1,1,3,1],[1,4,1],[2,1,2],[1,1,5],[2,3,2],[1,2,3],[1,1,5,1],[4,1,1,2],[2,2,4],[4,1,3],[3,1,3],[3,1,2]]
    columnRules28 = [[2,1,1,1,1,1],[3,2,1,1,2],[3,1,1,1,2],[1,3,1,1,1],[5,1,1,1],[1,2,1,4],[5,2,2,1],[1,1,3,1],[4,3,2],[1,1,1,1,2],[2,1,6,1],[2,1,3,3],[1,1,2,2],[1,1,1],[3,1,1,2]]
    rowRules28 = [[2,1,6],[2,3,1,2,2],[2,1,4,1],[1,3,1,1,1,1],[2,3,2],[1,4,1],[1,2,2,1,1],[3,1,2,3],[2,1,5],[3,6],[1,1,1,1],[1,3,2,1,1],[1,1,2,2,1],[2,1,3],[4,1,1,1]]
    columnRules29 = [[1,4,1],[2,1,2,1,1,1],[1,1,1,3],[2,3,6],[1,1,2,1],[2,1,1,3],[1,4,1,1,3],[2,8],[1,5,2,1],[3,1,3,2],[2,1,1,1,2,1],[3,4,4],[2,2,1,2],[1,2,2,2,1],[2,2,1]]
    rowRules29 = [[2,2,1,2,2],[3,2,3,1],[2,1,3],[1,5,1],[1,1,5,1,1],[2,2,1,4,2],[2,6,1,1],[1,1,1,1,2],[1,2,1,1],[3,3],[4,6,1],[1,1,1,3,1],[3,2,1,1],[2,2,1,2],[2,1,7]]
    columnRules30 = [[1,1,1,1,1,2],[2,1,4,3],[1,3],[1,3,2,2],[1,2,2,1],[1,3,1,1],[2,1,3,2],[1,4,1,1,2],[1,1,1,1],[1,9,1],[3,2,1,3],[2,2,2],[1,1,1,1],[3,2],[2,1,1,1]]
    rowRules30 = [[1,1,3,2],[2,1,1,4],[2,1,1,1],[1,1,1,1,1],[1,3,5],[1,2,1,2,1,1],[1,1,1,2,1],[1,1,2,2,2],[2,1,1,1],[2,1,1,1,1,1],[1,1,2,2],[2,2,3,1],[1,3,3,1],[2,2,1],[2,4,1]]

    #How we track the total sum of time for the backtracking algorithm vs ours
    backtrackSum = 0
    ourSum = 0

    #Set the columns and rows equal to the correct set of rules
    #Create and BoardStructure then a BoardLogic object
    #Grab the current time
    #Solve with backtracking or ouralgorithm
    #Grab the current time
    #Subtract the two times and add it to our sum for the correct algorithm
    #Print the time
    #Print the completed board

    #
    # TESTING FOR 5x5
    #

    print("BackTracking Algoritm")
    puzzle5.setColumns(columnRules1)
    puzzle5.setRows(rowRules1)
    board = BoardStructure(puzzle5, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle5.setColumns(columnRules1)
    puzzle5.setRows(rowRules1)
    board1 = BoardStructure(puzzle5, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle5.setColumns(columnRules2)
    puzzle5.setRows(rowRules2)
    board = BoardStructure(puzzle5, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle5.setColumns(columnRules2)
    puzzle5.setRows(rowRules2)
    board1 = BoardStructure(puzzle5, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle5.setColumns(columnRules3)
    puzzle5.setRows(rowRules3)
    board = BoardStructure(puzzle5, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle5.setColumns(columnRules3)
    puzzle5.setRows(rowRules3)
    board1 = BoardStructure(puzzle5, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle5.setColumns(columnRules4)
    puzzle5.setRows(rowRules4)
    board = BoardStructure(puzzle5, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle5.setColumns(columnRules4)
    puzzle5.setRows(rowRules4)
    board1 = BoardStructure(puzzle5, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle5.setColumns(columnRules5)
    puzzle5.setRows(rowRules5)
    board = BoardStructure(puzzle5, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle5.setColumns(columnRules5)
    puzzle5.setRows(rowRules5)
    board1 = BoardStructure(puzzle5, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle5.setColumns(columnRules6)
    puzzle5.setRows(rowRules6)
    board = BoardStructure(puzzle5, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle5.setColumns(columnRules6)
    puzzle5.setRows(rowRules6)
    board1 = BoardStructure(puzzle5, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle5.setColumns(columnRules7)
    puzzle5.setRows(rowRules7)
    board = BoardStructure(puzzle5, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle5.setColumns(columnRules7)
    puzzle5.setRows(rowRules7)
    board1 = BoardStructure(puzzle5, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle5.setColumns(columnRules8)
    puzzle5.setRows(rowRules8)
    board = BoardStructure(puzzle5, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle5.setColumns(columnRules8)
    puzzle5.setRows(rowRules8)
    board1 = BoardStructure(puzzle5, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle5.setColumns(columnRules9)
    puzzle5.setRows(rowRules9)
    board = BoardStructure(puzzle5, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle5.setColumns(columnRules9)
    puzzle5.setRows(rowRules9)
    board1 = BoardStructure(puzzle5, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle5.setColumns(columnRules10)
    puzzle5.setRows(rowRules10)
    board = BoardStructure(puzzle5, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle5.setColumns(columnRules10)
    puzzle5.setRows(rowRules10)
    board1 = BoardStructure(puzzle5, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()
    
    #Grab the average of both run times by dividing by 10
    #Print out their average times
    #Reset the sums
    backtrackSum = backtrackSum/10
    ourSum = ourSum/10
    print("The average of Backtracking was:")
    print(backtrackSum)
    print("The average of our algorithm was:")
    print(ourSum)
    backtrackSum = 0
    ourSum = 0

    #
    # NEXT LINE OF TESTING FOR 10x10
    #

    print("BackTracking Algoritm")
    puzzle10.setColumns(columnRules11)
    puzzle10.setRows(rowRules11)
    board = BoardStructure(puzzle10, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle10.setColumns(columnRules11)
    puzzle10.setRows(rowRules11)
    board1 = BoardStructure(puzzle10, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle10.setColumns(columnRules12)
    puzzle10.setRows(rowRules12)
    board = BoardStructure(puzzle10, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle10.setColumns(columnRules12)
    puzzle10.setRows(rowRules12)
    board1 = BoardStructure(puzzle10, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle10.setColumns(columnRules13)
    puzzle10.setRows(rowRules13)
    board = BoardStructure(puzzle10, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle10.setColumns(columnRules13)
    puzzle10.setRows(rowRules13)
    board1 = BoardStructure(puzzle10, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle10.setColumns(columnRules14)
    puzzle10.setRows(rowRules14)
    board = BoardStructure(puzzle10, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle10.setColumns(columnRules14)
    puzzle10.setRows(rowRules14)
    board1 = BoardStructure(puzzle10, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle10.setColumns(columnRules15)
    puzzle10.setRows(rowRules15)
    board = BoardStructure(puzzle10, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle10.setColumns(columnRules15)
    puzzle10.setRows(rowRules15)
    board1 = BoardStructure(puzzle10, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle10.setColumns(columnRules16)
    puzzle10.setRows(rowRules16)
    board = BoardStructure(puzzle10, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle10.setColumns(columnRules16)
    puzzle10.setRows(rowRules16)
    board1 = BoardStructure(puzzle10, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle10.setColumns(columnRules17)
    puzzle10.setRows(rowRules17)
    board = BoardStructure(puzzle10, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle10.setColumns(columnRules17)
    puzzle10.setRows(rowRules17)
    board1 = BoardStructure(puzzle10, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle10.setColumns(columnRules18)
    puzzle10.setRows(rowRules18)
    board = BoardStructure(puzzle10, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle10.setColumns(columnRules18)
    puzzle10.setRows(rowRules18)
    board1 = BoardStructure(puzzle10, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle10.setColumns(columnRules19)
    puzzle10.setRows(rowRules19)
    board = BoardStructure(puzzle10, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle10.setColumns(columnRules19)
    puzzle10.setRows(rowRules19)
    board1 = BoardStructure(puzzle10, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle10.setColumns(columnRules20)
    puzzle10.setRows(rowRules20)
    board = BoardStructure(puzzle10, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle10.setColumns(columnRules20)
    puzzle10.setRows(rowRules20)
    board1 = BoardStructure(puzzle10, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()
    
    #Grab the average of both run times by dividing by 10
    #Print out their average times
    #Reset the sums
    backtrackSum = backtrackSum/10
    ourSum = ourSum/10
    print("The average of Backtracking was:")
    print(backtrackSum)
    print("The average of our algorithm was:")
    print(ourSum)
    backtrackSum = 0
    ourSum = 0

    #
    # NEXT LINE OF TESTING FOR 15x15
    #

    print("BackTracking Algoritm")
    puzzle15.setColumns(columnRules22)
    puzzle15.setRows(rowRules22)
    board = BoardStructure(puzzle15, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle15.setColumns(columnRules22)
    puzzle15.setRows(rowRules22)
    board1 = BoardStructure(puzzle15, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle15.setColumns(columnRules25)
    puzzle15.setRows(rowRules25)
    board = BoardStructure(puzzle15, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle15.setColumns(columnRules25)
    puzzle15.setRows(rowRules25)
    board1 = BoardStructure(puzzle15, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle15.setColumns(columnRules26)
    puzzle15.setRows(rowRules26)
    board = BoardStructure(puzzle15, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle15.setColumns(columnRules26)
    puzzle15.setRows(rowRules26)
    board1 = BoardStructure(puzzle15, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()

    print("BackTracking Algoritm")
    puzzle15.setColumns(columnRules29)
    puzzle15.setRows(rowRules29)
    board = BoardStructure(puzzle15, None)
    boardSolver = BoardLogic(board)
    t0 = time.perf_counter_ns()
    boardSolver.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    backtrackSum += t1-t0
    print(t1-t0)
    boardSolver.Print()

    print("Our Algorithm")
    puzzle15.setColumns(columnRules29)
    puzzle15.setRows(rowRules29)
    board1 = BoardStructure(puzzle15, None)
    boardSolver1 = BoardLogic(board1)
    t0 = time.perf_counter_ns()
    boardSolver1.ourAlgorithm()
    boardSolver1.Solve(VerboseLevel.SILENT, None)
    t1 = time.perf_counter_ns()
    ourSum += t1-t0
    print(t1 - t0)
    boardSolver1.Print()
    
    #Grab the average of both run times by dividing by 10
    #Print out their average times
    #Reset the sums
    backtrackSum = backtrackSum/4
    ourSum = ourSum/4
    print("The average of Backtracking was:")
    print(backtrackSum)
    print("The average of our algorithm was:")
    print(ourSum)