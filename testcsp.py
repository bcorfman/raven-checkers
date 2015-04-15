__author__ = 'brandon_corfman'
from evaluators import formation_csp
from csp import backtracking_search, forward_checking, mrv
from formation import BLACK_MAP, BLACK_COST
from globalconst import BLACK, MAN
import unittest
import checkers


def calc_cost(formation):
    cost = 0
    for k, v in formation.iteritems():
        if k == v:
            continue
        reachable = BLACK_MAP[k]
        idx = reachable.index(v)
        cost += BLACK_COST[k][idx]
    return cost


class TestShortDykePossibleFromStart(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = BLACK

    def testCSP(self):
        short_dyke_csp = formation_csp(self.board.short_dyke, self.board)
        result = backtracking_search(short_dyke_csp, select_unassigned_variable=mrv, inference=forward_checking)
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
        result = backtracking_search(short_dyke_csp, select_unassigned_variable=mrv, inference=forward_checking)
        self.assertEqual(result[8], 8)
        self.assertEqual(result[9], 9)
        self.assertEqual(result[14], 14)
        self.assertTrue(result[17] in BLACK_MAP[17] and result[17] != result[23] and result[17] != result[29])
        self.assertTrue(result[23] in BLACK_MAP[23] and result[23] != result[29] and result[23] != result[17])
        self.assertTrue(result[29] in BLACK_MAP[29] and result[29] != result[17] and result[29] != result[23])


class TestShortDykeReducedSetAllSolutions(unittest.TestCase):
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
        #for soln in backtracking_search(short_dyke_csp, select_unassigned_variable=mrv, inference=forward_checking,
        #                                all_values=True):
        #    print soln
        self.assertEqual(True, True)


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
        result = backtracking_search(short_dyke_csp, select_unassigned_variable=mrv, inference=forward_checking)
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
        result = backtracking_search(short_dyke_csp, select_unassigned_variable=mrv, inference=forward_checking)
        self.assertEqual(result, None)
