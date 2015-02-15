from abc import ABCMeta, abstractmethod


class GoalEvaluator(object):
    __metaclass__ = ABCMeta

    def __init__(self, bias):
        self.bias = bias

    @abstractmethod
    def calculate_desirability(self, board):
        pass

    @abstractmethod
    def set_goal(self, board):
        pass
    

