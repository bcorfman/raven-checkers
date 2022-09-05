from tkinter import Scrollbar, TclError


class AutoScrollbar(Scrollbar):
    def __init__(self, master=None, cnf={}, **kw):
        self.container = kw.pop('container', None)
        self.row = kw.pop('row', 0)
        self.column = kw.pop('column', 0)
        self.sticky = kw.pop('sticky', '')
        Scrollbar.__init__(self, master, cnf, **kw)

    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call('grid', 'remove', self)
        else:
            if not self.container:
                self.grid()
            else:
                self.grid(in_=self.container, row=self.row,
                          column=self.column, sticky=self.sticky)
        Scrollbar.set(self, lo, hi)

    def pack(self, **kw):
        raise TclError('cannot use pack with this widget')

    def place(self, **kw):
        raise TclError('cannot use place with this widget')
