from tkinter import Frame, Listbox, Variable, SINGLE, TOP
from tkinter.simpledialog import Dialog
from gui.autoscrollbar import AutoScrollbar


class FileList(Dialog):
    def __init__(self, parent, game_titles):
        self._master = parent
        self.filelist = None
        self.scrollbar = None
        self.ok_button = None
        self.blank = None
        self.result = False
        self._titles = tuple(item.name for item in game_titles)
        super().__init__(self._master, "Select game title")

    def body(self, master):
        var = Variable(value=self._titles)
        panel = Frame(self, borderwidth=1, relief='sunken')
        self.scrollbar = AutoScrollbar(self, container=panel,
                                       row=1, column=1, sticky='ns')
        self.filelist = Listbox(self, width=60, height=20, listvariable=var, yscrollcommand=self.scrollbar.set)
        self.filelist.pack(side=TOP)
        self.scrollbar.config(command=self.filelist.yview)
        panel.pack(side='top', fill='both', expand=True)
        self.filelist.grid(in_=panel, row=1, column=0, sticky='nsew')
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

    def apply(self):
        self.result = True

    def cancel(self, _=None):
        if self._master is not None:
            self._master.focus_set()
        self.destroy()

