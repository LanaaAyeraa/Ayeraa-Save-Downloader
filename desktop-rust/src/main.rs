mod app;
mod bridge;
mod config;
mod download;
mod theme;

use app::IdmApp;
use eframe::egui;

fn main() -> Result<(), eframe::Error> {
    let args: Vec<String> = std::env::args().collect();
    let mut screenshot_path: Option<String> = None;

    let mut i = 1;
    while i < args.len() {
        if args[i] == "--screenshot" && i + 1 < args.len() {
            screenshot_path = Some(args[i + 1].clone());
            i += 2;
        } else {
            i += 1;
        }
    }

    let is_screenshot_mode = screenshot_path.is_some();

    let mut viewport = egui::ViewportBuilder::default()
        .with_title("Ayera Downloader Pro v2.0")
        .with_inner_size([1040.0, 650.0])
        .with_min_inner_size([820.0, 520.0])
        .with_visible(true);

    if is_screenshot_mode {
        viewport = viewport
            .with_active(false)
            .with_window_level(egui::viewport::WindowLevel::AlwaysOnBottom);
    }

    let native_options = eframe::NativeOptions {
        viewport,
        ..Default::default()
    };

    eframe::run_native(
        "Ayera Downloader Pro",
        native_options,
        Box::new(|_cc| Ok(Box::new(IdmApp::new(screenshot_path)))),
    )
}
