use serde::{Deserialize, Serialize};
use std::path::PathBuf;

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct CategoryInfo {
    pub id: u32,
    pub name: String,
    pub extensions: Vec<String>,
    pub default_folder: String,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AppConfig {
    pub max_connections: u32,
    pub connection_type: String,
    pub speed_limiter_enabled: bool,
    pub speed_limit_kb: u32,
    pub default_download_dir: String,
    pub categories: Vec<CategoryInfo>,
}

impl Default for AppConfig {
    fn default() -> Self {
        let base_dir = dirs_fallback();
        Self {
            max_connections: 8,
            connection_type: "High speed: Direct connection (Ethernet/Cable) / Wi-Fi / Mobile 4G".to_string(),
            speed_limiter_enabled: false,
            speed_limit_kb: 50,
            default_download_dir: base_dir.clone(),
            categories: vec![
                CategoryInfo {
                    id: 7,
                    name: "Compressed".to_string(),
                    extensions: vec!["zip", "rar", "7z", "tar", "gz", "bz2", "arj", "ace", "sit", "sitx"]
                        .into_iter().map(String::from).collect(),
                    default_folder: format!("{}\\Compressed", base_dir),
                },
                CategoryInfo {
                    id: 5,
                    name: "Documents".to_string(),
                    extensions: vec!["doc", "docx", "pdf", "ppt", "pptx", "pps", "txt", "xlsx", "xls"]
                        .into_iter().map(String::from).collect(),
                    default_folder: format!("{}\\Documents", base_dir),
                },
                CategoryInfo {
                    id: 2,
                    name: "Music".to_string(),
                    extensions: vec!["mp3", "wav", "wma", "mpa", "ram", "ra", "aac", "aif", "m4a", "flac"]
                        .into_iter().map(String::from).collect(),
                    default_folder: format!("{}\\Music", base_dir),
                },
                CategoryInfo {
                    id: 1,
                    name: "Programs".to_string(),
                    extensions: vec!["exe", "msi", "apk", "iso", "bin"]
                        .into_iter().map(String::from).collect(),
                    default_folder: format!("{}\\Programs", base_dir),
                },
                CategoryInfo {
                    id: 3,
                    name: "Video".to_string(),
                    extensions: vec!["avi", "mpg", "mpeg", "mp4", "mkv", "wmv", "mov", "qt", "flv", "webm", "m4v"]
                        .into_iter().map(String::from).collect(),
                    default_folder: format!("{}\\Video", base_dir),
                },
            ],
        }
    }
}

pub fn dirs_fallback() -> String {
    if let Ok(user_profile) = std::env::var("USERPROFILE") {
        let p = PathBuf::from(user_profile).join("Downloads");
        return p.to_string_lossy().to_string();
    }
    "C:\\Downloads".to_string()
}

pub fn detect_category(filename: &str, categories: &[CategoryInfo]) -> String {
    let ext = std::path::Path::new(filename)
        .extension()
        .and_then(|e| e.to_str())
        .unwrap_or("")
        .to_lowercase();

    for cat in categories {
        if cat.extensions.iter().any(|e| e.to_lowercase() == ext) {
            return cat.name.clone();
        }
    }
    "General".to_string()
}
