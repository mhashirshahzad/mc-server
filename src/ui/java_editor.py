from gi.repository import Adw, Gtk, GLib
from pathlib import Path

class JavaEditorWindow(Adw.Window):
    def __init__(self, parent, server_folder, **kwargs):
        super().__init__(**kwargs)
        
        self.server_folder = Path(server_folder)
        self.java_properties_file = self.server_folder / "java.properties"
        self.java_data = {}
        
        self.set_title(f"Java Settings - {self.server_folder.name}")
        self.set_default_size(500, 450)
        self.set_transient_for(parent)
        self.set_modal(True)
        
        # Main layout
        self.content = Adw.ToolbarView()
        
        # Header bar
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Edit Java Settings"))
        
        # Save button
        save_button = Gtk.Button(label="Save")
        save_button.add_css_class("suggested-action")
        save_button.connect("clicked", self.save_settings)
        header.pack_end(save_button)
        
        self.content.add_top_bar(header)
        
        # Scrolled window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        
        # Preferences page
        self.preferences_page = Adw.PreferencesPage()
        
        # Load existing settings
        self.load_settings()
        
        # Create UI
        self.create_java_settings()
        
        scrolled.set_child(self.preferences_page)
        self.content.set_content(scrolled)
        
        self.set_content(self.content)
    
    def load_settings(self):
        """Load java.properties file"""
        self.java_data = {}
        
        if self.java_properties_file.exists():
            with open(self.java_properties_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            self.java_data[key] = value
        
        # Set defaults
        defaults = {
            'java-path': 'java',
            'min-ram': '1',
            'max-ram': '2',
        }
        
        for key, default_value in defaults.items():
            if key not in self.java_data:
                self.java_data[key] = default_value
    
    def create_java_settings(self):
        """Create Java settings UI"""
        group = Adw.PreferencesGroup(title="Java Configuration")
        
        # Java Path
        java_path_row = Adw.EntryRow(title="Java Path")
        java_path_row.set_text(self.java_data.get('java-path', 'java'))
        java_path_row.set_tooltip_text("Path to Java executable (e.g., java, /usr/bin/java)")
        java_path_row.connect("changed", self.on_java_path_changed)
        group.add(java_path_row)
        
        # Minimum RAM (GB)
        min_ram_row = Adw.SpinRow()
        min_ram_row.set_title("Minimum RAM (GB)")
        min_ram_row.set_subtitle("Initial heap size (-Xms)")
        min_ram_row.set_range(0.5, 32)
        min_ram_row.set_value(float(self.java_data.get('min-ram', '1')))
        min_ram_row.set_digits(1)
        min_ram_row.connect("notify::value", self.on_min_ram_changed)
        group.add(min_ram_row)
        
        # Maximum RAM (GB)
        max_ram_row = Adw.SpinRow()
        max_ram_row.set_title("Maximum RAM (GB)")
        max_ram_row.set_subtitle("Maximum heap size (-Xmx)")
        max_ram_row.set_range(0.5, 64)
        max_ram_row.set_value(float(self.java_data.get('max-ram', '2')))
        max_ram_row.set_digits(1)
        max_ram_row.connect("notify::value", self.on_max_ram_changed)
        group.add(max_ram_row)
        
        self.preferences_page.add(group)
        
        # Preview section
        preview_group = Adw.PreferencesGroup(title="Command Preview")
        
        # Use a label inside an ActionRow for better styling
        preview_row = Adw.ActionRow()
        self.preview_label = Gtk.Label()
        self.preview_label.set_halign(Gtk.Align.START)
        self.preview_label.set_selectable(True)
        self.preview_label.set_margin_top(6)
        self.preview_label.set_margin_bottom(6)
        self.preview_label.set_margin_start(6)
        self.preview_label.set_margin_end(6)
        preview_row.set_child(self.preview_label)
        preview_group.add(preview_row)
        
        self.preferences_page.add(preview_group)
        
        # Store references for later updates
        self.java_path_row = java_path_row
        self.min_ram_row = min_ram_row
        self.max_ram_row = max_ram_row
        
        # Update preview initially
        self.update_preview()
    
    def on_java_path_changed(self, entry):
        """Handle Java path change"""
        self.java_data['java-path'] = entry.get_text()
        self.update_preview()
    
    def on_min_ram_changed(self, spin_row, *args):
        """Handle min RAM change"""
        self.java_data['min-ram'] = str(spin_row.get_value())
        self.update_preview()
    
    def on_max_ram_changed(self, spin_row, *args):
        """Handle max RAM change"""
        self.java_data['max-ram'] = str(spin_row.get_value())
        self.update_preview()
    
    def update_preview(self):
        """Update the command preview"""
        cmd = self.get_java_command()
        self.preview_label.set_text(cmd)
    
    def get_java_command(self):
        """Get the full Java command"""
        java_path = self.java_data.get('java-path', 'java')
        
        # Get RAM values safely
        try:
            min_ram = float(self.java_data.get('min-ram', '1'))
        except:
            min_ram = 1.0
        
        try:
            max_ram = float(self.java_data.get('max-ram', '2'))
        except:
            max_ram = 2.0
        
        # Format RAM values (e.g., 1 -> 1G, 1.5 -> 1536M)
        if min_ram == int(min_ram):
            min_ram_str = f"{int(min_ram)}G"
        else:
            min_ram_str = f"{int(min_ram * 1024)}M"
        
        if max_ram == int(max_ram):
            max_ram_str = f"{int(max_ram)}G"
        else:
            max_ram_str = f"{int(max_ram * 1024)}M"
        
        return f"{java_path} -Xms{min_ram_str} -Xmx{max_ram_str} -jar server.jar nogui"
    
    def save_settings(self, button):
        """Save Java settings to file"""
        content = "# Java settings for Grassy\n"
        content += f"# Generated by Grassy Server Manager\n\n"
        
        # Only save string values, not GObject properties
        for key, value in self.java_data.items():
            if isinstance(value, str):  # Only save string values
                content += f"{key}={value}\n"
        
        with open(self.java_properties_file, 'w') as f:
            f.write(content)
        
        self.close()
