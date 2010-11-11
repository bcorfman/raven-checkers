from globalconst import BLACK, WHITE, KING
import onek_onek
import unittest
import checkers

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

class TestOneKingAttackOneKingEvaluator(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.board.clear()
        squares = self.board.squares
        squares[6] = BLACK | KING
        squares[48] = WHITE | KING
        self.board.to_move = BLACK
        self.board.update_piece_count()

    def testInitialBlackMoves(self):
        ev = onek_onek.OneKingAttackOneKingEvaluator(1.0)
        self.assertEqual(ev.calculateDesirability(self.board), 1.0)
