__author__ = 'brandon_corfman'
from goalevaluator import GoalEvaluator
from formation import measure_formation_closeness
from globalconst import BLACK
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


class ShortDykeEvaluator(GoalEvaluator):
    def __init__(self, thinker):
        GoalEvaluator.__init__(self)
        self.thinker = thinker

    def calculate_desirability(self):
        player = self.thinker.get_model().to_move
        short_dyke = [8, 9, 14, 17, 23, 29] if player == BLACK else [14, 17, 21, 27, 31, 32]
        return 1.0 if measure_formation_closeness(short_dyke, self.thinker.get_model()) else 0.0

    def set_goal(self):
        self.thinker.remove_all_subgoals()
        self.thinker.add_subgoal(GoalShortDyke(self.thinker))


class LongDykeEvaluator(GoalEvaluator):
    def __init__(self, thinker):
        GoalEvaluator.__init__(self)
        self.thinker = thinker

    def calculate_desirability(self):
        player = self.thinker.get_model().to_move
        long_dyke = [8, 9, 14, 19, 24, 29] if player == BLACK else [14, 18, 23, 27, 31, 32]
        return 1.0 if measure_formation_closeness(long_dyke, self.thinker.get_model()) else 0.0

    def set_goal(self):
        self.thinker.remove_all_subgoals()
        self.thinker.add_subgoal(GoalLongDyke(self.thinker))


class PyramidEvaluator(GoalEvaluator):
    def __init__(self, thinker):
        GoalEvaluator.__init__(self)
        self.thinker = thinker

    def calculate_desirability(self):
        player = self.thinker.get_model().to_move
        pyramid = [1, 2, 3, 6, 7, 10] if player == BLACK else [23, 26, 27, 30, 31, 32]
        return 1.0 if measure_formation_closeness(pyramid, self.thinker.get_model()) else 0.0

    def set_goal(self):
        self.thinker.remove_all_subgoals()
        self.thinker.add_subgoal(GoalPyramid(self.thinker))


class PhalanxEvaluator(GoalEvaluator):
    def __init__(self, thinker):
        GoalEvaluator.__init__(self)
        self.thinker = thinker

    def calculate_desirability(self):
        player = self.thinker.get_model().to_move
        phalanx = [5, 6, 7, 8, 9, 10, 11, 14, 15] if player == BLACK else [18, 19, 22, 23, 24, 25, 26, 27, 28]
        return 1.0 if measure_formation_closeness(phalanx, self.thinker.get_model()) else 0.0

    def set_goal(self):
        self.thinker.remove_all_subgoals()
        self.thinker.add_subgoal(GoalPhalanx(self.thinker))


class MillEvaluator(GoalEvaluator):
    def __init__(self, thinker):
        GoalEvaluator.__init__(self)
        self.thinker = thinker

    def calculate_desirability(self):
        player = self.thinker.get_model().to_move
        mill = [1, 3, 5, 8, 9, 11, 14, 15, 18] if player == BLACK else [15, 18, 19, 22, 24, 25, 28, 30, 32]
        return 1.0 if measure_formation_closeness(mill, self.thinker.get_model()) else 0.0

    def set_goal(self):
        self.thinker.remove_all_subgoals()
        self.thinker.add_subgoal(GoalMill(self.thinker))


class EchelonEvaluator(GoalEvaluator):
    def __init__(self, thinker):
        GoalEvaluator.__init__(self)
        self.thinker = thinker

    def calculate_desirability(self):
        player = self.thinker.get_model().to_move
        echelon = [2, 3, 5, 6, 7, 9, 10, 14] if player == BLACK else [19, 23, 24, 26, 27, 28, 30, 31]
        return 1.0 if measure_formation_closeness(echelon, self.thinker.get_model()) else 0.0

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
