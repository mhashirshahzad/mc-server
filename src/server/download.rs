use std::fs::{self, File};
use std::io::copy;
use std::path::Path;

pub fn ensure_server_present() -> Result<(), Box<dyn std::error::Error>> {
    let jar_path = Path::new("servers/server.jar");

    if jar_path.exists() {
        return Ok(());
    }

    fs::create_dir_all("servers")?;

    let url = "https://piston-data.mojang.com/v1/objects/64bb6d763bed0a9f1d632ec347938594144943ed/server.jar";
    let response = reqwest::blocking::get(url)?;

    let mut file = File::create(jar_path)?;
    let mut content = response;
    copy(&mut content, &mut file)?;

    Ok(())
}
