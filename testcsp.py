__author__ = 'brandon_corfman'

from csp import backtracking_search
from globalconst import BLACK, MAN
from formation import formation_csp, BLACK_MAP
import unittest
import checkers


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


class TestLongDykePossibleFromStart(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = BLACK

    def testCSP(self):
        long_dyke_csp = formation_csp([8, 9, 14, 19, 24, 29], self.board)
        result = backtracking_search(long_dyke_csp)
        self.assertEqual(result[8], 8)
        self.assertEqual(result[9], 9)
        self.assertEqual(result[14], 14)
        self.assertTrue(result[19] in BLACK_MAP[19] and result[19] != result[24] and result[19] != result[29])
        self.assertTrue(result[24] in BLACK_MAP[24] and result[24] != result[29] and result[24] != result[19])
        self.assertTrue(result[29] in BLACK_MAP[29] and result[29] != result[24] and result[29] != result[24])


class TestLongDykeFailsWithMissingChecker(unittest.TestCase):
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
        long_dyke_csp = formation_csp([8, 9, 14, 19, 24, 29], self.board)
        result = backtracking_search(long_dyke_csp)
        self.assertEqual(result, None)


class TestLongDykeFailsWithWrongPositions(unittest.TestCase):
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
        squares[15] = BLACK | MAN

    def testCSP(self):
        long_dyke_csp = formation_csp([8, 9, 14, 19, 24, 29], self.board)
        result = backtracking_search(long_dyke_csp)
        self.assertEqual(result, None)
