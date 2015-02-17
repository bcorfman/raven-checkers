__author__ = 'brandon_corfman'
from goalevaluator import GoalEvaluator
from csp import backtracking_search
from formation import formation_csp, BLACK_MAP, WHITE_MAP, BLACK
from globalconst import WHITE
from shortdyke import GoalShortDyke
from search import Problem
from utils import manhattan_distance


class FormationProblem(Problem):
    def __init__(self, initial, goal, formation, board):
        Problem.__init__(initial, goal)
        self.start_row = None
        self.start_col = None
        self.end_row = None
        self.end_col = None
        self.formation = formation
        self.board = board

    def successor(self, state):
        # assign next element in state
        pos_map = BLACK_MAP if self.board.to_move == BLACK else WHITE_MAP
        next_var = self.formation[len(state)]
        goal_row, goal_col = self.board.grid_map[next_var]
        best_dist = 9999
        best_pos = None
        for p in pos_map[next_var]:
            row, col = self.board.grid_map[p]
            dist = manhattan_distance(row, col, goal_row, goal_col)
            if dist < best_dist and p not in state:
                best_dist = dist
                best_pos = p
        return state + [best_pos] if best_pos else None

    def goal_test(self, state):
        return len(state) == len(self.formation)

    def value(self):
        pass


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
        board.remove_all_subgoals()
        goal_set = board.add_white_subgoal if player == WHITE else board.add_black_subgoal
        goal_set(GoalShortDyke(board))

