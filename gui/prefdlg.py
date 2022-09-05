from tkinter import Frame, LabelFrame, LEFT, RIGHT, X
from tkinter.ttk import Combobox, Label
from tkinter.font import families
from tkinter.simpledialog import Dialog


class PreferencesDialog(Dialog):
    def __init__(self, parent, title, font, size):
        self._master = parent
        self.result = False
        self.font = font
        self.size = size
        Dialog.__init__(self, parent, title)

    def body(self, master):
        self._npFrame = LabelFrame(master, text='Annotation window text')
        self._npFrame.pack(fill=X)
        self._fontFrame = Frame(self._npFrame, borderwidth=0)
        self._fontLabel = Label(self._fontFrame, text='Font:', width=5)
        self._fontLabel.pack(side=LEFT, padx=3)
        self._fontCombo = Combobox(self._fontFrame, values=sorted(families()),
                                   state='readonly')
        self._fontCombo.pack(side=RIGHT, fill=X)
        self._sizeFrame = Frame(self._npFrame, borderwidth=0)
        self._sizeLabel = Label(self._sizeFrame, text='Size:', width=5)
        self._sizeLabel.pack(side=LEFT, padx=3)
        self._sizeCombo = Combobox(self._sizeFrame, values=range(8, 15),
                                   state='readonly')
        self._sizeCombo.pack(side=RIGHT, fill=X)
        self._fontFrame.pack()
        self._sizeFrame.pack()
        self._npFrame.pack(fill=X)
        self._fontCombo.set(self.font)
        self._sizeCombo.set(self.size)

    def apply(self):
        self.font = self._fontCombo.get()
        self.size = self._sizeCombo.get()
        self.result = True

    def cancel(self, event=None):
        if self.parent is not None:
            self.parent.focus_set()
        self.destroy()
