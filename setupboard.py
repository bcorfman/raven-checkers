from Tkinter import *
from globalconst import *
import centeredwindow as cw

class SetupBoard(Toplevel, cw.CenteredWindow):
    def __init__(self, master, gameManager):
        self._frame = Toplevel(master.root)
        self._frame.transient(master.root)
        self._frame.grab_set()
        self._frame.title("Set up board")
        self._manager = gameManager
        self._load_entry_box_vars()
        self._create_controls()
        if self._num_players.get() == 1:
            self._enable_player_color()
        else:
            self._disable_player_color()
        cw.CenteredWindow.__init__(self, self._frame)
        self._cancel.focus_set()

    def _create_controls(self):
        self._npLFrame = LabelFrame(self._frame, text='No. of players:')
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

        self._playerFrame = LabelFrame(self._frame, text='Player color:')
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

        self._rbFrame = LabelFrame(self._frame, text='Next to move:')
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

        self._bcFrame = LabelFrame(self._frame, text='Board configuration')
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

        self._buttonFrame = Frame(self._frame, borderwidth=0)
        self._ok = Button(self._buttonFrame, text='OK', padx='7m',
                          command=self._on_click_ok)
        self._cancel = Button(self._buttonFrame, text='Cancel', padx='5m',
                              command=self._on_click_cancel)
        self._ok.pack(side=LEFT, padx=25, pady=10)
        self._cancel.pack(side=LEFT, pady=10)
        self._buttonFrame.pack()

    def _load_entry_box_vars(self):
        self._white_men = StringVar()
        self._white_kings = StringVar()
        self._black_men = StringVar()
        self._black_kings = StringVar()
        self._player_color = IntVar()
        self._player_color.set(self._manager.player_color)
        self._player_turn = IntVar()
        self._num_players = IntVar()
        self._num_players.set(self._manager.num_players)
        model = self._manager.model
        self._player_turn.set(model.curr_state.to_move)
        view = self._manager.view
        self._white_men.set(', '.join(view.get_positions(WHITE | MAN)))
        self._white_kings.set(', '.join(view.get_positions(WHITE | KING)))
        self._black_men.set(', '.join(view.get_positions(BLACK | MAN)))
        self._black_kings.set(', '.join(view.get_positions(BLACK | KING)))

    def _on_click_ok(self):
        mgr = self._manager
        model = mgr.model
        wm_list = self._parse_int_list(self._white_men.get())
        wk_list = self._parse_int_list(self._white_kings.get())
        bm_list = self._parse_int_list(self._black_men.get())
        bk_list = self._parse_int_list(self._black_kings.get())
        if (wm_list == None or wk_list == None
            or bm_list == None or bk_list == None):
            return  # Error occurred during parsing
        if not self._all_unique(wm_list, wk_list, bm_list, bk_list):
            return  # A repeated index occurred
        view = mgr.view
        state = model.curr_state
        state.clear()
        sq = state.squares
        for item in wm_list:
            idx = view.squaremap[item]
            sq[idx] = WHITE | MAN
        for item in wk_list:
            idx = view.squaremap[item]
            sq[idx] = WHITE | KING
        for item in bm_list:
            idx = view.squaremap[item]
            sq[idx] = BLACK | MAN
        for item in bk_list:
            idx = view.squaremap[item]
            sq[idx] = BLACK | KING
        state.to_move = self._player_turn.get()
        state.reset_undo()
        mgr.player_color = self._player_color.get()
        mgr.num_players = self._num_players.get()
        mgr.set_controllers()
        view.reset_view(mgr.model)
        state.ok_to_move = True
        self._frame.destroy()
        mgr.turn_finished()

    def _on_click_cancel(self):
        mgr = self._manager
        mgr.set_controllers()
        mgr.view.reset_view(mgr.model)
        self._frame.destroy()
        mgr.turn_finished()

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
        s = list(s)
        s.sort()
        total_list.sort()
        return total_list == s

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
        return lst
