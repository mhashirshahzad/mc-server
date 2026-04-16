from gi.repository import Adw, Gtk, Gdk, GLib
import os
import appdirs
import socket
import subprocess
import re


class SettingsWindow(Adw.Window):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        
        self.parent = parent
        self.set_title("Settings")
        self.set_default_size(600, 500)
        self.set_transient_for(parent)
        self.set_modal(True)
        
        self.ip_revealed = False
        
        # Main layout
        self.content = Adw.ToolbarView()
        
        # Header bar
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Settings"))
        
        # Save button
        save_button = Gtk.Button(label="Save")
        save_button.add_css_class("suggested-action")
        save_button.connect("clicked", self.on_save_clicked)
        header.pack_end(save_button)
        
        self.content.add_top_bar(header)
        
        # Scrolled window for preferences
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        
        # Preferences page
        preferences_page = Adw.PreferencesPage()
        
        # Server Settings group
        server_group = Adw.PreferencesGroup(title="Server Settings")
        preferences_page.add(server_group)
        
        # Server directory setting
        self.server_dir_row = Adw.EntryRow(title="Minecraft Server Directory")
        self.server_dir_row.set_text(self.get_server_dir())
        self.server_dir_row.set_tooltip_text("Directory where server JAR files are stored")
        server_group.add(self.server_dir_row)
        
        # Browse button
        browse_row = Adw.ActionRow(title="Browse for directory")
        browse_button = Gtk.Button(label="Browse...")
        browse_button.connect("clicked", self.on_browse_clicked)
        browse_row.add_suffix(browse_button)
        server_group.add(browse_row)
        
        # Network Settings group
        network_group = Adw.PreferencesGroup(title="Network Information")
        preferences_page.add(network_group)
        
        # Local IP row
        local_ip_row = Adw.ActionRow(title="Local IP Address")
        self.local_ip_label = Gtk.Label(label=self.get_local_ip())
        self.local_ip_label.set_halign(Gtk.Align.END)
        self.local_ip_label.set_selectable(True)
        local_ip_row.add_suffix(self.local_ip_label)
        network_group.add(local_ip_row)
        
        # Public IP row (with reveal button)
        public_ip_row = Adw.ActionRow(title="Public IP Address")
        public_ip_row.set_subtitle("Click the eye to reveal your public IP")
        
        # Create a box to hold the IP label and buttons
        ip_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        ip_box.set_halign(Gtk.Align.END)
        
        # IP label (hidden by default)
        self.public_ip_label = Gtk.Label(label="••••••••")
        self.public_ip_label.set_selectable(True)
        ip_box.append(self.public_ip_label)
        
        # Reveal button (eye icon)
        self.reveal_button = Gtk.Button()
        self.reveal_button.set_icon_name("view-reveal-symbolic")
        self.reveal_button.set_tooltip_text("Show public IP")
        self.reveal_button.set_valign(Gtk.Align.CENTER)
        self.reveal_button.connect("clicked", self.on_reveal_ip_clicked)
        ip_box.append(self.reveal_button)
        
        # Copy button
        self.copy_button = Gtk.Button()
        self.copy_button.set_icon_name("edit-copy-symbolic")
        self.copy_button.set_tooltip_text("Copy IP address")
        self.copy_button.set_valign(Gtk.Align.CENTER)
        self.copy_button.set_sensitive(False)  # Disabled until IP is revealed
        self.copy_button.connect("clicked", self.on_copy_ip_clicked)
        ip_box.append(self.copy_button)
        
        # Refresh button
        refresh_button = Gtk.Button()
        refresh_button.set_icon_name("view-refresh-symbolic")
        refresh_button.set_tooltip_text("Refresh IP address")
        refresh_button.set_valign(Gtk.Align.CENTER)
        refresh_button.connect("clicked", self.on_refresh_ip_clicked)
        ip_box.append(refresh_button)
        
        public_ip_row.add_suffix(ip_box)
        network_group.add(public_ip_row)
        
        # Store the actual public IP
        self.public_ip = None
        self.load_public_ip()
        
        scrolled.set_child(preferences_page)
        self.content.set_content(scrolled)
        
        self.set_content(self.content)
    
    def get_local_ip(self):
        """Get the local IP address of the current system"""
        try:
            # Create a socket to determine the local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()
            return local_ip
        except Exception:
            try:
                # Fallback method
                hostname = socket.gethostname()
                local_ip = socket.gethostbyname(hostname)
                return local_ip
            except Exception:
                return "Unable to detect"
    
    def get_public_ip(self):
        """Get the public IP address using external services"""
        try:
            # Try multiple services for redundancy
            services = [
                "https://api.ipify.org",
                "https://icanhazip.com",
                "https://checkip.amazonaws.com"
            ]
            
            import requests
            for service in services:
                try:
                    response = requests.get(service, timeout=5)
                    if response.status_code == 200:
                        ip = response.text.strip()
                        if re.match(r'^\d+\.\d+\.\d+\.\d+$', ip):
                            return ip
                except:
                    continue
            
            return "Unable to detect"
        except Exception:
            return "Unable to detect"
    
    def load_public_ip(self):
        """Load public IP in background thread"""
        import threading
        
        def fetch_ip():
            ip = self.get_public_ip()
            self.public_ip = ip
            # Don't auto-reveal, just store it
        
        thread = threading.Thread(target=fetch_ip, daemon=True)
        thread.start()
    
    def on_reveal_ip_clicked(self, button):
        """Toggle IP visibility"""
        if not self.ip_revealed:
            # Reveal the IP
            if self.public_ip:
                self.public_ip_label.set_label(self.public_ip)
            else:
                self.public_ip_label.set_label("Loading...")
                # Try to get IP now if not loaded
                import threading
                def get_ip():
                    ip = self.get_public_ip()
                    self.public_ip = ip
                    GLib.idle_add(lambda: self.public_ip_label.set_label(ip))
                threading.Thread(target=get_ip, daemon=True).start()
            
            self.reveal_button.set_icon_name("view-conceal-symbolic")
            self.reveal_button.set_tooltip_text("Hide public IP")
            self.copy_button.set_sensitive(True)
            self.ip_revealed = True
        else:
            # Hide the IP
            self.public_ip_label.set_label("••••••••")
            self.reveal_button.set_icon_name("view-reveal-symbolic")
            self.reveal_button.set_tooltip_text("Show public IP")
            self.copy_button.set_sensitive(False)
            self.ip_revealed = False
    
    def on_copy_ip_clicked(self, button):
        """Copy the public IP to clipboard"""
        if self.public_ip and self.public_ip != "Unable to detect":
            clipboard = Gdk.Display.get_default().get_clipboard()
            clipboard.set(self.public_ip)
            
            # Show temporary notification
            self.show_temp_notification("IP copied to clipboard!")
    
    def on_refresh_ip_clicked(self, button):
        """Refresh the public IP address"""
        import threading
        
        # Show loading state
        if self.ip_revealed:
            self.public_ip_label.set_label("Refreshing...")
        else:
            self.public_ip_label.set_label("••••••••")
        
        def refresh():
            new_ip = self.get_public_ip()
            self.public_ip = new_ip
            if self.ip_revealed:
                GLib.idle_add(lambda: self.public_ip_label.set_label(new_ip))
            GLib.idle_add(lambda: self.show_temp_notification("IP address refreshed!"))
        
        thread = threading.Thread(target=refresh, daemon=True)
        thread.start()
    
    def show_temp_notification(self, message):
        """Show a temporary notification"""
        toast = Adw.Toast(title=message, timeout=2)
        self.parent.add_toast(toast) if hasattr(self.parent, 'add_toast') else None
    
    def get_config_dir(self):
        """Get the config directory"""
        config_dir = appdirs.user_config_dir("grassy")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def get_settings_file(self):
        """Get the settings file path"""
        return os.path.join(self.get_config_dir(), "settings.txt")
    
    def get_server_dir(self):
        """Get the server directory from settings"""
        settings_file = self.get_settings_file()        

        data_dir = appdirs.user_data_dir("grassy")
        default_dir = os.path.join(data_dir, "servers")
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
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        
        with open(settings_file, 'w') as f:
            f.write(server_dir)
    
    def on_save_clicked(self, button):
        """Handle save button click"""
        self.save_server_dir()
        
        # Notify parent to refresh server list
        if self.parent and hasattr(self.parent, 'refresh_server_list'):
            self.parent.refresh_server_list()
        
        # Close the dialog after saving
        self.destroy()
    
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
        dialog.present()
    
    def on_folder_selected(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            folder_path = dialog.get_file().get_path()
            self.server_dir_row.set_text(folder_path)
        dialog.destroy()
