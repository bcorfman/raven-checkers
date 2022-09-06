import util


class Observer(object):
    def update(self, change):
        util.abstract()
