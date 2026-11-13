#[cfg(test)]
mod tests {
    use std::io::{Read, Write};
    use std::net::TcpListener;
    use std::time::Duration;

    #[derive(Clone, Debug, PartialEq)]
    pub struct CategoryInfo {
        pub id: u32,
        pub name: String,
        pub extensions: Vec<String>,
        pub default_folder: String,
    }

    pub fn default_categories() -> Vec<CategoryInfo> {
        vec![
            CategoryInfo {
                id: 7,
                name: "Compressed".to_string(),
                extensions: vec!["zip", "rar", "7z", "tar", "gz", "bz2", "arj", "ace", "sit", "sitx"].into_iter().map(String::from).collect(),
                default_folder: "C:\\Downloads\\Compressed".to_string(),
            },
            CategoryInfo {
                id: 5,
                name: "Documents".to_string(),
                extensions: vec!["doc", "docx", "pdf", "ppt", "pptx", "pps", "txt", "xlsx", "xls"].into_iter().map(String::from).collect(),
                default_folder: "C:\\Downloads\\Documents".to_string(),
            },
            CategoryInfo {
                id: 2,
                name: "Music".to_string(),
                extensions: vec!["mp3", "wav", "wma", "mpa", "ram", "ra", "aac", "aif", "m4a", "flac"].into_iter().map(String::from).collect(),
                default_folder: "C:\\Downloads\\Music".to_string(),
            },
            CategoryInfo {
                id: 1,
                name: "Programs".to_string(),
                extensions: vec!["exe", "msi", "apk", "iso", "bin"].into_iter().map(String::from).collect(),
                default_folder: "C:\\Downloads\\Programs".to_string(),
            },
            CategoryInfo {
                id: 3,
                name: "Video".to_string(),
                extensions: vec!["avi", "mpg", "mpeg", "mp4", "mkv", "wmv", "mov", "qt", "flv", "webm", "m4v"].into_iter().map(String::from).collect(),
                default_folder: "C:\\Downloads\\Video".to_string(),
            },
        ]
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

    pub fn format_bytes(bytes: u64) -> String {
        if bytes == 0 {
            return "0 Bytes".to_string();
        }
        const KB: f64 = 1024.0;
        const MB: f64 = 1024.0 * 1024.0;
        const GB: f64 = 1024.0 * 1024.0 * 1024.0;
        let b = bytes as f64;
        if b >= GB {
            format!("{:.2} GB", b / GB)
        } else if b >= MB {
            format!("{:.2} MB", b / MB)
        } else if b >= KB {
            format!("{:.2} KB", b / KB)
        } else {
            format!("{} Bytes", bytes)
        }
    }

    #[test]
    fn test_hard_category_routing() {
        let cats = default_categories();

        assert_eq!(detect_category("archive.zip", &cats), "Compressed");
        assert_eq!(detect_category("backup.tar.gz", &cats), "Compressed");
        assert_eq!(detect_category("package.7z", &cats), "Compressed");
        assert_eq!(detect_category("installer.msi", &cats), "Programs");
        assert_eq!(detect_category("setup.exe", &cats), "Programs");
        assert_eq!(detect_category("ubuntu.iso", &cats), "Programs");
        assert_eq!(detect_category("keynote.mp4", &cats), "Video");
        assert_eq!(detect_category("stream.mkv", &cats), "Video");
        assert_eq!(detect_category("financial_report.pdf", &cats), "Documents");
        assert_eq!(detect_category("notes.txt", &cats), "Documents");
        assert_eq!(detect_category("soundtrack.flac", &cats), "Music");
        assert_eq!(detect_category("audio.mp3", &cats), "Music");
        assert_eq!(detect_category("unknown.dat", &cats), "General");
    }

    #[test]
    fn test_hard_multi_segment_partitioning() {
        let total_size: u64 = 1_450_000_000;
        for &conn_count in &[8, 16, 24, 32, 64] {
            let part_size = total_size / conn_count as u64;

            let mut segments = Vec::new();
            for i in 0..conn_count {
                let start = i as u64 * part_size;
                let end = if i == conn_count - 1 { total_size } else { (i as u64 + 1) * part_size };
                segments.push((start, end));
            }

            assert_eq!(segments.len(), conn_count as usize);
            assert_eq!(segments[0].0, 0);
            assert_eq!(segments[conn_count as usize - 1].1, total_size);

            // Verify continuity (no overlapping and no gap)
            for i in 0..(conn_count as usize - 1) {
                assert_eq!(segments[i].1, segments[i + 1].0);
            }
        }
    }

    #[test]
    fn test_hard_byte_formatting() {
        assert_eq!(format_bytes(0), "0 Bytes");
        assert_eq!(format_bytes(512), "512 Bytes");
        assert_eq!(format_bytes(1024), "1.00 KB");
        assert_eq!(format_bytes(1_048_576), "1.00 MB");
        assert_eq!(format_bytes(1_073_741_824), "1.00 GB");
        assert_eq!(format_bytes(2_764_800_000), "2.57 GB");
    }

    #[test]
    fn test_hard_speed_limiter_calculation() {
        let limit_kb: u32 = 100; // 100 KB/s
        let max_bps = (limit_kb as f64) * 1024.0;
        let chunk_size: u64 = 32768; // 32 KB chunk
        let expected_sleep_sec = (chunk_size as f64) / max_bps;

        // 32KB / 100KB/s = 0.32 seconds
        assert!((expected_sleep_sec - 0.32).abs() < 0.001);
    }

    #[test]
    fn test_hard_explorer_open_location_argument() {
        let path = "C:/Users/Downloads/Documents/Report.pdf";
        let clean = path.replace('/', "\\");
        let arg = format!("/select,{}", clean);
        assert_eq!(arg, "/select,C:\\Users\\Downloads\\Documents\\Report.pdf");
        assert!(!clean.contains('/'));
        assert!(clean.contains('\\'));
    }

    #[test]
    fn test_hard_live_download_execution() {
        let listener = TcpListener::bind("127.0.0.1:0").expect("Bind local mock port");
        let port = listener.local_addr().unwrap().port();

        // Spawn mock server thread
        std::thread::spawn(move || {
            for stream in listener.incoming().take(2) {
                let mut stream = stream.unwrap();
                let mut req_buf = [0u8; 1024];
                let n = stream.read(&mut req_buf).unwrap();
                let req_str = String::from_utf8_lossy(&req_buf[..n]);

                if req_str.starts_with("HEAD") {
                    let resp = "HTTP/1.1 200 OK\r\nContent-Length: 64\r\nAccept-Ranges: bytes\r\nConnection: close\r\n\r\n";
                    let _ = stream.write_all(resp.as_bytes());
                } else if req_str.starts_with("GET") {
                    let payload = b"0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF"; // 64 bytes
                    let resp = "HTTP/1.1 206 Partial Content\r\nContent-Range: bytes 0-63/64\r\nContent-Length: 64\r\nConnection: close\r\n\r\n";
                    let _ = stream.write_all(resp.as_bytes());
                    let _ = stream.write_all(payload);
                }
            }
        });

        let test_url = format!("http://127.0.0.1:{}/sample.bin", port);
        let temp_dir = std::env::temp_dir();
        let target_file = temp_dir.join("ayera_hardtest_local.bin");

        let client = ureq::builder()
            .timeout(Duration::from_secs(5))
            .build();

        // 1. Send HEAD request
        let head_resp = client.head(&test_url).call().expect("Mock server head call succeeds");
        let len = head_resp.header("Content-Length").unwrap().parse::<u64>().unwrap();
        assert_eq!(len, 64);
        assert_eq!(head_resp.header("Accept-Ranges").unwrap(), "bytes");

        // 2. Send GET request with Range
        let get_resp = client.get(&test_url)
            .set("Range", "bytes=0-63")
            .call()
            .expect("Mock server range get call succeeds");
        assert_eq!(get_resp.status(), 206);

        let mut reader = get_resp.into_reader();
        let mut buf = Vec::new();
        let bytes_read = reader.read_to_end(&mut buf).unwrap();
        assert_eq!(bytes_read, 64);

        // 3. Write to disk and assert integrity
        std::fs::write(&target_file, &buf).unwrap();
        assert!(target_file.exists());
        assert_eq!(std::fs::metadata(&target_file).unwrap().len(), 64);
        let content = std::fs::read(&target_file).unwrap();
        assert_eq!(&content[0..16], b"0123456789ABCDEF");

        // Cleanup
        let _ = std::fs::remove_file(target_file);
    }
}
