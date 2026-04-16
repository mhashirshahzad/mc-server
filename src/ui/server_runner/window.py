from gi.repository import Adw, Gtk, GLib
import subprocess
import threading
import os
import pty
from pathlib import Path

from .commands import CommandHandler
from .console import ConsoleHandler
from .widgets.console_view import ConsoleView
from .widgets.input_box import CommandInputBox
from .widgets.player_panel import PlayerPanel


class ServerRunnerWindow(Adw.Window):
    def __init__(self, parent, server_folder, **kwargs):
        super().__init__(**kwargs)

        self.server_folder = Path(server_folder)
        self.process = None
        self.console_thread = None
        self.pty_master = None

        self.set_title(f"Server Console - {self.server_folder.name}")
        self.set_default_size(1100, 700)
        self.set_transient_for(parent)
        self.set_modal(True)

        self.connect("destroy", self.on_window_destroy)

        self.command_handler = CommandHandler(self)
        self.console_handler = ConsoleHandler(self)

        self.setup_ui()
        self.start_server()

    def on_window_destroy(self, widget):
        """Kill server if user closes window manually"""
        if self.process:
            try:
                self.process.terminate()
            except:
                pass

    def setup_ui(self):
        self.content = Adw.ToolbarView()

        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label=f"Console: {self.server_folder.name}"))

        self.stop_button = Gtk.Button(label="Stop Server")
        self.stop_button.add_css_class("destructive-action")
        self.stop_button.connect("clicked", self.stop_server)
        header.pack_end(self.stop_button)

        self.content.add_top_bar(header)

        main_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        main_paned.set_position(300)

        self.player_panel = PlayerPanel(self.command_handler)
        main_paned.set_start_child(self.player_panel.get_widget())

        console_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        console_box.set_margin_top(6)
        console_box.set_margin_bottom(6)
        console_box.set_margin_start(6)
        console_box.set_margin_end(6)

        self.console_view = ConsoleView()
        console_box.append(self.console_view.get_widget())

        self.command_input = CommandInputBox(self.command_handler)
        console_box.append(self.command_input.get_widget())

        main_paned.set_end_child(console_box)

        self.content.set_content(main_paned)
        self.set_content(self.content)

    def start_server(self):
        server_jar = self.server_folder / "server.jar"

        if not server_jar.exists():
            self.append_console("Error: server.jar not found\n")
            return

        cmd = ["java", "-Xms2G", "-Xmx4G", "-jar", str(server_jar), "nogui"]

        try:
            master_fd, slave_fd = pty.openpty()
            self.pty_master = master_fd

            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.server_folder),
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                close_fds=True
            )

            os.close(slave_fd)

            self.append_console(f"Running: {' '.join(cmd)}\n")
            self.append_console("Server started\n")

            self.console_thread = threading.Thread(
                target=self.read_output,
                daemon=True
            )
            self.console_thread.start()

        except Exception as e:
            self.append_console(f"Error starting server: {e}\n")

    def stop_server(self, button=None):
        """Gracefully stop server"""
        if not self.process:
            self.append_console("No server running\n")
            return

        self.append_console("Stopping server...\n")

        try:
            self.command_handler.send_command("stop")
        except Exception as e:
            self.append_console(f"Stop failed: {e}\n")

    def read_output(self):
        """Read PTY output"""
        try:
            while True:
                data = os.read(self.pty_master, 1024).decode(errors="ignore")
                if not data:
                    break
                GLib.idle_add(self.parse_output, data)

        except Exception as e:
            GLib.idle_add(self.append_console, f"Read error: {e}\n")

        finally:
            GLib.idle_add(self.on_server_stopped)

    def on_server_stopped(self):
        """Called when server exits"""
        self.append_console("Server stopped\n")
        self.process = None

        # Close window after slight delay
        GLib.timeout_add(400, self.destroy)

    def parse_output(self, text):
        self.append_console(text)

        for line in text.splitlines():
            if "joined the game" in line:
                import re
                m = re.search(r'(\w+) joined the game', line)
                if m:
                    self.player_panel.add_player(m.group(1))

            elif "left the game" in line:
                import re
                m = re.search(r'(\w+) left the game', line)
                if m:
                    self.player_panel.remove_player(m.group(1))

            elif "online:" in line.lower():
                import re
                m = re.search(r'online:\s*(.*)', line, re.IGNORECASE)
                if m:
                    players = [p.strip() for p in m.group(1).split(',') if p.strip()]
                    self.player_panel.update_players(players)

    def append_console(self, text):
        GLib.idle_add(self.console_view.append, text)
