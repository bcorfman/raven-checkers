__author__ = 'brandon_corfman'
import time
import multiprocessing
import copy
from goal import Goal


class GoalCrossboard(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)
        self.process = multiprocessing.Process()
        self._child_conn = multiprocessing.Pipe()
        self._term_event = multiprocessing.Event()
        self._start_time = None

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        self.activate_if_inactive()

    def terminate(self):
        self.status = self.INACTIVE


def calc_move(model, search_time, term_event, child_conn):
    move = None
    term_event.clear()
    captures = model.captures_available()
    if captures:
        time.sleep(0.7)
        move = None  # longest_of(captures)
    else:
        depth = 0
        model_copy = copy.deepcopy(model)
        while 1:
            depth += 1
            move = None  # games.alphabeta_search(model_copy.curr_state,
                   #                              model_copy,
                   #                              depth)
            if term_event.is_set():  # a signal means terminate
                term_event.clear()
                move = None
                break
    child_conn.send(move)


class GoalShortDyke(Goal):
    def __init__(self, thinker):
        Goal.__init__(self, thinker)
        self._thinker = thinker
        #self.process = multiprocessing.Process(target=calc_move,
        #                                       args=(self._thinker.model, self.owner.search_time, self._term_event,
        #                                             self._child_conn))
        #self._start_time = time.time()
        #self.process.daemon = True
        #self.process.start()
        #self.owner.view.canvas.after(100, self.owner.get_move)

    def __repr__(self):
        return "GoalShortDyke"

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        self.activate_if_inactive()
        self.make_best_move(self._thinker.board.short_dyke)

    def terminate(self):
        self.status = self.INACTIVE


class GoalLongDyke(Goal):
    def __init__(self, thinker):
        Goal.__init__(self, thinker)
        self._thinker = thinker

    def __repr__(self):
        return "GoalLongDyke"

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        self.activate_if_inactive()
        self.make_best_move(self._thinker.board.long_dyke)

    def terminate(self):
        self.status = self.INACTIVE


class GoalPyramid(Goal):
    def __init__(self, thinker):
        Goal.__init__(self, thinker)
        self._thinker = thinker

    def __repr__(self):
        return "GoalPyramid"

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        self.activate_if_inactive()
        self.make_best_move(self._thinker.board.pyramid)

    def terminate(self):
        self.status = self.INACTIVE


class GoalPhalanx(Goal):
    def __init__(self, thinker):
        Goal.__init__(self, thinker)
        self._thinker = thinker

    def __repr__(self):
        return "GoalPhalanx"

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        self.activate_if_inactive()
        self.make_best_move(self._thinker.board.phalanx)

    def terminate(self):
        self.status = self.INACTIVE


class GoalMill(Goal):
    def __init__(self, thinker):
        Goal.__init__(self, thinker)
        self._thinker = thinker

    def __repr__(self):
        return "GoalMill"

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        self.activate_if_inactive()
        self.make_best_move(self._thinker.board.mill)

    def terminate(self):
        self.status = self.INACTIVE


class GoalEchelon(Goal):
    def __init__(self, thinker):
        Goal.__init__(self, thinker)
        self._thinker = thinker

    def __repr__(self):
        return "GoalEchelon"

    def activate(self):
        self.status = self.ACTIVE

    def process(self):
        self.activate_if_inactive()
        self.make_best_move(self._thinker.board.echelon)

    def terminate(self):
        self.status = self.INACTIVE
