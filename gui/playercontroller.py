from tkinter import Widget
from base.controller import Controller
from util.globalconst import HUMAN, OUTLINE_COLOR, DARK_SQUARES, FREE


class PlayerController(Controller):
    def __init__(self, **props):
        self._model = props['model']
        self._view = props['view']
        self._before_turn_event = None
        self._end_turn_event = props['end_turn_event']
        self._highlights = []
        self._move_in_progress = False
        self.idx = None
        self.moves = []

    def _register_event_handlers(self):
        Widget.bind(self._view.canvas, '<Button-1>', self.mouse_click)

    def _unregister_event_handlers(self):
        Widget.unbind(self._view.canvas, '<Button-1>')

    def stop_process(self):
        pass

    def set_search_time(self, time):
        pass

    def get_player_type(self):
        return HUMAN

    def set_before_turn_event(self, evt):
        self._before_turn_event = evt

    def add_highlights(self):
        for h in self._highlights:
            self._view.highlight_square(h, OUTLINE_COLOR)

    def remove_highlights(self):
        for h in self._highlights:
            self._view.highlight_square(h, DARK_SQUARES)

    def start_turn(self):
        self._register_event_handlers()
        self._model.curr_state.attach(self._view)

    def end_turn(self):
        self._unregister_event_handlers()
        self._model.curr_state.detach(self._view)

    def mouse_click(self, event):
        xi, yi = self._view.calc_board_loc(event.x, event.y)
        pos = self._view.calc_board_pos(xi, yi)
        sq = self._model.curr_state.squares[pos]
        if not self._move_in_progress:
            player = self._model.curr_state.to_move
            self.moves = self._model.legal_moves()
            if (sq & player) and self.moves:
                self._before_turn_event()
                # highlight the start square the user clicked on
                self._view.highlight_square(pos, OUTLINE_COLOR)
                self._highlights = [pos]
                # reduce moves to number matching the positions entered
                self.moves = self._filter_moves(pos, self.moves, 0)
                self.idx = 2 if self._model.captures_available() else 1
                # if only one move available, take it.
                if len(self.moves) == 1:
                    self._make_move()
                    self._view.canvas.after(100, self._end_turn_event)
                    return
                self._move_in_progress = True
        else:
            if sq & FREE:
                self.moves = self._filter_moves(pos, self.moves, self.idx)
                if len(self.moves) == 0:  # illegal move
                    # remove previous square highlights
                    for h in self._highlights:
                        self._view.highlight_square(h, DARK_SQUARES)
                    self._move_in_progress = False
                    return
                else:
                    self._view.highlight_square(pos, OUTLINE_COLOR)
                    self._highlights.append(pos)
                    if len(self.moves) == 1:
                        self._make_move()
                        self._view.canvas.after(100, self._end_turn_event)
                        return
                    self.idx += 2 if self._model.captures_available() else 1

    def _filter_moves(self, pos, moves, idx):
        del_list = []
        for i, m in enumerate(moves):
            if pos != m.affected_squares[idx][0]:
                del_list.append(i)
        for i in reversed(del_list):
            del moves[i]
        return moves

    def _make_move(self):
        move = self.moves[0].affected_squares
        step = 2 if len(move) > 2 else 1
        # highlight remaining board squares used in move
        for m in move[step::step]:
            idx = m[0]
            self._view.highlight_square(idx, OUTLINE_COLOR)
            self._highlights.append(idx)
        self._model.make_move(self.moves[0], None, True, True,
                              self._view.get_annotation())
        # a new move obliterates any more redo's along a branch of the game tree
        self._model.curr_state.delete_redo_list()
        self._move_in_progress = False
