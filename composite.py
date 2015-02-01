from goal import Goal

class CompositeGoal(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)
        self.subgoals = []

    def removeAllSubgoals(self):
        for s in self.subgoals:
            s.terminate()
        self.subgoals = []

    def processSubgoals(self):
        # remove all completed and failed goals from the front of the
        # subgoal list
        while (self.subgoals and (self.subgoals[0].isComplete or
                                  self.subgoals[0].hasFailed)):
            subgoal = self.subgoals.pop()
            subgoal.terminate()

        if self.subgoals:
            subgoal = self.subgoals.pop()
            status = subgoal.process()
            if status == self.COMPLETED and len(self.subgoals) > 1:
                return self.ACTIVE
            return status
        else:
            return self.COMPLETED


    def addSubgoal(self, goal):
        self.subgoals.append(goal)
