__author__ = 'brandon_corfman'
from goalevaluator import GoalEvaluator
from csp import backtracking_search
from formation import formation_csp
from globalconst import WHITE
from longdyke import GoalLongDyke


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


class LongDykeEvaluator(GoalEvaluator):
    def __init__(self, bias):
        GoalEvaluator.__init__(self, bias)

    def calculate_desirability(self, board):
        long_dyke_csp = formation_csp([8, 9, 14, 19, 24, 29], board)
        if backtracking_search(long_dyke_csp):
            return 1.0
        else:
            return 0.0

    def set_goal(self, board):
        player = board.to_move
        board.removeAllSubgoals()
        goal_set = board.addWhiteSubgoal if player == WHITE else board.addBlackSubgoal
        goal_set(GoalLongDyke(board))

