use std::io::{BufRead, BufReader, Write};
use std::process::{Child, Command, Stdio};
use std::sync::mpsc::Sender;
use std::thread;

pub struct McServer {
    child: Child,
}

impl McServer {
    pub fn start(ram_mb: u32, log_tx: Sender<String>) -> std::io::Result<Self> {
        let mut child = Command::new("java")
            .arg(format!("-Xmx{}M", ram_mb))
            .arg(format!("-Xms{}M", ram_mb))
            .arg("-jar")
            .arg("servers/server.jar")
            .arg("nogui")
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .spawn()?;

        let stdout = child.stdout.take().unwrap();
        let stderr = child.stderr.take().unwrap();

        let tx = log_tx.clone();
        thread::spawn(move || {
            let reader = BufReader::new(stdout);
            for line in reader.lines().flatten() {
                let _ = tx.send(line);
            }
        });

        let tx = log_tx;
        thread::spawn(move || {
            let reader = BufReader::new(stderr);
            for line in reader.lines().flatten() {
                let _ = tx.send(format!("[ERR] {}", line));
            }
        });

        Ok(Self { child })
    }

    pub fn send_command(&mut self, cmd: &str) {
        if let Some(stdin) = &mut self.child.stdin {
            let _ = writeln!(stdin, "{}", cmd);
        }
    }

    pub fn is_running(&mut self) -> bool {
        self.child.try_wait().ok().flatten().is_none()
    }

    pub fn stop(&mut self) {
        let _ = self.child.kill();
    }
}
