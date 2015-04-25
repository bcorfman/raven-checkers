__author__ = 'brandon_corfman'
from globalconst import BLACK, MAN, FREE
from Tkinter import Tk
from mainframe import MainFrame
import goalthink
import unittest
from goalformation import GoalShortDyke, GoalLongDyke, GoalPhalanx, GoalPyramid, GoalMill, GoalEchelon

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


class TestThinkFromInitialBoard(unittest.TestCase):
    def setUp(self):
        root = Tk()
        mainframe = MainFrame(root)
        mainframe.root.update()
        mainframe.root.withdraw()

        self.manager = mainframe.manager
        self.board = self.manager.model.curr_state
        self.board.to_move = BLACK
        squares = self.board.squares
        # make initial 11-15 move for Black
        squares[18] = FREE
        squares[24] = BLACK | MAN

    def testCorrectGoalSelected(self):
        self.manager.controller1.end_turn()
        self.manager.controller2.start_turn()
        self.assertIn(repr(self.manager.controller2._thinker.subgoals[0]), ['GoalShortDyke', 'GoalLongDyke',
                                                                            'GoalEchelon', 'GoalPhalanx',
                                                                            'GoalPyramid', 'GoalMill'])
