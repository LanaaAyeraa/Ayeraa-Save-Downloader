use crate::config::{detect_category, AppConfig};
use crate::download::{format_bytes, start_download_thread, DownloadItem, DownloadStatus};
use crate::theme::ClaudeTheme;
use eframe::egui::{self, Color32, Rounding, Stroke, Vec2};
use std::sync::{Arc, Mutex};

// Open file location in Windows Explorer with target file selected
pub fn open_file_location(path: &str) {
    #[cfg(target_os = "windows")]
    {
        let clean = path.replace('/', "\\");
        let _ = std::process::Command::new("explorer")
            .arg(format!("/select,{}", clean))
            .spawn();
    }
    #[cfg(not(target_os = "windows"))]
    {
        if let Some(parent) = std::path::Path::new(path).parent() {
            let _ = std::process::Command::new("open").arg(parent).spawn();
        }
    }
}

// Open / launch file directly
pub fn open_file(path: &str) {
    #[cfg(target_os = "windows")]
    {
        let clean = path.replace('/', "\\");
        let _ = std::process::Command::new("explorer")
            .arg(clean)
            .spawn();
    }
    #[cfg(not(target_os = "windows"))]
    {
        let _ = std::process::Command::new("open").arg(path).spawn();
    }
}

pub struct IdmApp {
    pub config: AppConfig,
    pub downloads: Vec<Arc<Mutex<DownloadItem>>>,
    pub selected_download_id: Option<u64>,
    pub selected_category: String,
    pub search_query: String,

    // Theme
    pub theme: ClaudeTheme,

    // Dialog flags
    pub show_add_url_dialog: bool,
    pub add_url_input: String,
    pub add_url_category: String,
    pub add_url_save_path: String,

    pub show_options_dialog: bool,
    pub options_tab: usize, // 0: Connection, 1: Speed Limiter, 2: Save To, 3: General

    pub show_scheduler_dialog: bool,
    pub scheduler_start_hour: u32,
    pub scheduler_start_min: u32,
    pub scheduler_stop_hour: u32,
    pub scheduler_stop_min: u32,
    pub scheduler_enabled: bool,

    pub show_details_dialog: bool,
    pub show_about_dialog: bool,

    pub speed_limit_shared: Arc<Mutex<Option<u32>>>,

    // Screenshot helper for Craft Anything test harness
    pub screenshot_path: Option<String>,
    pub frame_count: u32,
    pub screenshot_taken: bool,
}

impl IdmApp {
    pub fn new(screenshot_path: Option<String>) -> Self {
        let config = AppConfig::default();
        let speed_limit_shared = Arc::new(Mutex::new(if config.speed_limiter_enabled {
            Some(config.speed_limit_kb)
        } else {
            None
        }));

        // Seed with realistic initial downloads to showcase the IDM interface
        let mut sample_items = Vec::new();

        let mut item1 = DownloadItem::new(
            1,
            "https://speed.hetzner.de/100MB.bin".to_string(),
            "Ubuntu-24.04-desktop-amd64.iso".to_string(),
            format!("{}\\Programs\\Ubuntu-24.04-desktop-amd64.iso", config.default_download_dir),
            "Programs".to_string(),
            1_450_000_000,
        );
        item1.downloaded_bytes = 1_044_000_000;
        item1.speed_bps = 8_450_000.0;
        item1.status = DownloadStatus::Downloading;
        item1.time_left_sec = Some(48);
        item1.last_try_date = "2026-11-13 07:15".to_string();
        let seg_len = item1.segments.len().max(1);
        let part = item1.size_bytes / seg_len as u64;
        for (i, seg) in item1.segments.iter_mut().enumerate() {
            seg.active = true;
            seg.start_byte = i as u64 * part;
            seg.end_byte = if i == seg_len - 1 { item1.size_bytes } else { (i as u64 + 1) * part };
            let variance = (i as f64 * 0.015).min(0.20);
            seg.current_byte = seg.start_byte + ((seg.end_byte - seg.start_byte) as f64 * (0.68 + variance)).min((seg.end_byte - seg.start_byte) as f64) as u64;
        }
        sample_items.push(Arc::new(Mutex::new(item1)));

        let mut item2 = DownloadItem::new(
            2,
            "https://archive.org/download/sample_zip/data.zip".to_string(),
            "Web_Development_Assets_2026.zip".to_string(),
            format!("{}\\Compressed\\Web_Development_Assets_2026.zip", config.default_download_dir),
            "Compressed".to_string(),
            450_000_000,
        );
        item2.downloaded_bytes = 450_000_000;
        item2.status = DownloadStatus::Complete;
        item2.last_try_date = "2026-11-13 06:40".to_string();
        for seg in &mut item2.segments {
            seg.current_byte = seg.end_byte;
            seg.active = false;
        }
        sample_items.push(Arc::new(Mutex::new(item2)));

        let mut item3 = DownloadItem::new(
            3,
            "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4".to_string(),
            "Conference_Keynote_4K.mp4".to_string(),
            format!("{}\\Video\\Conference_Keynote_4K.mp4", config.default_download_dir),
            "Video".to_string(),
            850_000_000,
        );
        item3.downloaded_bytes = 320_000_000;
        item3.status = DownloadStatus::Paused;
        item3.time_left_sec = Some(180);
        item3.last_try_date = "2026-11-12 21:10".to_string();
        sample_items.push(Arc::new(Mutex::new(item3)));

        let mut item4 = DownloadItem::new(
            4,
            "https://example.com/docs/Annual_Financial_Report.pdf".to_string(),
            "Annual_Financial_Report.pdf".to_string(),
            format!("{}\\Documents\\Annual_Financial_Report.pdf", config.default_download_dir),
            "Documents".to_string(),
            18_400_000,
        );
        item4.downloaded_bytes = 18_400_000;
        item4.status = DownloadStatus::Complete;
        item4.last_try_date = "2026-11-11 14:22".to_string();
        sample_items.push(Arc::new(Mutex::new(item4)));

        Self {
            config,
            downloads: sample_items,
            selected_download_id: Some(1),
            selected_category: "All Downloads".to_string(),
            search_query: String::new(),

            theme: ClaudeTheme::new(true), // Default to elegant Warm Charcoal Dark Mode

            show_add_url_dialog: false,
            add_url_input: "https://".to_string(),
            add_url_category: "General".to_string(),
            add_url_save_path: "".to_string(),

            show_options_dialog: false,
            options_tab: 0,

            show_scheduler_dialog: false,
            scheduler_start_hour: 2,
            scheduler_start_min: 0,
            scheduler_stop_hour: 6,
            scheduler_stop_min: 0,
            scheduler_enabled: false,

            show_details_dialog: false,
            show_about_dialog: false,

            speed_limit_shared,

            screenshot_path,
            frame_count: 0,
            screenshot_taken: false,
        }
    }

    pub fn add_new_download(&mut self, url: String, category: String, save_path: String, start_now: bool) {
        let filename = url
            .split('/')
            .last()
            .unwrap_or("download.bin")
            .split('?')
            .next()
            .unwrap_or("download.bin")
            .to_string();

        let new_id = (self.downloads.len() as u64) + 1;
        let mut item = DownloadItem::new_with_connections(new_id, url, filename, save_path, category, 0, self.config.max_connections);

        if start_now {
            item.status = DownloadStatus::Connecting;
            let item_arc = Arc::new(Mutex::new(item));
            let handle = start_download_thread(item_arc.clone(), self.speed_limit_shared.clone());
            {
                let mut guard = item_arc.lock().unwrap();
                guard.cancel_flag = Some(handle.cancel_flag);
                guard.pause_flag = Some(handle.pause_flag);
            }
            self.downloads.insert(0, item_arc);
            self.selected_download_id = Some(new_id);
        } else {
            item.status = DownloadStatus::Queued;
            self.downloads.insert(0, Arc::new(Mutex::new(item)));
            self.selected_download_id = Some(new_id);
        }
    }
}

impl eframe::App for IdmApp {
    fn update(&mut self, ctx: &egui::Context, _frame: &mut eframe::Frame) {
        if self.frame_count == 0 {
            println!("First frame update() called successfully!");
        }
        // Apply Claude Warm Minimalist Theme
        self.theme.apply(ctx);

        // Keep requesting repaints for smooth active downloads
        let has_active = self.downloads.iter().any(|d| {
            let s = d.lock().unwrap().status.clone();
            s == DownloadStatus::Downloading || s == DownloadStatus::Connecting
        });
        if has_active {
            ctx.request_repaint_after(std::time::Duration::from_millis(100));
        }

        // Automated screenshot capture for Craft Anything checks
        if let Some(ref path) = self.screenshot_path {
            self.frame_count += 1;
            if self.frame_count >= 3 && !self.screenshot_taken {
                self.screenshot_taken = true;
                ctx.send_viewport_cmd(egui::ViewportCommand::Screenshot(Default::default()));
            }

            for event in ctx.input(|i| i.raw.events.clone()) {
                if let egui::Event::Screenshot { image, .. } = event {
                    let [w, h] = image.size;
                    let mut rgba = image::RgbaImage::new(w as u32, h as u32);
                    for y in 0..h {
                        for x in 0..w {
                            let c = image[(x as usize, y as usize)];
                            rgba.put_pixel(x as u32, y as u32, image::Rgba([c.r(), c.g(), c.b(), c.a()]));
                        }
                    }
                    if let Some(parent) = std::path::Path::new(path).parent() {
                        let _ = std::fs::create_dir_all(parent);
                    }
                    let _ = rgba.save(path);
                    ctx.send_viewport_cmd(egui::ViewportCommand::Close);
                }
            }
        }

        // ==========================================
        // 1. TOP APP HEADER & BRANDING BAR
        // ==========================================
        egui::TopBottomPanel::top("top_brand_bar")
            .frame(egui::Frame::none()
                .fill(self.theme.card_surface())
                .inner_margin(egui::Margin::symmetric(14.0, 8.0))
                .stroke(Stroke::new(1.0_f32, self.theme.border_subtle())))
            .show(ctx, |ui| {
                ui.horizontal(|ui| {
                    // AYERA Badge
                    let (badge_rect, _) = ui.allocate_exact_size(Vec2::new(56.0, 22.0), egui::Sense::hover());
                    let p = ui.painter();
                    p.rect_filled(badge_rect, Rounding::same(5.0_f32), self.theme.accent_terracotta());
                    p.text(badge_rect.center(), egui::Align2::CENTER_CENTER, "AYERA", egui::FontId::proportional(11.5), Color32::WHITE);

                    ui.add_space(4.0);
                    ui.label(egui::RichText::new("Ayera Downloader Pro").strong().size(14.0).color(self.theme.text_primary()));
                    if ui.add(egui::Button::new(egui::RichText::new("v2.0 Pro").size(11.0).color(self.theme.accent_terracotta())).frame(false)).clicked() {
                        self.show_about_dialog = true;
                    }

                    ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                        // Theme Toggle Button
                        let mode_label = if self.theme.is_dark { "Light Mode" } else { "Dark Mode" };
                        if ui.button(egui::RichText::new(mode_label).size(11.5)).clicked() {
                            self.theme.is_dark = !self.theme.is_dark;
                        }

                        ui.add_space(10.0);

                        // Quick Search Bar
                        let _search_edit = ui.add(
                            egui::TextEdit::singleline(&mut self.search_query)
                                .hint_text("Search downloads...")
                                .desired_width(170.0)
                        );
                    });
                });
            });

        // ==========================================
        // 2. MODERN ACTION TOOLBAR
        // ==========================================
        egui::TopBottomPanel::top("action_toolbar")
            .frame(egui::Frame::none()
                .fill(self.theme.bg_color())
                .inner_margin(egui::Margin::symmetric(14.0, 10.0))
                .stroke(Stroke::new(1.0_f32, self.theme.border_color())))
            .show(ctx, |ui| {
                ui.horizontal(|ui| {
                    ui.spacing_mut().item_spacing = Vec2::new(8.0, 0.0);

                    // Primary Add URL Button (Warm Terracotta Pill)
                    if self.theme.primary_button(ui, "+ Add URL").clicked() {
                        self.show_add_url_dialog = true;
                    }

                    ui.add_space(4.0);
                    let sep_color = self.theme.border_color();
                    let (sep_rect, _) = ui.allocate_exact_size(Vec2::new(1.0, 24.0), egui::Sense::hover());
                    ui.painter().rect_filled(sep_rect, Rounding::ZERO, sep_color);
                    ui.add_space(4.0);

                    let has_sel = self.selected_download_id.is_some();

                    // Transfer Controls
                    if self.theme.tool_button(ui, "Resume", has_sel).clicked() {
                        self.resume_selected();
                    }
                    if self.theme.tool_button(ui, "Pause", has_sel).clicked() {
                        self.stop_selected();
                    }
                    if self.theme.tool_button(ui, "Stop All", true).clicked() {
                        self.stop_all();
                    }

                    ui.add_space(4.0);
                    let (sep_rect2, _) = ui.allocate_exact_size(Vec2::new(1.0, 24.0), egui::Sense::hover());
                    ui.painter().rect_filled(sep_rect2, Rounding::ZERO, sep_color);
                    ui.add_space(4.0);

                    // Queue & Remove
                    if self.theme.tool_button(ui, "Remove", has_sel).clicked() {
                        self.delete_selected();
                    }
                    if self.theme.tool_button(ui, "Clear Done", true).clicked() {
                        self.delete_completed();
                    }

                    ui.add_space(4.0);
                    let (sep_rect3, _) = ui.allocate_exact_size(Vec2::new(1.0, 24.0), egui::Sense::hover());
                    ui.painter().rect_filled(sep_rect3, Rounding::ZERO, sep_color);
                    ui.add_space(4.0);

                    // Config & Details
                    if self.theme.tool_button(ui, "Settings", true).clicked() {
                        self.show_options_dialog = true;
                    }
                    if self.theme.tool_button(ui, "Schedule", true).clicked() {
                        self.show_scheduler_dialog = true;
                    }
                    if self.theme.tool_button(ui, "Details", has_sel).clicked() {
                        self.show_details_dialog = true;
                    }
                });
            });

        // ==========================================
        // 3. BOTTOM DASHBOARD STATUS FOOTER
        // ==========================================
        egui::TopBottomPanel::bottom("bottom_status_bar")
            .frame(egui::Frame::none()
                .fill(self.theme.card_surface())
                .inner_margin(egui::Margin::symmetric(14.0, 7.0))
                .stroke(Stroke::new(1.0_f32, self.theme.border_color())))
            .show(ctx, |ui| {
                ui.horizontal(|ui| {
                    let total_items = self.downloads.len();
                    let mut total_bytes = 0u64;
                    let mut total_speed = 0.0f64;
                    let mut active_count = 0usize;

                    for d in &self.downloads {
                        let guard = d.lock().unwrap();
                        total_bytes += guard.size_bytes;
                        total_speed += guard.speed_bps;
                        if guard.status == DownloadStatus::Downloading {
                            active_count += 1;
                        }
                    }

                    // Stat Pills
                    ui.label(egui::RichText::new(format!("Total: {} items ({})", total_items, format_bytes(total_bytes))).size(11.5).color(self.theme.text_muted()));
                    ui.label(egui::RichText::new("•").color(self.theme.border_color()));
                    
                    let active_col = if active_count > 0 { self.theme.accent_emerald() } else { self.theme.text_muted() };
                    ui.label(egui::RichText::new(format!("Active: {} downloading", active_count)).size(11.5).color(active_col).strong());
                    ui.label(egui::RichText::new("•").color(self.theme.border_color()));

                    let speed_str = if total_speed >= 1_048_576.0 {
                        format!("{:.2} MB/s", total_speed / 1_048_576.0)
                    } else {
                        format!("{:.2} KB/s", total_speed / 1024.0)
                    };
                    ui.label(egui::RichText::new(format!("Speed: {}", speed_str)).size(11.5).color(self.theme.accent_sky()).strong());
                    ui.label(egui::RichText::new("•").color(self.theme.border_color()));

                    let limiter_str = if self.config.speed_limiter_enabled {
                        format!("Limiter: {} KB/s", self.config.speed_limit_kb)
                    } else {
                        "Limiter: Off".to_string()
                    };
                    ui.label(egui::RichText::new(limiter_str).size(11.5).color(self.theme.text_muted()));

                    ui.with_layout(egui::Layout::right_to_left(egui::Align::Center), |ui| {
                        ui.label(egui::RichText::new(format!("Connections: {} threads", self.config.max_connections)).size(11.0).color(self.theme.text_muted()));
                    });
                });
            });

        // ==========================================
        // 4. CENTRAL VIEWPORT: SIDEBAR + MAIN TABLE
        // ==========================================
        egui::CentralPanel::default()
            .frame(egui::Frame::none().fill(self.theme.bg_color()))
            .show(ctx, |ui| {
                // LEFT SIDEBAR: CATEGORIES & QUICK FILTERS
                egui::SidePanel::left("left_sidebar_categories")
                    .frame(egui::Frame::none()
                        .fill(self.theme.card_surface())
                        .inner_margin(egui::Margin::symmetric(12.0, 14.0))
                        .stroke(Stroke::new(1.0_f32, self.theme.border_color())))
                    .resizable(true)
                    .default_width(210.0)
                    .width_range(180.0..=320.0)
                    .show_inside(ui, |ui| {
                        ui.label(egui::RichText::new("CATEGORIES").size(11.0).color(self.theme.text_muted()).strong());
                        ui.add_space(6.0);

                        let mut all_count = 0;
                        let mut unfin_count = 0;
                        let mut fin_count = 0;
                        let mut cat_counts = std::collections::HashMap::new();

                        for d in &self.downloads {
                            let guard = d.lock().unwrap();
                            all_count += 1;
                            if guard.status == DownloadStatus::Complete {
                                fin_count += 1;
                            } else {
                                unfin_count += 1;
                            }
                            *cat_counts.entry(guard.category.clone()).or_insert(0) += 1;
                        }

                        // Helper for styled sidebar item
                        let render_cat_item = |label: &str, count: usize, target: &str, sel: &mut String, theme: &ClaudeTheme, ui: &mut egui::Ui| {
                            let is_active = *sel == target;
                            let (rect, response) = ui.allocate_exact_size(Vec2::new(ui.available_width(), 28.0), egui::Sense::click());
                            if response.clicked() {
                                *sel = target.to_string();
                            }

                            let painter = ui.painter();
                            let bg = if is_active {
                                theme.row_selected()
                            } else if response.hovered() {
                                theme.row_hover()
                            } else {
                                Color32::TRANSPARENT
                            };

                            painter.rect_filled(rect, Rounding::same(6.0_f32), bg);

                            // Active accent indicator bar
                            if is_active {
                                let bar_rect = egui::Rect::from_min_size(rect.min, Vec2::new(3.0, rect.height()));
                                painter.rect_filled(bar_rect, Rounding::same(2.0_f32), theme.accent_terracotta());
                            }

                            // Text
                            let text_col = if is_active { theme.accent_terracotta() } else { theme.text_primary() };
                            let font_id = egui::FontId::proportional(12.5);
                            painter.text(
                                rect.left_center() + Vec2::new(12.0, 0.0),
                                egui::Align2::LEFT_CENTER,
                                label,
                                font_id,
                                text_col,
                            );

                            // Count Badge
                            if count > 0 {
                                let badge_str = format!("{}", count);
                                let font_badge = egui::FontId::proportional(11.0);
                                painter.text(
                                    rect.right_center() - Vec2::new(10.0, 0.0),
                                    egui::Align2::RIGHT_CENTER,
                                    badge_str,
                                    font_badge,
                                    theme.text_muted(),
                                );
                            }
                        };

                        render_cat_item("All Downloads", all_count, "All Downloads", &mut self.selected_category, &self.theme, ui);
                        ui.add_space(2.0);
                        render_cat_item("In Progress", unfin_count, "Unfinished", &mut self.selected_category, &self.theme, ui);
                        ui.add_space(2.0);
                        render_cat_item("Completed", fin_count, "Finished", &mut self.selected_category, &self.theme, ui);

                        ui.add_space(14.0);
                        ui.label(egui::RichText::new("FILE TYPES").size(11.0).color(self.theme.text_muted()).strong());
                        ui.add_space(6.0);

                        for cat in &self.config.categories {
                            let count = cat_counts.get(&cat.name).copied().unwrap_or(0);
                            render_cat_item(&cat.name, count, &cat.name, &mut self.selected_category, &self.theme, ui);
                            ui.add_space(2.0);
                        }

                        ui.add_space(14.0);
                        ui.label(egui::RichText::new("QUEUES").size(11.0).color(self.theme.text_muted()).strong());
                        ui.add_space(6.0);
                        render_cat_item("Main Queue", 0, "Main download queue", &mut self.selected_category, &self.theme, ui);
                        ui.add_space(2.0);
                        render_cat_item("Sync Queue", 0, "Synchronization queue", &mut self.selected_category, &self.theme, ui);

                        // Mini Storage / Destination card at bottom of sidebar
                        ui.with_layout(egui::Layout::bottom_up(egui::Align::Center), |ui| {
                            ui.add_space(6.0);
                            let (card_rect, _) = ui.allocate_exact_size(Vec2::new(ui.available_width(), 46.0), egui::Sense::hover());
                            let p = ui.painter();
                            p.rect_filled(card_rect, Rounding::same(6.0_f32), self.theme.card_subtle());
                            p.rect_stroke(card_rect, Rounding::same(6.0_f32), Stroke::new(1.0_f32, self.theme.border_subtle()));
                            p.text(card_rect.left_top() + Vec2::new(8.0, 7.0), egui::Align2::LEFT_TOP, "Default Folder:", egui::FontId::proportional(10.5), self.theme.text_muted());
                            
                            let dir_label = self.config.default_download_dir.chars().take(24).collect::<String>();
                            p.text(card_rect.left_top() + Vec2::new(8.0, 24.0), egui::Align2::LEFT_TOP, dir_label, egui::FontId::proportional(11.0), self.theme.text_primary());
                        });
                    });

                // MAIN CONTENT: DOWNLOADS TABLE
                egui::CentralPanel::default()
                    .frame(egui::Frame::none()
                        .fill(self.theme.bg_color())
                        .inner_margin(egui::Margin::symmetric(14.0, 10.0)))
                    .show_inside(ui, |ui| {
                        // Section Header
                        ui.horizontal(|ui| {
                            ui.label(egui::RichText::new(format!("Showing: {}", self.selected_category)).size(13.5).strong().color(self.theme.text_primary()));
                            if !self.search_query.is_empty() {
                                ui.label(egui::RichText::new(format!("(Filter: \"{}\")", self.search_query)).size(12.0).color(self.theme.accent_terracotta()));
                            }
                        });
                        ui.add_space(6.0);

                        // Downloads Table Card Frame
                        egui::Frame::none()
                            .fill(self.theme.card_surface())
                            .stroke(Stroke::new(1.0_f32, self.theme.border_color()))
                            .rounding(Rounding::same(8.0_f32))
                            .inner_margin(egui::Margin::same(10.0))
                            .show(ui, |ui| {
                                egui::ScrollArea::both()
                                    .auto_shrink([false, false])
                                    .show(ui, |ui| {
                                        egui::Grid::new("modern_downloads_grid")
                                            .striped(true)
                                            .min_col_width(75.0)
                                            .spacing([14.0, 9.0])
                                            .show(ui, |ui| {
                                                // Header Columns
                                                ui.label(egui::RichText::new("FILE NAME").size(11.0).color(self.theme.text_muted()).strong());
                                                ui.label(egui::RichText::new("SIZE").size(11.0).color(self.theme.text_muted()).strong());
                                                ui.label(egui::RichText::new("STATUS").size(11.0).color(self.theme.text_muted()).strong());
                                                ui.label(egui::RichText::new("PROGRESS").size(11.0).color(self.theme.text_muted()).strong());
                                                ui.label(egui::RichText::new("TIME LEFT").size(11.0).color(self.theme.text_muted()).strong());
                                                ui.label(egui::RichText::new("SPEED").size(11.0).color(self.theme.text_muted()).strong());
                                                ui.label(egui::RichText::new("CATEGORY").size(11.0).color(self.theme.text_muted()).strong());
                                                ui.label(egui::RichText::new("LAST TRY").size(11.0).color(self.theme.text_muted()).strong());
                                                ui.end_row();

                                                let mut clicked_id = None;
                                                let mut double_clicked_id = None;
                                                let mut action_open_loc = None;
                                                let mut action_open_file = None;
                                                let mut action_copy_url = None;
                                                let mut action_pause_id = None;
                                                let mut action_resume_id = None;
                                                let mut action_delete_id = None;

                                                for d in &self.downloads {
                                                    let item = d.lock().unwrap();

                                                    // Filter category
                                                    let matches_cat = match self.selected_category.as_str() {
                                                        "All Downloads" => true,
                                                        "Unfinished" => item.status != DownloadStatus::Complete,
                                                        "Finished" => item.status == DownloadStatus::Complete,
                                                        "Grabber projects" => false,
                                                        "Main download queue" | "Synchronization queue" => true,
                                                        other => item.category == other,
                                                    };

                                                    if !matches_cat {
                                                        continue;
                                                    }

                                                    // Filter search query
                                                    if !self.search_query.trim().is_empty() {
                                                        let query = self.search_query.to_lowercase();
                                                        let name_match = item.filename.to_lowercase().contains(&query);
                                                        let cat_match = item.category.to_lowercase().contains(&query);
                                                        if !name_match && !cat_match {
                                                            continue;
                                                        }
                                                    }

                                                    let is_selected = self.selected_download_id == Some(item.id);

                                                    // 1. File Name Column with extension badge
                                                    let ext = std::path::Path::new(&item.filename)
                                                        .extension()
                                                        .and_then(|e| e.to_str())
                                                        .unwrap_or("BIN")
                                                        .to_uppercase();
                                                    let label_text = format!("[{}] {}", ext, item.filename);
                                                    let name_label = egui::SelectableLabel::new(
                                                        is_selected,
                                                        egui::RichText::new(label_text).strong().color(if is_selected { self.theme.accent_terracotta() } else { self.theme.text_primary() }),
                                                    );
                                                    let resp = ui.add(name_label);
                                                    if resp.clicked() {
                                                        clicked_id = Some(item.id);
                                                    }
                                                    if resp.double_clicked() {
                                                        double_clicked_id = Some(item.id);
                                                    }

                                                    // Right-Click Context Menu
                                                    let item_save_path = item.save_path.clone();
                                                    let item_url = item.url.clone();
                                                    let item_id = item.id;
                                                    let item_status = item.status.clone();

                                                    resp.context_menu(|ui| {
                                                        ui.set_min_width(180.0);
                                                        if ui.button("📂 Open File Location").clicked() {
                                                            action_open_loc = Some(item_save_path.clone());
                                                            ui.close_menu();
                                                        }
                                                        if ui.button("▶ Open File").clicked() {
                                                            action_open_file = Some(item_save_path.clone());
                                                            ui.close_menu();
                                                        }
                                                        ui.separator();
                                                        if ui.button("📋 Copy Download Link").clicked() {
                                                            action_copy_url = Some(item_url.clone());
                                                            ui.close_menu();
                                                        }
                                                        ui.separator();
                                                        if item_status == DownloadStatus::Downloading {
                                                            if ui.button("⏸ Pause Download").clicked() {
                                                                action_pause_id = Some(item_id);
                                                                ui.close_menu();
                                                            }
                                                        } else if item_status != DownloadStatus::Complete {
                                                            if ui.button("▶ Resume Download").clicked() {
                                                                action_resume_id = Some(item_id);
                                                                ui.close_menu();
                                                            }
                                                        }
                                                        if ui.button("🗑 Delete from List").clicked() {
                                                            action_delete_id = Some(item_id);
                                                            ui.close_menu();
                                                        }
                                                        ui.separator();
                                                        if ui.button("📊 Progress Details").clicked() {
                                                            double_clicked_id = Some(item_id);
                                                            ui.close_menu();
                                                        }
                                                    });

                                                    // 2. Size Column
                                                    ui.label(egui::RichText::new(item.formatted_size()).color(self.theme.text_primary()));

                                                    // 3. Status Badge (Modern pill chip with dot)
                                                    self.theme.status_badge(ui, &item.status);

                                                    // 4. Modern Progress Bar
                                                    let ratio = item.progress_ratio();
                                                    self.theme.modern_progress_bar(ui, ratio, &item.status, 110.0);

                                                    // 5. Time Left
                                                    ui.label(egui::RichText::new(item.formatted_time_left()).color(self.theme.text_muted()));

                                                    // 6. Speed
                                                    let speed_color = if item.speed_bps > 0.0 { self.theme.accent_sky() } else { self.theme.text_muted() };
                                                    ui.label(egui::RichText::new(item.formatted_speed()).color(speed_color).strong());

                                                    // 7. Category
                                                    ui.label(egui::RichText::new(&item.category).color(self.theme.text_muted()));

                                                    // 8. Last Try Date
                                                    ui.label(egui::RichText::new(&item.last_try_date).color(self.theme.text_muted()).size(11.0));

                                                    ui.end_row();
                                                }

                                                if let Some(path) = action_open_loc {
                                                    open_file_location(&path);
                                                }
                                                if let Some(path) = action_open_file {
                                                    open_file(&path);
                                                }
                                                if let Some(url) = action_copy_url {
                                                    ctx.copy_text(url);
                                                }
                                                if let Some(id) = action_pause_id {
                                                    self.selected_download_id = Some(id);
                                                    self.stop_selected();
                                                }
                                                if let Some(id) = action_resume_id {
                                                    self.selected_download_id = Some(id);
                                                    self.resume_selected();
                                                }
                                                if let Some(id) = action_delete_id {
                                                    self.selected_download_id = Some(id);
                                                    self.delete_selected();
                                                }

                                                if let Some(id) = clicked_id {
                                                    self.selected_download_id = Some(id);
                                                }
                                                if let Some(id) = double_clicked_id {
                                                    self.selected_download_id = Some(id);
                                                    self.show_details_dialog = true;
                                                }
                                            });
                                    });
                            });
                    });
            });

        // ==========================================
        // 5. MODAL DIALOGS (GLOW-UP & REFINED)
        // ==========================================

        // DIALOG: ADD URL
        if self.show_add_url_dialog {
            egui::Window::new("Enter New Download Address")
                .resizable(false)
                .collapsible(false)
                .anchor(egui::Align2::CENTER_CENTER, Vec2::new(0.0, 0.0))
                .show(ctx, |ui| {
                    ui.set_min_width(460.0);
                    ui.add_space(4.0);
                    ui.label(egui::RichText::new("Target URL:").strong().color(self.theme.text_primary()));
                    let text_edit = ui.text_edit_singleline(&mut self.add_url_input);
                    if text_edit.changed() {
                        let filename = self.add_url_input.split('/').last().unwrap_or("");
                        let detected = detect_category(filename, &self.config.categories);
                        self.add_url_category = detected;
                        self.add_url_save_path = format!("{}\\Download.bin", self.config.default_download_dir);
                    }

                    ui.add_space(8.0);
                    ui.horizontal(|ui| {
                        ui.label(egui::RichText::new("Category:").strong());
                        egui::ComboBox::from_id_salt("add_cat_combo")
                            .selected_text(&self.add_url_category)
                            .show_ui(ui, |ui| {
                                ui.selectable_value(&mut self.add_url_category, "General".to_string(), "General");
                                for cat in &self.config.categories {
                                    ui.selectable_value(&mut self.add_url_category, cat.name.clone(), &cat.name);
                                }
                            });
                    });

                    ui.add_space(8.0);
                    ui.label(egui::RichText::new("Save Path:").strong());
                    ui.text_edit_singleline(&mut self.add_url_save_path);

                    ui.add_space(14.0);
                    ui.horizontal(|ui| {
                        if self.theme.primary_button(ui, "Download Now").clicked() {
                            if !self.add_url_input.trim().is_empty() {
                                let url = self.add_url_input.clone();
                                let cat = self.add_url_category.clone();
                                let path = if self.add_url_save_path.is_empty() {
                                    format!("{}\\download.bin", self.config.default_download_dir)
                                } else {
                                    self.add_url_save_path.clone()
                                };
                                self.add_new_download(url, cat, path, true);
                            }
                            self.show_add_url_dialog = false;
                        }

                        if self.theme.tool_button(ui, "Queue Later", true).clicked() {
                            if !self.add_url_input.trim().is_empty() {
                                let url = self.add_url_input.clone();
                                let cat = self.add_url_category.clone();
                                let path = if self.add_url_save_path.is_empty() {
                                    format!("{}\\download.bin", self.config.default_download_dir)
                                } else {
                                    self.add_url_save_path.clone()
                                };
                                self.add_new_download(url, cat, path, false);
                            }
                            self.show_add_url_dialog = false;
                        }

                        if self.theme.tool_button(ui, "Cancel", true).clicked() {
                            self.show_add_url_dialog = false;
                        }
                    });
                    ui.add_space(4.0);
                });
        }

        // DIALOG: OPTIONS & CONFIGURATION
        if self.show_options_dialog {
            egui::Window::new("IDM Configuration Preferences")
                .resizable(true)
                .collapsible(false)
                .anchor(egui::Align2::CENTER_CENTER, Vec2::new(0.0, 0.0))
                .show(ctx, |ui| {
                    ui.set_min_width(520.0);
                    ui.horizontal(|ui| {
                        ui.selectable_value(&mut self.options_tab, 0, "Connection");
                        ui.selectable_value(&mut self.options_tab, 1, "Speed Limiter");
                        ui.selectable_value(&mut self.options_tab, 2, "Save To");
                        ui.selectable_value(&mut self.options_tab, 3, "General");
                    });
                    ui.separator();

                    match self.options_tab {
                        0 => {
                            ui.heading("Network & Concurrency Settings");
                            ui.add_space(6.0);
                            ui.label("Connection Profile:");
                            egui::ComboBox::from_id_salt("conn_type_combo")
                                .selected_text(&self.config.connection_type)
                                .show_ui(ui, |ui| {
                                    ui.selectable_value(
                                        &mut self.config.connection_type,
                                        "High speed: Direct connection (Ethernet/Cable) / Wi-Fi / Mobile 4G".to_string(),
                                        "High speed: Fiber / Cable / Wi-Fi / 4G",
                                    );
                                    ui.selectable_value(
                                        &mut self.config.connection_type,
                                        "Medium speed: ADSL / DSL / Mobile 3G".to_string(),
                                        "Medium speed: ADSL / DSL / 3G",
                                    );
                                });

                            ui.add_space(10.0);
                            ui.label("Maximum connection threads per download:");
                            egui::ComboBox::from_id_salt("max_conn_combo")
                                .selected_text(format!("{} Connections", self.config.max_connections))
                                .show_ui(ui, |ui| {
                                    for count in [1, 2, 4, 8, 16, 24, 32] {
                                        ui.selectable_value(&mut self.config.max_connections, count, format!("{} Connections", count));
                                    }
                                });
                            ui.add_space(8.0);
                            ui.label(egui::RichText::new("Note: 8 to 16 threads provide maximum throughput without server rate-limiting.").color(self.theme.text_muted()).size(11.0));
                        }
                        1 => {
                            ui.heading("Speed Limiter");
                            ui.add_space(6.0);
                            let mut enabled = self.config.speed_limiter_enabled;
                            if ui.checkbox(&mut enabled, "Activate Download Bandwidth Limiter").changed() {
                                self.config.speed_limiter_enabled = enabled;
                                *self.speed_limit_shared.lock().unwrap() = if enabled {
                                    Some(self.config.speed_limit_kb)
                                } else {
                                    None
                                };
                            }

                            ui.add_space(10.0);
                            ui.horizontal(|ui| {
                                ui.label("Process Bandwidth Cap:");
                                let mut kb = self.config.speed_limit_kb;
                                if ui.add(egui::DragValue::new(&mut kb).speed(1.0).range(1..=100000)).changed() {
                                    self.config.speed_limit_kb = kb;
                                    if self.config.speed_limiter_enabled {
                                        *self.speed_limit_shared.lock().unwrap() = Some(kb);
                                    }
                                }
                                ui.label("KB/s");
                            });
                        }
                        2 => {
                            ui.heading("Default File Storage Folders");
                            ui.add_space(6.0);
                            ui.label("Root Downloads Folder:");
                            ui.text_edit_singleline(&mut self.config.default_download_dir);

                            ui.add_space(10.0);
                            ui.label(egui::RichText::new("Category Dedicated Subfolders:").strong());
                            for cat in &mut self.config.categories {
                                ui.horizontal(|ui| {
                                    ui.label(format!("{}:", cat.name));
                                    ui.text_edit_singleline(&mut cat.default_folder);
                                });
                            }
                        }
                        _ => {
                            ui.heading("System & Shell Integration");
                            ui.add_space(6.0);
                            ui.label("• Clipboard automatic download link sniffer: Active");
                            ui.label("• Multi-part chunk assembly engine: Ready");
                            ui.label("• Dynamic adaptive timeout retry: Enabled");
                        }
                    }

                    ui.add_space(16.0);
                    ui.separator();
                    ui.horizontal(|ui| {
                        if self.theme.primary_button(ui, "Save Changes").clicked() {
                            self.show_options_dialog = false;
                        }
                        if self.theme.tool_button(ui, "Cancel", true).clicked() {
                            self.show_options_dialog = false;
                        }
                    });
                });
        }

        // DIALOG: SCHEDULER
        if self.show_scheduler_dialog {
            egui::Window::new("Download Scheduler")
                .resizable(false)
                .collapsible(false)
                .anchor(egui::Align2::CENTER_CENTER, Vec2::new(0.0, 0.0))
                .show(ctx, |ui| {
                    ui.set_min_width(400.0);
                    ui.heading("Queue Timing Automation");
                    ui.separator();

                    ui.checkbox(&mut self.scheduler_enabled, "Enable Automated Queue Timing");

                    ui.add_space(10.0);
                    ui.horizontal(|ui| {
                        ui.label("Start Download Queue At:");
                        ui.add(egui::DragValue::new(&mut self.scheduler_start_hour).range(0..=23));
                        ui.label(":");
                        ui.add(egui::DragValue::new(&mut self.scheduler_start_min).range(0..=59));
                    });

                    ui.horizontal(|ui| {
                        ui.label("Pause Download Queue At:");
                        ui.add(egui::DragValue::new(&mut self.scheduler_stop_hour).range(0..=23));
                        ui.label(":");
                        ui.add(egui::DragValue::new(&mut self.scheduler_stop_min).range(0..=59));
                    });

                    ui.add_space(16.0);
                    ui.horizontal(|ui| {
                        if self.theme.primary_button(ui, "Apply Schedule").clicked() {
                            self.show_scheduler_dialog = false;
                        }
                        if self.theme.tool_button(ui, "Close", true).clicked() {
                            self.show_scheduler_dialog = false;
                        }
                    });
                });
        }

        // DIALOG: DOWNLOAD DETAILS (THE ICONIC SEGMENTED PROGRESS DIALOG)
        if self.show_details_dialog {
            if let Some(selected_item) = self.get_selected_item() {
                let item = selected_item.lock().unwrap().clone();

                egui::Window::new(format!("{} - Download Metrics", item.filename))
                    .resizable(true)
                    .collapsible(false)
                    .default_width(580.0)
                    .anchor(egui::Align2::CENTER_CENTER, Vec2::new(0.0, 0.0))
                    .show(ctx, |ui| {
                        // Header card
                        egui::Frame::none()
                            .fill(self.theme.card_subtle())
                            .stroke(Stroke::new(1.0_f32, self.theme.border_subtle()))
                            .rounding(Rounding::same(6.0_f32))
                            .inner_margin(egui::Margin::same(10.0))
                            .show(ui, |ui| {
                                ui.horizontal(|ui| {
                                    ui.label(egui::RichText::new("File:").strong().color(self.theme.text_primary()));
                                    ui.label(egui::RichText::new(&item.filename).color(self.theme.accent_terracotta()).strong());
                                });
                                ui.horizontal(|ui| {
                                    ui.label(egui::RichText::new("URL:").strong().color(self.theme.text_muted()));
                                    ui.label(egui::RichText::new(&item.url).color(self.theme.text_muted()).size(11.0));
                                });
                            });

                        ui.add_space(10.0);

                        // Stats Grid
                        egui::Grid::new("details_grid").num_columns(2).spacing([18.0, 6.0]).show(ui, |ui| {
                            ui.label("Status:");
                            self.theme.status_badge(ui, &item.status);
                            ui.end_row();

                            ui.label("File Size:");
                            ui.label(egui::RichText::new(item.formatted_size()).strong());
                            ui.end_row();

                            ui.label("Downloaded:");
                            ui.label(format!("{} ({:.1}%)", item.formatted_downloaded(), item.progress_ratio() * 100.0));
                            ui.end_row();

                            ui.label("Current Speed:");
                            ui.label(egui::RichText::new(item.formatted_speed()).color(self.theme.accent_sky()).strong());
                            ui.end_row();

                            ui.label("Time Remaining:");
                            ui.label(item.formatted_time_left());
                            ui.end_row();

                            ui.label("Resume Capability:");
                            let res_color = if item.resume_supported { self.theme.accent_emerald() } else { self.theme.accent_amber() };
                            ui.label(egui::RichText::new(if item.resume_supported { "Yes (Multi-part supported)" } else { "No" }).color(res_color).strong());
                            ui.end_row();
                        });

                        ui.add_space(10.0);
                        ui.label(egui::RichText::new("Overall Progress:").strong());
                        self.theme.modern_progress_bar(ui, item.progress_ratio(), &item.status, ui.available_width());

                        // ICONIC MULTI-THREAD SEGMENT VISUALIZER
                        ui.add_space(14.0);
                        ui.label(egui::RichText::new(format!("Active Connection Lanes ({} Threads Parallel):", item.segments.len())).strong().color(self.theme.text_primary()));
                        ui.add_space(4.0);

                        egui::Frame::none()
                            .fill(self.theme.card_subtle())
                            .stroke(Stroke::new(1.0_f32, self.theme.border_subtle()))
                            .rounding(Rounding::same(8.0_f32))
                            .inner_margin(egui::Margin::same(10.0))
                            .show(ui, |ui| {
                                egui::ScrollArea::vertical()
                                    .max_height(240.0)
                                    .auto_shrink([false, false])
                                    .show(ui, |ui| {
                                        for (idx, seg) in item.segments.iter().enumerate() {
                                            let seg_ratio = if seg.end_byte > seg.start_byte {
                                                ((seg.current_byte - seg.start_byte) as f32 / (seg.end_byte - seg.start_byte) as f32).clamp(0.0, 1.0)
                                            } else {
                                                1.0
                                            };

                                            ui.horizontal(|ui| {
                                                ui.label(egui::RichText::new(format!("Lane #{:02}:", idx + 1)).size(11.0).color(self.theme.text_muted()));
                                                
                                                let (rect, _) = ui.allocate_exact_size(Vec2::new(ui.available_width() - 60.0, 12.0), egui::Sense::hover());
                                                let p = ui.painter();
                                                p.rect_filled(rect, Rounding::same(6.0_f32), self.theme.card_surface());
                                                p.rect_stroke(rect, Rounding::same(6.0_f32), Stroke::new(1.0_f32, self.theme.border_color()));

                                                if seg_ratio > 0.0 {
                                                    let filled_w = rect.width() * seg_ratio;
                                                    let fill_rect = egui::Rect::from_min_size(rect.min, Vec2::new(filled_w, rect.height()));
                                                    let col = if seg.active {
                                                        self.theme.accent_terracotta()
                                                    } else {
                                                        self.theme.accent_emerald()
                                                    };
                                                    p.rect_filled(fill_rect, Rounding::same(6.0_f32), col);
                                                }

                                                ui.label(egui::RichText::new(format!("{:.0}%", seg_ratio * 100.0)).size(10.5).color(self.theme.text_muted()));
                                            });
                                            ui.add_space(2.0);
                                        }
                                    });
                            });

                        ui.add_space(14.0);
                        ui.horizontal(|ui| {
                            if item.status == DownloadStatus::Downloading {
                                if self.theme.tool_button(ui, "⏸ Pause", true).clicked() {
                                    self.stop_selected();
                                }
                            } else if self.theme.primary_button(ui, "▶ Resume").clicked() {
                                self.resume_selected();
                            }

                            if self.theme.tool_button(ui, "Close Window", true).clicked() {
                                self.show_details_dialog = false;
                            }
                        });
                    });
            } else {
                self.show_details_dialog = false;
            }
        }

        // DIALOG: ABOUT AYERA DOWNLOADER
        if self.show_about_dialog {
            egui::Window::new("About Ayera Downloader Pro")
                .resizable(false)
                .collapsible(false)
                .anchor(egui::Align2::CENTER_CENTER, Vec2::new(0.0, 0.0))
                .show(ctx, |ui| {
                    ui.set_min_width(400.0);
                    ui.add_space(4.0);
                    ui.horizontal(|ui| {
                        let (b_rect, _) = ui.allocate_exact_size(Vec2::new(48.0, 48.0), egui::Sense::hover());
                        let p = ui.painter();
                        p.rect_filled(b_rect, Rounding::same(10.0_f32), self.theme.accent_terracotta());
                        p.text(b_rect.center(), egui::Align2::CENTER_CENTER, "AYERA", egui::FontId::proportional(12.0), Color32::WHITE);
                        ui.vertical(|ui| {
                            ui.label(egui::RichText::new("Ayera Downloader Pro").strong().size(15.0).color(self.theme.text_primary()));
                            ui.label(egui::RichText::new("Version 2.0.0 • High-Speed Multi-Thread Engine").size(11.5).color(self.theme.accent_terracotta()));
                            ui.label(egui::RichText::new("Publisher: LanaaAyeraa").size(11.0).color(self.theme.text_muted()));
                        });
                    });
                    ui.add_space(10.0);
                    ui.separator();
                    ui.add_space(6.0);
                    ui.label("Ultra-fast multi-threaded download manager with intelligent dynamic segmentation, bandwidth limiter, right-click file location explorer, and category routing.");
                    ui.add_space(6.0);
                    ui.label(egui::RichText::new("Architecture: Rust + eframe/egui (Claude Minimalist Aesthetic)").size(11.0).color(self.theme.text_muted()));
                    ui.add_space(14.0);
                    if self.theme.primary_button(ui, "Close").clicked() {
                        self.show_about_dialog = false;
                    }
                    ui.add_space(4.0);
                });
        }
    }
}

impl IdmApp {
    fn get_selected_item(&self) -> Option<Arc<Mutex<DownloadItem>>> {
        let id = self.selected_download_id?;
        self.downloads.iter().find(|d| d.lock().unwrap().id == id).cloned()
    }

    fn resume_selected(&mut self) {
        if let Some(item_arc) = self.get_selected_item() {
            let status = {
                let guard = item_arc.lock().unwrap();
                guard.status.clone()
            };
            if status != DownloadStatus::Downloading && status != DownloadStatus::Complete {
                let handle = start_download_thread(item_arc.clone(), self.speed_limit_shared.clone());
                let mut guard = item_arc.lock().unwrap();
                guard.cancel_flag = Some(handle.cancel_flag);
                guard.pause_flag = Some(handle.pause_flag);
            }
        }
    }

    fn stop_selected(&mut self) {
        if let Some(item_arc) = self.get_selected_item() {
            let mut guard = item_arc.lock().unwrap();
            if let Some(ref p) = guard.pause_flag {
                p.store(true, std::sync::atomic::Ordering::Relaxed);
            }
            guard.status = DownloadStatus::Paused;
            guard.speed_bps = 0.0;
        }
    }

    fn stop_all(&mut self) {
        for d in &self.downloads {
            let mut guard = d.lock().unwrap();
            if let Some(ref p) = guard.pause_flag {
                p.store(true, std::sync::atomic::Ordering::Relaxed);
            }
            if guard.status == DownloadStatus::Downloading {
                guard.status = DownloadStatus::Paused;
                guard.speed_bps = 0.0;
            }
        }
    }

    fn delete_selected(&mut self) {
        if let Some(id) = self.selected_download_id {
            self.stop_selected();
            self.downloads.retain(|d| d.lock().unwrap().id != id);
            self.selected_download_id = self.downloads.first().map(|d| d.lock().unwrap().id);
        }
    }

    fn delete_completed(&mut self) {
        self.downloads.retain(|d| d.lock().unwrap().status != DownloadStatus::Complete);
        if let Some(id) = self.selected_download_id {
            if !self.downloads.iter().any(|d| d.lock().unwrap().id == id) {
                self.selected_download_id = self.downloads.first().map(|d| d.lock().unwrap().id);
            }
        }
    }
}
