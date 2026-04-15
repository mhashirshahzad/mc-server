from gi.repository import Adw, Gtk
import subprocess
import shutil
from pathlib import Path
from ui.server_editor import ServerEditorWindow
from ui.server_runner import ServerRunnerWindow

class ServerCard(Adw.PreferencesGroup):
    def __init__(self, server_folder, on_server_changed=None, **kwargs):
        super().__init__(**kwargs)
        
        self.server_folder = Path(server_folder)
        self.on_server_changed = on_server_changed
        
        # Store server properties
        self.server_name = self.server_folder.name
        self.motd = "A Minecraft Server"
        self.load_properties()
        
        # Add margin around the whole card
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        self.set_margin_start(12)
        self.set_margin_end(12)
        
        # Build the UI
        self.build_ui()
    
    def load_properties(self):
        """Load server.properties"""
        properties_file = self.server_folder / "server.properties"
        
        if properties_file.exists():
            try:
                with open(properties_file, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            if key == 'motd':
                                self.motd = value
            except:
                pass
    
    def build_ui(self):
        """Build the card UI with proper styling"""
        
        # Use a box as main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        
        # Top row: Main heading + buttons
        top_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        top_row.set_margin_top(12)
        top_row.set_margin_start(12)
        top_row.set_margin_end(12)
        
        # Main heading
        self.name_label = Gtk.Label(label=self.server_name)
        self.name_label.add_css_class("title-4")
        self.name_label.set_halign(Gtk.Align.START)
        self.name_label.set_hexpand(True)
        top_row.append(self.name_label)
        
        # Buttons box
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        # Delete button
        delete_btn = Gtk.Button.new_from_icon_name("user-trash-symbolic")
        delete_btn.set_tooltip_text("Delete Server")
        delete_btn.set_size_request(32, 32)
        delete_btn.add_css_class("circular")
        delete_btn.add_css_class("destructive-action")
        delete_btn.connect("clicked", self.on_delete_clicked)
        buttons_box.append(delete_btn)

        # Open folder button
        folder_btn = Gtk.Button.new_from_icon_name("folder-open-symbolic")
        folder_btn.set_tooltip_text("Open Server Folder")
        folder_btn.set_size_request(32, 32)
        folder_btn.add_css_class("circular")
        folder_btn.connect("clicked", self.on_folder_clicked)
        buttons_box.append(folder_btn)
        
        # Settings button
        settings_btn = Gtk.Button.new_from_icon_name("emblem-system-symbolic")
        settings_btn.set_tooltip_text("Server Settings")
        settings_btn.set_size_request(32, 32)
        settings_btn.add_css_class("circular")
        settings_btn.connect("clicked", self.on_settings_clicked)
        buttons_box.append(settings_btn)
        
        
        top_row.append(buttons_box)
        main_box.append(top_row)
        
        # Bottom row: Sub heading + Start button
        bottom_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        bottom_row.set_margin_bottom(12)
        bottom_row.set_margin_start(12)
        bottom_row.set_margin_end(12)
        
        # Sub heading (MOTD)
        self.motd_label = Gtk.Label(label=self.motd)
        self.motd_label.add_css_class("dim-label")
        self.motd_label.set_halign(Gtk.Align.START)
        self.motd_label.set_hexpand(True)
        bottom_row.append(self.motd_label)
        
        # Start button
        start_button = Gtk.Button(label="Start Server")
        start_button.add_css_class("suggested-action")
        start_button.connect("clicked", self.on_start_clicked)
        bottom_row.append(start_button)
        
        main_box.append(bottom_row)
        
        # Add the main box to the card
        self.add(main_box)
    
    def on_start_clicked(self, button):
        """Open server console popup"""
        popup = ServerRunnerWindow(parent=self.get_root(), server_folder=self.server_folder)
        popup.present()
    
    def on_settings_clicked(self, button):
        """Open server properties editor"""
        dialog = ServerEditorWindow(parent=self.get_root(), server_folder=self.server_folder)
        dialog.connect("destroy", self.on_settings_closed)
        dialog.present()
    
    def on_settings_closed(self, dialog):
        """Refresh card when settings are saved"""
        self.load_properties()
        self.motd_label.set_label(self.motd)
        if self.on_server_changed:
            self.on_server_changed()
    
    def on_folder_clicked(self, button):
        """Open server folder in file manager"""
        subprocess.Popen(["xdg-open", str(self.server_folder)])
    
    def on_delete_clicked(self, button):
        """Show confirmation dialog before deleting server"""
        # Create confirmation dialog
        dialog = Adw.MessageDialog.new(self.get_root(), 
                                       "Delete Server?", 
                                       f"Are you sure you want to delete '{self.server_name}'?\n\nThis action cannot be undone.")
        
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("delete", "Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")
        
        dialog.connect("response", self.on_delete_confirmed)
        dialog.present()
    
    def on_delete_confirmed(self, dialog, response):
        """Handle delete confirmation"""
        dialog.destroy()
        
        if response == "delete":
            try:
                # Delete the server folder and all its contents
                shutil.rmtree(self.server_folder)
                
                # Notify parent to refresh server list
                if self.on_server_changed:
                    self.on_server_changed()
                    
            except Exception as e:
                # Show error dialog if deletion fails
                error_dialog = Adw.MessageDialog.new(self.get_root(),
                                                     "Delete Failed",
                                                     f"Failed to delete server: {str(e)}")
                error_dialog.add_response("ok", "OK")
                error_dialog.set_default_response("ok")
                error_dialog.present()
    
    def refresh(self):
        """Refresh card data"""
        self.load_properties()
        self.motd_label.set_label(self.motd)
