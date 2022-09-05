import os
from tkinter import IntVar, Menu, Tk
import tkinter as tk
from tkinter.messagebox import askyesnocancel
from multiprocessing import freeze_support
from util.globalconst import RAVEN_ICON, VERSION, TITLE, BLACK, get_preferences_from_file, write_preferences_to_file
from gui.aboutbox import AboutBox
from gui.setupboard import SetupBoard
from game.gamemanager import GameManager
from gui.centeredwindow import CenteredWindow
from gui.prefdlg import PreferencesDialog


class MainFrame(CenteredWindow):
    def __init__(self, master):
        self.root = master
        self.root.withdraw()
        self.root.iconbitmap(RAVEN_ICON)
        self.root.title('Raven ' + VERSION)
        self.root.protocol('WM_DELETE_WINDOW', self._on_close)
        self.thinkTime = IntVar(value=5)
        self.manager = GameManager(root=self.root, parent=self)
        self.menu_bar = tk.Menu(self.root)
        self.create_game_menu()
        self.create_options_menu()
        self.create_help_menu()
        self.root.config(menu=self.menu_bar)
        CenteredWindow.__init__(self, self.root)
        self.root.deiconify()

    def _on_close(self):
        if self.manager.view.is_dirty():
            msg = 'Do you want to save your changes before exiting?'
            result = askyesnocancel(TITLE, msg)
            if result is True:
                self.manager.save_game()
            elif result is None:
                return
        self.root.destroy()

    def set_title_bar_filename(self, filename=None):
        if not filename:
            self.root.title(TITLE)
        else:
            self.root.title(TITLE + ' - ' + os.path.basename(filename))

    def undo_all_moves(self, *args):
        self.stop_processes()
        self.manager.model.undo_all_moves(None,
                                          self.manager.view.get_annotation())
        self.manager.controller1.remove_highlights()
        self.manager.controller2.remove_highlights()
        self.manager.view.update_statusbar()

    def redo_all_moves(self, *args):
        self.stop_processes()
        self.manager.model.redo_all_moves(None,
                                          self.manager.view.get_annotation())
        self.manager.controller1.remove_highlights()
        self.manager.controller2.remove_highlights()
        self.manager.view.update_statusbar()

    def undo_single_move(self, *args):
        self.stop_processes()
        self.manager.model.undo_move(None, None, True, True,
                                     self.manager.view.get_annotation())
        self.manager.controller1.remove_highlights()
        self.manager.controller2.remove_highlights()
        self.manager.view.update_statusbar()

    def redo_single_move(self, *args):
        self.stop_processes()
        annotation = self.manager.view.get_annotation()
        self.manager.model.redo_move(None, None, annotation)
        self.manager.controller1.remove_highlights()
        self.manager.controller2.remove_highlights()
        self.manager.view.update_statusbar()

    def create_game_menu(self):
        game = Menu(self.menu_bar, tearoff=0)
        game.add_command(label='New game', underline=0,
                         command=self.manager.new_game)
        game.add_command(label='Open game ...', underline=0,
                         command=self.manager.open_game)
        game.add_separator()
        game.add_command(label='Save game', underline=0,
                         command=self.manager.save_game)
        game.add_command(label='Save game As ...', underline=10,
                         command=self.manager.save_game_as)
        game.add_separator()
        game.add_command(label='Set up Board ...', underline=7,
                         command=self.show_setup_board_dialog)
        game.add_command(label='Flip board', underline=0,
                         command=self.flip_board)
        game.add_separator()
        game.add_command(label='Exit', underline=0,
                         command=self._on_close)
        self.menu_bar.add_cascade(label='Game', menu=game)

    def create_options_menu(self):
        options = Menu(self.menu_bar, tearoff=0)
        think = Menu(options, tearoff=0)
        think.add_radiobutton(label="1 second", underline=None,
                              command=self.set_think_time,
                              variable=self.thinkTime,
                              value=1)
        think.add_radiobutton(label="2 seconds", underline=None,
                              command=self.set_think_time,
                              variable=self.thinkTime,
                              value=2)
        think.add_radiobutton(label="5 seconds", underline=None,
                              command=self.set_think_time,
                              variable=self.thinkTime,
                              value=5)
        think.add_radiobutton(label="10 seconds", underline=None,
                              command=self.set_think_time,
                              variable=self.thinkTime,
                              value=10)
        think.add_radiobutton(label="30 seconds", underline=None,
                              command=self.set_think_time,
                              variable=self.thinkTime,
                              value=30)
        think.add_radiobutton(label="1 minute", underline=None,
                              command=self.set_think_time,
                              variable=self.thinkTime,
                              value=60)
        options.add_cascade(label='CPU think time', underline=0,
                            menu=think)
        options.add_separator()
        options.add_command(label='Preferences ...', underline=0,
                            command=self.show_preferences_dialog)
        self.menu_bar.add_cascade(label='Options', menu=options)

    def create_help_menu(self):
        help_menu = Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label='About Raven ...', underline=0,
                              command=self.show_about_box)
        self.menu_bar.add_cascade(label='Help', menu=help_menu)

    def stop_processes(self):
        # stop any controller processes from making moves
        self.manager.model.curr_state.ok_to_move = False
        self.manager.controller1.stop_process()
        self.manager.controller2.stop_process()

    def show_about_box(self):
        AboutBox(self.root, 'About Raven')

    def show_setup_board_dialog(self):
        self.stop_processes()
        _ = SetupBoard(self.root, 'Set up board', self.manager)
        self.manager.set_controllers()
        self.root.focus_set()
        self.manager.turn_finished()

    def show_preferences_dialog(self):
        font, size = get_preferences_from_file()
        dlg = PreferencesDialog(self.root, 'Preferences', font, size)
        if dlg.result:
            self.manager.view.init_font_sizes(dlg.font, dlg.size)
            self.manager.view.init_tags()
            write_preferences_to_file(dlg.font, dlg.size)

    def set_think_time(self):
        self.manager.controller1.set_search_time(self.thinkTime.get())
        self.manager.controller2.set_search_time(self.thinkTime.get())

    def flip_board(self):
        if self.manager.model.to_move == BLACK:
            self.manager.controller1.remove_highlights()
        else:
            self.manager.controller2.remove_highlights()
        self.manager.view.flip_board(not self.manager.view.flip_view)
        if self.manager.model.to_move == BLACK:
            self.manager.controller1.add_highlights()
        else:
            self.manager.controller2.add_highlights()


def start():
    root = Tk()
    mainframe = MainFrame(root)
    mainframe.root.update()
    mainframe.root.mainloop()


if __name__ == '__main__':
    freeze_support()
    start()
