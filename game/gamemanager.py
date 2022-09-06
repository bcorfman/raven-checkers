from tkinter import Label, SUNKEN, NW
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesnocancel, showerror
from util.globalconst import BLACK, WHITE, TITLE, VERSION, KING, MAN, PROGRAM_TITLE, TRAINING_DIR
from util.globalconst import square_map, keymap
from game.checkers import Checkers
from gui.boardview import BoardView
from gui.playercontroller import PlayerController
from gui.alphabetacontroller import AlphaBetaController
from parsing.gamepersist import SavedGame


class GameManager(object):
    def __init__(self, **props):
        self.model = Checkers()
        self._root = props['root']
        self.parent = props['parent']
        statusbar = Label(self._root, relief=SUNKEN, font=('Helvetica', 12),
                          anchor=NW)
        statusbar.pack(side='bottom', fill='x')
        self.view = BoardView(self._root, model=self.model, parent=self,
                              statusbar=statusbar)
        self.player_color = BLACK
        self.num_players = 1
        self.controller1 = None
        self.controller2 = None
        self.set_controllers()
        self.controller1.start_turn()
        self.filename = None

    def set_controllers(self):
        think_time = self.parent.thinkTime.get()
        if self.num_players == 0:
            self.controller1 = AlphaBetaController(model=self.model,
                                                   view=self.view,
                                                   searchtime=think_time,
                                                   end_turn_event=self.turn_finished)
            self.controller2 = AlphaBetaController(model=self.model,
                                                   view=self.view,
                                                   searchtime=think_time,
                                                   end_turn_event=self.turn_finished)
        elif self.num_players == 1:
            # assumption here is that Black is the player
            self.controller1 = PlayerController(model=self.model,
                                                view=self.view,
                                                end_turn_event=self.turn_finished)
            self.controller2 = AlphaBetaController(model=self.model,
                                                   view=self.view,
                                                   searchtime=think_time,
                                                   end_turn_event=self.turn_finished)
            # swap controllers if White is selected as the player
            if self.player_color == WHITE:
                self.controller1, self.controller2 = self.controller2, self.controller1
        elif self.num_players == 2:
            self.controller1 = PlayerController(model=self.model,
                                                view=self.view,
                                                end_turn_event=self.turn_finished)
            self.controller2 = PlayerController(model=self.model,
                                                view=self.view,
                                                end_turn_event=self.turn_finished)
        self.controller1.set_before_turn_event(self.controller2.remove_highlights)
        self.controller2.set_before_turn_event(self.controller1.remove_highlights)

    def _stop_updates(self):
        # stop alphabeta threads from making any moves
        self.model.curr_state.ok_to_move = False
        self.controller1.stop_process()
        self.controller2.stop_process()

    def _save_curr_game_if_needed(self):
        if self.view.is_dirty():
            msg = 'Do you want to save your changes'
            if self.filename:
                msg += ' to %s?' % self.filename
            else:
                msg += '?'
            result = askyesnocancel(TITLE, msg)
            if result is True:
                self.save_game()
            return result
        else:
            return False

    def new_game(self):
        self._stop_updates()
        self._save_curr_game_if_needed()
        self.filename = None
        self._root.title('Raven ' + VERSION)
        self.model = Checkers()
        self.player_color = BLACK
        self.view.reset_view(self.model)
        self.think_time = self.parent.thinkTime.get()
        self.set_controllers()
        self.view.update_statusbar()
        self.view.reset_toolbar_buttons()
        self.view.curr_annotation = ''
        self.controller1.start_turn()

    def load_game(self, filename):
        self._stop_updates()
        try:
            saved_game = SavedGame()
            saved_game.read(filename)
            self.model.curr_state.clear()
            self.model.curr_state.to_move = saved_game.to_move
            self.num_players = saved_game.num_players
            squares = self.model.curr_state.squares
            for i in saved_game.black_men:
                squares[square_map[i]] = BLACK | MAN
            for i in saved_game.black_kings:
                squares[square_map[i]] = BLACK | KING
            for i in saved_game.white_men:
                squares[square_map[i]] = WHITE | MAN
            for i in saved_game.white_kings:
                squares[square_map[i]] = WHITE | KING
            self.model.curr_state.reset_undo()
            self.model.curr_state.redo_list = saved_game.moves
            self.model.curr_state.update_piece_count()
            self.view.reset_view(self.model)
            self.view.serializer.restore(saved_game.description)
            self.view.curr_annotation = self.view.get_annotation()
            self.view.flip_board(saved_game.flip_board)
            self.view.update_statusbar()
            self.parent.set_title_bar_filename(filename)
            self.filename = filename
        except IOError as err:
            showerror(PROGRAM_TITLE, 'Invalid file. ' + str(err))

    def open_game(self):
        self._stop_updates()
        self._save_curr_game_if_needed()
        f = askopenfilename(filetypes=(('Raven Checkers files', '*.rcf'), ('All files', '*.*')),
                            initialdir=TRAINING_DIR)
        if not f:
            return
        self.load_game(f)

    def save_game_as(self):
        self._stop_updates()
        filename = asksaveasfilename(filetypes=(('Raven Checkers files', '*.rcf'), ('All files', '*.*')),
                                     initialdir=TRAINING_DIR,
                                     defaultextension='.rcf')
        if filename == '':
            return
        self._write_file(filename)

    def save_game(self):
        self._stop_updates()
        filename = self.filename
        if not self.filename:
            filename = asksaveasfilename(filetypes=(('Raven Checkers files', '*.rcf'),
                                                    ('All files', '*.*')),
                                         initialdir=TRAINING_DIR,
                                         defaultextension='.rcf')
            if filename == '':
                return
        self._write_file(filename)

    def _write_file(self, filename):
        try:
            saved_game = SavedGame()
            # undo moves back to the beginning of play
            undo_steps = 0
            while self.model.curr_state.undo_list:
                undo_steps += 1
                self.model.curr_state.undo_move(None, True, True,
                                                self.view.get_annotation())
            # save the state of the board
            saved_game.to_move = self.model.curr_state.to_move
            saved_game.num_players = self.num_players
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
            saved_game.description = self.view.serializer.dump()
            saved_game.moves = self.model.curr_state.redo_list
            saved_game.flip_board = self.view.flip_view
            saved_game.write(filename)
            # redo moves forward to the previous state
            for i in range(undo_steps):
                annotation = self.view.get_annotation()
                self.model.curr_state.redo_move(None, annotation)
            # record current filename in title bar
            self.parent.set_title_bar_filename(filename)
            self.filename = filename
        except IOError:
            showerror(PROGRAM_TITLE, 'Could not save file.')

    def turn_finished(self):
        if self.model.curr_state.to_move == BLACK:
            self.controller2.end_turn()  # end White's turn
            self._root.update()
            self.view.update_statusbar()
            self.controller1.start_turn()  # begin Black's turn
        else:
            self.controller1.end_turn()  # end Black's turn
            self._root.update()
            self.view.update_statusbar()
            self.controller2.start_turn()  # begin White's turn
