from abc import ABCMeta, abstractmethod


class Goal(object):
    __metaclass__ = ABCMeta

    INACTIVE = 0
    ACTIVE = 1
    COMPLETED = 2
    FAILED = 3

    def __init__(self, owner):
        self.owner = owner
        self.status = self.INACTIVE

    def handle_message(self, msg):
        return False

    def add_subgoal(self, goal):
        raise NotImplementedError('Cannot add goals to atomic goals')

    def reactivate_if_failed(self):
        if self.status == self.FAILED:
            self.status = self.INACTIVE

    def activate_if_inactive(self):
        if self.status == self.INACTIVE:
            self.status = self.ACTIVE

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def terminate(self):
        pass

