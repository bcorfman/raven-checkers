import unittest
import checkers
import games
from globalconst import *

class testBlackManSingleJump(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        squares = self.board.squares
        self.board.clear()
        squares[5] = BLACK | MAN
        squares[10] = WHITE | MAN

    def testJump(self):
        self.assertEqual(self.game.legal_moves(self.board),
                         [[[5, BLACK | MAN, FREE],
                           [10, WHITE | MAN, FREE],
                           [15, FREE, BLACK | MAN]]])

class testBlackManDoubleJump(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        squares = self.board.squares
        self.board.clear()
        squares[5] = BLACK | MAN
        squares[10] = WHITE | MAN
        squares[19] = WHITE | MAN

    def testJump(self):
        self.assertEqual(self.game.legal_moves(self.board),
                        [[[5, BLACK | MAN, FREE],
                          [10, WHITE | MAN, FREE],
                          [15, FREE, FREE],
                          [19, WHITE | MAN, FREE],
                          [23, FREE, BLACK | MAN]]])

class testBlackManCrownKingOnJump(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        squares = self.board.squares
        self.board.clear()
        squares[10] = BLACK | MAN
        squares[15] = WHITE | MAN
        squares[25] = WHITE | MAN
        squares[34] = WHITE | MAN
        # set another man on 33 to test that crowning
        # move ends the turn
        squares[33] = WHITE | MAN

    def testJump(self):
        self.assertEqual(self.game.legal_moves(self.board),
                         [[[10, BLACK | MAN, FREE],
                           [15, WHITE | MAN, FREE],
                           [20, FREE, FREE],
                           [25, WHITE | MAN, FREE],
                           [30, FREE, FREE],
                           [34, WHITE | MAN, FREE],
                           [38, FREE, BLACK | KING]]])

class testBlackManCrownKingOnMove(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        squares = self.board.squares
        self.board.clear()
        squares[32] = BLACK | MAN
        squares[15] = WHITE | MAN

    def testJump(self):
        self.assertEqual(self.game.legal_moves(self.board),
                         [[[32, BLACK | MAN, FREE],
                           [37, FREE, BLACK | KING]]])


class testBlackKingOptionalJumpDiamond(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        squares = self.board.squares
        self.board.clear()
        squares[11] = BLACK | KING
        squares[16] = WHITE | MAN
        squares[25] = WHITE | MAN
        squares[24] = WHITE | MAN
        squares[15] = WHITE | MAN

    def testJump(self):
        self.assertEqual(self.game.legal_moves(self.board),
                         [[[11, BLACK | KING, FREE], [15, WHITE | MAN, FREE],
                           [19, FREE, FREE], [24, WHITE | MAN, FREE],
                           [29, FREE, FREE], [25, WHITE | MAN, FREE],
                           [21, FREE, FREE], [16, WHITE | MAN, FREE],
                           [11, FREE, BLACK | KING]],
                          [[11, BLACK | KING, FREE], [16, WHITE | MAN, FREE],
                           [21, FREE, FREE], [25, WHITE | MAN, FREE],
                           [29, FREE, FREE], [24, WHITE | MAN, FREE],
                           [19, FREE, FREE], [15, WHITE | MAN, FREE],
                           [11, FREE, BLACK | KING]]])


class testWhiteManSingleJump(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = WHITE
        squares = self.board.squares
        self.board.clear()
        squares[34] = WHITE | MAN
        squares[30] = BLACK | MAN

    def testJump(self):
        self.assertEqual(self.game.legal_moves(self.board),
                         [[[34, WHITE | MAN, FREE],
                           [30, BLACK | MAN, FREE],
                           [26, FREE, WHITE | MAN]]])


class testWhiteManDoubleJump(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = WHITE
        squares = self.board.squares
        self.board.clear()
        squares[34] = WHITE | MAN
        squares[30] = BLACK | MAN
        squares[21] = BLACK | MAN

    def testJump(self):
        self.assertEqual(self.game.legal_moves(self.board),
                         [[[34, WHITE | MAN, FREE],
                           [30, BLACK | MAN, FREE],
                           [26, FREE, FREE],
                           [21, BLACK | MAN, FREE],
                           [16, FREE, WHITE | MAN]]])

class testWhiteManCrownKingOnMove(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = WHITE
        squares = self.board.squares
        self.board.clear()
        squares[13] = WHITE | MAN
        squares[30] = BLACK | MAN

    def testJump(self):
        self.assertEqual(self.game.legal_moves(self.board),
                         [[[13, WHITE | MAN, FREE],
                           [8, FREE, WHITE | KING]]])


class testWhiteManCrownKingOnJump(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = WHITE
        squares = self.board.squares
        self.board.clear()
        squares[34] = WHITE | MAN
        squares[30] = BLACK | MAN
        squares[21] = BLACK | MAN
        squares[11] = BLACK | KING
        # set another man on 10 to test that crowning
        # move ends the turn
        squares[10] = BLACK | KING

    def testJump(self):
        self.assertEqual(self.game.legal_moves(self.board),
                         [[[34, WHITE | MAN, FREE],
                           [30, BLACK | MAN, FREE],
                           [26, FREE, FREE],
                           [21, BLACK | MAN, FREE],
                           [16, FREE, FREE],
                           [11, BLACK | KING, FREE],
                           [6, FREE, WHITE | KING]]])

class testWhiteKingOptionalJumpDiamond(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = WHITE
        squares = self.board.squares
        self.board.clear()
        squares[11] = WHITE | KING
        squares[16] = BLACK | MAN
        squares[25] = BLACK | MAN
        squares[24] = BLACK | MAN
        squares[15] = BLACK | MAN

    def testJump(self):
        self.assertEqual(self.game.legal_moves(self.board),
                         [[[11, WHITE | KING, FREE], [15, BLACK | MAN, FREE],
                           [19, FREE, FREE], [24, BLACK | MAN, FREE],
                           [29, FREE, FREE], [25, BLACK | MAN, FREE],
                           [21, FREE, FREE], [16, BLACK | MAN, FREE],
                           [11, FREE, WHITE | KING]],
                          [[11, WHITE | KING, FREE], [16, BLACK | MAN, FREE],
                            [21, FREE, FREE], [25, BLACK | MAN, FREE],
                            [29, FREE, FREE], [24, BLACK | MAN, FREE],
                            [19, FREE, FREE], [15, BLACK | MAN, FREE],
                            [11, FREE, WHITE | KING]]])

class testUtilityFunc(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.to_move = WHITE
        self.squares = self.board.squares

    def testInitialUtility(self):
        self.assertEqual(self.board.utility(WHITE), -2)

class testSuccessorFuncForBlack(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        squares = self.board.squares

    def testInitialBlackMoves(self):
        # Tests whether initial game moves are correct from
        # Black's perspective
        moves = [m for m, s in self.game.successors(self.board)]
        self.assertEqual(moves, [[[14, BLACK | MAN, FREE],
                                  [19, FREE, BLACK | MAN]],
                                 [[15, BLACK | MAN, FREE],
                                  [19, FREE, BLACK | MAN]],
                                 [[15, BLACK | MAN, FREE],
                                  [20, FREE, BLACK | MAN]],
                                 [[16, BLACK | MAN, FREE],
                                  [20, FREE, BLACK | MAN]],
                                 [[16, BLACK | MAN, FREE],
                                  [21, FREE, BLACK | MAN]],
                                 [[17, BLACK | MAN, FREE],
                                  [21, FREE, BLACK | MAN]],
                                 [[17, BLACK | MAN, FREE],
                                  [22, FREE, BLACK | MAN]]])

class testSuccessorFuncForWhite(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        # I'm cheating here ... white never moves first in
        # a real game, but I want to see that the moves
        # would work anyway.
        self.board.to_move = WHITE
        squares = self.board.squares

    def testInitialWhiteMoves(self):
        # Tests whether initial game moves are correct from
        # White's perspective
        moves = [m for m, s in self.game.successors(self.board)]
        self.assertEqual(moves, [[[28, WHITE | MAN, FREE],
                                  [24, FREE, WHITE | MAN]],
                                 [[28, WHITE | MAN, FREE],
                                  [23, FREE, WHITE | MAN]],
                                 [[29, WHITE | MAN, FREE],
                                  [25, FREE, WHITE | MAN]],
                                 [[29, WHITE | MAN, FREE],
                                  [24, FREE, WHITE | MAN]],
                                 [[30, WHITE | MAN, FREE],
                                  [26, FREE, WHITE | MAN]],
                                 [[30, WHITE | MAN, FREE],
                                  [25, FREE, WHITE | MAN]],
                                 [[31, WHITE | MAN, FREE],
                                  [26, FREE, WHITE | MAN]]])


#   (white)
#            37  38  39  40
#          32  33  34  35
#            28  29  30  31
#          23  24  25  26
#            19  20  21  22
#          14  15  16  17
#            10  11  12  13
#          5   6   7   8
#   (black)

if __name__ == '__main__':
    game = checkers.Checkers()
    board = game.curr_state
    squares = board.squares
    board.clear()
    squares[37] = WHITE | MAN
    squares[32] = BLACK | MAN
    squares[24] = BLACK | MAN
    squares[34] = WHITE | KING
    board.to_move = WHITE
    games.play_game(game, checkers.AlphabetaPlayer(BLACK, 8),
                    checkers.AlphabetaPlayer(WHITE, 8))
