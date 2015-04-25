from abc import ABCMeta, abstractmethod
from globalconst import FAILED, INACTIVE, ACTIVE, COMPLETED


class Goal:
    __metaclass__ = ABCMeta

    def __init__(self, owner):
        self.owner = owner
        self.status = INACTIVE

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def process(self):
        pass

    @abstractmethod
    def terminate(self):
        pass

    def handle_message(self, msg):
        return False

    def reactivate_if_failed(self):
        if self.status == FAILED:
            self.status = INACTIVE

    def activate_if_inactive(self):
        if self.status == INACTIVE:
            self.status = ACTIVE

    def is_complete(self):
        return self.status == COMPLETED

    def has_failed(self):
        return self.status == FAILED

    def is_active(self):
        return self.status == ACTIVE


