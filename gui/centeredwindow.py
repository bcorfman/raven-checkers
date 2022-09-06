class CenteredWindow:
    def __init__(self, root):
        self.root = root
        self.root.after_idle(self.center_on_screen)
        self.root.update()

    def center_on_screen(self):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        new_geometry = "+%d+%d" % ((sw-w)/2, (sh-h)/2)
        self.root.geometry(newGeometry=new_geometry)
