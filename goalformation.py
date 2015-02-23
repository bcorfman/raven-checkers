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


class GoalShortDyke(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        # if status is inactive, activate
        self.activate_if_inactive()

    def terminate(self):
        self.status = self.INACTIVE


class GoalPyramid(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        # if status is inactive, activate
        self.activate_if_inactive()

    def terminate(self):
        self.status = self.INACTIVE


class GoalPhalanx(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        # if status is inactive, activate
        self.activate_if_inactive()

    def terminate(self):
        self.status = self.INACTIVE


class GoalMill(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        # if status is inactive, activate
        self.activate_if_inactive()

    def terminate(self):
        self.status = self.INACTIVE


class GoalEchelon(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        # if status is inactive, activate
        self.activate_if_inactive()

    def terminate(self):
        self.status = self.INACTIVE
