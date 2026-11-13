use crate::download::DownloadStatus;
use eframe::egui::{self, Color32, Rect, Response, Rounding, Stroke, Vec2};

/// Modern Anti-Slop High-Performance Desktop Tool Theme
/// Designed for maximum clarity, WCAG AA compliance, and tactile micro-interactions.
#[derive(Clone, Debug)]
pub struct AntiSlopTheme {
    pub is_dark: bool,
}

pub type ClaudeTheme = AntiSlopTheme; // Backward compatibility alias

impl AntiSlopTheme {
    pub fn new(is_dark: bool) -> Self {
        Self { is_dark }
    }

    // Surfaces & Backgrounds - Precision Deep Slate / Clean Arctic
    pub fn bg_color(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x0C, 0x0E, 0x12) // Deep carbon slate
        } else {
            Color32::from_rgb(0xF4, 0xF6, 0xF9) // Clean crisp arctic
        }
    }

    pub fn card_surface(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x14, 0x17, 0x1F) // Precision panel surface
        } else {
            Color32::from_rgb(0xFF, 0xFF, 0xFF)
        }
    }

    pub fn card_subtle(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x1A, 0x1E, 0x29) // Sub-panel / table header
        } else {
            Color32::from_rgb(0xEA, 0xEE, 0xF4)
        }
    }

    pub fn row_hover(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x20, 0x25, 0x34) // Distinct tactile hover
        } else {
            Color32::from_rgb(0xE2, 0xE8, 0xF0)
        }
    }

    pub fn row_selected(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x1B, 0x32, 0x47) // Focused selection highlight
        } else {
            Color32::from_rgb(0xDB, 0xEA, 0xFE)
        }
    }

    pub fn border_color(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x28, 0x2E, 0x3E) // High-contrast structural border
        } else {
            Color32::from_rgb(0xCB, 0xD5, 0xE1)
        }
    }

    pub fn border_subtle(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x1E, 0x22, 0x2E)
        } else {
            Color32::from_rgb(0xE2, 0xE8, 0xF0)
        }
    }

    // Typography - High Contrast (WCAG AA > 15:1 ratio)
    pub fn text_primary(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0xF8, 0xFA, 0xFC) // Pure frost white
        } else {
            Color32::from_rgb(0x0F, 0x17, 0x2A) // Rich slate ink
        }
    }

    pub fn text_muted(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x94, 0xA3, 0xB8) // Steel silver (> 5.5:1 ratio)
        } else {
            Color32::from_rgb(0x64, 0x74, 0x8B) // Slate grey
        }
    }

    // Accents - Purposeful & Restrained (Anti-Slop standard)
    pub fn accent_emerald(&self) -> Color32 {
        Color32::from_rgb(0x10, 0xB9, 0x81) // Precision Electric Emerald (Active Action & Complete)
    }

    pub fn accent_emerald_hover(&self) -> Color32 {
        Color32::from_rgb(0x05, 0x96, 0x69)
    }

    pub fn accent_sky(&self) -> Color32 {
        Color32::from_rgb(0x06, 0xB6, 0xD4) // Electric Cyan (Bandwidth Speed)
    }

    pub fn accent_amber(&self) -> Color32 {
        Color32::from_rgb(0xF5, 0x9E, 0x0B) // Warning / Paused
    }

    pub fn accent_danger(&self) -> Color32 {
        Color32::from_rgb(0xEF, 0x44, 0x44) // Error / Delete
    }

    // Compatibility methods for previous calls
    pub fn accent_terracotta(&self) -> Color32 {
        self.accent_emerald()
    }

    pub fn accent_terracotta_hover(&self) -> Color32 {
        self.accent_emerald_hover()
    }

    pub fn apply(&self, ctx: &egui::Context) {
        let mut visuals = if self.is_dark {
            egui::Visuals::dark()
        } else {
            egui::Visuals::light()
        };

        visuals.panel_fill = self.bg_color();
        visuals.window_fill = self.card_surface();
        visuals.window_stroke = Stroke::new(1.0_f32, self.border_color());
        visuals.window_rounding = Rounding::same(6.0_f32);
        visuals.menu_rounding = Rounding::same(6.0_f32);
        visuals.extreme_bg_color = self.card_subtle();

        visuals.widgets.inactive.bg_fill = self.card_surface();
        visuals.widgets.inactive.bg_stroke = Stroke::new(1.0_f32, self.border_color());
        visuals.widgets.inactive.fg_stroke = Stroke::new(1.0_f32, self.text_primary());
        visuals.widgets.inactive.rounding = Rounding::same(5.0_f32);

        visuals.widgets.hovered.bg_fill = self.row_hover();
        visuals.widgets.hovered.bg_stroke = Stroke::new(1.0_f32, self.accent_emerald());
        visuals.widgets.hovered.fg_stroke = Stroke::new(1.0_f32, self.text_primary());
        visuals.widgets.hovered.rounding = Rounding::same(5.0_f32);

        visuals.widgets.active.bg_fill = self.accent_emerald();
        visuals.widgets.active.bg_stroke = Stroke::new(1.0_f32, self.accent_emerald_hover());
        visuals.widgets.active.fg_stroke = Stroke::new(1.0_f32, Color32::WHITE);
        visuals.widgets.active.rounding = Rounding::same(5.0_f32);

        visuals.widgets.noninteractive.bg_fill = self.card_surface();
        visuals.widgets.noninteractive.bg_stroke = Stroke::new(1.0_f32, self.border_color());
        visuals.widgets.noninteractive.fg_stroke = Stroke::new(1.0_f32, self.text_primary());
        visuals.widgets.noninteractive.rounding = Rounding::same(5.0_f32);

        visuals.selection.bg_fill = self.row_selected();
        visuals.selection.stroke = Stroke::new(1.0_f32, self.accent_emerald());

        ctx.set_visuals(visuals);
    }

    // Interactive Tactile Primary Button with Physical Press State
    pub fn primary_button(&self, ui: &mut egui::Ui, text: &str) -> Response {
        let (rect, response) = ui.allocate_exact_size(Vec2::new(124.0, 32.0), egui::Sense::click());
        let is_down = response.is_pointer_button_down_on();
        let bg = if is_down {
            self.accent_emerald_hover()
        } else if response.hovered() {
            self.accent_emerald()
        } else {
            Color32::from_rgb(0x05, 0x96, 0x69)
        };

        let painter = ui.painter();
        painter.rect_filled(rect, Rounding::same(5.0_f32), bg);
        if response.hovered() {
            painter.rect_stroke(rect, Rounding::same(5.0_f32), Stroke::new(1.5_f32, Color32::WHITE));
        }

        // Tactile micro-depression on active click (down 1 pixel)
        let text_offset = if is_down { Vec2::new(0.0, 1.0) } else { Vec2::ZERO };
        let font_id = egui::FontId::proportional(12.5);
        painter.text(
            rect.center() + text_offset,
            egui::Align2::CENTER_CENTER,
            text,
            font_id,
            Color32::WHITE,
        );

        response
    }

    // Tactile Tool Button with Physical State Changes
    pub fn tool_button(&self, ui: &mut egui::Ui, text: &str, enabled: bool) -> Response {
        let (rect, response) = ui.allocate_exact_size(Vec2::new(96.0, 32.0), egui::Sense::click());
        if !enabled {
            let painter = ui.painter();
            painter.rect_filled(rect, Rounding::same(5.0_f32), self.card_subtle());
            painter.rect_stroke(rect, Rounding::same(5.0_f32), Stroke::new(1.0_f32, self.border_subtle()));
            let font_id = egui::FontId::proportional(12.0);
            painter.text(rect.center(), egui::Align2::CENTER_CENTER, text, font_id, self.border_color());
            return response;
        }

        let is_down = response.is_pointer_button_down_on();
        let painter = ui.painter();
        let (bg, border, text_color) = if is_down {
            (self.row_selected(), self.accent_emerald(), self.accent_emerald())
        } else if response.hovered() {
            (self.row_hover(), self.accent_emerald(), self.text_primary())
        } else {
            (self.card_surface(), self.border_color(), self.text_primary())
        };

        painter.rect_filled(rect, Rounding::same(5.0_f32), bg);
        painter.rect_stroke(rect, Rounding::same(5.0_f32), Stroke::new(1.0_f32, border));

        let text_offset = if is_down { Vec2::new(0.0, 1.0) } else { Vec2::ZERO };
        let font_id = egui::FontId::proportional(12.0);
        painter.text(rect.center() + text_offset, egui::Align2::CENTER_CENTER, text, font_id, text_color);

        response
    }

    // Modern High-Contrast Status Chip
    pub fn status_badge(&self, ui: &mut egui::Ui, status: &DownloadStatus) {
        let (bg, fg, dot_col, text) = match status {
            DownloadStatus::Downloading => {
                if self.is_dark {
                    (Color32::from_rgb(0x06, 0x34, 0x26), Color32::from_rgb(0x34, 0xD3, 0x99), Color32::from_rgb(0x10, 0xB9, 0x81), "Downloading")
                } else {
                    (Color32::from_rgb(0xDC, 0xFC, 0xE7), Color32::from_rgb(0x04, 0x78, 0x57), Color32::from_rgb(0x05, 0x96, 0x69), "Downloading")
                }
            }
            DownloadStatus::Complete => {
                if self.is_dark {
                    (Color32::from_rgb(0x0F, 0x29, 0x42), Color32::from_rgb(0x38, 0xBD, 0xF8), Color32::from_rgb(0x02, 0x84, 0xC7), "Complete")
                } else {
                    (Color32::from_rgb(0xE0, 0xF2, 0xFE), Color32::from_rgb(0x03, 0x69, 0xA1), Color32::from_rgb(0x02, 0x84, 0xC7), "Complete")
                }
            }
            DownloadStatus::Paused => {
                if self.is_dark {
                    (Color32::from_rgb(0x3B, 0x28, 0x07), Color32::from_rgb(0xFB, 0xBF, 0x24), Color32::from_rgb(0xD9, 0x77, 0x06), "Paused")
                } else {
                    (Color32::from_rgb(0xFE, 0xF3, 0xC7), Color32::from_rgb(0xB4, 0x53, 0x09), Color32::from_rgb(0xD9, 0x77, 0x06), "Paused")
                }
            }
            DownloadStatus::Queued => {
                if self.is_dark {
                    (Color32::from_rgb(0x1E, 0x23, 0x30), Color32::from_rgb(0x94, 0xA3, 0xB8), Color32::from_rgb(0x64, 0x74, 0x8B), "Queued")
                } else {
                    (Color32::from_rgb(0xF1, 0xF5, 0xF9), Color32::from_rgb(0x47, 0x55, 0x69), Color32::from_rgb(0x64, 0x74, 0x8B), "Queued")
                }
            }
            DownloadStatus::Connecting => {
                if self.is_dark {
                    (Color32::from_rgb(0x28, 0x1A, 0x3D), Color32::from_rgb(0xC0, 0x84, 0xFC), Color32::from_rgb(0x93, 0x33, 0xEA), "Connecting")
                } else {
                    (Color32::from_rgb(0xF3, 0xE8, 0xFF), Color32::from_rgb(0x7E, 0x22, 0xCE), Color32::from_rgb(0x93, 0x33, 0xEA), "Connecting")
                }
            }
            DownloadStatus::Error(_) => {
                if self.is_dark {
                    (Color32::from_rgb(0x3B, 0x12, 0x12), Color32::from_rgb(0xF8, 0x71, 0x71), Color32::from_rgb(0xDC, 0x26, 0x26), "Error")
                } else {
                    (Color32::from_rgb(0xFE, 0xE2, 0xE2), Color32::from_rgb(0xB9, 0x1C, 0x1C), Color32::from_rgb(0xDC, 0x26, 0x26), "Error")
                }
            }
        };

        let (rect, _) = ui.allocate_exact_size(Vec2::new(96.0, 22.0), egui::Sense::hover());
        let painter = ui.painter();
        painter.rect_filled(rect, Rounding::same(4.0_f32), bg);
        painter.rect_stroke(rect, Rounding::same(4.0_f32), Stroke::new(1.0_f32, dot_col));

        // State indicator dot
        let dot_center = egui::pos2(rect.min.x + 12.0, rect.center().y);
        painter.circle_filled(dot_center, 3.5_f32, dot_col);

        let font_id = egui::FontId::proportional(11.0);
        painter.text(rect.center() + Vec2::new(5.0, 0.0), egui::Align2::CENTER_CENTER, text, font_id, fg);
    }

    // High Precision Performance Progress Bar
    pub fn modern_progress_bar(&self, ui: &mut egui::Ui, ratio: f32, status: &DownloadStatus, width: f32) {
        let (rect, _) = ui.allocate_exact_size(Vec2::new(width, 16.0), egui::Sense::hover());
        let painter = ui.painter();

        // Background track with crisp structural border
        painter.rect_filled(rect, Rounding::same(4.0_f32), self.card_subtle());
        painter.rect_stroke(rect, Rounding::same(4.0_f32), Stroke::new(1.0_f32, self.border_subtle()));

        // Filled track
        let clamped = ratio.clamp(0.0, 1.0);
        if clamped > 0.0 {
            let fill_width = rect.width() * clamped;
            let filled_rect = Rect::from_min_size(rect.min, Vec2::new(fill_width, rect.height()));
            let fill_color = match status {
                DownloadStatus::Complete => Color32::from_rgb(0x02, 0x84, 0xC7), // Crisp Blue for complete
                DownloadStatus::Downloading => self.accent_emerald(),           // Emerald for downloading
                DownloadStatus::Paused => self.accent_amber(),                 // Amber for paused
                DownloadStatus::Error(_) => self.accent_danger(),              // Red for error
                _ => self.text_muted(),
            };
            painter.rect_filled(filled_rect, Rounding::same(4.0_f32), fill_color);
        }

        // Percentage text overlay
        let pct_str = format!("{:.1}%", clamped * 100.0);
        let text_color = if clamped > 0.55 {
            Color32::WHITE
        } else {
            self.text_primary()
        };
        let font_id = egui::FontId::proportional(10.5);
        painter.text(rect.center(), egui::Align2::CENTER_CENTER, pct_str, font_id, text_color);
    }

    // Keyboard Keycap Style Tag (Micro-UI feature)
    pub fn keycap_hint(&self, ui: &mut egui::Ui, key: &str) {
        let (rect, _) = ui.allocate_exact_size(Vec2::new(42.0, 18.0), egui::Sense::hover());
        let painter = ui.painter();
        painter.rect_filled(rect, Rounding::same(3.0_f32), self.card_subtle());
        painter.rect_stroke(rect, Rounding::same(3.0_f32), Stroke::new(1.0_f32, self.border_color()));
        let font_id = egui::FontId::monospace(10.0);
        painter.text(rect.center(), egui::Align2::CENTER_CENTER, key, font_id, self.text_muted());
    }
}
