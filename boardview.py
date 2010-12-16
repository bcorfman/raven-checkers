from Tkinter import *
from Tkconstants import END
from command import *
from observer import *
from globalconst import *
from textserialize import dump_text_widget, restore_text_widget
from tkFont import Font

class BoardView(Observer):
    def __init__(self, root, **props):
        self._statusbar = props['statusbar']
        self.root = root
        self._model = props['model']
        self._model.curr_state.attach(self)
        self._board_side = props.get('side') or DEFAULT_SIZE
        self.light_squares = props.get('lightsquares') or LIGHT_SQUARES
        self.dark_squares = props.get('darksquares') or DARK_SQUARES
        self.light_color = props.get('lightcheckers') or LIGHT_CHECKERS
        self.dark_color = props.get('darkcheckers') or DARK_CHECKERS
        self._square_size = self._board_side / 8
        self._piece_offset = self._square_size / 5
        self._crownpic = PhotoImage(file=CROWN_IMAGE)
        self._boardpos = create_position_map()
        self._gridpos = create_grid_map()
        self._keymap = create_key_map()
        self.squaremap = self._flip_map(self._keymap)
        self.canvas = Canvas(root, width=self._board_side,
                             height=self._board_side)
        self.canvas.pack(side=TOP)
        self.toolbar = Frame(root)
        self.bold = Button(name='bold', text='B', borderwidth=1,
                           font=('Times New Roman', '9', 'bold'),
                           command=self._on_bold)
        self.bold.pack(in_=self.toolbar, side='left')
        self.italic = Button(name='italic', text='I', borderwidth=1, padx=2,
                             font=('Times New Roman', '9', ('bold', 'italic')),
                             command=self._on_italic)
        self.italic.pack(in_=self.toolbar, side='left')
        font, size = get_preferences_from_file()
        self._b_font = Font(root, (font, size, 'bold'))
        self._i_font = Font(root, (font, size, 'italic'))
        self.toolbar.pack(side='top', fill='x')
        self.txt = Text(root, width=0, height=4, font=(font,size))
        self.txt.pack(side=TOP, fill=BOTH, expand=True)
        self.txt.tag_config('bold', font=self._b_font)
        self.txt.tag_config('italic', font=self._i_font)
        self._setup_board(root)
        starting_squares = [i for i in self._model.curr_state.valid_squares
                            if self._model.curr_state.squares[i] &
                            (BLACK | WHITE)]
        self._draw_checkers(Command(add=starting_squares))
        self.flip_view = False # black on bottom
        self._label_board()
        self.update_statusbar()

    def _toggle_state(self, tag, btn, other_btns):
        # toggle the text state based on the first character in the
        # selected range.
        if self.txt.tag_ranges('sel'):
            current_tags = self.txt.tag_names('sel.first')
            already_tagged = tag in current_tags
            for t in current_tags:
                if t != 'sel':
                    self.txt.tag_remove(t, 'sel.first', 'sel.last')
            if not already_tagged:
                self.txt.tag_add(tag, 'sel.first', 'sel.last')
                btn.configure(relief='sunken')
                for b in other_btns:
                    b.configure(relief='raised')
            else:
                btn.configure(relief='raised')

    def _on_bold(self):
        self._toggle_state('bold', self.bold, [self.italic])

    def _on_italic(self):
        self._toggle_state('italic', self.italic, [self.bold])

    def reset_view(self, model):
        self._model = model
        sq = self._model.curr_state.valid_squares
        self.canvas.delete(self.dark_color)
        self.canvas.delete(self.light_color)
        starting_squares = [i for i in sq if (self._model.curr_state.squares[i]
                                              & (BLACK | WHITE))]
        self._draw_checkers(Command(add=starting_squares))
        for i in sq:
            self.highlight_square(i, DARK_SQUARES)

    def calc_board_loc(self, x, y):
        vx, vy = self.calc_valid_xy(x, y)
        xi = int(vx / self._square_size)
        yi = int(vy / self._square_size)
        return xi, yi

    def calc_board_pos(self, xi, yi):
        return self._boardpos.get(xi + yi * 8, 0)

    def calc_grid_pos(self, pos):
        return self._gridpos[pos]

    def highlight_square(self, idx, color):
        row, col = self._gridpos[idx]
        hpos = col + row * 8
        self.canvas.itemconfigure('o'+str(hpos), outline=color)

    def calc_valid_xy(self, x, y):
        return (min(max(0, self.canvas.canvasx(x)), self._board_side-1),
                min(max(0, self.canvas.canvasy(y)), self._board_side-1))

    def notify(self, move):
        add_lst = []
        rem_lst = []
        for idx, _, newval in move.affected_squares:
            if newval & FREE:
                rem_lst.append(idx)
            else:
                add_lst.append(idx)
        cmd = Command(add=add_lst, remove=rem_lst)
        self._draw_checkers(cmd)
        self.txt.delete('1.0', END)
        restore_text_widget(move.annotation, self.txt)

    def get_annotation(self):
        return dump_text_widget(self.txt)

    def erase_checker(self, index):
        self.canvas.delete('c'+str(index))

    def flip_board(self, flip):
        self._delete_labels()
        self.canvas.delete(self.dark_color)
        self.canvas.delete(self.light_color)
        if self.flip_view != flip:
            self.flip_view = flip
            self._gridpos = self._reverse_map(self._gridpos)
            self._boardpos = self._reverse_map(self._boardpos)
        self._label_board()
        starting_squares = [i for i in self._model.curr_state.valid_squares
                            if self._model.curr_state.squares[i] &
                            (BLACK | WHITE)]
        all_checkers = Command(add=starting_squares)
        self._draw_checkers(all_checkers)

    def _flip_map(self, m):
        d = {}
        keys = [k for k, _ in m.iteritems()]
        vals = [v for _, v in m.iteritems()]
        for k, v in zip(vals, keys):
            d[k] = v
        return d

    def _reverse_map(self, m):
        d = {}
        keys = [k for k, _ in m.iteritems()]
        vals = [v for _, v in m.iteritems()]
        for k, v in zip(keys, reversed(vals)):
            d[k] = v
        return d

    def update_statusbar(self, output=None):
        if output:
            self._statusbar['text'] = output
            self.root.update()
            return

        if self._model.terminal_test():
            text = "Game over. "
            if self._model.curr_state.to_move == WHITE:
                text += "Black won."
            else:
                text += "White won."
            self._statusbar['text'] = text
            return

        if self._model.curr_state.to_move == WHITE:
            self._statusbar['text'] = "White to move"
        else:
            self._statusbar['text'] = "Black to move"

    def get_positions(self, type):
        return map(str, sorted((self._keymap[i]
                for i in self._model.curr_state.valid_squares
                if self._model.curr_state.squares[i] == type)))

    # private functions
    def _setup_board(self, root):
        for r in range(0, 8, 2):
            row = r * self._square_size
            for c in range(0, 8, 2):
                col = c * self._square_size
                self.canvas.create_rectangle(col, row, col+self._square_size-1,
                                             row+self._square_size-1,
                                             fill=LIGHT_SQUARES,
                                             outline=LIGHT_SQUARES)
            for c in range(1, 8, 2):
                col = c * self._square_size
                self.canvas.create_rectangle(col, row+self._square_size,
                                             col+self._square_size-1,
                                             row+self._square_size*2-1,
                                             fill=LIGHT_SQUARES,
                                             outline=LIGHT_SQUARES)
        for r in range(0, 8, 2):
            row = r * self._square_size
            for c in range(1, 8, 2):
                col = c * self._square_size
                self.canvas.create_rectangle(col, row, col+self._square_size-1,
                                             row+self._square_size-1,
                                             fill=DARK_SQUARES,
                                             outline=DARK_SQUARES,
                                             tags='o'+str(r*8+c))
            for c in range(0, 8, 2):
                col = c * self._square_size
                self.canvas.create_rectangle(col, row+self._square_size,
                                             col+self._square_size-1,
                                             row+self._square_size*2-1,
                                             fill=DARK_SQUARES,
                                             outline=DARK_SQUARES,
                                             tags='o'+str(((r+1)*8)+c))

    def _label_board(self):
        for key, pair in self._gridpos.iteritems():
            row, col = pair
            xpos, ypos = col * self._square_size, row * self._square_size
            self.canvas.create_text(xpos+self._square_size-7,
                                    ypos+self._square_size-7,
                                    text=str(self._keymap[key]),
                                    fill=LIGHT_SQUARES, tag='label')

    def _delete_labels(self):
        self.canvas.delete('label')

    def _draw_checkers(self, change):
        if change == None:
            return
        for i in change.remove:
            self.canvas.delete('c'+str(i))
        for i in change.add:
            checker = self._model.curr_state.squares[i]
            color = self.dark_color if checker & COLORS == BLACK else self.light_color
            row, col = self._gridpos[i]
            x = col * self._square_size + self._piece_offset
            y = row * self._square_size + self._piece_offset
            tag = 'c'+str(i)
            self.canvas.create_oval(x+2, y+2, x+2+CHECKER_SIZE,
                                    y+2+CHECKER_SIZE, outline='black',
                                    fill='black', tags=(color, tag))
            self.canvas.create_oval(x, y, x+CHECKER_SIZE, y+CHECKER_SIZE,
                                    outline='black', fill=color,
                                    tags=(color, tag))
            if checker & KING:
                self.canvas.create_image(x+15, y+15, image=self._crownpic,
                                         anchor=CENTER, tags=(color, tag))
