import os
from tkinter import PhotoImage, Canvas, Frame, Text, Button, IntVar, Widget
from tkinter.constants import END, W, INSERT, CENTER
from tkinter.filedialog import askopenfilename
from tkinter.font import Font
from base.command import Command
from base.observer import Observer
from util.globalconst import NUMBERS_IMAGE, BULLET_IMAGE, BULLETS_IMAGE, DEFAULT_SIZE, LIGHT_SQUARES, DARK_SQUARES, \
    LIGHT_CHECKERS, DARK_CHECKERS, CROWN_IMAGE, REDO_IMAGE, REDO_ALL_IMAGE, UNDO_IMAGE, UNDO_ALL_IMAGE, \
    REMLINK_IMAGE, ADDLINK_IMAGE, ITALIC_IMAGE, BOLD_IMAGE, BLACK, WHITE, CUR_DIR, FREE, FIRST, LAST, \
    COLORS, CHECKER_SIZE, KING
from util.globalconst import create_grid_map, create_position_map, get_preferences_from_file, parse_index, to_string, \
    keymap, reverse_dict
from gui.autoscrollbar import AutoScrollbar
from parsing.textserialize import Serializer
from gui.hyperlinkmgr import HyperlinkManager
from gui.tooltip import ToolTip


class BoardView(Observer):
    def __init__(self, root, **props):
        self._statusbar = props['statusbar']
        self.root = root
        self._model = props['model']
        self._model.curr_state.attach(self)
        self._gameMgr = props['parent']
        self._board_side = props.get('side') or DEFAULT_SIZE
        self.light_squares = props.get('lightsquares') or LIGHT_SQUARES
        self.dark_squares = props.get('darksquares') or DARK_SQUARES
        self.light_color = props.get('lightcheckers') or LIGHT_CHECKERS
        self.dark_color = props.get('darkcheckers') or DARK_CHECKERS
        self._square_size = self._board_side / 8
        self._piece_offset = self._square_size / 5
        self._crown_pic = PhotoImage(file=CROWN_IMAGE)
        self._board_pos = create_position_map()
        self._grid_pos = create_grid_map()
        self._b_font = None
        self._i_font = None

        self.canvas = Canvas(root, width=self._board_side,
                             height=self._board_side, borderwidth=0,
                             highlightthickness=0)
        right_panel = Frame(root, borderwidth=1, relief='sunken')

        self.toolbar = Frame(root)
        font, size = get_preferences_from_file()
        self.scrollbar = AutoScrollbar(root, container=right_panel,
                                       row=1, column=1, sticky='ns')
        self.txt = Text(root, width=40, height=1, borderwidth=0,
                        font=(font, size), wrap='word',
                        yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.txt.yview)
        self.canvas.pack(side='left', fill='both', expand=False)
        self.toolbar.grid(in_=right_panel, row=0, column=0, sticky='ew')
        right_panel.pack(side='right', fill='both', expand=True)
        self.txt.grid(in_=right_panel, row=1, column=0, sticky='nsew')
        right_panel.grid_rowconfigure(1, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        self.redo_all_image = PhotoImage(file=REDO_ALL_IMAGE)
        self.redo_image = PhotoImage(file=REDO_IMAGE)
        self.undo_all_image = PhotoImage(file=UNDO_ALL_IMAGE)
        self.undo_image = PhotoImage(file=UNDO_IMAGE)
        self.numbers_image = PhotoImage(file=NUMBERS_IMAGE)
        self.bullet_image = PhotoImage(file=BULLET_IMAGE)
        self.bullets_image = PhotoImage(file=BULLETS_IMAGE)
        self.remove_link_image = PhotoImage(file=REMLINK_IMAGE)
        self.add_link_image = PhotoImage(file=ADDLINK_IMAGE)
        self.italic_image = PhotoImage(file=ITALIC_IMAGE)
        self.bold_image = PhotoImage(file=BOLD_IMAGE)
        self.bold = Button(name='bold', image=self.bold_image,
                           borderwidth=1, command=self._on_bold)
        self.bold.grid(in_=self.toolbar, row=0, column=0, sticky=W)
        self.italic = Button(name='italic', image=self.italic_image,
                             borderwidth=1, command=self._on_italic)
        self.italic.grid(in_=self.toolbar, row=0, column=1, sticky=W)
        self.bullets = Button(name='bullets', image=self.bullets_image,
                              borderwidth=1, command=self._on_bullets)
        self.bullets.grid(in_=self.toolbar, row=0, column=2, sticky=W)
        self.numbers = Button(name='numbers', image=self.numbers_image,
                              borderwidth=1, command=self._on_numbers)
        self.numbers.grid(in_=self.toolbar, row=0, column=3, sticky=W)
        self.addLink = Button(name='addlink', image=self.add_link_image,
                              borderwidth=1, command=self._on_add_link)
        self.addLink.grid(in_=self.toolbar, row=0, column=4, sticky=W)
        self.remLink = Button(name='remlink', image=self.remove_link_image,
                              borderwidth=1, command=self._on_remove_link)
        self.remLink.grid(in_=self.toolbar, row=0, column=5, sticky=W)
        self.frame = Frame(width=0)
        self.frame.grid(in_=self.toolbar, padx=5, row=0, column=6, sticky=W)
        self.undo_all = Button(name='undo_all', image=self.undo_all_image,
                               borderwidth=1, command=self._on_undo_all)
        self.undo_all.grid(in_=self.toolbar, row=0, column=7, sticky=W)
        self.undo = Button(name='undo', image=self.undo_image,
                           borderwidth=1, command=self._on_undo)
        self.undo.grid(in_=self.toolbar, row=0, column=8, sticky=W)
        self.redo = Button(name='redo', image=self.redo_image,
                           borderwidth=1, command=self._on_redo)
        self.redo.grid(in_=self.toolbar, row=0, column=9, sticky=W)
        self.redo_all = Button(name='redo_all', image=self.redo_all_image,
                               borderwidth=1, command=self._on_redo_all)
        self.redo_all.grid(in_=self.toolbar, row=0, column=10, sticky=W)
        self.bold_tooltip = ToolTip(self.bold, 'Bold')
        self.italic_tooltip = ToolTip(self.italic, 'Italic')
        self.bullets_tooltip = ToolTip(self.bullets, 'Bullet list')
        self.numbers_tooltip = ToolTip(self.numbers, 'Numbered list')
        self.add_link_tooltip = ToolTip(self.addLink, 'Add hyperlink')
        self.remove_link_tooltip = ToolTip(self.remLink, 'Remove hyperlink')
        self.undo_all_tooltip = ToolTip(self.undo_all, 'First move')
        self.undo_tooltip = ToolTip(self.undo, 'Back one move')
        self.redo_tooltip = ToolTip(self.redo, 'Forward one move')
        self.redo_all_tooltip = ToolTip(self.redo_all, 'Last move')
        self.init_font_sizes(font, size)
        self.init_tags()
        self._register_event_handlers()
        self.button_set = {self.bold, self.italic, self.addLink, self.remLink}
        self.button_map = {'bold': self.bold, 'italic': self.italic,
                           'bullet': self.bullets, 'number': self.numbers,
                           'hyper': self.addLink}
        self.link_manager = HyperlinkManager(self.txt, self._gameMgr.load_game)
        self.serializer = Serializer(self.txt, self.link_manager)
        self.curr_annotation = ''
        self._setup_board(root)
        starting_squares = [i for i in self._model.curr_state.valid_squares
                            if self._model.curr_state.squares[i] &
                            (BLACK | WHITE)]
        self._draw_checkers(Command(add=starting_squares))
        self.flip_view = False  # black on bottom
        self._label_board()
        self.update_statusbar()

    def _toggle_state(self, tags, btn):
        # toggle the text state based on the first character in the
        # selected range.
        if self.txt.tag_ranges('sel'):
            current_tags = self.txt.tag_names('sel.first')
        elif self.txt.tag_ranges('insert'):
            current_tags = self.txt.tag_names('insert')
        else:
            return
        for tag in tags:
            already_tagged = any((x for x in current_tags if
                                  x.startswith(tag)))
            for t in current_tags:
                if t != 'sel':
                    self.txt.tag_remove(t, 'sel.first', 'sel.last')
            if not already_tagged:
                self.txt.tag_add(tag, 'sel.first', 'sel.last')
                btn.configure(relief='sunken')
                other_btns = self.button_set.difference([btn])
                for b in other_btns:
                    b.configure(relief='raised')
            else:
                btn.configure(relief='raised')

    def _on_bold(self):
        self.bold_tooltip.hide()
        self._toggle_state(['bold'], self.bold)

    def _on_italic(self):
        self.italic_tooltip.hide()
        self._toggle_state(['italic'], self.italic)

    def _on_bullets(self):
        self._process_button_click('bullet', self.bullets_tooltip,
                                   self._add_bullets_if_needed,
                                   self._remove_bullets_if_needed)

    def _on_numbers(self):
        self._process_button_click('number', self.numbers_tooltip,
                                   self._add_numbers_if_needed,
                                   self._remove_numbers_if_needed)

    def _process_button_click(self, tag, tooltip, add_func, remove_func):
        tooltip.hide()
        if self.txt.tag_ranges('sel'):
            startline, _ = parse_index(self.txt.index('sel.first'))
            endline, _ = parse_index(self.txt.index('sel.last'))
        else:
            startline, _ = parse_index(self.txt.index(INSERT))
            endline = startline
        current_tags = self.txt.tag_names('%d.0' % startline)
        if tag not in current_tags:
            add_func(startline, endline)
        else:
            remove_func(startline, endline)

    def _add_bullets_if_needed(self, startline, endline):
        self._remove_numbers_if_needed(startline, endline)
        for line in range(startline, endline+1):
            current_tags = self.txt.tag_names('%d.0' % line)
            if 'bullet' not in current_tags:
                start = '%d.0' % line
                end = '%d.end' % line
                self.txt.insert(start, '\t')
                self.txt.image_create(start, image=self.bullet_image)
                self.txt.insert(start, '\t')
                self.txt.tag_add('bullet', start, end)
        self.bullets.configure(relief='sunken')
        self.numbers.configure(relief='raised')

    def _remove_bullets_if_needed(self, startline, endline):
        for line in range(startline, endline+1):
            current_tags = self.txt.tag_names('%d.0' % line)
            if 'bullet' in current_tags:
                start = '%d.0' % line
                end = '%d.end' % line
                self.txt.tag_remove('bullet', start, end)
                start = '%d.0' % line
                end = '%d.3' % line
                self.txt.delete(start, end)
        self.bullets.configure(relief='raised')

    def _add_numbers_if_needed(self, startline, endline):
        self._remove_bullets_if_needed(startline, endline)
        num = 1
        for line in range(startline, endline+1):
            current_tags = self.txt.tag_names('%d.0' % line)
            if 'number' not in current_tags:
                start = '%d.0' % line
                end = '%d.end' % line
                self.txt.insert(start, '\t')
                numstr = '%d.' % num
                self.txt.insert(start, numstr)
                self.txt.insert(start, '\t')
                self.txt.tag_add('number', start, end)
                num += 1
        self.numbers.configure(relief='sunken')
        self.bullets.configure(relief='raised')

    def _remove_numbers_if_needed(self, startline, endline):
        cnt = IntVar()
        for line in range(startline, endline+1):
            current_tags = self.txt.tag_names('%d.0' % line)
            if 'number' in current_tags:
                start = '%d.0' % line
                end = '%d.end' % line
                self.txt.tag_remove('number', start, end)
                # Regex to match a tab, followed by any number of digits,
                # followed by a period, all at the start of a line.
                # The cnt variable stores the number of characters matched.
                pos = self.txt.search(r'^\t\d+\.\t', start, end, None, None,
                                      None, True, None, cnt)
                if pos:
                    end = '%d.%d' % (line, cnt.get())
                    self.txt.delete(start, end)
        self.numbers.configure(relief='raised')

    def _on_undo(self):
        self.undo_tooltip.hide()
        self._gameMgr.parent.undo_single_move()

    def _on_undo_all(self):
        self.undo_all_tooltip.hide()
        self._gameMgr.parent.undo_all_moves()

    def _on_redo(self):
        self.redo_tooltip.hide()
        self._gameMgr.parent.redo_single_move()

    def _on_redo_all(self):
        self.redo_all_tooltip.hide()
        self._gameMgr.parent.redo_all_moves()

    def _on_add_link(self):
        filename = askopenfilename(initialdir='training')
        if filename:
            filename = os.path.relpath(filename, CUR_DIR)
            self._toggle_state(self.link_manager.add(filename), self.addLink)

    def _on_remove_link(self):
        if self.txt.tag_ranges('sel'):
            current_tags = self.txt.tag_names('sel.first')
            if 'hyper' in current_tags:
                self._toggle_state(['hyper'], self.addLink)

    def _register_event_handlers(self):
        self.txt.event_add('<<KeyRel>>', '<KeyRelease-Home>', '<KeyRelease-End>',
                           '<KeyRelease-Left>', '<KeyRelease-Right>',
                           '<KeyRelease-Up>', '<KeyRelease-Down>',
                           '<KeyRelease-Delete>', '<KeyRelease-BackSpace>')
        Widget.bind(self.txt, '<<Selection>>', self._sel_changed)
        Widget.bind(self.txt, '<ButtonRelease-1>', self._sel_changed)
        Widget.bind(self.txt, '<<KeyRel>>', self._key_release)

    def _key_release(self, _):
        line, char = parse_index(self.txt.index(INSERT))
        self.update_button_state(to_string(line, char))

    def _sel_changed(self, _):
        self.update_button_state(self.txt.index(INSERT))

    def is_dirty(self):
        return self.curr_annotation != self.get_annotation()

    def reset_toolbar_buttons(self):
        for btn in self.button_set:
            btn.configure(relief='raised')

    def update_button_state(self, index):
        if self.txt.tag_ranges('sel'):
            current_tags = self.txt.tag_names('sel.first')
        else:
            current_tags = self.txt.tag_names(index)
        for btn in self.button_map.values():
            btn.configure(relief='raised')
        for tag in current_tags:
            if tag in self.button_map.keys():
                self.button_map[tag].configure(relief='sunken')

    def init_font_sizes(self, font, size):
        self.txt.config(font=[font, size])
        self._b_font = Font(self.root, (font, size, 'bold'))
        self._i_font = Font(self.root, (font, size, 'italic'))

    def init_tags(self):
        self.txt.tag_config('bold', font=self._b_font, wrap='word')
        self.txt.tag_config('italic', font=self._i_font, wrap='word')
        self.txt.tag_config('number', tabs='.5c center 1c left',
                            lmargin1='0', lmargin2='1c')
        self.txt.tag_config('bullet', tabs='.5c center 1c left',
                            lmargin1='0', lmargin2='1c')

    def reset_view(self, model):
        self._model = model
        self.txt.delete('1.0', END)
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
        return self._board_pos.get(xi + yi * 8, 0)

    def calc_grid_pos(self, pos):
        return self._grid_pos[pos]

    def highlight_square(self, idx, color):
        row, col = self._grid_pos[idx]
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
        self.serializer.restore(move.annotation)
        self.curr_annotation = move.annotation
        if self.txt.get('1.0', 'end').strip() == '':
            start = keymap[move.affected_squares[FIRST][0]]
            dest = keymap[move.affected_squares[LAST][0]]
            move_str = '%d-%d' % (start, dest)
            self.txt.insert('1.0', move_str)

    def get_annotation(self):
        return self.serializer.dump()

    def erase_checker(self, index):
        self.canvas.delete('c'+str(index))

    def flip_board(self, flip):
        self._delete_labels()
        self.canvas.delete(self.dark_color)
        self.canvas.delete(self.light_color)
        if self.flip_view != flip:
            self.flip_view = flip
            self._grid_pos = reverse_dict(self._grid_pos)
            self._board_pos = reverse_dict(self._board_pos)
        self._label_board()
        starting_squares = [i for i in self._model.curr_state.valid_squares
                            if self._model.curr_state.squares[i] &
                            (BLACK | WHITE)]
        all_checkers = Command(add=starting_squares)
        self._draw_checkers(all_checkers)

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

    def get_positions(self, square_type):
        return map(str, sorted((keymap[i]
                                for i in self._model.curr_state.valid_squares
                                if self._model.curr_state.squares[i] == square_type)))

    # private functions
    def _setup_board(self, _):
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
        for key, pair in self._grid_pos.items():
            row, col = pair
            xpos, ypos = col * self._square_size, row * self._square_size
            self.canvas.create_text(xpos+self._square_size-7,
                                    ypos+self._square_size-7,
                                    text=str(keymap[key]),
                                    fill=LIGHT_SQUARES, tag='label')

    def _delete_labels(self):
        self.canvas.delete('label')

    def _draw_checkers(self, change):
        if change is None:
            return
        for i in change.remove:
            self.canvas.delete('c'+str(i))
        for i in change.add:
            checker = self._model.curr_state.squares[i]
            color = self.dark_color if checker & COLORS == BLACK else self.light_color
            row, col = self._grid_pos[i]
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
                self.canvas.create_image(x + 15, y + 15, image=self._crown_pic,
                                         anchor=CENTER, tags=(color, tag))
