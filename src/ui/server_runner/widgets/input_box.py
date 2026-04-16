from gi.repository import Gtk


class CommandInputBox:
    def __init__(self, command_handler):
        self.command_handler = command_handler
        
        # Create container
        self.box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.box.set_margin_top(6)
        self.box.set_vexpand(False)
        
        # Command entry
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("Type a command and press Enter to send...")
        self.entry.connect("activate", self.on_send)
        self.entry.set_hexpand(True)
        self.box.append(self.entry)
        
        # Send button
        self.send_button = Gtk.Button(label="Send")
        self.send_button.add_css_class("suggested-action")
        self.send_button.connect("clicked", self.on_send)
        self.box.append(self.send_button)
    
    def get_widget(self):
        """Return the box widget to add to UI"""
        return self.box
    
    def on_send(self, widget):
        """Send command when button clicked or Enter pressed"""
        command = self.entry.get_text().strip()
        if command:
            self.command_handler.send_command(command)
            self.entry.set_text("")
