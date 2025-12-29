use colored::Colorize;
use std::process::{Child, Command};

macro_rules! logln {
    ($($arg:tt)*) => {
        println!(
            "{} {}",
            "[Server]".green().bold(),
            format!($($arg)*)
        );
    };
}

#[derive(clap::ValueEnum, Clone)]
pub enum ServerAction {
    Start,
    Stop,
    Restart,
    Status,
    Download,
}

pub fn handle_server(action: ServerAction) {
    match action {
        ServerAction::Start => start_server(),
        ServerAction::Stop => stop_server(),
        ServerAction::Restart => {
            stop_server();
            start_server();
        }
        ServerAction::Download => {
            let _ = download_server();
        }
        ServerAction::Status => server_status(),
    }
}

fn start_server() {
    logln!("Starting Minecraft server...");
    let _child = Command::new("java")
        .arg("-Xmx2G")
        .arg("-Xms1G")
        .arg("-jar")
        .arg("servers/server.jar")
        .arg("nogui")
        .spawn()
        .expect("Failed to start server");
}

fn download_server() -> Result<(), Box<dyn std::error::Error>> {
    use std::fs::{self, File};
    use std::io::copy;
    use std::path::Path;
    let server_url = "https://piston-data.mojang.com/v1/objects/64bb6d763bed0a9f1d632ec347938594144943ed/server.jar";
    let server_dir = Path::new("servers");
    if !server_dir.exists() {
        fs::create_dir_all(server_dir)?;
    }
    let server_path = server_dir.join("server.jar");
    logln!("Downloading server...");
    let response = reqwest::blocking::get(server_url)?;
    let mut file = File::create(server_path)?;
    let mut content = response;
    copy(&mut content, &mut file)?;
    logln!("Server downloaded succesfully...");
    Ok(())
}
fn stop_server() {
    logln!("Stopping server...");
    // Implement PID tracking or graceful shutdown
}

fn server_status() {
    logln!("Checking server status...");
    // Implement process checking
}
