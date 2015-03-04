__author__ = 'brandon_corfman'
import time
import copy
import games
import multiprocessing
from goal import Goal
from globalconst import *


class GoalCrossboard(Goal):
    def __init__(self, owner):
        Goal.__init__(self, owner)
        self.process = None
        self._child_conn = multiprocessing.Pipe()
        self._term_event = multiprocessing.Event()
        self.process = multiprocessing.Process()
        self._start_time = None

    def activate(self):
        self.status = self.ACTIVE
        self.process = multiprocessing.Process(target=calc_move,
                                               args=(self.owner.model, self.owner.search_time, self._term_event,
                                                     self._child_conn))
        self._start_time = time.time()
        self.process.daemon = True
        self.process.start()
        self.owner.view.canvas.after(100, self.owner.get_move)

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
        move = longest_of(captures)
    else:
        depth = 0
        start_time = time.time()
        curr_time = start_time
        model_copy = copy.deepcopy(model)
        while 1:
            depth += 1
            move = games.alphabeta_search(model_copy.curr_state,
                                          model_copy,
                                          depth)
            checkpoint = curr_time
            curr_time = time.time()
            rem_time = search_time - (curr_time - checkpoint)
            if term_event.is_set():  # a signal means terminate
                term_event.clear()
                move = None
                break
            if curr_time - start_time > search_time or (curr_time - checkpoint) * 2 > rem_time or depth > MAXDEPTH:
                break
    child_conn.send(move)


def longest_of(moves):
    length = -1
    selected = None
    for move in moves:
        l = len(move.affected_squares)
        if l > length:
            length = l
            selected = move
    return selected

