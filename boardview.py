from Tkinter import *
from command import *
from observer import *
from globalconst import *

class BoardView(Observer, Canvas):
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
        self._boardpos = self._create_position_map()
        self._gridpos = create_grid_map()
        self._keymap = self._create_key_map()
        self.squaremap = self._flip_map(self._keymap)
        self._create_board(root)
        starting_squares = [i for i in self._model.curr_state.valid_squares
                            if self._model.curr_state.squares[i] &
                            (BLACK | WHITE)]
        self._draw_checkers(Command(add=starting_squares))
        self.flip_view = False # black on bottom
        self._label_board()
        self.update_statusbar()

    def reset_view(self, model):
        self._model = model
        sq = self._model.curr_state.valid_squares
        self.delete(self.dark_color)
        self.delete(self.light_color)
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
        self.itemconfigure('o'+str(hpos), outline=color)

    def calc_valid_xy(self, x, y):
        return (min(max(0, self.canvasx(x)), self._board_side-1),
                min(max(0, self.canvasy(y)), self._board_side-1))

    def notify(self, move):
        add_lst = []
        rem_lst = []
        for m in move:
            idx, oldval, newval = m
            if newval & FREE:
                rem_lst.append(idx)
            else:
                add_lst.append(idx)
        cmd = Command(add=add_lst, remove=rem_lst)
        self._draw_checkers(cmd)

    def erase_checker(self, index):
        self.delete('c'+str(index))

    def flip_board(self, flip):
        self._delete_labels()
        self.delete(self.dark_color)
        self.delete(self.light_color)
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
    def _create_position_map(self):
        """ Maps compressed grid indices xi + yi * 8 to internal
            board indices """
        pos = {}
        sq = self._model.curr_state.squares
        pos[1] = 37;   pos[3]  = 38; pos[5] =  39; pos[7]  = 40
        pos[8] = 32;   pos[10] = 33; pos[12] = 34; pos[14] = 35
        pos[17] = 28;  pos[19] = 29; pos[21] = 30; pos[23] = 31
        pos[24] = 23;  pos[26] = 24; pos[28] = 25; pos[30] = 26
        pos[33] = 19;  pos[35] = 20; pos[37] = 21; pos[39] = 22
        pos[40] = 14;  pos[42] = 15; pos[44] = 16; pos[46] = 17
        pos[49] = 10;  pos[51] = 11; pos[53] = 12; pos[55] = 13
        pos[56] = 5;   pos[58] = 6;  pos[60] =  7; pos[62] = 8
        return pos

    def _create_key_map(self):
        """ Maps internal board indices to checkerboard label numbers """
        key = {}
        key[5]  = 4;  key[6]  = 3;  key[7]  = 2;  key[8]  = 1
        key[10] = 8;  key[11] = 7;  key[12] = 6;  key[13] = 5
        key[14] = 12; key[15] = 11; key[16] = 10; key[17] = 9
        key[19] = 16; key[20] = 15; key[21] = 14; key[22] = 13
        key[23] = 20; key[24] = 19; key[25] = 18; key[26] = 17
        key[28] = 24; key[29] = 23; key[30] = 22; key[31] = 21
        key[32] = 28; key[33] = 27; key[34] = 26; key[35] = 25
        key[37] = 32; key[38] = 31; key[39] = 30; key[40] = 29
        return key

    def _create_board(self, root):
        Canvas.__init__(self, root, width=self._board_side,
                        height=self._board_side)
        for r in range(0, 8, 2):
            row = r * self._square_size
            for c in range(0, 8, 2):
                col = c * self._square_size
                self.create_rectangle(col, row, col+self._square_size-1,
                                      row+self._square_size-1,
                                      fill=LIGHT_SQUARES,
                                      outline=LIGHT_SQUARES)
            for c in range(1, 8, 2):
                col = c * self._square_size
                self.create_rectangle(col, row+self._square_size,
                                      col+self._square_size-1,
                                      row+self._square_size*2-1,
                                      fill=LIGHT_SQUARES, outline=LIGHT_SQUARES)
        for r in range(0, 8, 2):
            row = r * self._square_size
            for c in range(1, 8, 2):
                col = c * self._square_size
                self.create_rectangle(col, row, col+self._square_size-1,
                                      row+self._square_size-1,
                                      fill=DARK_SQUARES,
                                      outline=DARK_SQUARES, tags='o'+str(r*8+c))
            for c in range(0, 8, 2):
                col = c * self._square_size
                self.create_rectangle(col, row+self._square_size,
                                      col+self._square_size-1,
                                      row+self._square_size*2-1,
                                      fill=DARK_SQUARES, outline=DARK_SQUARES,
                                      tags='o'+str(((r+1)*8)+c))

    def _label_board(self):
        for key, pair in self._gridpos.iteritems():
            row, col = pair
            xpos, ypos = col * self._square_size, row * self._square_size
            self.create_text(xpos+self._square_size-7, ypos+self._square_size-7,
                             text=str(self._keymap[key]), fill=LIGHT_SQUARES,
                             tag='label')

    def _delete_labels(self):
        self.delete('label')

    def _draw_checkers(self, change):
        if change == None:
            return
        for i in change.remove:
            self.delete('c'+str(i))
        for i in change.add:
            checker = self._model.curr_state.squares[i]
            color = self.dark_color if checker & COLORS == BLACK else self.light_color
            row, col = self._gridpos[i]
            x = col * self._square_size + self._piece_offset
            y = row * self._square_size + self._piece_offset
            tag = 'c'+str(i)
            self.create_oval(x+2, y+2, x+2+CHECKER_SIZE,
                             y+2+CHECKER_SIZE, outline='black',
                             fill='black', tags=(color, tag))
            self.create_oval(x, y, x+CHECKER_SIZE, y+CHECKER_SIZE, outline='black',
                             fill=color, tags=(color, tag))
            if checker & KING:
                self.create_image(x+15, y+15, image=self._crownpic, anchor=CENTER,
                                  tags=(color, tag))
