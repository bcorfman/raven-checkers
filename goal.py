from abc import ABCMeta, abstractmethod

class Goal:
    __metaclass__ = ABCMeta

    INACTIVE = 0
    ACTIVE = 1
    COMPLETED = 2
    FAILED = 3

    def __init__(self, owner):
        self.owner = owner
        self.status = self.INACTIVE

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def terminate(self):
        pass

    def handleMessage(self, msg):
        return False

    def addSubgoal(self, goal):
        raise NotImplementedError('Cannot add goals to atomic goals')

    def reactivateIfFailed(self):
        if self.status == self.FAILED:
            self.status = self.INACTIVE

    def activateIfInactive(self):
        if self.status == self.INACTIVE:
            self.status = self.ACTIVE
