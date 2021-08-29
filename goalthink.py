from goal import Goal
from composite import CompositeGoal
from utils import argmax_random_tie


class GoalThink(CompositeGoal):
    def __init__(self, controller):
        CompositeGoal.__init__(self, controller)
        self.controller = controller
        self.most_desirable = None
        self.evaluators = []  # [ShortDykeEvaluator(self), LongDykeEvaluator(self), PhalanxEvaluator(self),
        # PyramidEvaluator(self), EchelonEvaluator(self), MillEvaluator(self), CrossboardEvaluator(self)]

    def activate(self):
        self.arbitrate()
        self.status = Goal.ACTIVE

    def process(self):
        self.activate_if_inactive()
        if self.most_desirable:
            desirability = self.most_desirable.calculate_desirability()
            print desirability
            if desirability > 0.0:
                status = self.process_subgoals()
            else:
                status = Goal.FAILED
        else:
            status = Goal.FAILED
        if status == Goal.COMPLETED or status == Goal.FAILED:
            self.most_desirable = None
            self.status = Goal.INACTIVE
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
