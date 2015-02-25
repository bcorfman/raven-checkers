from composite import CompositeGoal
from evaluators import ShortDykeEvaluator, LongDykeEvaluator, PhalanxEvaluator
from evaluators import PyramidEvaluator, EchelonEvaluator, MillEvaluator
from utils import argmax_random_tie


class GoalThink(CompositeGoal):
    def __init__(self, owner):
        CompositeGoal.__init__(self, owner)
        self.owner = owner
        self.evaluators = [ShortDykeEvaluator(1.0), LongDykeEvaluator(1.0), PhalanxEvaluator(1.0),
                           PyramidEvaluator(1.0), EchelonEvaluator(1.0), MillEvaluator(1.0)]

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
        most_desirable = argmax_random_tie(self.evaluators, lambda e: e.calculate_desirability(self.owner))
        most_desirable.set_goal(self.owner)
    