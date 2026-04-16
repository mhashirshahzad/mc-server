from gi.repository import Gtk, Gdk, Gio


class PlayerPanel:
    def __init__(self, command_handler):
        self.command_handler = command_handler
        self.players = {}  # {player_name: {"uuid": "", "widget": row}}
        
        # Create container
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.box.set_margin_top(6)
        self.box.set_margin_bottom(6)
        self.box.set_margin_start(6)
        self.box.set_margin_end(6)
        
        # Title row with refresh button
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        title_box.set_halign(Gtk.Align.FILL)
        
        title = Gtk.Label(label="Online Players")
        title.add_css_class("heading")
        title.set_halign(Gtk.Align.START)
        title.set_hexpand(True)
        title_box.append(title)
        
        # Refresh button
        refresh_button = Gtk.Button.new_from_icon_name("view-refresh-symbolic")
        refresh_button.set_tooltip_text("Refresh player list")
        refresh_button.add_css_class("flat")
        refresh_button.connect("clicked", self.on_refresh_clicked)
        title_box.append(refresh_button)
        
        self.box.append(title_box)
        
        # Player count label
        self.count_label = Gtk.Label(label="0 players online")
        self.count_label.set_halign(Gtk.Align.START)
        self.count_label.add_css_class("dim-label")
        self.box.append(self.count_label)
        
        # Separator
        sep = Gtk.Separator()
        sep.set_margin_top(6)
        sep.set_margin_bottom(6)
        self.box.append(sep)
        
        # Player list (scrollable)
        self.player_list = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.player_list.set_vexpand(True)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_child(self.player_list)
        self.box.append(scrolled)
    
    def get_widget(self):
        """Return the box widget to add to UI"""
        return self.box
    
    def on_refresh_clicked(self, button):
        """Refresh the player list"""
        self.command_handler.list_players()

    def update_players(self, player_names):
        """Update the player list with current online players"""
        print(f"DEBUG: update_players called with: {player_names}")  # Debug
    
        # Remove players not in the list
        for name in list(self.players.keys()):
            if name not in player_names:
                self.remove_player(name)
    
        # Add new players
        for name in player_names:
            if name not in self.players:
                self.add_player(name)
    
        count = len(player_names)
        self.count_label.set_text(f"{count} player{'s' if count != 1 else ''} online")    

    def add_player(self, player_name):
        """Add a player to the list"""
        if player_name in self.players:
            return
        
        # Create player row
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        row.set_margin_top(3)
        row.set_margin_bottom(3)
        
        # Player icon
        icon = Gtk.Image.new_from_icon_name("avatar-default-symbolic")
        icon.set_pixel_size(24)
        row.append(icon)
        
        # Player name
        name_label = Gtk.Label(label=player_name)
        name_label.set_halign(Gtk.Align.START)
        name_label.set_hexpand(True)
        row.append(name_label)
        
        # Actions menu button
        menu_button = Gtk.MenuButton()
        menu_button.set_icon_name("view-more-symbolic")
        
        # Create popover menu
        popover = Gtk.PopoverMenu()
        menu_model = Gio.Menu()
        
        # Add menu actions
        menu_model.append("Kick", f"player.kick.{player_name}")
        menu_model.append("Ban", f"player.ban.{player_name}")
        menu_model.append("OP", f"player.op.{player_name}")
        menu_model.append("Deop", f"player.deop.{player_name}")
        menu_model.append("Teleport to me", f"player.tp_here.{player_name}")
        menu_model.append("Teleport to player", f"player.tp_to.{player_name}")
        menu_model.append("Gamemode Survival", f"player.gm_survival.{player_name}")
        menu_model.append("Gamemode Creative", f"player.gm_creative.{player_name}")
        menu_model.append("Gamemode Adventure", f"player.gm_adventure.{player_name}")
        menu_model.append("Gamemode Spectator", f"player.gm_spectator.{player_name}")
        
        popover.set_menu_model(menu_model)
        menu_button.set_popover(popover)
        
        # Create actions for this player
        self.create_player_actions(player_name)
        
        row.append(menu_button)
        
        self.player_list.append(row)
        self.players[player_name] = {"widget": row, "uuid": None}
    
    def create_player_actions(self, player_name):
        """Create Gio actions for player management"""
        
        actions = {
            f"kick.{player_name}": lambda: self.command_handler.kick_player(player_name),
            f"ban.{player_name}": lambda: self.command_handler.ban_player(player_name),
            f"op.{player_name}": lambda: self.command_handler.op_player(player_name),
            f"deop.{player_name}": lambda: self.command_handler.deop_player(player_name),
            f"tp_here.{player_name}": lambda: self.command_handler.teleport(player_name, "@p"),
            f"tp_to.{player_name}": lambda: self.command_handler.teleport("@p", player_name),
            f"gm_survival.{player_name}": lambda: self.command_handler.gamemode(player_name, "survival"),
            f"gm_creative.{player_name}": lambda: self.command_handler.gamemode(player_name, "creative"),
            f"gm_adventure.{player_name}": lambda: self.command_handler.gamemode(player_name, "adventure"),
            f"gm_spectator.{player_name}": lambda: self.command_handler.gamemode(player_name, "spectator"),
        }
        
        for action_name, callback in actions.items():
            action = Gio.SimpleAction.new(action_name.split('.')[-1], None)
            action.connect("activate", lambda a, p, cb=callback: cb())
            self.command_handler.window.add_action(action)
    
    def remove_player(self, player_name):
        """Remove a player from the list"""
        if player_name in self.players:
            self.player_list.remove(self.players[player_name]["widget"])
            del self.players[player_name]
    
    def set_player_uuid(self, player_name, uuid):
        """Store player UUID for inventory viewing"""
        if player_name in self.players:
            self.players[player_name]["uuid"] = uuid
