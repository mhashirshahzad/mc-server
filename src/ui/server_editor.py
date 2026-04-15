from gi.repository import Adw, Gtk
import os
from pathlib import Path
from ui.java_editor import JavaEditorWindow

class ServerEditorWindow(Adw.Window):
    def __init__(self, parent, server_folder, **kwargs):
        super().__init__(**kwargs)
        
        self.server_folder = server_folder
        self.properties_file = server_folder / "server.properties"
        self.properties_data = {}
        
        self.set_title(f"Server Properties - {server_folder.name}")
        self.set_default_size(800, 600)
        self.set_transient_for(parent)
        self.set_modal(True)
        
        # Main layout
        self.content = Adw.ToolbarView()
        
        # Header bar
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Edit Server Properties"))
        
        # Save button
        save_button = Gtk.Button(label="Save")
        save_button.add_css_class("suggested-action")
        save_button.connect("clicked", self.save_properties)
        header.pack_end(save_button)
        
        self.content.add_top_bar(header)
        
        # Scrolled window for preferences
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        
        # Preferences page
        self.preferences_page = Adw.PreferencesPage()
        
        # Load properties
        self.load_properties()
        
        # Create UI sections
        self.create_java_button()
        self.create_basic_settings()
        self.create_gameplay_settings()
        self.create_network_settings()
        self.create_performance_settings()
        self.create_security_settings()
        self.create_advanced_settings()
        
        scrolled.set_child(self.preferences_page)
        self.content.set_content(scrolled)
        
        self.set_content(self.content)
    
    def load_properties(self):
        """Load server.properties file"""
        self.properties_data = {}
        
        if self.properties_file.exists():
            with open(self.properties_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            self.properties_data[key] = value
        
        # Set defaults for missing properties
        defaults = {
            'accepts-transfers': 'false',
            'allow-flight': 'false',
            'broadcast-console-to-ops': 'true',
            'broadcast-rcon-to-ops': 'true',
            'difficulty': 'hard',
            'enable-jmx-monitoring': 'false',
            'enable-query': 'false',
            'enable-rcon': 'false',
            'enable-status': 'true',
            'enforce-secure-profile': 'true',
            'enforce-whitelist': 'false',
            'entity-broadcast-range-percentage': '100',
            'force-gamemode': 'false',
            'function-permission-level': '2',
            'gamemode': 'survival',
            'generate-structures': 'true',
            'hardcore': 'true',
            'hide-online-players': 'false',
            'log-ips': 'true',
            'max-players': '20',
            'motd': 'A Minecraft Server',
            'network-compression-threshold': '256',
            'online-mode': 'false',
            'op-permission-level': '4',
            'pause-when-empty-seconds': '60',
            'player-idle-timeout': '0',
            'prevent-proxy-connections': 'false',
            'rate-limit': '0',
            'require-resource-pack': 'false',
            'server-port': '25565',
            'simulation-distance': '10',
            'spawn-protection': '16',
            'sync-chunk-writes': 'true',
            'use-native-transport': 'true',
            'view-distance': '10',
            'white-list': 'false',
        }
        
        for key, default_value in defaults.items():
            if key not in self.properties_data:
                self.properties_data[key] = default_value


    def create_java_button(self):
        """Add a button to open Java settings"""
        group = Adw.PreferencesGroup(title="Java Settings")
    
        # Button row
        button_row = Adw.ActionRow(title="Configure Java")
        button_row.set_subtitle("Memory allocation and Java path")
    
        config_button = Gtk.Button(label="Configure...")
        config_button.add_css_class("suggested-action")
        config_button.connect("clicked", self.on_java_settings_clicked)
        button_row.add_suffix(config_button)
    
        group.add(button_row)
        self.preferences_page.add(group)

    def on_java_settings_clicked(self, button):
        """Open Java settings dialog"""
        dialog = JavaEditorWindow(parent=self, server_folder=self.server_folder)
        dialog.present()

    def create_basic_settings(self):
        """Basic server settings section"""
        group = Adw.PreferencesGroup(title="Basic Settings")
        
        # Server Name (MOTD)
        motd_row = Adw.EntryRow(title="Server Name (MOTD)")
        motd_row.set_text(self.properties_data.get('motd', 'A Minecraft Server'))
        motd_row.connect("changed", self.on_entry_changed, 'motd')
        group.add(motd_row)
        
        # Server Port
        port_row = Adw.EntryRow(title="Server Port")
        port_row.set_text(self.properties_data.get('server-port', '25565'))
        port_row.connect("changed", self.on_entry_changed, 'server-port')
        group.add(port_row)
        
        # Max Players
        max_players_row = Adw.SpinRow()
        max_players_row.set_title("Max Players")
        max_players_row.set_range(1, 100)
        max_players_row.set_value(int(self.properties_data.get('max-players', '20')))
        max_players_row.connect("changed", self.on_spin_changed, 'max-players')
        group.add(max_players_row)
        
        # World Name
        level_name_row = Adw.EntryRow(title="World Name")
        level_name_row.set_text(self.properties_data.get('level-name', 'world'))
        level_name_row.connect("changed", self.on_entry_changed, 'level-name')
        group.add(level_name_row)
        
        # World Seed
        level_seed_row = Adw.EntryRow(title="World Seed")
        level_seed_row.set_text(self.properties_data.get('level-seed', ''))
        # level_seed_row.set_placeholder_text("Random seed if empty")
        level_seed_row.connect("changed", self.on_entry_changed, 'level-seed')
        group.add(level_seed_row)
        
        self.preferences_page.add(group)
    
    def create_gameplay_settings(self):
        """Gameplay settings section"""
        group = Adw.PreferencesGroup(title="Gameplay Settings")
        
        # Difficulty
        difficulty_row = Adw.ComboRow()
        difficulty_row.set_title("Difficulty")
        difficulty_model = Gtk.StringList()
        for diff in ['peaceful', 'easy', 'normal', 'hard']:
            difficulty_model.append(diff)
        difficulty_row.set_model(difficulty_model)
        current_diff = self.properties_data.get('difficulty', 'hard')
        difficulty_row.set_selected(['peaceful', 'easy', 'normal', 'hard'].index(current_diff))
        difficulty_row.connect("notify::selected", self.on_difficulty_changed)
        group.add(difficulty_row)
        
        # Gamemode
        gamemode_row = Adw.ComboRow()
        gamemode_row.set_title("Default Gamemode")
        gamemode_model = Gtk.StringList()
        for mode in ['survival', 'creative', 'adventure', 'spectator']:
            gamemode_model.append(mode)
        gamemode_row.set_model(gamemode_model)
        current_mode = self.properties_data.get('gamemode', 'survival')
        gamemode_row.set_selected(['survival', 'creative', 'adventure', 'spectator'].index(current_mode))
        gamemode_row.connect("notify::selected", self.on_gamemode_changed)
        group.add(gamemode_row)
        
        # Hardcore mode
        hardcore_row = Adw.SwitchRow()
        hardcore_row.set_title("Hardcore Mode")
        hardcore_row.set_subtitle("Players don't respawn after death")
        hardcore_row.set_active(self.properties_data.get('hardcore', 'true') == 'true')
        hardcore_row.connect("notify::active", self.on_switch_changed, 'hardcore')
        group.add(hardcore_row)
        
        # Allow Flight
        allow_flight_row = Adw.SwitchRow()
        allow_flight_row.set_title("Allow Flight")
        allow_flight_row.set_subtitle("Allow players to fly in survival mode")
        allow_flight_row.set_active(self.properties_data.get('allow-flight', 'false') == 'true')
        allow_flight_row.connect("notify::active", self.on_switch_changed, 'allow-flight')
        group.add(allow_flight_row)
        
        # Force Gamemode
        force_gamemode_row = Adw.SwitchRow()
        force_gamemode_row.set_title("Force Gamemode")
        force_gamemode_row.set_subtitle("Force players to join in default gamemode")
        force_gamemode_row.set_active(self.properties_data.get('force-gamemode', 'false') == 'true')
        force_gamemode_row.connect("notify::active", self.on_switch_changed, 'force-gamemode')
        group.add(force_gamemode_row)
        
        # Generate Structures
        structures_row = Adw.SwitchRow()
        structures_row.set_title("Generate Structures")
        structures_row.set_subtitle("Generate villages, dungeons, etc.")
        structures_row.set_active(self.properties_data.get('generate-structures', 'true') == 'true')
        structures_row.connect("notify::active", self.on_switch_changed, 'generate-structures')
        group.add(structures_row)
        
        self.preferences_page.add(group)
    
    def create_network_settings(self):
        """Network settings section"""
        group = Adw.PreferencesGroup(title="Network Settings")
        
        # Online Mode
        online_mode_row = Adw.SwitchRow()
        online_mode_row.set_title("Online Mode")
        online_mode_row.set_subtitle("Verify player identities with Mojang servers")
        online_mode_row.set_active(self.properties_data.get('online-mode', 'false') == 'true')
        online_mode_row.connect("notify::active", self.on_switch_changed, 'online-mode')
        group.add(online_mode_row)
        
        # Enable Status
        enable_status_row = Adw.SwitchRow()
        enable_status_row.set_title("Enable Server Status")
        enable_status_row.set_subtitle("Allow server to appear in server list")
        enable_status_row.set_active(self.properties_data.get('enable-status', 'true') == 'true')
        enable_status_row.connect("notify::active", self.on_switch_changed, 'enable-status')
        group.add(enable_status_row)
        
        # Enable Query
        enable_query_row = Adw.SwitchRow()
        enable_query_row.set_title("Enable Query")
        enable_query_row.set_subtitle("Enable GameSpy4 query protocol")
        enable_query_row.set_active(self.properties_data.get('enable-query', 'false') == 'true')
        enable_query_row.connect("notify::active", self.on_switch_changed, 'enable-query')
        group.add(enable_query_row)
        
        # Enable RCON
        enable_rcon_row = Adw.SwitchRow()
        enable_rcon_row.set_title("Enable RCON")
        enable_rcon_row.set_subtitle("Enable remote console access")
        enable_rcon_row.set_active(self.properties_data.get('enable-rcon', 'false') == 'true')
        enable_rcon_row.connect("notify::active", self.on_switch_changed, 'enable-rcon')
        group.add(enable_rcon_row)
        
        # RCON Password
        rcon_password_row = Adw.PasswordEntryRow(title="RCON Password")
        rcon_password_row.set_text(self.properties_data.get('rcon.password', ''))
        rcon_password_row.connect("changed", self.on_entry_changed, 'rcon.password')
        group.add(rcon_password_row)
        
        # View Distance
        view_distance_row = Adw.SpinRow()
        view_distance_row.set_title("View Distance")
        view_distance_row.set_range(3, 32)
        view_distance_row.set_value(int(self.properties_data.get('view-distance', '10')))
        view_distance_row.connect("changed", self.on_spin_changed, 'view-distance')
        group.add(view_distance_row)
        
        # Simulation Distance
        sim_distance_row = Adw.SpinRow()
        sim_distance_row.set_title("Simulation Distance")
        sim_distance_row.set_range(3, 32)
        sim_distance_row.set_value(int(self.properties_data.get('simulation-distance', '10')))
        sim_distance_row.connect("changed", self.on_spin_changed, 'simulation-distance')
        group.add(sim_distance_row)
        
        self.preferences_page.add(group)
    
    def create_performance_settings(self):
        """Performance settings section"""
        group = Adw.PreferencesGroup(title="Performance Settings")
        
        # Max Tick Time
        max_tick_row = Adw.SpinRow()
        max_tick_row.set_title("Max Tick Time")
        max_tick_row.set_subtitle("Maximum time in milliseconds a tick can take")
        max_tick_row.set_range(0, 60000)
        max_tick_row.set_value(int(self.properties_data.get('max-tick-time', '60000')))
        max_tick_row.connect("changed", self.on_spin_changed, 'max-tick-time')
        group.add(max_tick_row)
        
        # Network Compression Threshold
        compression_row = Adw.SpinRow()
        compression_row.set_title("Network Compression Threshold")
        compression_row.set_range(-1, 65536)
        compression_row.set_value(int(self.properties_data.get('network-compression-threshold', '256')))
        compression_row.connect("changed", self.on_spin_changed, 'network-compression-threshold')
        group.add(compression_row)
        
        # Entity Broadcast Range
        broadcast_row = Adw.SpinRow()
        broadcast_row.set_title("Entity Broadcast Range %")
        broadcast_row.set_range(10, 1000)
        broadcast_row.set_value(int(self.properties_data.get('entity-broadcast-range-percentage', '100')))
        broadcast_row.connect("changed", self.on_spin_changed, 'entity-broadcast-range-percentage')
        group.add(broadcast_row)
        
        # Use Native Transport
        native_transport_row = Adw.SwitchRow()
        native_transport_row.set_title("Use Native Transport")
        native_transport_row.set_subtitle("Use native Linux network transport")
        native_transport_row.set_active(self.properties_data.get('use-native-transport', 'true') == 'true')
        native_transport_row.connect("notify::active", self.on_switch_changed, 'use-native-transport')
        group.add(native_transport_row)
        
        self.preferences_page.add(group)
    
    def create_security_settings(self):
        """Security settings section"""
        group = Adw.PreferencesGroup(title="Security Settings")
        
        # White List
        whitelist_row = Adw.SwitchRow()
        whitelist_row.set_title("White List")
        whitelist_row.set_subtitle("Only whitelisted players can join")
        whitelist_row.set_active(self.properties_data.get('white-list', 'false') == 'true')
        whitelist_row.connect("notify::active", self.on_switch_changed, 'white-list')
        group.add(whitelist_row)
        
        # Enforce White List
        enforce_whitelist_row = Adw.SwitchRow()
        enforce_whitelist_row.set_title("Enforce White List")
        enforce_whitelist_row.set_subtitle("Kick players not on whitelist")
        enforce_whitelist_row.set_active(self.properties_data.get('enforce-whitelist', 'false') == 'true')
        enforce_whitelist_row.connect("notify::active", self.on_switch_changed, 'enforce-whitelist')
        group.add(enforce_whitelist_row)
        
        # Enforce Secure Profile
        secure_profile_row = Adw.SwitchRow()
        secure_profile_row.set_title("Enforce Secure Profile")
        secure_profile_row.set_subtitle("Require chat signing")
        secure_profile_row.set_active(self.properties_data.get('enforce-secure-profile', 'true') == 'true')
        secure_profile_row.connect("notify::active", self.on_switch_changed, 'enforce-secure-profile')
        group.add(secure_profile_row)
        
        # Prevent Proxy Connections
        prevent_proxy_row = Adw.SwitchRow()
        prevent_proxy_row.set_title("Prevent Proxy Connections")
        prevent_proxy_row.set_subtitle("Block connections from proxies/VPNs")
        prevent_proxy_row.set_active(self.properties_data.get('prevent-proxy-connections', 'false') == 'true')
        prevent_proxy_row.connect("notify::active", self.on_switch_changed, 'prevent-proxy-connections')
        group.add(prevent_proxy_row)
        
        # Log IPs
        log_ips_row = Adw.SwitchRow()
        log_ips_row.set_title("Log IPs")
        log_ips_row.set_active(self.properties_data.get('log-ips', 'true') == 'true')
        log_ips_row.connect("notify::active", self.on_switch_changed, 'log-ips')
        group.add(log_ips_row)
        
        self.preferences_page.add(group)
    
    def create_advanced_settings(self):
        """Advanced settings section"""
        group = Adw.PreferencesGroup(title="Advanced Settings")
        
        # Spawn Protection
        spawn_protection_row = Adw.SpinRow()
        spawn_protection_row.set_title("Spawn Protection")
        spawn_protection_row.set_range(0, 64)
        spawn_protection_row.set_value(int(self.properties_data.get('spawn-protection', '16')))
        spawn_protection_row.connect("changed", self.on_spin_changed, 'spawn-protection')
        group.add(spawn_protection_row)
        
        # OP Permission Level
        op_level_row = Adw.ComboRow()
        op_level_row.set_title("OP Permission Level")
        op_model = Gtk.StringList()
        for level in ['1 - Bypass spawn protection', '2 - Use commands', '3 - Manage players', '4 - All permissions']:
            op_model.append(level)
        op_level_row.set_model(op_model)
        op_value = int(self.properties_data.get('op-permission-level', '4')) - 1
        op_level_row.set_selected(op_value)
        op_level_row.connect("notify::selected", self.on_opperm_changed)
        group.add(op_level_row)
        
        # Function Permission Level
        func_level_row = Adw.ComboRow()
        func_level_row.set_title("Function Permission Level")
        func_model = Gtk.StringList()
        for level in ['1', '2', '3', '4']:
            func_model.append(level)
        func_level_row.set_model(func_model)
        func_value = int(self.properties_data.get('function-permission-level', '2')) - 1
        func_level_row.set_selected(func_value)
        func_level_row.connect("notify::selected", self.on_funcperm_changed)
        group.add(func_level_row)
        
        # Player Idle Timeout
        idle_timeout_row = Adw.SpinRow()
        idle_timeout_row.set_title("Player Idle Timeout (minutes)")
        idle_timeout_row.set_range(0, 60)
        idle_timeout_row.set_value(int(self.properties_data.get('player-idle-timeout', '0')))
        idle_timeout_row.set_subtitle("0 = disabled")
        idle_timeout_row.connect("changed", self.on_spin_changed, 'player-idle-timeout')
        group.add(idle_timeout_row)
        
        # Rate Limit
        rate_limit_row = Adw.SpinRow()
        rate_limit_row.set_title("Rate Limit")
        rate_limit_row.set_range(0, 100)
        rate_limit_row.set_value(int(self.properties_data.get('rate-limit', '0')))
        rate_limit_row.set_subtitle("Max packets per second, 0 = unlimited")
        rate_limit_row.connect("changed", self.on_spin_changed, 'rate-limit')
        group.add(rate_limit_row)
        
        self.preferences_page.add(group)

        
    # Event handlers
    def on_entry_changed(self, entry, key):
        self.properties_data[key] = entry.get_text()
    
    def on_spin_changed(self, spin_row, *args):
        # The key is stored as callback data
        key = args[0] if args else None
        if key:
            self.properties_data[key] = str(int(spin_row.get_value()))
    
    def on_switch_changed(self, switch_row, *args):
        # notify::active passes the GParamSpec as second argument
        key = args[0] if args else None
        if key:
            self.properties_data[key] = 'true' if switch_row.get_active() else 'false'
    
    def on_difficulty_changed(self, combo_row, *args):
        difficulties = ['peaceful', 'easy', 'normal', 'hard']
        selected = combo_row.get_selected()
        self.properties_data['difficulty'] = difficulties[selected]
    
    def on_gamemode_changed(self, combo_row, *args):
        gamemodes = ['survival', 'creative', 'adventure', 'spectator']
        selected = combo_row.get_selected()
        self.properties_data['gamemode'] = gamemodes[selected]
    
    def on_opperm_changed(self, combo_row, *args):
        selected = combo_row.get_selected()
        self.properties_data['op-permission-level'] = str(selected + 1)
    
    def on_funcperm_changed(self, combo_row, *args):
        selected = combo_row.get_selected()
        self.properties_data['function-permission-level'] = str(selected + 1)    

    # Save button
    def save_properties(self, button):
        """Save all properties to server.properties"""
        # Write comments header
        content = "#Minecraft server properties\n"
        content += f"#{self.get_timestamp()}\n"
        
        # Write all properties
        for key, value in sorted(self.properties_data.items()):
            content += f"{key}={value}\n"
        
        # Save file
        with open(self.properties_file, 'w') as f:
            f.write(content)
        
        self.close()
    
    def get_timestamp(self):
        """Get current timestamp for file header"""
        from datetime import datetime
        return datetime.now().strftime("%a %b %d %H:%M:%S %Y")
