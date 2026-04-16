from gi.repository import Adw, Gtk, GLib
import requests
import threading
from pathlib import Path
import appdirs
import re

from utils import get_servers_dir, save_servers_dir

class FabricDownloaderWindow(Adw.Window):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)

        self.parent = parent
        self.set_title("Download Fabric Server")
        self.set_default_size(550, 500)
        self.set_transient_for(parent)
        self.set_modal(True)

        # Data stores
        self.all_mc_versions = []
        self.loader_versions = []
        self.installer_versions = []
        
        self.selected_mc = None
        self.selected_loader = None
        self.selected_installer = None

        # UI setup
        self.content = Adw.ToolbarView()

        # Header
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Download Fabric Server"))

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

        # --- Minecraft Version ---
        mc_label = Gtk.Label(label="Minecraft Version")
        mc_label.set_halign(Gtk.Align.START)
        mc_label.add_css_class("heading")
        main_box.append(mc_label)

        self.mc_entry = Gtk.Entry()
        self.mc_entry.set_placeholder_text("Loading Minecraft versions...")
        self.mc_entry.set_sensitive(False)
        main_box.append(self.mc_entry)

        self.mc_spinner = Gtk.Spinner()
        self.mc_spinner.set_visible(False)
        main_box.append(self.mc_spinner)

        # --- Separator ---
        sep1 = Gtk.Separator()
        sep1.set_margin_top(12)
        sep1.set_margin_bottom(12)
        main_box.append(sep1)

        # --- Fabric Loader Version ---
        loader_label = Gtk.Label(label="Fabric Loader Version")
        loader_label.set_halign(Gtk.Align.START)
        loader_label.add_css_class("heading")
        main_box.append(loader_label)

        self.loader_entry = Gtk.Entry()
        self.loader_entry.set_placeholder_text("Select Minecraft version first")
        self.loader_entry.set_sensitive(False)
        main_box.append(self.loader_entry)

        self.loader_spinner = Gtk.Spinner()
        self.loader_spinner.set_visible(False)
        main_box.append(self.loader_spinner)

        # --- Separator ---
        sep2 = Gtk.Separator()
        sep2.set_margin_top(12)
        sep2.set_margin_bottom(12)
        main_box.append(sep2)

        # --- Fabric Installer Version ---
        installer_label = Gtk.Label(label="Fabric Installer Version")
        installer_label.set_halign(Gtk.Align.START)
        installer_label.add_css_class("heading")
        main_box.append(installer_label)

        self.installer_entry = Gtk.Entry()
        self.installer_entry.set_placeholder_text("Select Fabric loader first")
        self.installer_entry.set_sensitive(False)
        main_box.append(self.installer_entry)

        self.installer_spinner = Gtk.Spinner()
        self.installer_spinner.set_visible(False)
        main_box.append(self.installer_spinner)

        # --- Separator ---
        sep3 = Gtk.Separator()
        sep3.set_margin_top(12)
        sep3.set_margin_bottom(12)
        main_box.append(sep3)

        # --- Download Button ---
        self.download_button = Gtk.Button(label="Download Fabric Server")
        self.download_button.add_css_class("suggested-action")
        self.download_button.set_sensitive(False)
        self.download_button.connect("clicked", self.on_download_clicked)
        main_box.append(self.download_button)

        # --- Progress & Status ---
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_visible(False)
        main_box.append(self.progress_bar)

        self.status_label = Gtk.Label(label="")
        self.status_label.set_visible(False)
        self.status_label.set_halign(Gtk.Align.CENTER)
        self.status_label.add_css_class("dim-label")
        main_box.append(self.status_label)

        # Finalize UI
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(main_box)
        self.content.set_content(scrolled)
        self.set_content(self.content)

        # Start loading data
        self.load_minecraft_versions()
        self.load_installer_versions()

    # ----------------------------------------------------------------------
    # 1. LOAD MINECRAFT VERSIONS
    # ----------------------------------------------------------------------
    def load_minecraft_versions(self):
        self.mc_spinner.set_visible(True)
        self.mc_spinner.start()
        self.mc_entry.set_placeholder_text("Loading Minecraft versions...")
        threading.Thread(target=self.fetch_mc_versions, daemon=True).start()

    def fetch_mc_versions(self):
        try:
            url = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            data = r.json()
            versions = [v["id"] for v in data["versions"] if v["type"] == "release"]
            versions.sort(reverse=True)
            self.all_mc_versions = versions
            GLib.idle_add(self.update_mc_list, versions)
        except Exception as e:
            GLib.idle_add(self.show_error, f"Failed to load Minecraft versions: {str(e)}")

    def update_mc_list(self, versions):
        self.mc_spinner.stop()
        self.mc_spinner.set_visible(False)

        if not versions:
            self.mc_entry.set_placeholder_text("No versions found")
            return

        model = Gtk.ListStore(str)
        for v in versions:
            model.append([v])

        completion = Gtk.EntryCompletion()
        completion.set_model(model)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        completion.set_popup_completion(True)

        self.mc_entry.set_completion(completion)
        self.mc_entry.set_text(versions[0])
        self.mc_entry.set_sensitive(True)

        self.on_mc_changed()
        self.mc_entry.connect("changed", self.on_mc_changed)

    def on_mc_changed(self, *args):
        text = self.mc_entry.get_text().strip()
        if text in self.all_mc_versions:
            self.selected_mc = text
            self.load_fabric_loaders(text)
        else:
            self.selected_mc = None
            self.download_button.set_sensitive(False)

    # ----------------------------------------------------------------------
    # 2. LOAD FABRIC LOADER VERSIONS
    # ----------------------------------------------------------------------
    def load_fabric_loaders(self, mc_version):
        self.loader_entry.set_sensitive(False)
        self.loader_entry.set_placeholder_text("Loading Fabric loaders...")
        self.loader_spinner.set_visible(True)
        self.loader_spinner.start()
        self.download_button.set_sensitive(False)
        threading.Thread(target=self.fetch_fabric_loaders, args=(mc_version,), daemon=True).start()

    def fetch_fabric_loaders(self, mc_version):
        try:
            url = f"https://meta.fabricmc.net/v2/versions/loader/{mc_version}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        
            data = response.json()
        
            loaders = []
            if isinstance(data, list):
                for item in data:
                    if 'loader' in item and 'version' in item['loader']:
                        version = item['loader']['version']
                        parts = version.split('.')
                        if len(parts) == 3:
                            if all(part.isdigit() for part in parts):
                                loaders.append(version)
        
            loaders = sorted(list(set(loaders)), reverse=True)
            self.loader_versions = loaders
            GLib.idle_add(self.update_loader_list, loaders)
        
        except Exception as e:
            GLib.idle_add(self.show_error, f"Failed to load Fabric loaders: {str(e)}")

    def update_loader_list(self, versions):
        self.loader_spinner.stop()
        self.loader_spinner.set_visible(False)

        if not versions:
            self.loader_entry.set_placeholder_text("No loaders found for this MC version")
            self.loader_entry.set_sensitive(False)
            return

        model = Gtk.ListStore(str)
        for v in versions:
            model.append([v])

        completion = Gtk.EntryCompletion()
        completion.set_model(model)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        completion.set_popup_completion(True)

        self.loader_entry.set_completion(completion)
        self.loader_entry.set_text(versions[0])
        self.loader_entry.set_sensitive(True)

        self.selected_loader = versions[0]
        self.update_download_button()

        self.loader_entry.connect("changed", self.on_loader_changed)

    def on_loader_changed(self, *args):
        text = self.loader_entry.get_text().strip()
        if text in self.loader_versions:
            self.selected_loader = text
        else:
            self.selected_loader = None
        self.update_download_button()

    # ----------------------------------------------------------------------
    # 3. LOAD FABRIC INSTALLER VERSIONS
    # ----------------------------------------------------------------------
    def load_installer_versions(self):
        self.installer_spinner.set_visible(True)
        self.installer_spinner.start()
        self.installer_entry.set_placeholder_text("Loading installer versions...")
        threading.Thread(target=self.fetch_installer_versions, daemon=True).start()

    def fetch_installer_versions(self):
        try:
            url = "https://maven.fabricmc.net/net/fabricmc/fabric-installer/"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        
            content = response.text
        
            version_pattern = r'href="([1-9][0-9]*\.[0-9]+\.[0-9]+/)"'
            matches = re.findall(version_pattern, content)
        
            versions = [v.rstrip('/') for v in matches]
        
            versions.sort(key=lambda v: [int(x) for x in v.split('.')], reverse=True)
        
            self.installer_versions = versions
            GLib.idle_add(self.update_installer_list, versions)
        
        except Exception as e:
            GLib.idle_add(self.show_error, f"Failed to load installer versions: {str(e)}")

    def update_installer_list(self, versions):
        self.installer_spinner.stop()
        self.installer_spinner.set_visible(False)

        if not versions:
            self.installer_entry.set_placeholder_text("No installer versions found")
            self.installer_entry.set_sensitive(False)
            return

        model = Gtk.ListStore(str)
        for v in versions:
            model.append([v])

        completion = Gtk.EntryCompletion()
        completion.set_model(model)
        completion.set_text_column(0)
        completion.set_inline_completion(True)
        completion.set_popup_completion(True)

        self.installer_entry.set_completion(completion)
        self.installer_entry.set_text(versions[0])
        self.installer_entry.set_sensitive(True)

        self.selected_installer = versions[0]
        self.update_download_button()
        self.installer_entry.connect("changed", self.on_installer_changed)

    def on_installer_changed(self, *args):
        text = self.installer_entry.get_text().strip()
        if text in self.installer_versions:
            self.selected_installer = text
        else:
            self.selected_installer = None
        self.update_download_button()

    def update_download_button(self):
        if self.selected_mc and self.selected_loader and self.selected_installer:
            self.download_button.set_sensitive(True)
        else:
            self.download_button.set_sensitive(False)

    # ----------------------------------------------------------------------
    # 4. DOWNLOAD PROCESS
    # ----------------------------------------------------------------------
    def on_download_clicked(self, btn):
        if not (self.selected_mc and self.selected_loader and self.selected_installer):
            self.show_error("Please select all three versions")
            return

        self.download_button.set_sensitive(False)
        self.mc_entry.set_sensitive(False)
        self.loader_entry.set_sensitive(False)
        self.installer_entry.set_sensitive(False)

        self.progress_bar.set_visible(True)
        self.status_label.set_visible(True)
        self.status_label.set_label(f"Downloading Fabric {self.selected_loader}...")

        threading.Thread(
            target=self.download_fabric_server,
            args=(self.selected_mc, self.selected_loader, self.selected_installer),
            daemon=True
        ).start()

    def download_fabric_server(self, mc_version, loader_version, installer_version):
        try:
            url = f"https://meta.fabricmc.net/v2/versions/loader/{mc_version}/{loader_version}/{installer_version}/server/jar"

            servers_dir = get_servers_dir()
            
            folder_name = f"fabric_{mc_version}"
            folder = Path(servers_dir) / folder_name
            folder.mkdir(parents=True, exist_ok=True)

            jar_path = folder / "server.jar"

            response = requests.get(url, stream=True, timeout=60)
            response.raise_for_status()

            total = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(jar_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total:
                            GLib.idle_add(self.update_progress, downloaded / total)

            eula_path = folder / "eula.txt"
            with open(eula_path, 'w') as f:
                f.write("eula=true\n")

            GLib.idle_add(self.download_complete, f"Fabric {loader_version}", folder_name)

        except Exception as e:
            GLib.idle_add(self.show_error, f"Download failed: {str(e)}")

    def update_progress(self, fraction):
        self.progress_bar.set_fraction(fraction)

    def download_complete(self, version, folder_name):
        self.status_label.set_label(f"✓ Successfully installed {version}!")
        self.progress_bar.set_fraction(1.0)
        GLib.timeout_add(1500, self.close_and_refresh)

    def close_and_refresh(self):
        if self.parent and hasattr(self.parent, "refresh_server_list"):
            self.parent.refresh_server_list()
        self.destroy()
        return False

    # ----------------------------------------------------------------------
    # UTILITIES
    # ----------------------------------------------------------------------
    def show_error(self, msg):
        self.status_label.set_visible(True)
        self.status_label.set_label(f"Error: {msg}")
        self.status_label.add_css_class("error")
        self.download_button.set_sensitive(True)
        self.mc_entry.set_sensitive(True)
        self.loader_entry.set_sensitive(True)
        self.installer_entry.set_sensitive(True)
        self.progress_bar.set_visible(False)
        
        for spinner in [self.mc_spinner, self.loader_spinner, self.installer_spinner]:
            spinner.stop()
            spinner.set_visible(False)
