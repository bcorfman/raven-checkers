import onek_onek
import unittest

class TestOneKingAttackOneKingEvaluator(unittest.TestCase):
    def setUp(self):
        self.game = checkers.Checkers()
        self.board = self.game.curr_state
        self.eval = onek_onek.OneKingAttackOneKingEvaluator()
    def testInitialBlackMoves(self):
        # Tests whether initial game moves are correct from
        # Black's perspective
        moves = [m for m, _ in self.game.successors(self.board)]
        self.assertEqual(moves, [[[17, BLACK | MAN, FREE],
                                  [23, FREE, BLACK | MAN]],
                                 [[18, BLACK | MAN, FREE],
                                  [23, FREE, BLACK | MAN]],
                                 [[18, BLACK | MAN, FREE],
                                  [24, FREE, BLACK | MAN]],
                                 [[19, BLACK | MAN, FREE],
                                  [24, FREE, BLACK | MAN]],
                                 [[19, BLACK | MAN, FREE],
                                  [25, FREE, BLACK | MAN]],
                                 [[20, BLACK | MAN, FREE],
                                  [25, FREE, BLACK | MAN]],
                                 [[20, BLACK | MAN, FREE],
                                  [26, FREE, BLACK | MAN]]])
        

