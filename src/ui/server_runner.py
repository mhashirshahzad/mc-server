from gi.repository import Adw, Gtk, GLib
import subprocess
import threading
from pathlib import Path

class ServerRunnerWindow(Adw.Window):
    def __init__(self, parent, server_folder, **kwargs):
        super().__init__(**kwargs)
        
        self.server_folder = Path(server_folder)
        self.process = None
        self.console_thread = None
        
        self.set_title(f"Server Console - {self.server_folder.name}")
        self.set_default_size(900, 600)
        self.set_transient_for(parent)
        self.set_modal(True)
        
        # Main layout
        self.content = Adw.ToolbarView()
        
        # Header bar with stop button
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label=f"Console: {self.server_folder.name}"))
        
        # Stop button in header
        self.stop_button = Gtk.Button(label="Stop Server")
        self.stop_button.add_css_class("destructive-action")
        self.stop_button.connect("clicked", self.stop_server)
        header.pack_end(self.stop_button)
        
        self.content.add_top_bar(header)
        
        # Main content box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        main_box.set_vexpand(True)  # Make main box expand vertically
        main_box.set_margin_top(6)
        main_box.set_margin_bottom(6)
        main_box.set_margin_start(6)
        main_box.set_margin_end(6)
        
        # Console output area - this should expand to fill space
        scrolled_console = Gtk.ScrolledWindow()
        scrolled_console.set_vexpand(True)  # Make console expand vertically
        scrolled_console.set_hexpand(True)  # Make console expand horizontally
        
        self.console_buffer = Gtk.TextBuffer()
        self.console_view = Gtk.TextView.new_with_buffer(self.console_buffer)
        self.console_view.set_editable(False)
        self.console_view.set_monospace(True)
        self.console_view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        
        scrolled_console.set_child(self.console_view)
        main_box.append(scrolled_console)
        
        # Command input area (fixed at bottom)
        input_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        input_box.set_margin_top(6)
        input_box.set_vexpand(False)  # Don't expand, keep at bottom
        
        self.command_entry = Gtk.Entry()
        self.command_entry.set_placeholder_text("Type a command and press Enter to send...")
        self.command_entry.connect("activate", self.send_command)  # Enter key sends command
        self.command_entry.set_hexpand(True)  # Make entry expand horizontally
        input_box.append(self.command_entry)
        
        send_button = Gtk.Button(label="Send")
        send_button.add_css_class("suggested-action")
        send_button.connect("clicked", self.send_command)
        input_box.append(send_button)
        
        main_box.append(input_box)
        
        self.content.set_content(main_box)
        self.set_content(self.content)
        
        # Auto-start the server when popup opens
        self.start_server()

    def start_server(self):
        """Start the Minecraft server with Java settings"""
        server_jar = self.server_folder / "server.jar"
    
        if not server_jar.exists():
            self.append_console(f"Error: server.jar not found in {self.server_folder}\n")
            return
    
        # Load Java settings
        java_properties = self.server_folder / "java.properties"
        java_path = "java"
        min_ram = "2"
        max_ram = "4"
    
        if java_properties.exists():
            try:
                with open(java_properties, 'r') as f:
                    for line in f:
                        if '=' in line and not line.startswith('#'):
                            key, value = line.strip().split('=', 1)
                            if key == 'java-path':
                                java_path = value
                            elif key == 'min-ram':
                                min_ram = value
                            elif key == 'max-ram':
                                max_ram = value
            except:
                pass
    
        # Format RAM values
        def format_ram(ram):
            try:
                ram_float = float(ram)
                if ram_float == int(ram_float):
                    return f"{int(ram_float)}G"
                else:
                    return f"{int(ram_float * 1024)}M"
            except:
                return f"{ram}G" if ram.isdigit() else ram
    
        min_ram_str = format_ram(min_ram)
        max_ram_str = format_ram(max_ram)
    
        # Accept EULA if needed
        eula_file = self.server_folder / "eula.txt"
        if not eula_file.exists() or (eula_file.exists() and "eula=false" in eula_file.read_text()):
            with open(eula_file, 'w') as f:
                f.write("eula=true")
            self.append_console("Accepted EULA\n")
    
        try:
            # Build command
            cmd = [java_path, f"-Xms{min_ram_str}", f"-Xmx{max_ram_str}", "-jar", str(server_jar), "nogui"]
            cmd_str = " ".join(cmd)
            self.append_console(f"Running: {cmd_str}\n")
        
            # Start server process
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.server_folder),
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
        
            self.append_console(f"Server started with {min_ram_str} min, {max_ram_str} max RAM\n")
            self.append_console(f"Type 'help' for commands.\n")
        
            # Start reading output
            self.console_thread = threading.Thread(target=self.read_output, daemon=True)
            self.console_thread.start()
        
        except Exception as e:
            self.append_console(f"Error starting server: {e}\n")
            self.process = None
   
    
    def stop_server(self, button=None):
        """Stop the Minecraft server"""
        if self.process:
            try:
                # Send stop command first for graceful shutdown
                self.send_command_text("stop")
                self.process.wait(timeout=10)
                self.append_console("Server stopped gracefully\n")
            except:
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                    self.append_console("Server stopped\n")
                except:
                    self.process.kill()
                    self.append_console("Server killed (force stop)\n")
            
            self.process = None
            
            # Close the window after stopping
            GLib.timeout_add(1000, self.close)
    
    def send_command(self, button=None):
        """Send command from entry field"""
        command = self.command_entry.get_text()
        if command and self.process:
            self.send_command_text(command)
            self.command_entry.set_text("")
    
    def send_command_text(self, command):
        """Send a command to the server"""
        if self.process and self.process.stdin:
            try:
                self.process.stdin.write(command + "\n")
                self.process.stdin.flush()
                self.append_console(f"> {command}\n")
            except:
                self.append_console("Failed to send command\n")
    
    def read_output(self):
        """Read server output in background thread"""
        for line in iter(self.process.stdout.readline, ''):
            if line:
                GLib.idle_add(self.append_console, line)
    
    def append_console(self, text):
        """Add text to console buffer (thread-safe)"""
        end_iter = self.console_buffer.get_end_iter()
        self.console_buffer.insert(end_iter, text)
        # Auto-scroll to bottom
        self.console_view.scroll_to_iter(end_iter, 0.0, False, 0, 0)
