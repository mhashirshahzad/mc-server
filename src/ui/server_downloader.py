from gi.repository import Adw, Gtk, GLib
import requests
import os
import threading
from pathlib import Path

class DownloadsWindow(Adw.Window):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        
        self.parent = parent
        self.set_title("Download Minecraft Server")
        self.set_default_size(500, 300)
        self.set_transient_for(parent)
        self.set_modal(True)
        
        # Main layout
        self.content = Adw.ToolbarView()
        
        # Header bar
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Download Server"))
        
        # Cancel button
        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda x: self.destroy())
        header.pack_end(cancel_button)
        
        self.content.add_top_bar(header)
        
        # Main content box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        
        # Version selection
        version_label = Gtk.Label(label="Minecraft Version")
        version_label.set_halign(Gtk.Align.START)
        version_label.add_css_class("heading")
        main_box.append(version_label)
        
        # Version entry with suggestions
        self.version_entry = Adw.EntryRow()
        self.version_entry.set_text("latest")
        main_box.append(self.version_entry)
        
        # Common versions hint
        versions_hint = Gtk.Label(label="Common versions: 1.20.4, 1.21.4, 1.19.4")
        versions_hint.set_halign(Gtk.Align.START)
        versions_hint.add_css_class("dim-label")
        versions_hint.set_margin_start(6)
        main_box.append(versions_hint)
        
        # Separator
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(12)
        separator.set_margin_bottom(12)
        main_box.append(separator)
        
        # Download button
        self.download_button = Gtk.Button(label="Download")
        self.download_button.add_css_class("suggested-action")
        self.download_button.connect("clicked", self.on_download_clicked)
        main_box.append(self.download_button)
        
        # Progress bar (initially hidden)
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_hexpand(True)
        self.progress_bar.set_visible(False)
        main_box.append(self.progress_bar)
        
        # Status label
        self.status_label = Gtk.Label(label="")
        self.status_label.set_halign(Gtk.Align.CENTER)
        self.status_label.add_css_class("dim-label")
        self.status_label.set_visible(False)
        main_box.append(self.status_label)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(main_box)
        self.content.set_content(scrolled)
        
        self.set_content(self.content)
    
    def get_servers_dir(self):
        """Get the servers directory from settings"""
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
    
    def on_download_clicked(self, button):
        """Start download in separate thread"""
        version = self.version_entry.get_text().strip()
        
        if not version:
            self.show_error("Please enter a Minecraft version")
            return
        
        # Disable download button during download
        self.download_button.set_sensitive(False)
        self.download_button.set_label("Downloading...")
        
        # Show progress bar
        self.progress_bar.set_visible(True)
        self.progress_bar.set_fraction(0.0)
        self.status_label.set_visible(True)
        self.status_label.set_label(f"Downloading Minecraft {version}...")
        
        # Start download thread
        thread = threading.Thread(target=self.download_server, args=(version,))
        thread.daemon = True
        thread.start()
    
    def download_server(self, version):
        """Download server.jar in background thread"""
        try:
            # Get version manifest
            self.update_status("Fetching version information...")
            manifest_url = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
            response = requests.get(manifest_url, timeout=30)
            response.raise_for_status()
            manifest = response.json()
            
            # Find the requested version
            version_info = None
            if version.lower() == "latest":
                version_info = manifest["latest"]["release"]
                version = version_info
            else:
                for v in manifest["versions"]:
                    if v["id"] == version:
                        version_info = v["id"]
                        break
            
            if not version_info:
                GLib.idle_add(self.show_error, f"Version {version} not found")
                return
            
            # Get version details
            self.update_status(f"Getting download URL for {version}...")
            version_url = None
            for v in manifest["versions"]:
                if v["id"] == version_info:
                    version_url = v["url"]
                    break
            
            if not version_url:
                GLib.idle_add(self.show_error, f"Could not find URL for {version}")
                return
            
            version_response = requests.get(version_url, timeout=30)
            version_response.raise_for_status()
            version_data = version_response.json()
            
            # Get server download URL
            server_url = version_data["downloads"]["server"]["url"]
            
            # Create server directory
            servers_dir = self.get_servers_dir()
            server_folder = Path(servers_dir) / f"server_{version}"
            server_folder.mkdir(parents=True, exist_ok=True)
            
            # Download server.jar
            self.update_status(f"Downloading server_{version}/server.jar...")
            jar_path = server_folder / "server.jar"
            
            # Download with progress
            response = requests.get(server_url, stream=True, timeout=60)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(jar_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = downloaded / total_size
                            GLib.idle_add(self.update_progress, progress)
            
            # Accept EULA
            eula_path = server_folder / "eula.txt"
            with open(eula_path, 'w') as f:
                f.write("eula=true\n")
            
            GLib.idle_add(self.download_complete, version, server_folder)
            
        except requests.RequestException as e:
            GLib.idle_add(self.show_error, f"Download failed: {str(e)}")
        except Exception as e:
            GLib.idle_add(self.show_error, f"Error: {str(e)}")
    
    def update_status(self, message):
        """Update status label from background thread"""
        GLib.idle_add(lambda: self.status_label.set_label(message))
    
    def update_progress(self, fraction):
        """Update progress bar"""
        self.progress_bar.set_fraction(fraction)
    
    def download_complete(self, version, server_folder):
        """Handle successful download"""
        self.status_label.set_label(f"✓ Successfully downloaded Minecraft {version}!")
        self.progress_bar.set_fraction(1.0)
        
        # Close after delay
        GLib.timeout_add(1500, self.close_and_refresh)
    
    def close_and_refresh(self):
        """Close dialog and refresh server list"""
        # Refresh parent's server list
        if self.parent and hasattr(self.parent, 'refresh_server_list'):
            self.parent.refresh_server_list()
        self.destroy()
        return False  # Don't repeat the timeout
    
    def show_error(self, error_message):
        """Show error message"""
        self.status_label.set_label(f"Error: {error_message}")
        self.status_label.add_css_class("error")
        self.download_button.set_sensitive(True)
        self.download_button.set_label("Download")
        self.progress_bar.set_visible(False)
