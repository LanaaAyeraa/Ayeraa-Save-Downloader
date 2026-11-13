use serde::{Deserialize, Serialize};
use std::sync::{
    atomic::{AtomicBool, Ordering},
    Arc, Mutex,
};
use std::time::{Duration, Instant};

#[derive(Clone, Debug, PartialEq, Serialize, Deserialize)]
pub enum DownloadStatus {
    Queued,
    Connecting,
    Downloading,
    Paused,
    Complete,
    Error(String),
}

impl DownloadStatus {
    pub fn as_str(&self) -> &str {
        match self {
            DownloadStatus::Queued => "Queued",
            DownloadStatus::Connecting => "Connecting",
            DownloadStatus::Downloading => "Downloading",
            DownloadStatus::Paused => "Paused",
            DownloadStatus::Complete => "Complete",
            DownloadStatus::Error(_) => "Error",
        }
    }
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct SegmentProgress {
    pub id: usize,
    pub start_byte: u64,
    pub current_byte: u64,
    pub end_byte: u64,
    pub active: bool,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct DownloadItem {
    pub id: u64,
    pub url: String,
    pub filename: String,
    pub save_path: String,
    pub category: String,
    pub size_bytes: u64,
    pub downloaded_bytes: u64,
    pub speed_bps: f64,
    pub status: DownloadStatus,
    pub time_left_sec: Option<u64>,
    pub last_try_date: String,
    pub resume_supported: bool,
    pub connection_count: u32,
    pub segments: Vec<SegmentProgress>,
    #[serde(skip)]
    pub cancel_flag: Option<Arc<AtomicBool>>,
    #[serde(skip)]
    pub pause_flag: Option<Arc<AtomicBool>>,
}

impl DownloadItem {
    pub fn new(id: u64, url: String, filename: String, save_path: String, category: String, size_bytes: u64) -> Self {
        Self::new_with_connections(id, url, filename, save_path, category, size_bytes, 16)
    }

    pub fn new_with_connections(
        id: u64,
        url: String,
        filename: String,
        save_path: String,
        category: String,
        size_bytes: u64,
        conn_count: u32,
    ) -> Self {
        let count = conn_count.max(1);
        let mut segments = Vec::new();
        let part_size = if size_bytes > 0 { size_bytes / count as u64 } else { 0 };
        for i in 0..count {
            let start = i as u64 * part_size;
            let end = if i == count - 1 { size_bytes } else { (i as u64 + 1) * part_size };
            segments.push(SegmentProgress {
                id: i as usize,
                start_byte: start,
                current_byte: start,
                end_byte: end,
                active: false,
            });
        }

        Self {
            id,
            url,
            filename,
            save_path,
            category,
            size_bytes,
            downloaded_bytes: 0,
            speed_bps: 0.0,
            status: DownloadStatus::Queued,
            time_left_sec: None,
            last_try_date: chrono_fallback(),
            resume_supported: true,
            connection_count: count,
            segments,
            cancel_flag: None,
            pause_flag: None,
        }
    }

    pub fn progress_ratio(&self) -> f32 {
        if self.size_bytes == 0 {
            0.0
        } else {
            (self.downloaded_bytes as f32 / self.size_bytes as f32).clamp(0.0, 1.0)
        }
    }

    pub fn formatted_size(&self) -> String {
        format_bytes(self.size_bytes)
    }

    pub fn formatted_downloaded(&self) -> String {
        format_bytes(self.downloaded_bytes)
    }

    pub fn formatted_speed(&self) -> String {
        if self.speed_bps <= 0.0 {
            "0.00 KB/s".to_string()
        } else if self.speed_bps >= 1_048_576.0 {
            format!("{:.2} MB/s", self.speed_bps / 1_048_576.0)
        } else {
            format!("{:.2} KB/s", self.speed_bps / 1024.0)
        }
    }

    pub fn formatted_time_left(&self) -> String {
        match self.time_left_sec {
            Some(sec) => {
                let h = sec / 3600;
                let m = (sec % 3600) / 60;
                let s = sec % 60;
                if h > 0 {
                    format!("{} hr {} min", h, m)
                } else if m > 0 {
                    format!("{} min {} sec", m, s)
                } else {
                    format!("{} sec", s)
                }
            }
            None => {
                if self.status == DownloadStatus::Complete {
                    "Finished".to_string()
                } else {
                    "--".to_string()
                }
            }
        }
    }
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

fn chrono_fallback() -> String {
    "2026-11-13 07:30".to_string()
}

pub struct DownloadHandle {
    pub cancel_flag: Arc<AtomicBool>,
    pub pause_flag: Arc<AtomicBool>,
}

pub fn start_download_thread(
    item_mutex: Arc<Mutex<DownloadItem>>,
    speed_limit_kb: Arc<Mutex<Option<u32>>>,
) -> DownloadHandle {
    let cancel_flag = Arc::new(AtomicBool::new(false));
    let pause_flag = Arc::new(AtomicBool::new(false));

    let cancel_worker = cancel_flag.clone();
    let pause_worker = pause_flag.clone();

    std::thread::spawn(move || {
        let (url, save_path, mut downloaded) = {
            let mut item = item_mutex.lock().unwrap();
            item.status = DownloadStatus::Connecting;
            item.cancel_flag = Some(cancel_worker.clone());
            item.pause_flag = Some(pause_worker.clone());
            (item.url.clone(), item.save_path.clone(), item.downloaded_bytes)
        };

        let client = ureq::builder()
            .timeout(Duration::from_secs(15))
            .build();

        let head_resp = client.head(&url).call();
        let total_size = match head_resp {
            Ok(resp) => {
                let len = resp.header("Content-Length")
                    .and_then(|s| s.parse::<u64>().ok())
                    .unwrap_or(0);
                let accept_ranges = resp.header("Accept-Ranges")
                    .map(|s| s.contains("bytes"))
                    .unwrap_or(false);
                let mut item = item_mutex.lock().unwrap();
                if len > 0 && item.size_bytes == 0 {
                    item.size_bytes = len;
                }
                item.resume_supported = accept_ranges;
                len
            }
            Err(_) => 0,
        };

        if cancel_worker.load(Ordering::Relaxed) {
            let mut item = item_mutex.lock().unwrap();
            item.status = DownloadStatus::Paused;
            return;
        }

        let mut req = client.get(&url);
        if downloaded > 0 {
            req = req.set("Range", &format!("bytes={}-", downloaded));
        }

        let resp = match req.call() {
            Ok(r) => r,
            Err(e) => {
                let mut item = item_mutex.lock().unwrap();
                item.status = DownloadStatus::Error(format!("Connection error: {}", e));
                return;
            }
        };

        {
            let mut item = item_mutex.lock().unwrap();
            item.status = DownloadStatus::Downloading;
            for seg in &mut item.segments {
                seg.active = true;
            }
        }

        let mut reader = resp.into_reader();
        let mut buffer = [0u8; 32768];
        let mut last_speed_check = Instant::now();
        let mut bytes_since_check = 0u64;

        let file_res = std::fs::OpenOptions::new()
            .create(true)
            .write(true)
            .append(downloaded > 0)
            .open(&save_path);

        let mut file = match file_res {
            Ok(f) => f,
            Err(e) => {
                let mut item = item_mutex.lock().unwrap();
                item.status = DownloadStatus::Error(format!("File create error: {}", e));
                return;
            }
        };

        use std::io::{Read, Write};

        loop {
            if cancel_worker.load(Ordering::Relaxed) {
                let mut item = item_mutex.lock().unwrap();
                item.status = DownloadStatus::Paused;
                break;
            }
            if pause_worker.load(Ordering::Relaxed) {
                let mut item = item_mutex.lock().unwrap();
                item.status = DownloadStatus::Paused;
                break;
            }

            match reader.read(&mut buffer) {
                Ok(0) => {
                    let mut item = item_mutex.lock().unwrap();
                    item.status = DownloadStatus::Complete;
                    item.speed_bps = 0.0;
                    item.time_left_sec = Some(0);
                    item.downloaded_bytes = item.size_bytes;
                    for seg in &mut item.segments {
                        seg.current_byte = seg.end_byte;
                        seg.active = false;
                    }
                    break;
                }
                Ok(n) => {
                    if let Err(e) = file.write_all(&buffer[..n]) {
                        let mut item = item_mutex.lock().unwrap();
                        item.status = DownloadStatus::Error(format!("Disk write error: {}", e));
                        break;
                    }

                    downloaded += n as u64;
                    bytes_since_check += n as u64;

                    let elapsed = last_speed_check.elapsed();
                    if elapsed >= Duration::from_millis(500) {
                        let bps = (bytes_since_check as f64) / elapsed.as_secs_f64();
                        let total = if total_size > 0 { total_size } else { downloaded };
                        let time_left = if bps > 0.0 && total > downloaded {
                            Some(((total - downloaded) as f64 / bps) as u64)
                        } else {
                            None
                        };

                        {
                            let mut item = item_mutex.lock().unwrap();
                            item.downloaded_bytes = downloaded;
                            item.speed_bps = bps;
                            item.time_left_sec = time_left;

                            let seg_count = item.segments.len();
                            if seg_count > 0 && total > 0 {
                                for (idx, seg) in item.segments.iter_mut().enumerate() {
                                    let seg_part = total / seg_count as u64;
                                    let seg_start = idx as u64 * seg_part;
                                    let seg_end = if idx == seg_count - 1 { total } else { (idx as u64 + 1) * seg_part };
                                    seg.start_byte = seg_start;
                                    seg.end_byte = seg_end;
                                    let fraction = (downloaded as f64 / total as f64).clamp(0.0, 1.0);
                                    let done_up_to = (total as f64 * fraction) as u64;
                                    if done_up_to >= seg_end {
                                        seg.current_byte = seg_end;
                                    } else if done_up_to <= seg_start {
                                        seg.current_byte = seg_start;
                                    } else {
                                        seg.current_byte = done_up_to;
                                    }
                                }
                            }
                        }

                        last_speed_check = Instant::now();
                        bytes_since_check = 0;
                    }

                    let limit_kb = *speed_limit_kb.lock().unwrap();
                    if let Some(kb) = limit_kb {
                        if kb > 0 {
                            let max_bps = (kb as f64) * 1024.0;
                            let expected_time = (n as f64) / max_bps;
                            std::thread::sleep(Duration::from_secs_f64(expected_time));
                        }
                    }
                }
                Err(e) => {
                    let mut item = item_mutex.lock().unwrap();
                    item.status = DownloadStatus::Error(format!("Read error: {}", e));
                    break;
                }
            }
        }
    });

    DownloadHandle {
        cancel_flag,
        pause_flag,
    }
}
