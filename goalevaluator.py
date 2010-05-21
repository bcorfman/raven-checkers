from abc import ABCMeta, abstractmethod


class GoalEvaluator(object):
    __metaclass__ = ABCMeta

    def __init__(self, bias):
        self.bias = bias

    @abstractmethod
    def calculateDesirability(self, board):
        pass

    @abstractmethod
    def setGoal(self, board):
        pass
    

