from Tkinter import *
from Tkconstants import W, E, N, S
from tkFileDialog import askopenfilename, asksaveasfilename
from tkMessageBox import showerror
from globalconst import *
from checkers import Checkers
from boardview import BoardView
from playercontroller import PlayerController
from alphabetacontroller import AlphaBetaController
from gamepersist import SavedGame
from textserialize import Serializer

class GameManager(object):
    def __init__(self, **props):
        self.model = Checkers()
        self._root = props['root']
        self.parent = props['parent']
        statusbar = Label(self._root, relief=SUNKEN, font=('Helvetica',7),
                          anchor=NW)
        statusbar.pack(side='bottom', fill='x')
        self.view = BoardView(self._root, model=self.model, parent=self,
                              statusbar=statusbar)
        self.player_color = BLACK
        self.num_players = 1
        self.set_controllers()
        self._controller1.start_turn()
        self.filename = None

    def set_controllers(self):
        think_time = self.parent.thinkTime.get()
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


    def _stop_updates(self):
        # stop alphabeta threads from making any moves
        self.model.curr_state.ok_to_move = False
        self._controller1.stop_process()
        self._controller2.stop_process()

    def new_game(self):
        self._stop_updates()
        self.filename = None
        self.model = Checkers()
        self.player_color = BLACK
        self.view.reset_view(self.model)
        self.think_time = self.parent.thinkTime.get()
        self.set_controllers()
        self.view.update_statusbar()
        self._controller1.start_turn()

    def load_game(self, filename):
        self._stop_updates()
        try:
            saved_game = SavedGame()
            saved_game.read(filename)
            self.model.curr_state.clear()
            self.model.curr_state.to_move = saved_game.to_move
            squares = self.model.curr_state.squares
            for i in saved_game.black_men:
                squares[squaremap[i]] = BLACK | MAN
            for i in saved_game.black_kings:
                squares[squaremap[i]] = BLACK | KING
            for i in saved_game.white_men:
                squares[squaremap[i]] = WHITE | MAN
            for i in saved_game.white_kings:
                squares[squaremap[i]] = WHITE | KING
            self.model.curr_state.reset_undo()
            self.model.curr_state.redo_list = saved_game.moves
            self.model.curr_state.update_piece_count()
            self.view.reset_view(self.model)
            self.view.serializer.restore(saved_game.description)
            self.view.flip_board(saved_game.flip_board)
            self.parent.set_title_bar_filename(filename)
        except IOError as (err):
            showerror(PROGRAM_TITLE, 'Invalid file. ' + str(err))

    def open_game(self):
        self._stop_updates()
        f = askopenfilename(filetypes=(('Raven Checkers files','*.rcf'),
                                       ('All files','*.*')),
                            initialdir=TRAINING_DIR)
        if not f:
            return
        self.load_game(f)
        self.filename = f

    def save_game_as(self):
        self._stop_updates()
        filename = asksaveasfilename(filetypes=(('Raven Checkers files','*.rcf'),
                                                ('All files','*.*')),
                                     initialdir=TRAINING_DIR,
                                     defaultextension='.rcf')
        if filename == '':
            return
        self._write_file(filename)

    def save_game(self):
        self._stop_updates()
        filename = self.filename
        if not self.filename:
            filename = asksaveasfilename(filetypes=(('Raven Checkers files','*.rcf'),
                                                    ('All files','*.*')),
                                         initialdir=TRAINING_DIR,
                                         defaultextension='.rcf')
            if filename == '':
                return
        self._write_file(filename)
        self.filename = filename

    def _write_file(self, filename):
        try:
            saved_game = SavedGame()
            saved_game.to_move = self.model.curr_state.to_move
            saved_game.black_men = []
            saved_game.black_kings = []
            saved_game.white_men = []
            saved_game.white_kings = []
            for i, sq in enumerate(self.model.curr_state.squares):
                if sq == BLACK | MAN:
                    saved_game.black_men.append(keymap[i])
                elif sq == BLACK | KING:
                    saved_game.black_kings.append(keymap[i])
                elif sq == WHITE | MAN:
                    saved_game.white_men.append(keymap[i])
                elif sq == WHITE | KING:
                    saved_game.white_kings.append(keymap[i])
            if not self.model.curr_state.undo_list:
                saved_game.description = self.view.serializer.dump()
                saved_game.moves = self.model.curr_state.redo_list
            else:
                showerror(PROGRAM_TITLE, 'Undo list in invalid state.')
                return
            saved_game.flip_board = self.view.flip_view
            saved_game.write(filename)
            self.parent.set_title_bar_filename(filename)
            self.filename = filename
        except IOError:
            showerror(PROGRAM_TITLE, 'Could not save file.')

    def turn_finished(self):
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
