use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::{Arc, Mutex};
use std::thread;
use serde::{Deserialize, Serialize};

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct IncomingDownload {
    pub url: String,
    pub filename: Option<String>,
    pub category: Option<String>,
    pub referrer: Option<String>,
    pub start_now: Option<bool>,
}

#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct BridgeStatusResponse {
    pub status: String,
    pub app: String,
    pub version: String,
    pub max_connections: u32,
    pub active_downloads: usize,
}

pub struct BridgeServer {
    pub incoming_queue: Arc<Mutex<Vec<IncomingDownload>>>,
    pub active_count: Arc<Mutex<usize>>,
    pub port: u16,
}

impl BridgeServer {
    pub fn new(port: u16) -> Self {
        Self {
            incoming_queue: Arc::new(Mutex::new(Vec::new())),
            active_count: Arc::new(Mutex::new(0)),
            port,
        }
    }

    pub fn start(&self) -> Result<(), String> {
        let queue = self.incoming_queue.clone();
        let active_count = self.active_count.clone();
        let port = self.port;

        let listener = match TcpListener::bind(format!("127.0.0.1:{}", port)) {
            Ok(l) => l,
            Err(e) => return Err(format!("Failed to bind to port {}: {}", port, e)),
        };

        thread::spawn(move || {
            for stream in listener.incoming() {
                if let Ok(mut stream) = stream {
                    let queue_clone = queue.clone();
                    let active_clone = active_count.clone();
                    thread::spawn(move || {
                        handle_client(&mut stream, queue_clone, active_clone);
                    });
                }
            }
        });

        Ok(())
    }
}

fn read_http_request(stream: &mut TcpStream) -> Result<Vec<u8>, std::io::Error> {
    let _ = stream.set_read_timeout(Some(std::time::Duration::from_millis(1500)));
    let mut req_bytes = Vec::new();
    let mut chunk = [0u8; 4096];
    let mut content_length: Option<usize> = None;
    let mut header_end: Option<usize> = None;

    loop {
        match stream.read(&mut chunk) {
            Ok(0) => break,
            Ok(n) => {
                req_bytes.extend_from_slice(&chunk[..n]);

                if header_end.is_none() {
                    if let Some(pos) = req_bytes.windows(4).position(|w| w == b"\r\n\r\n") {
                        header_end = Some(pos + 4);
                        let header_str = String::from_utf8_lossy(&req_bytes[..pos]);
                        for line in header_str.lines() {
                            if line.to_ascii_lowercase().starts_with("content-length:") {
                                if let Some(val) = line.split(':').nth(1) {
                                    if let Ok(cl) = val.trim().parse::<usize>() {
                                        content_length = Some(cl);
                                    }
                                }
                            }
                        }
                    }
                }

                if let (Some(h_end), Some(cl)) = (header_end, content_length) {
                    let body_len = req_bytes.len().saturating_sub(h_end);
                    if body_len >= cl {
                        break;
                    }
                } else if header_end.is_some() && content_length.is_none() {
                    break;
                }
            }
            Err(ref e) if e.kind() == std::io::ErrorKind::WouldBlock || e.kind() == std::io::ErrorKind::TimedOut => {
                break;
            }
            Err(e) => return Err(e),
        }
    }
    Ok(req_bytes)
}

fn handle_client(
    stream: &mut TcpStream,
    queue: Arc<Mutex<Vec<IncomingDownload>>>,
    active_count: Arc<Mutex<usize>>,
) {
    let raw_bytes = match read_http_request(stream) {
        Ok(b) if !b.is_empty() => b,
        _ => return,
    };

    let req_str = String::from_utf8_lossy(&raw_bytes);
    let mut lines = req_str.lines();
    let request_line = match lines.next() {
        Some(line) => line,
        None => return,
    };

    let parts: Vec<&str> = request_line.split_whitespace().collect();
    if parts.len() < 2 {
        return;
    }

    let method = parts[0];
    let path = parts[1];

    let cors_headers = "Access-Control-Allow-Origin: *\r\n\
Access-Control-Allow-Methods: GET, POST, OPTIONS\r\n\
Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With\r\n\
Access-Control-Max-Age: 86400\r\n";

    // Handle CORS Preflight
    if method == "OPTIONS" {
        let resp = format!(
            "HTTP/1.1 204 No Content\r\n{}\
Connection: close\r\n\r\n",
            cors_headers
        );
        let _ = stream.write_all(resp.as_bytes());
        return;
    }

    if method == "GET" && (path == "/status" || path == "/ping") {
        let current_active = *active_count.lock().unwrap();
        let status = BridgeStatusResponse {
            status: "ok".to_string(),
            app: "Ayera Downloader Pro".to_string(),
            version: "2.0.0".to_string(),
            max_connections: 32,
            active_downloads: current_active,
        };
        let body = serde_json::to_string(&status).unwrap_or_else(|_| "{}".to_string());
        let resp = format!(
            "HTTP/1.1 200 OK\r\n{}\
Content-Type: application/json\r\n\
Content-Length: {}\r\n\
Connection: close\r\n\r\n{}",
            cors_headers,
            body.len(),
            body
        );
        let _ = stream.write_all(resp.as_bytes());
        return;
    }

    if method == "POST" && (path == "/add-download" || path == "/download") {
        // Find body after double CRLF
        let body_start = req_str.find("\r\n\r\n").map(|idx| idx + 4).unwrap_or(raw_bytes.len());
        let body_str = &req_str[body_start..];

        match serde_json::from_str::<IncomingDownload>(body_str.trim()) {
            Ok(item) => {
                if !item.url.trim().is_empty() {
                    queue.lock().unwrap().push(item.clone());
                    let res_json = serde_json::json!({
                        "success": true,
                        "message": "Download queued successfully",
                        "url": item.url,
                        "channels": 32
                    });
                    let body = res_json.to_string();
                    let resp = format!(
                        "HTTP/1.1 200 OK\r\n{}\
Content-Type: application/json\r\n\
Content-Length: {}\r\n\
Connection: close\r\n\r\n{}",
                        cors_headers,
                        body.len(),
                        body
                    );
                    let _ = stream.write_all(resp.as_bytes());
                    return;
                }
            }
            Err(e) => {
                let res_json = serde_json::json!({
                    "success": false,
                    "error": format!("Invalid JSON: {}", e)
                });
                let body = res_json.to_string();
                let resp = format!(
                    "HTTP/1.1 400 Bad Request\r\n{}\
Content-Type: application/json\r\n\
Content-Length: {}\r\n\
Connection: close\r\n\r\n{}",
                    cors_headers,
                    body.len(),
                    body
                );
                let _ = stream.write_all(resp.as_bytes());
                return;
            }
        }
    }

    // Default 404
    let body = r#"{"error":"Not Found"}"#;
    let resp = format!(
        "HTTP/1.1 404 Not Found\r\n{}\
Content-Type: application/json\r\n\
Content-Length: {}\r\n\
Connection: close\r\n\r\n{}",
        cors_headers,
        body.len(),
        body
    );
    let _ = stream.write_all(resp.as_bytes());
}
