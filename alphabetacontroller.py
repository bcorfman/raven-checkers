import multiprocessing
import time
from controller import Controller
from goalthink import GoalThink
from globalconst import *


class AlphaBetaController(Controller):
    def __init__(self, **props):
        self.model = props['model']
        self.view = props['view']
        self.search_time = props['searchtime']  # in seconds
        self._before_turn_event = None
        self._end_turn_event = props['end_turn_event']
        self._highlights = []
        self._parent_conn, self.child_conn = multiprocessing.Pipe()
        self._term_event = multiprocessing.Event()
        self.process = multiprocessing.Process()
        self._start_time = None
        self._call_id = 0
        self._thinker = GoalThink(self)

    def add_highlights(self):
        for h in self._highlights:
            self.view.highlight_square(h, OUTLINE_COLOR)

    def remove_highlights(self):
        for h in self._highlights:
            self.view.highlight_square(h, DARK_SQUARES)

    def start_turn(self):
        if self.model.terminal_test():
            self._before_turn_event()
            self.model.curr_state.attach(self.view)
            return
        self.view.update_statusbar('Thinking ...')
        if not self._thinker.is_active():
            self._thinker.activate()
        self._thinker.process()
        self.view.canvas.after(100, self.get_move)

    def get_move(self):
        self._highlights = []
        moved = self._parent_conn.poll()
        if not moved and (time.time() - self._start_time) < self.search_time * 2:
            # continue calling get_move until we have a move
            self._call_id = self.view.canvas.after(500, self.get_move)
            return
        self.view.canvas.after_cancel(self._call_id)  # cancel pending get_move call
        move = self._parent_conn.recv()
        self._before_turn_event()

        # highlight remaining board squares used in move
        step = 2 if len(move.affected_squares) > 2 else 1
        for m in move.affected_squares[0::step]:
            idx = m[0]
            self.view.highlight_square(idx, OUTLINE_COLOR)
            self._highlights.append(idx)

        self.model.curr_state.attach(self.view)
        self.model.make_move(move, None, True, True, self.view.get_annotation())
        # a new move obliterates any more redo's along a branch of the game tree
        self.model.curr_state.delete_redo_list()
        self._end_turn_event()

    def set_before_turn_event(self, evt):
        self._before_turn_event = evt

    def stop_process(self):
        self._term_event.set()
        self.view.canvas.after_cancel(self._call_id)

    def end_turn(self):
        self.view.update_statusbar()
        self.model.curr_state.detach(self.view)


