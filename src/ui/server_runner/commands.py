import os


class CommandHandler:
    def __init__(self, window):
        self.window = window
    
    def send_command(self, command):
        """Send a command to the server via PTY"""
        if not self.window.process or self.window.pty_master is None:
            self.window.append_console("Server is not running\n")
            return False
        
        try:
            # Write directly to PTY (this replaces screen)
            os.write(self.window.pty_master, (command + "\n").encode())

            # Echo command in console UI
            self.window.append_console(f"> {command}\n")
            return True

        except Exception as e:
            self.window.append_console(f"Failed to send command: {e}\n")
            return False
    
    def kick_player(self, player_name, reason="No reason"):
        return self.send_command(f"kick {player_name} {reason}")
    
    def ban_player(self, player_name, reason="Banned by operator"):
        return self.send_command(f"ban {player_name} {reason}")
    
    def pardon_player(self, player_name):
        return self.send_command(f"pardon {player_name}")
    
    def op_player(self, player_name):
        return self.send_command(f"op {player_name}")
    
    def deop_player(self, player_name):
        return self.send_command(f"deop {player_name}")
    
    def teleport(self, player_name, target):
        return self.send_command(f"tp {player_name} {target}")
    
    def gamemode(self, player_name, mode):
        return self.send_command(f"gamemode {mode} {player_name}")
    
    def give_item(self, player_name, item, amount=1):
        return self.send_command(f"give {player_name} {item} {amount}")
    
    def list_players(self):
        return self.send_command("list")
    
    def get_player_inventory(self, player_name):
        return self.send_command(f"data get entity {player_name} Inventory")
    
    def get_player_health(self, player_name):
        return self.send_command(f"data get entity {player_name} Health")
    
    def get_player_position(self, player_name):
        return self.send_command(f"data get entity {player_name} Pos")
    
    def set_time(self, time_value):
        return self.send_command(f"time set {time_value}")
    
    def add_time(self, amount):
        return self.send_command(f"time add {amount}")
    
    def set_weather(self, weather_type):
        return self.send_command(f"weather {weather_type}")
    
    def save_all(self):
        return self.send_command("save-all")
    
    def save_off(self):
        return self.send_command("save-off")
    
    def save_on(self):
        return self.send_command("save-on")
    
    def stop_server(self):
        return self.send_command("stop")
    
    def reload_server(self):
        return self.send_command("reload")
    
    def seed(self):
        return self.send_command("seed")
    
    def spawn(self, player_name):
        return self.send_command(f"spawnpoint {player_name}")
    
    def heal_player(self, player_name):
        return self.send_command(f"effect give {player_name} minecraft:instant_health 1 255")
    
    def feed_player(self, player_name):
        return self.send_command(f"effect give {player_name} minecraft:saturation 1 255")
    
    def clear_inventory(self, player_name):
        return self.send_command(f"clear {player_name}")
    
    def kill_player(self, player_name):
        return self.send_command(f"kill {player_name}")
    
    def whisper(self, player_name, message):
        return self.send_command(f"msg {player_name} {message}")
    
    def broadcast(self, message):
        return self.send_command(f"say {message}")
    
    def set_spawn(self):
        return self.send_command("setworldspawn")
    
    def get_player_list(self):
        return self.send_command("list uuids")
