import unittest
import checkers
import games
from globalconst import *

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
class TestBlackManSingleJump(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        squares = self.board.squares
        self.board.clear()
        squares[6] = BLACK | MAN
        squares[12] = WHITE | MAN

    def testJump(self):
        moves = self.game.legal_moves(self.board)
        self.assertEqual(moves[0].affected_squares,
                         [[6, BLACK | MAN, FREE],
                          [12, WHITE | MAN, FREE],
                          [18, FREE, BLACK | MAN]])

class TestBlackManDoubleJump(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        squares = self.board.squares
        self.board.clear()
        squares[6] = BLACK | MAN
        squares[12] = WHITE | MAN
        squares[23] = WHITE | MAN

    def testJump(self):
        moves = self.game.legal_moves(self.board)
        self.assertEqual(moves[0].affected_squares,
                        [[6, BLACK | MAN, FREE],
                         [12, WHITE | MAN, FREE],
                         [18, FREE, FREE],
                         [23, WHITE | MAN, FREE],
                         [28, FREE, BLACK | MAN]])

class TestBlackManCrownKingOnJump(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        squares = self.board.squares
        self.board.clear()
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
        squares[12] = BLACK | MAN
        squares[18] = WHITE | MAN
        squares[30] = WHITE | MAN
        squares[41] = WHITE | MAN
        # set another man on 40 to test that crowning
        # move ends the turn
        squares[40] = WHITE | MAN

    def testJump(self):
        moves = self.game.legal_moves(self.board)
        self.assertEqual(moves[0].affected_squares,
                         [[12, BLACK | MAN, FREE],
                          [18, WHITE | MAN, FREE],
                          [24, FREE, FREE],
                          [30, WHITE | MAN, FREE],
                          [36, FREE, FREE],
                          [41, WHITE | MAN, FREE],
                          [46, FREE, BLACK | KING]])

class TestBlackManCrownKingOnMove(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        squares = self.board.squares
        self.board.clear()
        squares[39] = BLACK | MAN
        squares[18] = WHITE | MAN

    def testJump(self):
        moves = self.game.legal_moves(self.board)
        self.assertEqual(moves[0].affected_squares,
                         [[39, BLACK | MAN, FREE],
                          [45, FREE, BLACK | KING]])


class TestBlackKingOptionalJumpDiamond(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        squares = self.board.squares
        self.board.clear()
        squares[13] = BLACK | KING
        squares[19] = WHITE | MAN
        squares[30] = WHITE | MAN
        squares[29] = WHITE | MAN
        squares[18] = WHITE | MAN

    def testJump(self):
        moves = self.game.legal_moves(self.board)
        self.assertEqual(moves[0].affected_squares,
                         [[13, BLACK | KING, FREE], [18, WHITE | MAN, FREE],
                          [23, FREE, FREE], [29, WHITE | MAN, FREE],
                          [35, FREE, FREE], [30, WHITE | MAN, FREE],
                          [25, FREE, FREE], [19, WHITE | MAN, FREE],
                          [13, FREE, BLACK | KING]])
        self.assertEqual(moves[1].affected_squares,
                         [[13, BLACK | KING, FREE], [19, WHITE | MAN, FREE],
                          [25, FREE, FREE], [30, WHITE | MAN, FREE],
                          [35, FREE, FREE], [29, WHITE | MAN, FREE],
                          [23, FREE, FREE], [18, WHITE | MAN, FREE],
                          [13, FREE, BLACK | KING]])

class TestWhiteManSingleJump(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = WHITE
        squares = self.board.squares
        self.board.clear()
        squares[41] = WHITE | MAN
        squares[36] = BLACK | MAN

    def testJump(self):
        moves = self.game.legal_moves(self.board)
        self.assertEqual(moves[0].affected_squares,
                         [[41, WHITE | MAN, FREE],
                          [36, BLACK | MAN, FREE],
                          [31, FREE, WHITE | MAN]])


class TestWhiteManDoubleJump(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = WHITE
        squares = self.board.squares
        self.board.clear()
        squares[41] = WHITE | MAN
        squares[36] = BLACK | MAN
        squares[25] = BLACK | MAN

    def testJump(self):
        moves = self.game.legal_moves(self.board)
        self.assertEqual(moves[0].affected_squares,
                         [[41, WHITE | MAN, FREE],
                          [36, BLACK | MAN, FREE],
                          [31, FREE, FREE],
                          [25, BLACK | MAN, FREE],
                          [19, FREE, WHITE | MAN]])

class TestWhiteManCrownKingOnMove(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = WHITE
        squares = self.board.squares
        self.board.clear()
        squares[15] = WHITE | MAN
        squares[36] = BLACK | MAN

    def testJump(self):
        moves = self.game.legal_moves(self.board)
        self.assertEqual(moves[0].affected_squares,
                         [[15, WHITE | MAN, FREE],
                          [9, FREE, WHITE | KING]])


class TestWhiteManCrownKingOnJump(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = WHITE
        squares = self.board.squares
        self.board.clear()
        squares[41] = WHITE | MAN
        squares[36] = BLACK | MAN
        squares[25] = BLACK | MAN
        squares[13] = BLACK | KING
        # set another man on 10 to test that crowning
        # move ends the turn
        squares[12] = BLACK | KING

    def testJump(self):
        moves = self.game.legal_moves(self.board)
        self.assertEqual(moves[0].affected_squares,
                         [[41, WHITE | MAN, FREE],
                          [36, BLACK | MAN, FREE],
                          [31, FREE, FREE],
                          [25, BLACK | MAN, FREE],
                          [19, FREE, FREE],
                          [13, BLACK | KING, FREE],
                          [7, FREE, WHITE | KING]])

class TestWhiteKingOptionalJumpDiamond(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = WHITE
        squares = self.board.squares
        self.board.clear()
        squares[13] = WHITE | KING
        squares[19] = BLACK | MAN
        squares[30] = BLACK | MAN
        squares[29] = BLACK | MAN
        squares[18] = BLACK | MAN

    def testJump(self):
        moves = self.game.legal_moves(self.board)
        self.assertEqual(moves[0].affected_squares,
                         [[13, WHITE | KING, FREE], [18, BLACK | MAN, FREE],
                          [23, FREE, FREE], [29, BLACK | MAN, FREE],
                          [35, FREE, FREE], [30, BLACK | MAN, FREE],
                          [25, FREE, FREE], [19, BLACK | MAN, FREE],
                          [13, FREE, WHITE | KING]])
        self.assertEqual(moves[1].affected_squares,
                         [[13, WHITE | KING, FREE], [19, BLACK | MAN, FREE],
                          [25, FREE, FREE], [30, BLACK | MAN, FREE],
                          [35, FREE, FREE], [29, BLACK | MAN, FREE],
                          [23, FREE, FREE], [18, BLACK | MAN, FREE],
                          [13, FREE, WHITE | KING]])

class TestUtilityFunc(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = WHITE
        self.squares = self.board.squares

    def testInitialUtility(self):
        code = sum(self.board.value[s] for s in self.squares)
        nwm = code % 16
        nwk = (code >> 4) % 16
        nbm = (code >> 8) % 16
        nbk = (code >> 12) % 16
        nm = nbm + nwm
        nk = nbk + nwk

        self.assertEqual(self.board._eval_cramp(self.squares), 0)
        self.assertEqual(self.board._eval_backrankguard(self.squares), 0)
        self.assertEqual(self.board._eval_doublecorner(self.squares), 0)
        self.assertEqual(self.board._eval_center(self.squares), 0)
        self.assertEqual(self.board._eval_edge(self.squares), 0)
        self.assertEqual(self.board._eval_tempo(self.squares, nm, nbk,
                                                nbm, nwk, nwm), 0)
        self.assertEqual(self.board._eval_playeropposition(self.squares, nwm,
                                                           nwk, nbk, nbm, nm,
                                                           nk), 0)
        self.assertEqual(self.board.utility(WHITE), -2)

class TestSuccessorFuncForBlack(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state

    def testInitialBlackMoves(self):
        # Tests whether initial game moves are correct from
        # Black's perspective
        moves = [m for m, _ in self.game.successors(self.board)]
        self.assertEqual(moves[0].affected_squares,
                         [[17, BLACK | MAN, FREE],
                          [23, FREE, BLACK | MAN]])
        self.assertEqual(moves[1].affected_squares,
                         [[18, BLACK | MAN, FREE],
                          [23, FREE, BLACK | MAN]])
        self.assertEqual(moves[2].affected_squares,
                         [[18, BLACK | MAN, FREE],
                          [24, FREE, BLACK | MAN]])
        self.assertEqual(moves[3].affected_squares,
                         [[19, BLACK | MAN, FREE],
                          [24, FREE, BLACK | MAN]])
        self.assertEqual(moves[4].affected_squares,
                         [[19, BLACK | MAN, FREE],
                          [25, FREE, BLACK | MAN]])
        self.assertEqual(moves[5].affected_squares,
                         [[20, BLACK | MAN, FREE],
                          [25, FREE, BLACK | MAN]])
        self.assertEqual(moves[6].affected_squares,
                         [[20, BLACK | MAN, FREE],
                          [26, FREE, BLACK | MAN]])

class TestSuccessorFuncForWhite(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        # I'm cheating here ... white never moves first in
        # a real game, but I want to see that the moves
        # would work anyway.
        self.board.to_move = WHITE

    def testInitialWhiteMoves(self):
        # Tests whether initial game moves are correct from
        # White's perspective
        moves = [m for m, _ in self.game.successors(self.board)]
        self.assertEqual(moves[0].affected_squares,
                         [[34, WHITE | MAN, FREE],
                          [29, FREE, WHITE | MAN]])
        self.assertEqual(moves[1].affected_squares,
                         [[34, WHITE | MAN, FREE],
                          [28, FREE, WHITE | MAN]])
        self.assertEqual(moves[2].affected_squares,
                         [[35, WHITE | MAN, FREE],
                          [30, FREE, WHITE | MAN]])
        self.assertEqual(moves[3].affected_squares,
                         [[35, WHITE | MAN, FREE],
                          [29, FREE, WHITE | MAN]])
        self.assertEqual(moves[4].affected_squares,
                         [[36, WHITE | MAN, FREE],
                          [31, FREE, WHITE | MAN]])
        self.assertEqual(moves[5].affected_squares,
                         [[36, WHITE | MAN, FREE],
                          [30, FREE, WHITE | MAN]])
        self.assertEqual(moves[6].affected_squares,
                         [[37, WHITE | MAN, FREE],
                          [31, FREE, WHITE | MAN]])

if __name__ == '__main__':
    unittest.main()
