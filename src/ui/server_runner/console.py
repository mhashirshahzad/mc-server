from gi.repository import GLib


class ConsoleHandler:
    def __init__(self, window):
        self.window = window
    
    def append(self, text):
        """Append text to console"""
        self.window.console_view.append(text)
    
    def clear(self):
        """Clear console"""
        self.window.console_view.clear()
