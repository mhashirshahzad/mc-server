from gi.repository import Gtk


class ConsoleView:
    def __init__(self):
        self.buffer = Gtk.TextBuffer()
        self.view = Gtk.TextView.new_with_buffer(self.buffer)
        self.view.set_editable(False)
        self.view.set_monospace(True)
        self.view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        
        # Scrollable container
        self.scrolled = Gtk.ScrolledWindow()
        self.scrolled.set_vexpand(True)
        self.scrolled.set_hexpand(True)
        self.scrolled.set_child(self.view)
        
        # Connect to the view's vadjustment to auto-scroll
        self.vadjustment = self.scrolled.get_vadjustment()
    
    def get_widget(self):
        """Return the scrollable widget to add to UI"""
        return self.scrolled
    
    def append(self, text):
        """Append text to console and auto-scroll to bottom"""
        end_iter = self.buffer.get_end_iter()
        self.buffer.insert(end_iter, text)
        # Auto-scroll to bottom
        self.vadjustment.set_value(self.vadjustment.get_upper() - self.vadjustment.get_page_size())
    
    def clear(self):
        """Clear console"""
        start_iter = self.buffer.get_start_iter()
        end_iter = self.buffer.get_end_iter()
        self.buffer.delete(start_iter, end_iter)
