from copy import copy, deepcopy

import os,sys,inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 

from Game import Game
import Solver
from GameManager import *
from util import Value

FIRST = "X"
SECOND = "O"
NONE = " "

class TTT(Game):

    def __init__(self, size=3, turn=FIRST):
        self.turn = turn
        self.name = "TTT"+str(size)+"Optimized.csv"
        self.board = [[NONE for _ in range(size)] for _ in range(size)]
    
    def getTurn(self):
        return self.turn

    def getFirstPlayer(self):
        return FIRST

    def getSecondPlayer(self):
        return SECOND

    def generateMoves(self):
        moves = []
        for row in range(len(self.board)):
            for col in range(len(self.board[0])):
                if self.board[row][col] == NONE:
                    moves += [(row, col)]
        return moves

    def doMove(self, move):
        assert move[0] is not None and move[1] is not None
        switch = { FIRST : SECOND, SECOND : FIRST }
        board = deepcopy(self.board)
        board[move[0]][move[1]] = self.turn
        game = TTT(turn=switch[self.turn])
        game.board = board
        return game

    def primitive(self):
        # Horizontals
        for row in self.board:
            if len(set(row)) == 1 and row[0] != NONE: return Value.LOSE
        
        # Verticals
        for col_num in range(len(self.board[0])):
            col = [row[col_num] for row in self.board]
            if len(set(col)) == 1 and col[0] != NONE: return Value.LOSE
        
        # Diagonals
            diag1 = [self.board[i][i] for i in range(len(self.board[0]))]
            diag2 = [self.board[i][len(self.board[0])-1-i] for i in range(len(self.board[0]))]
            if len(set(diag1)) == 1 and diag1[0] != NONE: return Value.LOSE
            if len(set(diag2)) == 1 and diag2[0] != NONE: return Value.LOSE

        if len(self.generateMoves()) == 0:
            return Value.TIE

        return Value.UNDECIDED

    def toString(self):
        string = ""
        for row in self.board:
            string += "".join(row) + "\n"
        return string

    def serialize(self):
        switch = { 
            FIRST : { FIRST : FIRST, SECOND : SECOND, NONE : NONE }, 
            SECOND : { FIRST : SECOND, SECOND : FIRST, NONE : NONE } 
        }
        flatten_list = [switch[self.turn][entry] for row in self.reduction() for entry in row]
        return "".join(flatten_list)

    # Returns lowest equivalent state
    def reduction(self):
        def value(board):
            values = { NONE : "0", FIRST : "1", SECOND : "2" }
            flatten_list = [values[entry] for row in board for entry in row]
            return int("".join(flatten_list))
        def rotate(board):
            return [list(row) for row in zip(*board[::-1])]
        def flip(board):
            return board[::-1]
        board, lowest_value, lowest_board = self.board, int("2" * len(self.board) * len(self.board[0])), self.board
        for _ in range(2):
            for _ in range(4):
                board_value = value(board)
                if board_value <= lowest_value: lowest_board, lowest_value = board, board_value
                board = rotate(board)
            board = flip(board)                        
        return lowest_board

    def moveFromInput(self, prompt):
        print(prompt)
        return tuple(int(x.strip()) for x in input().split(','))

if __name__ == '__main__':
    game = TTT(size=4)
    solver = Solver.Solver(name=game.name)
    gameManager = GameManager(game, solver)
    gameManager.play()