from gi.repository import Adw, Gio
from window import GrassyWindow

class GrassyApp(Adw.Application):
    def __init__(self):
        super().__init__(
            application_id="org.bongo.grassy",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )
    
    def do_activate(self):
        window = GrassyWindow(application=self)
        window.present()
