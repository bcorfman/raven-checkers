__author__ = 'brandon_corfman'
from globalconst import BLACK
from Tkinter import Tk
from mainframe import MainFrame
import think
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

    def testCorrectGoalSelected(self):
        self.manager.controller2.start_turn()
        self.assertIn(repr(self.manager.controller2._thinker.subgoals[0]), ['GoalShortDyke', 'GoalLongDyke',
                                                                            'GoalEchelon', 'GoalPhalanx',
                                                                            'GoalPyramid', 'GoalMill'])
