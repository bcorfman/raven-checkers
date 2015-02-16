__author__ = 'brandon_corfman'
from goalevaluator import GoalEvaluator
from csp import backtracking_search
from formation import formation_csp
from globalconst import WHITE
from shortdyke import GoalShortDyke


class ShortDykeEvaluator(GoalEvaluator):
    def __init__(self, bias):
        GoalEvaluator.__init__(self, bias)

    def calculate_desirability(self, board):
        short_dyke_csp = formation_csp([8, 9, 14, 17, 23, 29], board)
        if backtracking_search(short_dyke_csp):
            return 1.0
        else:
            return 0.0

    def set_goal(self, board):
        player = board.to_move
        board.removeAllSubgoals()
        goal_set = board.addWhiteSubgoal if player == WHITE else board.addBlackSubgoal
        goal_set(GoalShortDyke(board))

