use std::env;

mod app;
mod server;
mod state;

use app::McManagerApp;

fn main() -> eframe::Result<()> {
    let options = eframe::NativeOptions::default();

    env::set_current_dir("servers").expect("Error changing dir.");
    eframe::run_native(
        "Minecraft Server Manager",
        options,
        Box::new(|_| Ok(Box::new(McManagerApp::new()))),
    )
}

