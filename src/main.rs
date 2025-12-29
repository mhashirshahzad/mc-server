mod commands;
mod config;
mod logs;

use clap::{Parser, Subcommand};

#[derive(Parser)]
#[command(name = "mc-manager")]
#[command(about = "Minecraft Server Manager CLI", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    Server {
        #[arg(value_enum)]
        action: commands::server::ServerAction,
    },
    Backup {
        #[arg(value_enum)]
        action: commands::backup::BackupAction,
    },
    Logs {
        #[arg(short, long)]
        tail: bool,
    },
}

fn main() {
    let cli = Cli::parse();

    match cli.command {
        Commands::Server { action } => commands::server::handle_server(action),
        Commands::Backup { action } => commands::backup::handle_backup(action),
        Commands::Logs { tail } => logs::show_logs(tail),
    }
}
