import Solver
from util import *
from multiprocessing import Process, Value, Array, Manager, current_process

class TierSolver(Solver.Solver):

    def __init__(self, *args, **kwargs):
        super(TierSolver, self).__init__(*args, **kwargs)
        if self.mp: self.solve = self.solveTierMP
        else: self.solve = self.solveTier
        self.generateTierBoards()

    def solveTier(self, game):
        serial = game.serialize()
        if serial in self.memory: return self.memory[serial]
        for i in range(game.getNumTiers(), -1, -1):
            boards = self.tiers[game.getCurTier()].values()
            self.solveBoards(boards)
        return self.memory[serial]

    def solveTierMP(self, game):
        serial = game.serialize()
        if serial in self.memory: return self.memory[serial]
        self.memory = Manager().dict()
        self.remoteness = Manager().dict()
        for i in range(game.getNumTiers(), -1, -1):
            boards = self.tiers[game.getCurTier()].values()
            if len(boards) < 4: 
                processes = [Process(target=self.solveBoards, args=(boards,))]
            else: 
                processes = [Process(target=self.solveBoards, 
                    args=(boards[i:i + n],)) for i in range(0, len(boards), len(boards) // 4)]
            for p in processes:
                p.start()
            for p in processes:
                p.join()
        return self.memory[serial]

    def solveBoards(self, boards):
        for board in boards:
            if board.primitive() != GameValue.UNDECIDED: 
                self.memory[board.serialize()] = board.primitive()
                self.remoteness[board.serialize()] = 0
            else:
                self.solveTraverse(board)

    def generateTierBoards(self):
        self.tiers = { i:{} for i in range(self.base.getNumTiers()) }
        def helper(game):
            serialized = game.serialize()
            if serialized not in self.tiers[game.getCurTier()]:
                self.tiers[game.getCurTier()][serialized] = game
                for move in game.generateMoves():
                    helper(game.doMove(move))
        helper(self.base)