import appdirs
import os
from pathlib import Path


def get_servers_dir():
    """Get the servers directory from settings.txt or return default"""
    config_dir = appdirs.user_config_dir("grassy")
    settings_file = os.path.join(config_dir, "settings.txt")
    data_dir = appdirs.user_data_dir("grassy")
    default_dir = os.path.join(data_dir, "servers")
    
    if os.path.exists(settings_file):
        try:
            with open(settings_file, "r") as f:
                saved = f.read().strip()
                if saved:
                    return saved
        except:
            pass
    
    os.makedirs(default_dir, exist_ok=True)
    
    # Save the default path to settings.txt
    try:
        os.makedirs(config_dir, exist_ok=True)
        with open(settings_file, "w") as f:
            f.write(default_dir)
    except:
        pass
    
    return default_dir


def save_servers_dir(path):
    """Save the servers directory to settings.txt"""
    config_dir = appdirs.user_config_dir("grassy")
    settings_file = os.path.join(config_dir, "settings.txt")
    
    try:
        os.makedirs(config_dir, exist_ok=True)
        with open(settings_file, "w") as f:
            f.write(path)
        return True
    except:
        return False

def kill_process_on_port(port=25565):
    """Kill any process using the specified port"""
    import subprocess
    import os
    import signal
    
    try:
        # Find process using the port
        result = subprocess.run(
            f"lsof -t -i:{port}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        pids = result.stdout.strip().split()
        
        for pid in pids:
            if pid:
                try:
                    os.kill(int(pid), signal.SIGKILL)
                    print(f"Killed process {pid} on port {port}")
                except:
                    pass
        
        return len(pids)
    except Exception as e:
        print(f"Error killing process on port {port}: {e}")
        return 0
