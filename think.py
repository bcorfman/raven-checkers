from composite import CompositeGoal
from evaluators import ShortDykeEvaluator, LongDykeEvaluator, PhalanxEvaluator
from evaluators import PyramidEvaluator, EchelonEvaluator, MillEvaluator
from utils import argmax_random_tie


class GoalThink(CompositeGoal):
    def __init__(self, owner):
        CompositeGoal.__init__(self, owner)
        self.evaluators = [ShortDykeEvaluator(self), LongDykeEvaluator(self),
                           PhalanxEvaluator(self), PyramidEvaluator(self),
                           EchelonEvaluator(self), MillEvaluator(self)]

    def activate(self):
        self.arbitrate()
        self.status = self.ACTIVE

    def process(self):
        self.activate_if_inactive()
        status = self.process_subgoals()
        if status == self.COMPLETED or status == self.FAILED:
            self.status = self.INACTIVE
        return status

    def terminate(self):
        pass

    def arbitrate(self):
        most_desirable = argmax_random_tie(self.evaluators, lambda e: e.calculate_desirability())
        most_desirable.set_goal()

    def get_model(self):
        return self.owner.get_model()