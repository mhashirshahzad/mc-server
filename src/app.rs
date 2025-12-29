use eframe::egui;
use std::sync::mpsc::channel;

use crate::server::{download::ensure_server_present, process::McServer};
use crate::state::AppState;

pub struct McManagerApp {
    state: AppState,
}

impl McManagerApp {
    pub fn new() -> Self {
        ensure_server_present().expect("Failed to download server");

        Self {
            state: AppState {
                ram_mb: 4096,
                logs: Vec::new(),
                command_input: String::new(),
                server: None,
                log_rx: None,
                downloading: false,
                auto_restart: false,
            },
        }
    }
}

impl eframe::App for McManagerApp {
    fn update(&mut self, ctx: &egui::Context, _: &mut eframe::Frame) {
        let s = &mut self.state;

        egui::CentralPanel::default().show(ctx, |ui| {
            ui.heading("Minecraft Server Manager");

            ui.horizontal(|ui| {
                ui.label("RAM (MB):");
                ui.add(egui::DragValue::new(&mut s.ram_mb).speed(256));
            });

            ui.checkbox(&mut s.auto_restart, "Auto Restart on Crash");

            ui.horizontal(|ui| {
                if ui.button("Start").clicked() && s.server.is_none() {
                    let (tx, rx) = channel();
                    let server = McServer::start(s.ram_mb, tx).unwrap();
                    s.server = Some(server);
                    s.log_rx = Some(rx);
                }

                if ui.button("Stop").clicked() {
                    if let Some(server) = &mut s.server {
                        server.stop();
                    }
                    s.server = None;
                }
            });

            ui.separator();

            egui::ScrollArea::vertical()
                .stick_to_bottom(true)
                .max_height(50.0)
                .show(ui, |ui| {
                    for line in &s.logs {
                        ui.label(line);
                    }
                });
            ui.separator();

            let send = ui
                .add_sized(
                    [ui.available_width(), 28.0],
                    egui::TextEdit::singleline(&mut s.command_input),
                )
                .lost_focus()
                && ui.input(|i| i.key_pressed(egui::Key::Enter));

            if send {
                if let Some(server) = &mut s.server {
                    server.send_command(&s.command_input);
                    s.command_input.clear();
                }
            }
        });

        if let Some(rx) = &s.log_rx {
            while let Ok(line) = rx.try_recv() {
                s.logs.push(line);
            }
        }

        // Crash detection
        if let Some(server) = &mut s.server {
            if !server.is_running() {
                s.server = None;
                if s.auto_restart {
                    let (tx, rx) = channel();
                    let server = McServer::start(s.ram_mb, tx).unwrap();
                    s.server = Some(server);
                    s.log_rx = Some(rx);
                }
            }
        }
    }
}
