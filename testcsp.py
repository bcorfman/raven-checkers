__author__ = 'brandon_corfman'

from csp import CSP, different_values_constraint, backtracking_search
from globalconst import BLACK_MAP, WHITE_MAP, BLACK, MAN
import unittest
import checkers


def formation_csp(variables, board):
    """Return an instance of the CSP to see if the short dyke formation can be obtained."""
    domains = {}
    player = board.to_move
    pos_map = BLACK_MAP if player == BLACK else WHITE_MAP
    neighbors = {}
    for var in variables:
        domains[var] = [pos for pos in pos_map[var] if board.squares[pos] == player + MAN]
        neighbors[var] = set(variables) - {var}
    return CSP(variables, domains, neighbors, different_values_constraint)


class TestShortDykePossibleFromStart(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = BLACK

    def testCSP(self):
        short_dyke_csp = formation_csp([8, 9, 14, 17, 23, 29], self.board)
        result = backtracking_search(short_dyke_csp)
        self.assertEqual(result[8], 8)
        self.assertEqual(result[9], 9)
        self.assertEqual(result[14], 14)
        self.assertTrue(result[17] in BLACK_MAP[17] and result[17] != result[23] and result[17] != result[29])
        self.assertTrue(result[23] in BLACK_MAP[23] and result[23] != result[29] and result[23] != result[17])
        self.assertTrue(result[29] in BLACK_MAP[29] and result[29] != result[17] and result[29] != result[23])

#   (white)
#            45  46  47  48
#          39  40  41  42
#            34  35  36  37
#          28  29  30  31
#            23  24  25  26
#          17  18  19  20
#            12  13  14  15
#          6   7   8   9
#   (black)


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
        short_dyke_csp = formation_csp([8, 9, 14, 17, 23, 29], self.board)
        result = backtracking_search(short_dyke_csp)
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
        short_dyke_csp = formation_csp([8, 9, 14, 17, 23, 29], self.board)
        result = backtracking_search(short_dyke_csp)
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
        short_dyke_csp = formation_csp([8, 9, 14, 17, 23, 29], self.board)
        result = backtracking_search(short_dyke_csp)
        self.assertEqual(result, None)
