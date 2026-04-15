# Grassy
 A beautiful and easy-to-use Minecraft server manager built with Python and GTK4/libadwaita.

### Main window
![Main Window][assets/main_window.png]

### Settings
![Settings][assets/settings.png]

### Server Settings
![Server Settings][assets/server_settings.png]

### Dependencies
Arch:

```bash
sudo pacman -S python-gobject gtk4 libadwaita gobject-introspection make
```
Fedora:

```bash
sudo dnf install python3-gobject gtk4 libadwaita make
```

Debian/Ubuntu:

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 libadwaita-1-0 make
```
### Running

```bash
git clone https://github.com/mhashirshahzad/grassy

cd grassy

make run
```
