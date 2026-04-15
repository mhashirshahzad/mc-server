from gi.repository import Adw, Gtk, GLib
import subprocess
import threading
from pathlib import Path
from ui.server_editor import ServerEditorDialog
from ui.server_popup import ServerPopup

class ServerCard(Adw.PreferencesGroup):
    def __init__(self, server_folder, on_server_changed=None, **kwargs):
        super().__init__(**kwargs)
        
        self.server_folder = Path(server_folder)
        self.on_server_changed = on_server_changed
        self.process = None
        self.console_thread = None
        
        # Store server properties
        self.server_name = self.server_folder.name
        self.motd = "A Minecraft Server"
        self.server_port = "25565"
        self.load_properties()
        
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
                            elif key == 'server-port':
                                self.server_port = value
            except:
                pass
    
    def build_ui(self):
        """Build the card UI"""
        # Set card styling
        self.set_margin_top(6)
        self.set_margin_bottom(6)
        
        # Header section with title and buttons
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        header_box.set_margin_top(12)
        header_box.set_margin_bottom(6)
        header_box.set_margin_start(12)
        header_box.set_margin_end(12)
        
        # Titles box (vertical)
        titles_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        titles_box.set_hexpand(True)
        
        # Big heading - Server folder name
        self.name_label = Gtk.Label(label=self.server_name)
        self.name_label.add_css_class("title-4")
        self.name_label.set_halign(Gtk.Align.START)
        titles_box.append(self.name_label)
        
        # Small heading - MOTD
        self.motd_label = Gtk.Label(label=self.motd)
        self.motd_label.add_css_class("dim-label")
        self.motd_label.set_halign(Gtk.Align.START)
        titles_box.append(self.motd_label)
        
        header_box.append(titles_box)
        
        # Buttons box (top right)
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        
        # Settings button
        settings_btn = Gtk.Button.new_from_icon_name("emblem-system-symbolic")
        settings_btn.set_tooltip_text("Server Settings")
        settings_btn.connect("clicked", self.on_settings_clicked)
        buttons_box.append(settings_btn)
        
        # Open folder button
        folder_btn = Gtk.Button.new_from_icon_name("folder-open-symbolic")
        folder_btn.set_tooltip_text("Open Server Folder")
        folder_btn.connect("clicked", self.on_folder_clicked)
        buttons_box.append(folder_btn)
        
        header_box.append(buttons_box)
        
        # Add header as a custom row
        header_row = Adw.ActionRow()
        header_row.set_child(header_box)
        self.add(header_row)
        
        # Status and control section
        control_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        control_box.set_margin_top(6)
        control_box.set_margin_bottom(12)
        control_box.set_margin_start(12)
        control_box.set_margin_end(12)
        
        # Status indicator
        self.status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.status_box.set_hexpand(True)
        
        self.status_dot = Gtk.Label(label="●")
        self.status_dot.add_css_class("error")
        self.status_label = Gtk.Label(label="Stopped")
        self.status_label.add_css_class("dim-label")
        
        self.status_box.append(self.status_dot)
        self.status_box.append(self.status_label)
        
        control_box.append(self.status_box)
        
        # Start button (big)
        self.start_button = Gtk.Button(label="Start Server")
        self.start_button.add_css_class("suggested-action")
        self.start_button.set_size_request(120, -1)
        self.start_button.connect("clicked", self.toggle_server)
        control_box.append(self.start_button)
        
        control_row = Adw.ActionRow()
        control_row.set_child(control_box)
        self.add(control_row)
        
        # Console output section (collapsible)
        self.console_expander = Gtk.Expander(label="Console Output")
        self.console_expander.set_margin_top(6)
        self.console_expander.set_margin_bottom(6)
        self.console_expander.set_margin_start(12)
        self.console_expander.set_margin_end(12)
        
        self.console_buffer = Gtk.TextBuffer()
        console_view = Gtk.TextView.new_with_buffer(self.console_buffer)
        console_view.set_editable(False)
        console_view.set_monospace(True)
        console_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        console_view.set_size_request(-1, 150)
        
        scrolled_console = Gtk.ScrolledWindow()
        scrolled_console.set_child(console_view)
        scrolled_console.set_min_content_height(150)
        
        self.console_expander.set_child(scrolled_console)
        
        console_row = Adw.ActionRow()
        console_row.set_child(self.console_expander)
        self.add(console_row)
    

    def toggle_server(self, button):
        """Open server console popup"""
        popup = ServerPopup(parent=self.get_root(), server_folder=self.server_folder)
        popup.present()
    
    def start_server(self):
        """Start the Minecraft server"""
        server_jar = self.server_folder / "server.jar"
        
        if not server_jar.exists():
            self.append_console_text(f"Error: server.jar not found in {self.server_folder}\n")
            return
        
        # Accept EULA if needed
        eula_file = self.server_folder / "eula.txt"
        if not eula_file.exists() or (eula_file.exists() and "eula=false" in eula_file.read_text()):
            with open(eula_file, 'w') as f:
                f.write("eula=true")
            self.append_console_text("Accepted EULA\n")
        
        try:
            # Start server process
            self.process = subprocess.Popen(
                ["java", "-jar", str(server_jar), "nogui"],
                cwd=str(self.server_folder),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Update UI
            self.status_dot.remove_css_class("error")
            self.status_dot.add_css_class("success")
            self.status_label.set_label("Running")
            self.start_button.set_label("Stop Server")
            self.start_button.remove_css_class("suggested-action")
            self.start_button.add_css_class("destructive-action")
            
            # Start reading output
            self.console_thread = threading.Thread(target=self.read_output, daemon=True)
            self.console_thread.start()
            
            self.append_console_text(f"Server started on port {self.server_port}\n")
            
        except Exception as e:
            self.append_console_text(f"Error starting server: {e}\n")
            self.process = None
    
    def stop_server(self):
        """Stop the Minecraft server"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=10)
                self.append_console_text("Server stopped\n")
            except:
                self.process.kill()
                self.append_console_text("Server killed (force stop)\n")
            
            self.process = None
            
            # Update UI
            self.status_dot.remove_css_class("success")
            self.status_dot.add_css_class("error")
            self.status_label.set_label("Stopped")
            self.start_button.set_label("Start Server")
            self.start_button.remove_css_class("destructive-action")
            self.start_button.add_css_class("suggested-action")
    
    def read_output(self):
        """Read server output in background thread"""
        for line in iter(self.process.stdout.readline, ''):
            if line:
                GLib.idle_add(self.append_console_text, line)
    
    def append_console_text(self, text):
        """Add text to console buffer (thread-safe)"""
        end_iter = self.console_buffer.get_end_iter()
        self.console_buffer.insert(end_iter, text)
        # Auto-expand console when there's output
        if not self.console_expander.get_expanded():
            self.console_expander.set_expanded(True)
    
    def on_settings_clicked(self, button):
        """Open server properties editor"""
        dialog = ServerEditorDialog(parent=self.get_root(), server_folder=self.server_folder)
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
    
    def refresh(self):
        """Refresh card data"""
        self.load_properties()
        self.motd_label.set_label(self.motd)
