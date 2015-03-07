__author__ = 'brandon_corfman'
from csp import CSP, different_values_constraint, backtracking_search
from globalconst import BLACK, MAN
from goalevaluator import GoalEvaluator
from formation import BLACK_MAP, WHITE_MAP
from goalformation import GoalShortDyke, GoalLongDyke, GoalPhalanx, GoalPyramid, GoalMill, GoalEchelon
from goalcrossboard import GoalCrossboard


def formation_csp(variables, board):
    """Return an instance of the CSP to see if the formation can be obtained."""
    domains = {}
    player = board.to_move
    pos_map = BLACK_MAP if player == BLACK else WHITE_MAP
    neighbors = {}
    for var in variables:
        domains[var] = [pos for pos in pos_map[var] if board.squares[pos] == player + MAN]
        neighbors[var] = set(variables) - {var}
    return CSP(variables, domains, neighbors, different_values_constraint)


class ShortDykeEvaluator(GoalEvaluator):
    def __init__(self, thinker):
        GoalEvaluator.__init__(self)
        self.thinker = thinker

    def calculate_desirability(self):
        short_dyke_csp = formation_csp(self.thinker.board.short_dyke, self.thinker.board)
        return 1.0 if backtracking_search(short_dyke_csp, mcv=True, lcv=True) else 0.0

    def set_goal(self):
        self.thinker.remove_all_subgoals()
        self.thinker.add_subgoal(GoalShortDyke(self.thinker))


class LongDykeEvaluator(GoalEvaluator):
    def __init__(self, thinker):
        GoalEvaluator.__init__(self)
        self.thinker = thinker

    def calculate_desirability(self):
        long_dyke_csp = formation_csp(self.thinker.board.short_dyke, self.thinker.board)
        return 1.0 if backtracking_search(long_dyke_csp, mcv=True, lcv=True) else 0.0

    def set_goal(self):
        self.thinker.remove_all_subgoals()
        self.thinker.add_subgoal(GoalLongDyke(self.thinker))


class PyramidEvaluator(GoalEvaluator):
    def __init__(self, thinker):
        GoalEvaluator.__init__(self)
        self.thinker = thinker

    def calculate_desirability(self):
        pyramid_csp = formation_csp(self.thinker.board.pyramid, self.thinker.board)
        return 1.0 if backtracking_search(pyramid_csp, mcv=True, lcv=True) else 0.0

    def set_goal(self):
        self.thinker.remove_all_subgoals()
        self.thinker.add_subgoal(GoalPyramid(self.thinker))


class PhalanxEvaluator(GoalEvaluator):
    def __init__(self, thinker):
        GoalEvaluator.__init__(self)
        self.thinker = thinker

    def calculate_desirability(self):
        phalanx_csp = formation_csp(self.thinker.board.phalanx, self.thinker.board)
        return 1.0 if backtracking_search(phalanx_csp, mcv=True, lcv=True) else 0.0

    def set_goal(self):
        self.thinker.remove_all_subgoals()
        self.thinker.add_subgoal(GoalPhalanx(self.thinker))


class MillEvaluator(GoalEvaluator):
    def __init__(self, thinker):
        GoalEvaluator.__init__(self)
        self.thinker = thinker

    def calculate_desirability(self):
        mill_csp = formation_csp(self.thinker.board.mill, self.thinker.board)
        return 1.0 if backtracking_search(mill_csp, mcv=True, lcv=True) else 0.0

    def set_goal(self):
        self.thinker.remove_all_subgoals()
        self.thinker.add_subgoal(GoalMill(self.thinker))


class EchelonEvaluator(GoalEvaluator):
    def __init__(self, thinker):
        GoalEvaluator.__init__(self)
        self.thinker = thinker

    def calculate_desirability(self):
        echelon_csp = formation_csp(self.thinker.board.echelon, self.thinker.board)
        return 1.0 if backtracking_search(echelon_csp, mcv=True, lcv=True) else 0.0

    def set_goal(self):
        self.thinker.remove_all_subgoals()
        self.thinker.add_subgoal(GoalEchelon(self.thinker))


class CrossboardEvaluator(GoalEvaluator):
    def __init__(self, thinker):
        GoalEvaluator.__init__(self)
        self.thinker = thinker

    def calculate_desirability(self):
        """ Make crossboard play slightly less desirable than other strategies.
        That way, it will only get used if nothing else is applicable. """
        return 0.9

    def set_goal(self):
        self.thinker.remove_all_subgoals()
        self.thinker.add_subgoal(GoalCrossboard(self.thinker))
