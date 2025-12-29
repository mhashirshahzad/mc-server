use std::fs;

pub fn update_property(key: &str, value: &str) {
    let path = "server.properties";
    let content = fs::read_to_string(path).expect("Failed to read server.properties");

    let new_content = content
        .lines()
        .map(|line| {
            if line.starts_with(&format!("{}=", key)) {
                format!("{}={}", key, value)
            } else {
                line.to_string()
            }
        })
        .collect::<Vec<_>>()
        .join("\n");

    fs::write(path, new_content).expect("Failed to write server.properties");
}
