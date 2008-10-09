from Tkinter import *
from globalconst import *
from checkers import Checkers
from boardview import BoardView
from playercontroller import PlayerController
from alphabetacontroller import AlphaBetaController

class GameManager(object):
    def __init__(self, **props):
        self.model = Checkers()
        self._root = props['root']
        self._parent = props['parent']
        statusbar = Label(self._root, relief=SUNKEN, font=('Helvetica',7),
                          anchor=NW)
        statusbar.pack(side=BOTTOM, fill=X)
        self.view = BoardView(self._root, model=self.model,
                              statusbar=statusbar)
        self.view.pack(side=TOP, expand=0)
        self.player_color = BLACK
        self.num_players = 1
        self.set_controllers()
        self._controller1.start_turn()

    def set_controllers(self):
        think_time = self._parent.thinkTime.get()
        if self.num_players == 0:
            self._controller1 = AlphaBetaController(model=self.model,
                                                    view=self.view,
                                                    searchtime=think_time,
                                                    end_turn_event=self.turn_finished)
            self._controller2 = AlphaBetaController(model=self.model,
                                                    view=self.view,
                                                    searchtime=think_time,
                                                    end_turn_event=self.turn_finished)
        elif self.num_players == 1:
            self._controller1 = PlayerController(model=self.model,
                                                 view=self.view,
                                                 end_turn_event=self.turn_finished)
            self._controller2 = AlphaBetaController(model=self.model,
                                                    view=self.view,
                                                    searchtime=think_time,
                                                    end_turn_event=self.turn_finished)
            if self.player_color == WHITE:
                self._controller1, self._controller2 = self._controller2, self._controller1
        elif self.num_players == 2:
            self._controller1 = PlayerController(model=self.model,
                                                 view=self.view,
                                                 end_turn_event=self.turn_finished)
            self._controller2 = PlayerController(model=self.model,
                                                 view=self.view,
                                                 end_turn_event=self.turn_finished)
        self._controller1.set_before_turn_event(self._controller2.remove_highlights)
        self._controller2.set_before_turn_event(self._controller1.remove_highlights)


    def new_game(self):
        # stop alphabeta threads from making any moves
        self.model.curr_state.ok_to_move = False
        self._controller1.stop_process()
        self._controller2.stop_process()
        self.model = Checkers()
        self.player_color = BLACK
        self.view.reset_view(self.model)
        self.think_time = self._parent.thinkTime.get()
        self.set_controllers()
        self.view.update_statusbar()
        self._controller1.start_turn()

    def turn_finished(self):
        if not self.model.terminal_test():
            if self.model.curr_state.to_move == BLACK:
                self._controller2.end_turn()
                self._root.update()
                self.view.update_statusbar()
                self._controller1.start_turn()
            else:
                self._controller1.end_turn()
                self._root.update()
                self.view.update_statusbar()
                self._controller2.start_turn()
        else:
            self.view.update_statusbar()
            self._controller1.end_turn()
            self._controller2.end_turn()
