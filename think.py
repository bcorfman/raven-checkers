from composite import CompositeGoal
from onek_onek import OneKingAttackOneKingEvaluator, OneKingFleeOneKingEvaluator


class GoalThink(CompositeGoal):
    def __init__(self, owner):
        CompositeGoal.__init__(self, owner)
        self.evaluators = [OneKingAttackOneKingEvaluator(1.0),
                           OneKingFleeOneKingEvaluator(1.0)]

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
        most_desirable = None
        best_score = 0
        for e in self.evaluators:
            d = e.calculate_desirability()
            if d > best_score:
                most_desirable = e
                best_score = d
        if most_desirable:
            most_desirable.set_goal(self.owner)

    

    