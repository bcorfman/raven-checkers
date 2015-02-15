from goal import Goal
from collections import deque
from abc import ABCMeta, abstractmethod


class CompositeGoal(Goal):
    __metaclass__ = ABCMeta

    def __init__(self, owner):
        Goal.__init__(self, owner)
        self.subgoals = deque()

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def terminate(self):
        pass

    def remove_all_subgoals(self):
        for s in self.subgoals:
            s.terminate()
        self.subgoals.clear()

    def process_subgoals(self):
        # remove all completed and failed goals from the front of the
        # subgoal list
        while (self.subgoals and (self.subgoals[0].isComplete or
                                  self.subgoals[0].hasFailed)):
            subgoal = self.subgoals.popleft()
            subgoal.terminate()

        if self.subgoals:
            subgoal = self.subgoals.pop()
            status = subgoal.process()
            if status == self.COMPLETED and len(self.subgoals) > 1:
                return self.ACTIVE
            return status
        else:
            return self.COMPLETED

    def add_subgoal(self, goal):
        self.subgoals.appendleft(goal)

    def handle_message(self, msg):
        return self.forward_message_to_frontmost_subgoal(msg)

    def forward_message_to_frontmost_subgoal(self, msg):
        if self.subgoals:
            return self.subgoals.popleft().handle_message(msg)
        return False
