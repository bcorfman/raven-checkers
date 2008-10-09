from Tkinter import *
import centeredwindow as cw
from globalconst import *

class AboutBox(Toplevel, cw.CenteredWindow):
    def __init__(self, master):
        self.frame = Toplevel(master.root)
        self.frame.transient(master.root)
        self.frame.grab_set()
        self.frame.title("About Raven")
        self.canvas = Canvas(self.frame, width=300, height=275)
        self.canvas.pack(side=TOP, fill=BOTH, expand=0)
        self.canvas.create_text(152,47,text='Raven', fill='black',
                                font=('Helvetica', 36))
        self.canvas.create_text(150,45,text='Raven', fill='white',
                                font=('Helvetica', 36))
        self.canvas.create_text(150,85,text='Version '+ VERSION,
                                fill='black',
                                font=('Helvetica', 12))
        self.canvas.create_text(150,115,text='An open source checkers program',
                                fill='black',
                                font=('Helvetica', 10))
        self.canvas.create_text(150,130,text='by Brandon Corfman',
                                fill='black',
                                font=('Helvetica', 10))
        self.canvas.create_text(150,160,text='Evaluation function translated from',
                                fill='black',
                                font=('Helvetica', 10))
        self.canvas.create_text(150,175,text="Martin Fierz's Simple Checkers",
                                fill='black',
                                font=('Helvetica', 10))
        self.canvas.create_text(150,205,text="Alpha-beta search code written by",
                                fill='black',
                                font=('Helvetica', 10))
        self.canvas.create_text(150,220,text="Peter Norvig for the AIMA project;",
                                fill='black',
                                font=('Helvetica', 10))
        self.canvas.create_text(150,235,text="adopted for checkers usage",
                                fill='black',
                                font=('Helvetica', 10))
        self.canvas.create_text(150,250,text="by Brandon Corfman",
                                fill='black',
                                font=('Helvetica', 10))

        self.button = Button(self.frame, text='OK', padx='5m', command=self.frame.destroy)
        self.blank = Canvas(self.frame, width=10, height=20)
        self.blank.pack(side=BOTTOM, fill=BOTH, expand=0)
        self.button.pack(side=BOTTOM)
        cw.CenteredWindow.__init__(self, self.frame)
        self.button.focus_set()
