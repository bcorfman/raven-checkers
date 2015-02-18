__author__ = 'brandon_corfman'
from goalevaluator import GoalEvaluator
from csp import backtracking_search
from formation import formation_csp, BLACK_MAP, WHITE_MAP, BLACK
from globalconst import WHITE
from shortdyke import GoalShortDyke
from search import Problem, depth_first_tree_search
from utils import manhattan_distance, argmin_random_tie


class FormationProblem(Problem):
    def __init__(self, formation, board):
        self.start_row = None
        self.start_col = None
        self.end_row = None
        self.end_col = None
        self.formation = formation
        self.board = board
        self.initial = []

    def successor(self, state):
        # assign next element in state
        pos_map = BLACK_MAP if self.board.to_move == BLACK else WHITE_MAP
        next_var = self.formation[len(state)]
        goal_row, goal_col = self.board.gridmap[next_var]

        def calc_dist(loc):
            if loc not in state:
                row, col = self.board.gridmap[loc]
                return manhattan_distance(row, col, goal_row, goal_col)
            else:
                return 9999  # location has already been used, so don't let the distance be selected

        best = argmin_random_tie(list(pos_map[next_var]), calc_dist)
        return state + [best] if best else None

    def goal_test(self, state):
        return len(state) == len(self.formation)

    def value(self):
        pass


def measure_formation_closeness(formation, board):
    solution = depth_first_tree_search(FormationProblem(formation, board))
    if solution:
        diff = 0.0
        for p in formation:
            goal_row, goal_col = board.gridmap[p]
            for s in solution:
                soln_row, soln_col = board.gridmap[s]
                diff += manhattan_distance(soln_row, soln_col, goal_row, goal_col)
        return diff
    else:
        return 0.0


class ShortDykeEvaluator(GoalEvaluator):
    def __init__(self, bias):
        GoalEvaluator.__init__(self, bias)

    def calculate_desirability(self, board):
        return measure_formation_closeness([8, 9, 14, 17, 23, 29], board)

    def set_goal(self, board):
        player = board.to_move
        board.remove_all_subgoals()
        goal_set = board.add_white_subgoal if player == WHITE else board.add_black_subgoal
        goal_set(GoalShortDyke(board))
