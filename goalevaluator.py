from abc import ABCMeta, abstractmethod


class GoalEvaluator(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_desirability(self):
        pass

    @abstractmethod
    def set_goal(self):
        pass
    

