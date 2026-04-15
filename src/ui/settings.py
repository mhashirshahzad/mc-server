from gi.repository import Adw, Gtk
import os

class SettingsDialog(Adw.PreferencesWindow):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        
        self.parent = parent
        self.set_title("Settings")
        self.set_default_size(600, 400)
        self.set_transient_for(parent)
        self.set_modal(True)
        
        # Create preferences page
        preferences_page = Adw.PreferencesPage()
        preferences_group = Adw.PreferencesGroup(title="Server Settings")
        preferences_page.add(preferences_group)
        
        # Server directory setting
        self.server_dir_row = Adw.EntryRow(title="Minecraft Server Directory")
        self.server_dir_row.set_text(self.get_server_dir())
        self.server_dir_row.set_tooltip_text("Directory where server JAR files are stored")
        self.server_dir_row.connect("changed", self.on_server_dir_changed)
        preferences_group.add(self.server_dir_row)
        
        # Browse button
        browse_row = Adw.ActionRow(title="Browse for directory")
        browse_button = Gtk.Button(label="Browse...")
        browse_button.connect("clicked", self.on_browse_clicked)
        browse_row.add_suffix(browse_button)
        preferences_group.add(browse_row)
        
        self.add(preferences_page)
    
    def get_config_dir(self):
        """Get the config directory"""
        config_dir = os.path.expanduser("~/.config/grassy")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def get_settings_file(self):
        """Get the settings file path"""
        return os.path.join(self.get_config_dir(), "settings.txt")
    
    def get_server_dir(self):
        """Get the server directory from settings"""
        settings_file = self.get_settings_file()
        default_dir = os.path.expanduser("~/.local/share/grassy/servers")
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r') as f:
                    saved_dir = f.read().strip()
                    if saved_dir:
                        return saved_dir
            except:
                pass
        
        return default_dir
    
    def save_server_dir(self):
        """Save the server directory setting"""
        server_dir = self.server_dir_row.get_text()
        settings_file = self.get_settings_file()
        
        with open(settings_file, 'w') as f:
            f.write(server_dir)
    
    def on_server_dir_changed(self, entry):
        """Save when directory changes"""
        self.save_server_dir()
        # Notify parent to refresh server list
        if self.parent and hasattr(self.parent, 'refresh_server_list'):
            self.parent.refresh_server_list()
    
    def on_browse_clicked(self, button):
        """Open file chooser dialog"""
        dialog = Gtk.FileChooserDialog(
            title="Select Minecraft Server Directory",
            transient_for=self,
            action=Gtk.FileChooserAction.SELECT_FOLDER
        )
        
        dialog.add_buttons(
            "_Cancel", Gtk.ResponseType.CANCEL,
            "_Select", Gtk.ResponseType.ACCEPT
        )
        
        dialog.connect("response", self.on_folder_selected)
        dialog.show()
    
    def on_folder_selected(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            folder_path = dialog.get_file().get_path()
            self.server_dir_row.set_text(folder_path)
        dialog.destroy()
