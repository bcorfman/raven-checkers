from tkinter import Toplevel, StringVar, Message, Tk, Button, N, S, E, W
from time import time, localtime, strftime


class ToolTip(Toplevel):
    """
    Provides a ToolTip widget for Tkinter.
    To apply a ToolTip to any Tkinter widget, simply pass the widget to the
    ToolTip constructor
    """
    def __init__(self, wdgt, msg=None, msg_func=None, delay=1, follow=True):
        """
        Initialize the ToolTip

        Arguments:
          wdgt: The widget this ToolTip is assigned to
          msg:  A static string message assigned to the ToolTip
          msg_func: A function that retrieves a string to use as the ToolTip text
          delay:   The delay in seconds before the ToolTip appears(may be float)
          follow:  If True, the ToolTip follows motion, otherwise hides
        """
        self.wdgt = wdgt
        self.parent = self.wdgt.master   # The parent of the ToolTip is the parent of the ToolTips widget
        Toplevel.__init__(self, self.parent, bg='black', padx=1, pady=1)      # Initialize the Toplevel
        self.withdraw()                                                         # Hide initially
        self.overrideredirect(True)   # The ToolTip Toplevel should have no frame or title bar

        self.msgVar = StringVar()     # The msgVar will contain the text displayed by the ToolTip
        if msg is None:
            self.msgVar.set('No message provided')
        else:
            self.msgVar.set(msg)
        self.msgFunc = msg_func
        self.delay = delay
        self.follow = follow
        self.visible = 0
        self.lastMotion = 0
        Message(self, textvariable=self.msgVar, bg='#FFFFDD',
                aspect=1000).grid()  # The test of the ToolTip is displayed in a Message widget
        # Add bindings to the widget.  This will NOT override bindings that the widget already has
        self.wdgt.bind('<Enter>', self.spawn, '+')
        self.wdgt.bind('<Leave>', self.hide, '+')
        self.wdgt.bind('<Motion>', self.move, '+')

    def spawn(self, event=None):
        """
        Spawn the ToolTip.  This simply makes the ToolTip eligible for display.
        Usually this is caused by entering the widget

        Arguments:
          event: The event that called this function
        """
        self.visible = 1
        self.after(int(self.delay * 1000), self.show)  # The after function takes a time argument in milliseconds

    def show(self):
        """
        Displays the ToolTip if the time delay has been long enough
        """
        if self.visible == 1 and time() - self.lastMotion > self.delay:
            self.visible = 2
        if self.visible == 2:
            self.deiconify()

    def move(self, event):
        """
        Processes motion within the widget.

        Arguments:
          event: The event that called this function
        """
        self.lastMotion = time()
        if not self.follow:   # If the follow flag is not set, motion within the widget will make the ToolTip disappear
            self.withdraw()
            self.visible = 1
        self.geometry('+%i+%i' % (event.x_root+10, event.y_root+10))   # Offset the ToolTip 10x10 pixels southwest
        try:
            # Try to call the message function.  Will not change the message if the message
            # function is None or the message function fails
            self.msgVar.set(self.msgFunc())
        except TypeError:
            pass
        self.after(int(self.delay * 1000), self.show)

    def hide(self, event=None):
        """
        Hides the ToolTip.  Usually this is caused by leaving the widget

        Arguments:
          event: The event that called this function
        """
        self.visible = 0
        self.withdraw()


def xrange2d(n, m):
    """
    Returns a generator of values in a 2d range

    Arguments:
      n: The number of rows in the 2d range
      m: The number of columns in the 2d range
    Returns:
      A generator of values in a 2d range
    """
    return ((i, j) for i in range(n) for j in range(m))


def range2d(n, m):
    """
    Returns a list of values in a 2d range

    Arguments:
      n: The number of rows in the 2d range
      m: The number of columns in the 2d range
    Returns:
      A list of values in a 2d range
    """
    return [(i, j) for i in range(n) for j in range(m)]


def print_time():
    """
    Prints the current time in the following fmt:
    HH:MM:SS.00
    """
    t = time()
    time_string = 'time='
    time_string += strftime('%H:%M:', localtime(t))
    time_string += '%.2f' % (t % 60, )
    return time_string


def main():
    root = Tk()
    btn_list = []
    for (i, j) in range2d(6, 4):
        text = 'delay=%i\n' % i
        delay = i
        if j >= 2:
            follow = True
            text += '+follow\n'
        else:
            follow = False
            text += '-follow\n'
        if j % 2 == 0:
            msg = None
            msg_func = print_time
            text += 'Message Function'
        else:
            msg = 'Button at %s' % str((i, j))
            msg_func = None
            text += 'Static Message'
        btn_list.append(Button(root, text=text))
        ToolTip(btn_list[-1], msg=msg, msg_func=msg_func, follow=follow, delay=delay)
        btn_list[-1].grid(row=i, column=j, sticky=N+S+E+W)
    root.mainloop()


if __name__ == '__main__':
    main()
