use std::fs;
use std::path::Path;

#[derive(clap::ValueEnum, Clone)]
pub enum BackupAction {
    Create,
    Restore,
}

pub fn handle_backup(action: BackupAction) {
    match action {
        BackupAction::Create => create_backup(),
        BackupAction::Restore => restore_backup(),
    }
}

fn create_backup() {
    println!("Creating backup...");
    // Implement copying world files
}

fn restore_backup() {
    println!("Restoring backup...");
    // Implement restoring world files
}
