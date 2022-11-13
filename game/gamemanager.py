import os
from tkinter import Label, SUNKEN, NW
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import askyesnocancel, showerror, showinfo
from datetime import datetime
from game.checkers import Checkers
from gui.boardview import BoardView
from gui.filelist import FileList
from gui.playercontroller import PlayerController
from gui.alphabetacontroller import AlphaBetaController
from parsing.PDN import PDNReader, PDNWriter, board_to_PDN_ready
from parsing.migrate import RCF2PDN, build_move_annotation_pairs
from util.globalconst import BLACK, WHITE, TITLE, VERSION, KING, MAN, PROGRAM_TITLE, TRAINING_DIR
from util.globalconst import square_map, keymap


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
        self.think_time = self.parent.thinkTime.get()
        self.num_players = 1
        self.controller1 = None
        self.controller2 = None
        self.set_controllers()
        # noinspection PyUnresolvedReferences
        self.controller1.start_turn()
        self.filepath = None

    def set_controllers(self):
        if self.num_players == 0:
            self.controller1 = AlphaBetaController(model=self.model,
                                                   view=self.view,
                                                   searchtime=self.think_time,
                                                   end_turn_event=self.turn_finished)
            self.controller2 = AlphaBetaController(model=self.model,
                                                   view=self.view,
                                                   searchtime=self.think_time,
                                                   end_turn_event=self.turn_finished)
        elif self.num_players == 1:
            # assumption here is that Black is the player
            self.controller1 = PlayerController(model=self.model,
                                                view=self.view,
                                                end_turn_event=self.turn_finished)
            self.controller2 = AlphaBetaController(model=self.model,
                                                   view=self.view,
                                                   searchtime=self.think_time,
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
            if self.filepath:
                msg += ' to %s?' % self.filepath
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
        self.filepath = None
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

    def load_game(self, filepath):
        self._stop_updates()
        try:
            reader = PDNReader.from_file(filepath)
            game_list = reader.get_game_list()
            game = None
            if len(game_list) > 1:
                dlg = FileList(self._root, game_list)
                if dlg.result:
                    game = reader.read_game(dlg.result)
            else:
                game = reader.read_game(0)
            if game is not None:
                self.model.curr_state.clear()
                self.model.curr_state.to_move = game.next_to_move
                self.num_players = 2
                if game.black_player.startswith("Computer"):
                    self.num_players -= 1
                if game.white_player.startswith("Computer"):
                    self.num_players -= 1
                squares = self.model.curr_state.squares
                for i in game.black_men:
                    squares[square_map[i]] = BLACK | MAN
                for i in game.black_kings:
                    squares[square_map[i]] = BLACK | KING
                for i in game.white_men:
                    squares[square_map[i]] = WHITE | MAN
                for i in game.white_kings:
                    squares[square_map[i]] = WHITE | KING
                self.model.curr_state.reset_undo()
                self.model.curr_state.redo_list = game.moves
                self.model.curr_state.update_piece_count()
                self.view.reset_view(self.model)
                self.view.serializer.restore(game.description)
                self.view.curr_annotation = self.view.get_annotation()
                self.view.flip_board(game.board_orientation == "white_on_top")
                self.view.update_statusbar()
                self.parent.set_title_bar_filename(os.path.basename(filepath))
                self.filepath = filepath
        except IOError as err:
            showerror(PROGRAM_TITLE, 'Invalid file. ' + str(err))

    def open_game(self):
        self._stop_updates()
        self._save_curr_game_if_needed()
        in_path = askopenfilename(filetypes=(('Portable Draughts Notation files', '*.pdn'),
                                             ('Raven Checkers files', '*.rcf'), ('All files', '*.*')),
                                  initialdir=TRAINING_DIR)
        if not in_path:
            return
        root, ext = os.path.splitext(in_path)
        if ext == '.rcf':
            showinfo("Migrate RCF file", "RCF files use the legacy Raven Checkers format and must be converted to "
                     "PDN format. Choose a PDN save file to perform the conversion.")
            out_path = asksaveasfilename(filetypes=(('Portable Draughts Notation files', '*.pdn'), ('All files', '*.*')),
                                         initialdir=TRAINING_DIR,
                                         initialfile=os.path.basename(root) + '.pdn',
                                         defaultextension='.pdn')
            if not out_path:
                return
            RCF2PDN.with_file(in_path, out_path)
            self.load_game(out_path)
        else:
            self.load_game(in_path)

    def save_game_as(self):
        self._stop_updates()
        filename = asksaveasfilename(filetypes=(('Portable Draughts Notation files', '*.pdn'), ('All files', '*.*')),
                                     initialdir=TRAINING_DIR,
                                     defaultextension='.pdn')
        if filename == '':
            return

        self._write_file(filename)

    def save_game(self):
        self._stop_updates()
        filename = self.filepath
        if not self.filepath:
            filename = asksaveasfilename(filetypes=(('Portable Draughts Notation files', '*.pdn'),
                                                    ('All files', '*.*')),
                                         initialdir=TRAINING_DIR,
                                         defaultextension='.pdn')
            if filename == '':
                return
        self._write_file(filename)

    def _write_file(self, filename):
        try:
            # redo moves up to the end of play, if possible
            to_move = self.model.curr_state.to_move
            scoring = self.model.utility(to_move, self.model.curr_state)
            if scoring == -4000:
                if to_move == WHITE:
                    result = "1-0"
                else:
                    result = "0-1"
            elif scoring == 4000:
                if to_move == WHITE:
                    result = "0-1"
                else:
                    result = "1-0"
            else:
                result = "*"
            # undo moves back to the beginning of play
            undo_steps = 0
            while self.model.curr_state.undo_list:
                undo_steps += 1
                self.model.curr_state.undo_move(None, True, True, self.view.get_annotation())
            # save the state of the board
            to_move = 'black' if self.model.curr_state.to_move == BLACK else 'white'
            black_men = []
            black_kings = []
            white_men = []
            white_kings = []
            for i, sq in enumerate(self.model.curr_state.squares):
                if sq == BLACK | MAN:
                    black_men.append(keymap[i])
                elif sq == BLACK | KING:
                    black_kings.append(keymap[i])
                elif sq == WHITE | MAN:
                    white_men.append(keymap[i])
                elif sq == WHITE | KING:
                    white_kings.append(keymap[i])
            # change description into line comments
            description = self.view.serializer.dump()
            description = '% ' + description
            description = description.replace('\n', '\n% ')
            board_moves = self.model.curr_state.redo_list
            board_orientation = "white_on_top" if self.view.flip_view is False else "black_on_top"
            black_player = "Player1"
            white_player = "Player2"
            move_list, anno_list = board_to_PDN_ready(board_moves)
            moves, annotations = build_move_annotation_pairs(move_list, anno_list)
            PDNWriter.to_file(filename, '*', '*', datetime.now().strftime("%d/%m/%Y"), '*', black_player, white_player,
                              to_move, black_men, white_men, black_kings, white_kings, result, board_orientation,
                              moves, annotations, description)

            # redo moves forward to the previous state
            for i in range(undo_steps):
                annotation = self.view.get_annotation()
                self.model.curr_state.redo_move(None, annotation)
            # record current filename in title bar
            self.parent.set_title_bar_filename(filename)
            self.filepath = filename
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
