from Tkinter import *
from globalconst import *
from aboutbox import AboutBox
from setupboard import SetupBoard
from gamemanager import GameManager
from centeredwindow import CenteredWindow

class MainFrame(object, CenteredWindow):
    def __init__(self, master):
        self.root = master
        self.root.title("Raven "+VERSION)
        self.frame = Frame(self.root)
        self.frame.pack(fill=X)
        self.thinkTime = IntVar(value=5)
        self.manager = GameManager(root=self.root, parent=self)
        gameMenu = self.createGameMenu()
        movesMenu = self.createMovesMenu()
        optionsMenu = self.createOptionsMenu()
        helpMenu = self.createHelpMenu()
        self.frame.tk_menuBar(gameMenu, helpMenu)
        CenteredWindow.__init__(self, self.root)
        self.root.minsize(self.root.winfo_reqwidth(), self.root.winfo_reqheight())
        self.root.maxsize(self.root.winfo_reqwidth(), self.root.winfo_reqheight())
        self._bind_events()

    def _bind_events(self):
        # TODO: Move these events to PlayerController?
        self.root.bind('<Home>', self._undo_all_moves)
        self.root.bind('<End>', self._redo_all_moves)
        self.root.bind('<Left>', self._undo_single_move)
        self.root.bind('<Right>', self._redo_single_move)

    def _undo_all_moves(self, *args):
        #self.manager._controller1.stop_process()
        #self.manager._controller2.stop_process()
        self.manager.model.undo_all_moves()
        self.manager._controller1.remove_highlights()
        self.manager._controller2.remove_highlights()
        self.manager.view.update_statusbar()

    def _redo_all_moves(self, *args):
        #self.manager._controller1.stop_process()
        #self.manager._controller2.stop_process()
        self.manager.model.redo_all_moves()
        self.manager._controller1.remove_highlights()
        self.manager._controller2.remove_highlights()
        self.manager.view.update_statusbar()

    def _undo_single_move(self, *args):
        #self.manager._controller1.stop_process()
        #self.manager._controller2.stop_process()
        self.manager.model.undo_move()
        self.manager._controller1.remove_highlights()
        self.manager._controller2.remove_highlights()
        self.manager.view.update_statusbar()

    def _redo_single_move(self, *args):
        #self.manager._controller1.stop_process()
        #self.manager._controller2.stop_process()
        self.manager.model.redo_move()
        self.manager._controller1.remove_highlights()
        self.manager._controller2.remove_highlights()
        self.manager.view.update_statusbar()

    def createGameMenu(self):
        gameBtn = Menubutton(self.frame, text='Game', underline=0)
        gameBtn.pack(side=LEFT)
        gameBtn.menu = Menu(gameBtn, tearoff=0)
        gameBtn.menu.add_command(label='New game', underline=0,
                                 command=self.manager.new_game)
        gameBtn.menu.add_separator()
        gameBtn.menu.add_command(label='Set up board ...', underline=0,
                                 command=self.showSetupBoardDialog)
        gameBtn.menu.add_command(label='Flip board', underline=0,
                                 command=self.flipBoard)
        gameBtn.menu.add_separator()
        gameBtn.menu.add_command(label='Exit', underline=0, command=gameBtn.quit)
        gameBtn['menu'] = gameBtn.menu
        return gameBtn

    def createMovesMenu(self):
        movesBtn = Menubutton(self.frame, text='Moves', underline=0)
        movesBtn.pack(side=LEFT)
        movesBtn.menu = Menu(movesBtn, tearoff=0)
        movesBtn.menu.add_command(label='Undo one move',
                                  command=self._undo_single_move,
                                  accelerator='<-')
        movesBtn.menu.add_command(label='Redo one move',
                                  command=self._redo_single_move,
                                  accelerator='->')
        movesBtn.menu.add_command(label='Undo all moves',
                                  command=self._undo_all_moves,
                                  accelerator='Home')
        movesBtn.menu.add_command(label='Redo all moves',
                                  command=self._redo_all_moves,
                                  accelerator='End')

        movesBtn['menu'] = movesBtn.menu
        return movesBtn

    def createOptionsMenu(self):
        optBtn = Menubutton(self.frame, text='Options', underline=0)
        optBtn.pack(side=LEFT)
        optBtn.menu = Menu(optBtn, tearoff=0)
        thinkMenu = Menu(optBtn.menu, tearoff=0)
        thinkMenu.add_radiobutton(label="1 second", underline=None,
                                  command=self.setThinkTime,
                                  variable=self.thinkTime,
                                  value=1)
        thinkMenu.add_radiobutton(label="2 seconds", underline=None,
                                  command=self.setThinkTime,
                                  variable=self.thinkTime,
                                  value=2)
        thinkMenu.add_radiobutton(label="5 seconds", underline=None,
                                  command=self.setThinkTime,
                                  variable=self.thinkTime,
                                  value=5)
        thinkMenu.add_radiobutton(label="10 seconds", underline=None,
                                  command=self.setThinkTime,
                                  variable=self.thinkTime,
                                  value=10)
        thinkMenu.add_radiobutton(label="30 seconds", underline=None,
                                  command=self.setThinkTime,
                                  variable=self.thinkTime,
                                  value=30)
        thinkMenu.add_radiobutton(label="1 minute", underline=None,
                                  command=self.setThinkTime,
                                  variable=self.thinkTime,
                                  value=60)
        optBtn.menu.add_cascade(label='CPU think time', underline=0,
                                menu=thinkMenu)
        optBtn['menu'] = optBtn.menu
        return optBtn

    def createHelpMenu(self):
        helpBtn = Menubutton(self.frame, text='Help', underline=0)
        helpBtn.pack(side=LEFT)
        helpBtn.menu = Menu(helpBtn, tearoff=0)
        helpBtn.menu.add_command(label='About Raven ...', underline=0,
                                 command=self.showAboutBox)
        helpBtn['menu'] = helpBtn.menu
        return helpBtn

    def showAboutBox(self):
        AboutBox(self)

    def showSetupBoardDialog(self):
        # stop alphabeta thread from making any moves
        self.manager.model.curr_state.ok_to_move = False
        self.manager._controller1.stop_process()
        self.manager._controller2.stop_process()
        SetupBoard(self, self.manager)

    def setThinkTime(self):
        self.manager._controller1.set_search_time(self.thinkTime.get())
        self.manager._controller2.set_search_time(self.thinkTime.get())

    def flipBoard(self):
        if self.manager.model.to_move == BLACK:
            self.manager._controller1.remove_highlights()
        else:
            self.manager._controller2.remove_highlights()
        self.manager.view.flip_board(not self.manager.view.flip_view)
        if self.manager.model.to_move == BLACK:
            self.manager._controller1.add_highlights()
        else:
            self.manager._controller2.add_highlights()

def start():
    root = Tk()
    mainframe = MainFrame(root)
    mainframe.root.update()
    mainframe.root.mainloop()

if __name__=='__main__':
    start()
