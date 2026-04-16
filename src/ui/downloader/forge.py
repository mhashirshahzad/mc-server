from gi.repository import Adw, Gtk


class ForgeDownloaderWindow(Adw.Window):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)

        self.parent = parent
        self.set_title("Download Forge Server")
        self.set_default_size(600, 500)
        self.set_transient_for(parent)
        self.set_modal(True)

        # UI setup
        self.content = Adw.ToolbarView()

        # Header
        header = Adw.HeaderBar()
        header.set_title_widget(Gtk.Label(label="Download Forge Server"))

        cancel_button = Gtk.Button(label="Close")
        cancel_button.connect("clicked", lambda x: self.destroy())
        header.pack_end(cancel_button)

        self.content.add_top_bar(header)

        # Main layout
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_margin_top(48)
        main_box.set_margin_bottom(48)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        main_box.set_valign(Gtk.Align.CENTER)
        main_box.set_halign(Gtk.Align.CENTER)

        # Info icon
        icon = Gtk.Image.new_from_icon_name("dialog-information-symbolic")
        icon.set_pixel_size(64)
        main_box.append(icon)

        # Message
        label = Gtk.Label(label="Forge Support Coming Soon")
        label.add_css_class("title-1")
        main_box.append(label)

        sublabel = Gtk.Label(label="Forge server download will be added in a future update")
        sublabel.add_css_class("dim-label")
        main_box.append(sublabel)

        # Close button
        close_button = Gtk.Button(label="Close")
        close_button.add_css_class("suggested-action")
        close_button.connect("clicked", lambda x: self.destroy())
        main_box.append(close_button)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_child(main_box)
        self.content.set_content(scrolled)
        self.set_content(self.content)
