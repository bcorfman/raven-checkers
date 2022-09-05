from tkinter import LabelFrame, Frame, Radiobutton, Label, Entry, StringVar, IntVar
from tkinter import DISABLED, NORMAL, LEFT, X
from tkinter.ttk import Checkbutton
from tkinter.simpledialog import Dialog
from util.globalconst import BLACK, WHITE, square_map, MAN, KING, MAX_VALID_SQ


class SetupBoard(Dialog):
    def __init__(self, parent, title, game_manager):
        self._master = parent
        self._manager = game_manager
        self._load_entry_box_vars()
        self.result = False
        Dialog.__init__(self, parent, title)

    def body(self, master):
        self._npLFrame = LabelFrame(master, text='No. of players:')
        self._npFrameEx1 = Frame(self._npLFrame, width=30)
        self._npFrameEx1.pack(side=LEFT, pady=5, expand=1)
        self._npButton1 = Radiobutton(self._npLFrame, text='Zero (autoplay)',
                                      value=0, variable=self._num_players,
                                      command=self._disable_player_color)
        self._npButton1.pack(side=LEFT, pady=5, expand=1)
        self._npButton2 = Radiobutton(self._npLFrame, text='One',
                                      value=1, variable=self._num_players,
                                      command=self._enable_player_color)
        self._npButton2.pack(side=LEFT, pady=5, expand=1)
        self._npButton3 = Radiobutton(self._npLFrame, text='Two',
                                      value=2, variable=self._num_players,
                                      command=self._disable_player_color)
        self._npButton3.pack(side=LEFT, pady=5, expand=1)
        self._npFrameEx2 = Frame(self._npLFrame, width=30)
        self._npFrameEx2.pack(side=LEFT, pady=5, expand=1)
        self._npLFrame.pack(fill=X)

        self._playerFrame = LabelFrame(master, text='Player color:')
        self._playerFrameEx1 = Frame(self._playerFrame, width=50)
        self._playerFrameEx1.pack(side=LEFT, pady=5, expand=1)
        self._rbColor1 = Radiobutton(self._playerFrame, text='Black',
                                     value=BLACK, variable=self._player_color)
        self._rbColor1.pack(side=LEFT, padx=0, pady=5, expand=1)
        self._rbColor2 = Radiobutton(self._playerFrame, text='White',
                                     value=WHITE, variable=self._player_color)
        self._rbColor2.pack(side=LEFT, padx=0, pady=5, expand=1)
        self._playerFrameEx2 = Frame(self._playerFrame, width=50)
        self._playerFrameEx2.pack(side=LEFT, pady=5, expand=1)
        self._playerFrame.pack(fill=X)

        self._rbFrame = LabelFrame(master, text='Next to move:')
        self._rbFrameEx1 = Frame(self._rbFrame, width=50)
        self._rbFrameEx1.pack(side=LEFT, pady=5, expand=1)
        self._rbTurn1 = Radiobutton(self._rbFrame, text='Black',
                                    value=BLACK, variable=self._player_turn)
        self._rbTurn1.pack(side=LEFT, padx=0, pady=5, expand=1)
        self._rbTurn2 = Radiobutton(self._rbFrame, text='White',
                                    value=WHITE, variable=self._player_turn)
        self._rbTurn2.pack(side=LEFT, padx=0, pady=5, expand=1)
        self._rbFrameEx2 = Frame(self._rbFrame, width=50)
        self._rbFrameEx2.pack(side=LEFT, pady=5, expand=1)
        self._rbFrame.pack(fill=X)

        self._bcFrame = LabelFrame(master, text='Board configuration')
        self._wmFrame = Frame(self._bcFrame, borderwidth=0)
        self._wmLabel = Label(self._wmFrame, text='White men:')
        self._wmLabel.pack(side=LEFT, padx=7, pady=10)
        self._wmEntry = Entry(self._wmFrame, width=40,
                              textvariable=self._white_men)
        self._wmEntry.pack(side=LEFT, padx=10)
        self._wmFrame.pack()

        self._wkFrame = Frame(self._bcFrame, borderwidth=0)
        self._wkLabel = Label(self._wkFrame, text='White kings:')
        self._wkLabel.pack(side=LEFT, padx=5, pady=10)
        self._wkEntry = Entry(self._wkFrame, width=40,
                              textvariable=self._white_kings)
        self._wkEntry.pack(side=LEFT, padx=10)
        self._wkFrame.pack()

        self._bmFrame = Frame(self._bcFrame, borderwidth=0)
        self._bmLabel = Label(self._bmFrame, text='Black men:')
        self._bmLabel.pack(side=LEFT, padx=7, pady=10)
        self._bmEntry = Entry(self._bmFrame, width=40,
                              textvariable=self._black_men)
        self._bmEntry.pack(side=LEFT, padx=10)
        self._bmFrame.pack()

        self._bkFrame = Frame(self._bcFrame, borderwidth=0)
        self._bkLabel = Label(self._bkFrame, text='Black kings:')
        self._bkLabel.pack(side=LEFT, padx=5, pady=10)
        self._bkEntry = Entry(self._bkFrame, width=40,
                              textvariable=self._black_kings)
        self._bkEntry.pack(side=LEFT, padx=10)
        self._bkFrame.pack()
        self._bcFrame.pack(fill=X)

        self._bsState = IntVar()
        self._bsFrame = Frame(master, borderwidth=0)
        self._bsCheck = Checkbutton(self._bsFrame, variable=self._bsState,
                                    text='Start new game with the current setup?')
        self._bsCheck.pack()
        self._bsFrame.pack(fill=X)

        if self._num_players.get() == 1:
            self._enable_player_color()
        else:
            self._disable_player_color()

    def validate(self):
        self.wm_list = self._parse_int_list(self._white_men.get())
        self.wk_list = self._parse_int_list(self._white_kings.get())
        self.bm_list = self._parse_int_list(self._black_men.get())
        self.bk_list = self._parse_int_list(self._black_kings.get())
        if (self.wm_list is None or self.wk_list is None
                or self.bm_list is None or self.bk_list is None):
            return 0  # Error occurred during parsing
        if not self._all_unique(self.wm_list, self.wk_list,
                                self.bm_list, self.bk_list):
            return 0  # A repeated index occurred
        return 1

    def apply(self):
        mgr = self._manager
        model = mgr.model
        view = mgr.view
        state = model.curr_state
        mgr.player_color = self._player_color.get()
        mgr.num_players = self._num_players.get()
        mgr.model.curr_state.to_move = self._player_turn.get()

        # only reset the BoardView if men or kings have new positions
        if (sorted(self.wm_list) != sorted(self._orig_white_men) or
                sorted(self.wk_list) != sorted(self._orig_white_kings) or
                sorted(self.bm_list) != sorted(self._orig_black_men) or
                sorted(self.bk_list) != sorted(self._orig_black_kings) or
                self._bsState.get() == 1):
            state.clear()
            sq = state.squares
            for item in self.wm_list:
                idx = square_map[item]
                sq[idx] = WHITE | MAN
            for item in self.wk_list:
                idx = square_map[item]
                sq[idx] = WHITE | KING
            for item in self.bm_list:
                idx = square_map[item]
                sq[idx] = BLACK | MAN
            for item in self.bk_list:
                idx = square_map[item]
                sq[idx] = BLACK | KING
            state.to_move = self._player_turn.get()
            state.reset_undo()
            view.reset_view(mgr.model)
        if self._bsState.get() == 1:
            mgr.filename = None
            mgr.parent.set_title_bar_filename()
        state.ok_to_move = True
        self.result = True
        self.destroy()

    def cancel(self, event=None):
        self.destroy()

    def _load_entry_box_vars(self):
        self._white_men = StringVar()
        self._white_kings = StringVar()
        self._black_men = StringVar()
        self._black_kings = StringVar()
        self._player_color = IntVar()
        self._player_turn = IntVar()
        self._num_players = IntVar()
        self._player_color.set(self._manager.player_color)
        self._num_players.set(self._manager.num_players)
        model = self._manager.model
        self._player_turn.set(model.curr_state.to_move)
        view = self._manager.view
        self._white_men.set(', '.join(view.get_positions(WHITE | MAN)))
        self._white_kings.set(', '.join(view.get_positions(WHITE | KING)))
        self._black_men.set(', '.join(view.get_positions(BLACK | MAN)))
        self._black_kings.set(', '.join(view.get_positions(BLACK | KING)))
        self._orig_white_men = map(int, view.get_positions(WHITE | MAN))
        self._orig_white_kings = map(int, view.get_positions(WHITE | KING))
        self._orig_black_men = map(int, view.get_positions(BLACK | MAN))
        self._orig_black_kings = map(int, view.get_positions(BLACK | KING))

    def _disable_player_color(self):
        self._rbColor1.configure(state=DISABLED)
        self._rbColor2.configure(state=DISABLED)

    def _enable_player_color(self):
        self._rbColor1.configure(state=NORMAL)
        self._rbColor2.configure(state=NORMAL)

    def _all_unique(self, *lists):
        s = set()
        total_list = []
        for i in lists:
            total_list.extend(i)
            s = s.union(i)
        return sorted(total_list) == sorted(s)

    def _parse_int_list(self, parsestr):
        try:
            lst = parsestr.split(',')
        except AttributeError:
            return None

        if lst == ['']:
            return []

        try:
            lst = [int(i) for i in lst]
        except ValueError:
            return None

        if not all(((1 <= x <= MAX_VALID_SQ) for x in lst)):
            return None

        return lst
