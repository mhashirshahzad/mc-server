from gi.repository import Adw, Gtk
from pathlib import Path
import os
from ui.settings import SettingsDialog
from ui.card import ServerCard

class GrassyWindow(Adw.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title("Grassy")
        self.set_default_size(800, 600)

        # Main content - server list
        self.server_list = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=6
        )
        self.server_list.set_margin_top(12)
        self.server_list.set_margin_bottom(12)
        self.server_list.set_margin_start(12)
        self.server_list.set_margin_end(12)
        
        # Scrolled window for server list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(self.server_list)

        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Grassy - Minecraft Server Manager"))

        # Settings button (left side)
        settings_button = Gtk.Button.new_from_icon_name("emblem-system-symbolic")
        settings_button.set_tooltip_text("Settings")
        settings_button.connect("clicked", self.on_settings_clicked)
        header.pack_start(settings_button)

        # Scan button (right side)
        scan_button = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        scan_button.set_tooltip_text("Scan for servers")
        scan_button.connect("clicked", self.on_scan_clicked)
        header.pack_end(scan_button)

        toolbar = Adw.ToolbarView()
        toolbar.add_top_bar(header)
        toolbar.set_content(scrolled)

        self.set_content(toolbar)
        
        # Load servers on startup
        self.refresh_server_list()
    
    def get_servers_dir(self):
        """Get servers directory from settings"""
        settings_file = os.path.expanduser("~/.config/grassy/settings.txt")
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
    
    def refresh_server_list(self):
        """Refresh the server list"""
        # Clear existing list
        for child in list(self.server_list):
            self.server_list.remove(child)
        
        servers_dir = self.get_servers_dir()
        
        if not os.path.exists(servers_dir):
            os.makedirs(servers_dir, exist_ok=True)
            self.show_empty_state(servers_dir)
            return
        
        # Find all directories that contain a server.jar
        server_folders = []
        for item in Path(servers_dir).iterdir():
            if item.is_dir():
                server_jar = item / "server.jar"
                if server_jar.exists():
                    server_folders.append(item)
        
        if not server_folders:
            self.show_empty_state(servers_dir)
            return
        
        # Create a card for each server folder
        for i, folder in enumerate(sorted(server_folders)):
            card = ServerCard(folder, on_server_changed=self.refresh_server_list)
            self.server_list.append(card)
    
            # Add separator after each card except the last one
            if i < len(server_folders) - 1:
                separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
                separator.set_margin_start(12)
                separator.set_margin_end(12)
                self.server_list.append(separator)    

    def show_empty_state(self, servers_dir):
        """Show message when no servers found"""
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        info_box.set_halign(Gtk.Align.CENTER)
        info_box.set_valign(Gtk.Align.CENTER)
        info_box.set_vexpand(True)
        
        icon = Gtk.Image.new_from_icon_name("folder-symbolic")
        icon.set_pixel_size(64)
        info_box.append(icon)
        
        label = Gtk.Label(label="No servers found")
        label.add_css_class("title-4")
        info_box.append(label)
        
        sublabel = Gtk.Label(label=f"Create a folder in:\n{servers_dir}\nand place server.jar inside it")
        sublabel.set_halign(Gtk.Align.CENTER)
        sublabel.add_css_class("dim-label")
        info_box.append(sublabel)
        
        self.server_list.append(info_box)
    
    
    def on_settings_clicked(self, button):
        """Open settings dialog"""
        dialog = SettingsDialog(parent=self)
        dialog.connect("destroy", lambda d: self.refresh_server_list())
        dialog.present()

    def on_scan_clicked(self, button):
        
        """Manually scan for servers"""
        self.refresh_server_list()
