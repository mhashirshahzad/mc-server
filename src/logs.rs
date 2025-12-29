use colored::Colorize;
use std::fs::File;
use std::io::{BufRead, BufReader};

macro_rules! logln {
    ($($arg:tt)*) => {
        println!(
            "{} {}",
            "[Logs]".blue().bold(),
            format!($($arg)*)
        );
    };
}

pub fn show_logs(tail: bool) {
    let log_path = "logs/latest.log";
    let file = File::open(log_path).expect("Cannot open log file");
    let reader = BufReader::new(file);

    if tail {
        logln!("Tailing logs...");
        for line in reader.lines() {
            println!("{}", line.unwrap());
        }
    } else {
        logln!("Showing logs...");
        for line in reader.lines() {
            println!("{}", line.unwrap());
        }
    }
}
