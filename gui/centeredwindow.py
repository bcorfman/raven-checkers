import os


class CenteredWindow:
    def __init__(self, root):
        self.root = root
        self.root.after_idle(self.center_on_screen)

    def center_on_screen(self):
        self.root.update_idletasks()

        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()

        # Wayland: avoid virtual-desktop centering (causes straddling).
        # Let the compositor choose a single monitor by NOT setting +x+y.
        if os.environ.get("WAYLAND_DISPLAY"):
            # Keep size if you want; omit positioning.
            self.root.geometry(f"{w}x{h}")

            # Nudge some WMs to re-place it cleanly
            self.root.withdraw()
            self.root.update_idletasks()
            self.root.deiconify()
            return

        # X11 / Windows / macOS: traditional centering
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")
