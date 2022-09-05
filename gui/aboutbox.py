from tkinter import Canvas, Button, TOP, BOTTOM, BOTH
from tkinter.simpledialog import Dialog
from util.globalconst import VERSION


class AboutBox(Dialog):
    def __init__(self, parent):
        Dialog.__init__(self, parent)
        self.canvas = None
        self.button = None
        self.blank = None

    def body(self, master):
        self.canvas = Canvas(self, width=300, height=275)
        self.canvas.pack(side=TOP, fill=BOTH, expand=0)
        self.canvas.create_text(152, 47, text='Raven', fill='black',
                                font=('Helvetica', 36))
        self.canvas.create_text(150, 45, text='Raven', fill='white',
                                font=('Helvetica', 36))
        self.canvas.create_text(150, 85, text='Version ' + VERSION,
                                fill='black',
                                font=('Helvetica', 12))
        self.canvas.create_text(150, 115, text='An open source checkers program',
                                fill='black',
                                font=('Helvetica', 10))
        self.canvas.create_text(150, 130, text='by Brandon Corfman',
                                fill='black',
                                font=('Helvetica', 10))
        self.canvas.create_text(150, 160, text='Evaluation function translated from',
                                fill='black',
                                font=('Helvetica', 10))
        self.canvas.create_text(150, 175, text="Martin Fierz's Simple Checkers",
                                fill='black',
                                font=('Helvetica', 10))
        self.canvas.create_text(150, 205, text="Alpha-beta search code written by",
                                fill='black',
                                font=('Helvetica', 10))
        self.canvas.create_text(150, 220, text="Peter Norvig for the AIMA project;",
                                fill='black',
                                font=('Helvetica', 10))
        self.canvas.create_text(150, 235, text="adopted for checkers usage",
                                fill='black',
                                font=('Helvetica', 10))
        self.canvas.create_text(150, 250, text="by Brandon Corfman",
                                fill='black',
                                font=('Helvetica', 10))
        return self.canvas

    def cancel(self, event=None):
        self.destroy()

    def buttonbox(self):
        self.button = Button(self, text='OK', padx='5m', command=self.cancel)
        self.blank = Canvas(self, width=10, height=20)
        self.blank.pack(side=BOTTOM, fill=BOTH, expand=0)
        self.button.pack(side=BOTTOM)
        self.button.focus_set()
        self.bind("<Escape>", self.cancel)
