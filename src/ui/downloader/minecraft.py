from gi.repository import Adw, Gtk, GLib
import requests
import threading
from pathlib import Path
import appdirs

from utils import get_servers_dir

class MinecraftDownloaderWindow(Adw.Window):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)

        self.parent = parent
        self.set_title("Download Minecraft Server")
        self.set_default_size(500, 300)
        self.set_transient_for(parent)
        self.set_modal(True)

        self.all_versions = []

        # model for autocomplete
        self.version_model = Gtk.ListStore(str)

        self.content = Adw.ToolbarView()

        # Header
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Download Server"))

        cancel_button = Gtk.Button(label="Cancel")
        cancel_button.connect("clicked", lambda x: self.destroy())
        header.pack_end(cancel_button)

        self.content.add_top_bar(header)

        # Main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)

        # Title
        label = Gtk.Label(label="Minecraft Version")
        label.set_halign(Gtk.Align.START)
        label.add_css_class("heading")
        main_box.append(label)

        # ENTRY (replaces ComboRow)
        self.version_entry = Gtk.Entry()
        self.version_entry.set_placeholder_text("Loading versions...")
        self.version_entry.set_sensitive(False)
        main_box.append(self.version_entry)

        # Spinner
        self.spinner = Gtk.Spinner()
        self.spinner.set_visible(False)
        main_box.append(self.spinner)

        # separator
        sep = Gtk.Separator()
        sep.set_margin_top(12)
        sep.set_margin_bottom(12)
        main_box.append(sep)

        # download button
        self.download_button = Gtk.Button(label="Download")
        self.download_button.add_css_class("suggested-action")
        self.download_button.set_sensitive(False)
        self.download_button.connect("clicked", self.on_download_clicked)
        main_box.append(self.download_button)

        # progress
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_visible(False)
        main_box.append(self.progress_bar)

        # status
        self.status_label = Gtk.Label(label="")
        self.status_label.set_visible(False)
        self.status_label.set_halign(Gtk.Align.CENTER)
        self.status_label.add_css_class("dim-label")
        main_box.append(self.status_label)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(main_box)

        self.content.set_content(scrolled)
        self.set_content(self.content)

        self.load_versions()

    # -----------------------
    # LOAD VERSIONS
    # -----------------------
    def load_versions(self):
        self.spinner.set_visible(True)
        self.spinner.start()
        self.version_entry.set_placeholder_text("Loading versions...")

        threading.Thread(target=self.fetch_versions, daemon=True).start()

    def fetch_versions(self):
        try:
            url = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            data = r.json()

            versions = [
                v["id"] for v in data["versions"]
                if v["type"] == "release"
            ]

            versions.sort(reverse=True)

            self.all_versions = versions
            GLib.idle_add(self.update_version_list, versions)

        except Exception as e:
            GLib.idle_add(self.show_error, str(e))

    # -----------------------
    # UPDATE UI + AUTOCOMPLETE
    # -----------------------
    def update_version_list(self, versions):
        self.spinner.stop()
        self.spinner.set_visible(False)

        if not versions:
            self.version_entry.set_placeholder_text("No versions found")
            return

        # fill model
        self.version_model.clear()
        for v in versions:
            self.version_model.append([v])

        completion = Gtk.EntryCompletion()
        completion.set_model(self.version_model)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        completion.set_popup_completion(True)

        self.version_entry.set_completion(completion)

        self.version_entry.set_text(versions[0])
        self.version_entry.set_sensitive(True)

        self.download_button.set_sensitive(True)

    # -----------------------
    # GET VERSION
    # -----------------------
    def get_selected_version(self):
        text = self.version_entry.get_text().strip()
        if text in self.all_versions:
            return text
        return None

    # -----------------------
    # DOWNLOAD
    # -----------------------
    def on_download_clicked(self, btn):
        version = self.get_selected_version()

        if not version:
            self.show_error(f"Invalid version selected. Available versions: {self.all_versions[0]} - {self.all_versions[-1]}")
            return

        self.download_button.set_sensitive(False)
        self.version_entry.set_sensitive(False)

        self.progress_bar.set_visible(True)
        self.status_label.set_visible(True)
        self.status_label.set_label(f"Downloading {version}...")

        threading.Thread(
            target=self.download_server,
            args=(version,),
            daemon=True
        ).start()

    # -----------------------
    # DOWNLOAD ENGINE
    # -----------------------
    def download_server(self, version):
        try:
            manifest_url = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
            r = requests.get(manifest_url)
            data = r.json()

            version_url = None
            for v in data["versions"]:
                if v["id"] == version:
                    version_url = v["url"]
                    break

            if not version_url:
                GLib.idle_add(self.show_error, f"Version {version} not found in manifest")
                return

            vr = requests.get(version_url).json()
            server_url = vr["downloads"]["server"]["url"]

            servers_dir = get_servers_dir()
            folder = Path(servers_dir) / version  # Changed from server_{version} to just {version}
            folder.mkdir(parents=True, exist_ok=True)

            jar_path = folder / "server.jar"

            r = requests.get(server_url, stream=True)
            total = int(r.headers.get("content-length", 0))
            done = 0

            with open(jar_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
                    done += len(chunk)
                    if total:
                        GLib.idle_add(self.update_progress, done / total)

            GLib.idle_add(self.download_done, version)

        except Exception as e:
            GLib.idle_add(self.show_error, str(e))

    # -----------------------
    # PROGRESS
    # -----------------------
    def update_progress(self, v):
        self.progress_bar.set_fraction(v)

    def download_done(self, version):
        self.status_label.set_label(f"Done: {version}")
        self.progress_bar.set_fraction(1.0)

        GLib.timeout_add(1200, self.close_and_refresh)

    def close_and_refresh(self):
        if self.parent and hasattr(self.parent, "refresh_server_list"):
            self.parent.refresh_server_list()
        self.destroy()
        return False

    # -----------------------
    # UTIL
    # -----------------------
    def show_error(self, msg):
        self.status_label.set_visible(True)
        self.status_label.set_label(f"Error: {msg}")
        self.download_button.set_sensitive(True)
        self.version_entry.set_sensitive(True)
        self.spinner.stop()
        self.spinner.set_visible(False)
