__author__ = 'brandon_corfman'
from evaluators import formation_csp
from csp import backtracking_search
from formation import BLACK_MAP
from globalconst import BLACK, MAN
import unittest
import checkers


class TestShortDykePossibleFromStart(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = BLACK

    def testCSP(self):
        short_dyke_csp = formation_csp(self.board.short_dyke, self.board)
        result = backtracking_search(short_dyke_csp, mcv=True, lcv=True)
        self.assertEqual(result[8], 8)
        self.assertEqual(result[9], 9)
        self.assertEqual(result[14], 14)
        self.assertTrue(result[17] in BLACK_MAP[17] and result[17] != result[23] and result[17] != result[29])
        self.assertTrue(result[23] in BLACK_MAP[23] and result[23] != result[29] and result[23] != result[17])
        self.assertTrue(result[29] in BLACK_MAP[29] and result[29] != result[17] and result[29] != result[23])


class TestShortDykePossibleWithReducedSet(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = BLACK
        squares = self.board.squares
        self.board.clear()
        squares[8] = BLACK | MAN
        squares[9] = BLACK | MAN
        squares[14] = BLACK | MAN
        squares[13] = BLACK | MAN
        squares[6] = BLACK | MAN
        squares[18] = BLACK | MAN

    def testCSP(self):
        short_dyke_csp = formation_csp(self.board.short_dyke, self.board)
        result = backtracking_search(short_dyke_csp, mcv=True, lcv=True)
        self.assertEqual(result[8], 8)
        self.assertEqual(result[9], 9)
        self.assertEqual(result[14], 14)
        self.assertTrue(result[17] in BLACK_MAP[17] and result[17] != result[23] and result[17] != result[29])
        self.assertTrue(result[23] in BLACK_MAP[23] and result[23] != result[29] and result[23] != result[17])
        self.assertTrue(result[29] in BLACK_MAP[29] and result[29] != result[17] and result[29] != result[23])


class TestShortDykeFailsWithMissingChecker(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = BLACK
        squares = self.board.squares
        self.board.clear()
        squares[8] = BLACK | MAN
        squares[9] = BLACK | MAN
        squares[14] = BLACK | MAN
        squares[13] = BLACK | MAN
        squares[6] = BLACK | MAN

    def testCSP(self):
        short_dyke_csp = formation_csp(self.board.short_dyke, self.board)
        result = backtracking_search(short_dyke_csp, mcv=True, lcv=True)
        self.assertEqual(result, None)


class TestShortDykeFailsWithWrongPositions(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = BLACK
        squares = self.board.squares
        self.board.clear()
        squares[8] = BLACK | MAN
        squares[9] = BLACK | MAN
        squares[14] = BLACK | MAN
        squares[13] = BLACK | MAN
        squares[6] = BLACK | MAN
        squares[30] = BLACK | MAN

    def testCSP(self):
        short_dyke_csp = formation_csp(self.board.short_dyke, self.board)
        result = backtracking_search(short_dyke_csp, mcv=True, lcv=True)
        self.assertEqual(result, None)
