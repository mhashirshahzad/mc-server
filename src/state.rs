use std::sync::mpsc::Receiver;

use crate::server::process::McServer;

pub struct AppState {
    pub ram_mb: u32,
    pub logs: Vec<String>,
    pub command_input: String,

    pub server: Option<McServer>,
    pub log_rx: Option<Receiver<String>>,

    pub downloading: bool,
    pub auto_restart: bool,
}
