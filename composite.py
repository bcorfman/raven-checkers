from goal import Goal


class CompositeGoal(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)
        self.subgoals = []

    def remove_all_subgoals(self):
        for s in self.subgoals:
            s.terminate()
        self.subgoals = []

    def process_subgoals(self):
        # remove all completed and failed goals from the front of the
        # subgoal list
        while (self.subgoals and (self.subgoals[0].isComplete or
                                  self.subgoals[0].hasFailed)):
            subgoal = self.subgoals.pop()
            subgoal.terminate()

        if self.subgoals:
            subgoal = self.subgoals.pop()
            status = subgoal.process()
            if status == Goal.COMPLETED and len(self.subgoals) > 1:
                return Goal.ACTIVE
            return status
        else:
            return Goal.COMPLETED

    def add_subgoal(self, goal):
        self.subgoals.append(goal)

    def activate(self):
        pass

    def process(self):
        pass

    def terminate(self):
        pass
