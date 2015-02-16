__author__ = 'brandon_corfman'
from goal import Goal


class GoalLongDyke(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        # if status is inactive, activate
        self.activate_if_inactive()

    def terminate(self):
        self.status = self.INACTIVE
