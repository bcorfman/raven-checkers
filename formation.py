__author__ = 'brandon_corfman'
from search import Problem, best_first_graph_search
from globalconst import BLACK_IDX, WHITE_IDX, BLACK, MAN


# other squares reachable from a particular square with a black man
BLACK_MAP = {45: {45,39,40,34,35,28,29,30,23,24,25,17,18,19,20,12,13,14,15,6,7,8,9},
             46: {46,40,41,34,35,36,28,29,30,31,23,24,25,26,17,18,19,20,12,13,14,15,6,7,8,9},
             47: {47,41,42,35,36,37,29,30,31,23,24,25,26,17,18,19,20,12,13,14,15,6,7,8,9},
             48: {48,42,36,37,30,31,24,25,26,18,19,20,12,13,14,15,6,7,8,9},
             39: {39,34,28,29,23,24,17,18,19,12,13,14,6,7,8,9},
             40: {40,34,35,28,29,30,23,24,25,17,18,19,20,12,13,14,15,6,7,8,9},
             41: {41,35,36,29,30,31,23,24,25,26,17,18,19,20,12,13,14,15,6,7,8,9},
             42: {42,36,37,30,31,24,25,26,18,19,20,12,13,14,15,6,7,8,9},
             34: {34,28,29,23,24,17,18,19,12,13,14,6,7,8,9},
             35: {35,29,30,23,24,25,17,18,19,20,12,13,14,15,6,7,8,9},
             36: {36,30,31,24,25,26,18,19,20,12,13,14,15,6,7,8,9},
             37: {37,31,25,26,19,20,13,14,15,7,8,9},
             28: {28,23,17,18,12,13,6,7,8},
             29: {29,23,24,17,18,19,12,13,14,6,7,8,9},
             30: {30,24,25,18,19,20,12,13,14,15,6,7,8,9},
             31: {31,25,26,19,20,13,14,15,7,8,9},
             23: {23,17,18,12,13,6,7,8},
             24: {24,18,19,12,13,14,6,7,8,9},
             25: {25,19,20,13,14,15,7,8,9},
             26: {26,20,14,15,8,9},
             17: {17,12,6,7},
             18: {18,12,13,6,7,8},
             19: {19,13,14,7,8,9},
             20: {20,14,15,8,9},
             12: {12,6,7},
             13: {13,7,8},
             14: {14,8,9},
             15: {15,9},
             6: {6},
             7: {7},
             8: {8},
             9: {9} }

# other squares reachable from a particular square with a white man
WHITE_MAP = {6: {6,12,17,18,23,24,28,29,30,34,35,36,39,40,41,42,45,46,47,48},
             7: {7,12,13,17,18,19,23,24,25,28,29,30,31,34,35,36,37,39,40,41,42,45,46,47,48},
             8: {8,13,14,18,19,20,23,24,25,26,28,29,30,31,34,35,36,37,39,40,41,42,45,46,47,48},
             9: {9,14,15,19,20,24,25,26,29,30,31,34,35,36,37,39,40,41,42,45,46,47,48},
             12: {12,17,18,23,24,28,29,30,34,35,36,39,40,41,42,45,46,47,48},
             13: {13,18,19,23,24,25,28,29,30,31,34,35,36,37,39,40,41,42,45,46,47,48},
             14: {14,19,20,24,25,26,29,30,31,34,35,36,37,39,40,41,42,45,46,47,48},
             15: {15,20,25,26,30,31,35,36,37,40,41,42,45,46,47,48},
             17: {17,23,28,29,34,35,39,40,41,45,46,47},
             18: {18,23,24,28,29,30,34,35,36,39,40,41,42,45,46,47,48},
             19: {19,24,25,29,30,31,34,35,36,37,39,40,41,42,45,46,47,48},
             20: {20,25,26,30,31,35,36,37,40,41,42,45,46,47,48},
             23: {23,28,29,34,35,39,40,41,45,46,47},
             24: {24,29,30,34,35,36,39,40,41,42,45,46,47,48},
             25: {25,30,31,35,36,37,40,41,42,45,46,47,48},
             26: {26,31,36,37,41,42,46,47,48},
             28: {28,34,39,40,45,46},
             29: {29,34,35,39,40,41,45,46,47},
             30: {30,35,36,40,41,42,45,46,47,48},
             31: {31,36,37,41,42,46,47,48},
             34: {34,39,40,45,46},
             35: {35,40,41,45,46,47},
             36: {36,41,42,46,47,48},
             37: {37,42,47,48},
             39: {39,45},
             40: {40,45,46},
             41: {41,46,47},
             42: {42,47,48},
             45: {45},
             46: {46},
             47: {47},
             48: {48}}


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