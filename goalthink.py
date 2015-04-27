from globalconst import ACTIVE, COMPLETED, FAILED, INACTIVE
from composite import CompositeGoal
from evaluators import ShortDykeEvaluator, LongDykeEvaluator, PhalanxEvaluator
from evaluators import PyramidEvaluator, EchelonEvaluator, MillEvaluator, CrossboardEvaluator
from utils import argmax_random_tie


class GoalThink(CompositeGoal):
    def __init__(self, controller):
        CompositeGoal.__init__(self, controller)
        self.controller = controller
        self.most_desirable = None
        self.evaluators = [ShortDykeEvaluator(self), LongDykeEvaluator(self), PhalanxEvaluator(self),
                           PyramidEvaluator(self), EchelonEvaluator(self), MillEvaluator(self),
                           CrossboardEvaluator(self)]

    def activate(self):
        self.arbitrate()
        self.status = ACTIVE

    def process(self):
        self.activate_if_inactive()
        if self.most_desirable:
            desirability = self.most_desirable.calculate_desirability()
            print desirability
            if desirability > 0.0:
                status = self.process_subgoals()
            else:
                status = FAILED
        else:
            status = FAILED
        if status == COMPLETED or status == FAILED:
            self.most_desirable = None
            self.status = INACTIVE
        return status

    def terminate(self):
        pass

    def arbitrate(self):
        self.most_desirable = argmax_random_tie(self.evaluators, lambda e: e.calculate_desirability())
        self.most_desirable.set_goal()

    def _get_board(self):
        return self.controller.model.curr_state

    board = property(_get_board)

    def _get_game(self):
        return self.controller.model

    game = property(_get_game)
