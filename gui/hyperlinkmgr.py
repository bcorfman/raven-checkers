from tkinter import CURRENT


class HyperlinkManager(object):
    def __init__(self, text_widget, link_func):
        self.txt = text_widget
        self.link_func = link_func
        self.txt.tag_config('hyper', foreground='blue', underline=1)
        self.txt.tag_bind('hyper', '<Enter>', self._enter)
        self.txt.tag_bind('hyper', '<Leave>', self._leave)
        self.txt.tag_bind('hyper', '<Button-1>', self._click)
        self.filenames = {}

    def reset(self):
        self.filenames = {}

    def add(self, filename):
        # Add a link with associated filename. The link function returns tags
        # to use in the associated text widget.
        tag = 'hyper-%d' % len(self.filenames)
        self.filenames[tag] = filename
        return 'hyper', tag

    def _enter(self, event):
        self.txt.config(cursor='hand2')

    def _leave(self, event):
        self.txt.config(cursor='')

    def _click(self, event):
        for tag in self.txt.tag_names(CURRENT):
            if tag.startswith('hyper-'):
                self.link_func(self.filenames[tag])
                return
