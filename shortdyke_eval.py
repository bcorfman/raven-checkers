__author__ = 'brandon_corfman'
from goalevaluator import GoalEvaluator
from formation import BLACK_MAP, WHITE_MAP, BLACK, MAN
from globalconst import WHITE, BLACK_IDX, WHITE_IDX
from shortdyke import GoalShortDyke
from search import Problem, best_first_graph_search

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


class FormationProblem(Problem):
    def __init__(self, goal, board):
        self.board = board
        self.initial = ()
        self.goal = goal

    def actions(self, state):
        player = self.board.to_move
        pos_map = BLACK_MAP if player == BLACK else WHITE_MAP
        next_var = self.goal[len(state)]
        actions = [pos for pos in pos_map[next_var] if self.board.squares[pos] == player + MAN]
        for a in actions:
            if a not in state:
                yield a

    def result(self, state, action):
        return state + (action, )

    def goal_test(self, state):
        return len(state) == len(self.goal)

    def path_cost(self, c, state1, action, state2):
        if not state2:
            return 0
        player = self.board.to_move
        index_list = BLACK_IDX if player == BLACK else WHITE_IDX
        start_sq = state2[-1]
        goal_sq = self.goal[len(state2) - 1]
        frontier = [(start_sq, c)]
        while frontier:
            curr_sq, cost = frontier.pop()
            if curr_sq == goal_sq:
                return cost
            for i in index_list:
                if curr_sq + i <= goal_sq:
                    frontier.append((curr_sq + i, cost + 1))
        return 99999


def measure_formation_closeness(formation, board):
    problem = FormationProblem(formation, board)

    def f(current_node):
        return sum(abs(s - formation[i]) for i, s in enumerate(current_node.state))

    node = best_first_graph_search(problem, f)
    return node.path_cost if node.solution() else 0.0


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
