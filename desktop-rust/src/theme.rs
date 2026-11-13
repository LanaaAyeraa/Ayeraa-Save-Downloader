use crate::download::DownloadStatus;
use eframe::egui::{self, Color32, Rect, Response, Rounding, Stroke, Vec2};

#[derive(Clone, Debug)]
pub struct ClaudeTheme {
    pub is_dark: bool,
}

impl ClaudeTheme {
    pub fn new(is_dark: bool) -> Self {
        Self { is_dark }
    }

    // Surfaces & Backgrounds
    pub fn bg_color(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x1A, 0x19, 0x18) // Rich warm charcoal
        } else {
            Color32::from_rgb(0xFA, 0xF9, 0xF5) // Warm sand / cream
        }
    }

    pub fn card_surface(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x24, 0x23, 0x21) // Card surface
        } else {
            Color32::from_rgb(0xFF, 0xFF, 0xFF)
        }
    }

    pub fn card_subtle(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x1F, 0x1E, 0x1C) // Sub-panel / table background
        } else {
            Color32::from_rgb(0xF3, 0xF1, 0xEA)
        }
    }

    pub fn row_hover(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x2E, 0x2C, 0x29)
        } else {
            Color32::from_rgb(0xEE, 0xEA, 0xE2)
        }
    }

    pub fn row_selected(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x3B, 0x29, 0x21) // Subtle warm terracotta tint
        } else {
            Color32::from_rgb(0xF9, 0xEB, 0xE4)
        }
    }

    pub fn border_color(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x36, 0x34, 0x31)
        } else {
            Color32::from_rgb(0xE2, 0xDF, 0xD7)
        }
    }

    pub fn border_subtle(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x2A, 0x28, 0x26)
        } else {
            Color32::from_rgb(0xEB, 0xE8, 0xE1)
        }
    }

    // Typography
    pub fn text_primary(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0xEC, 0xEA, 0xE4) // Warm cream ink
        } else {
            Color32::from_rgb(0x1F, 0x1E, 0x1D) // Deep espresso ink
        }
    }

    pub fn text_muted(&self) -> Color32 {
        if self.is_dark {
            Color32::from_rgb(0x9E, 0x9B, 0x93)
        } else {
            Color32::from_rgb(0x73, 0x71, 0x6A)
        }
    }

    // Accent Colors
    pub fn accent_terracotta(&self) -> Color32 {
        Color32::from_rgb(0xCC, 0x5A, 0x37) // Iconic Claude terracotta
    }

    pub fn accent_terracotta_hover(&self) -> Color32 {
        Color32::from_rgb(0xB8, 0x4E, 0x2E)
    }

    pub fn accent_amber(&self) -> Color32 {
        Color32::from_rgb(0xD9, 0x77, 0x06) // Warm amber
    }

    pub fn accent_emerald(&self) -> Color32 {
        Color32::from_rgb(0x10, 0xB9, 0x81) // Crisp success green
    }

    pub fn accent_sky(&self) -> Color32 {
        Color32::from_rgb(0x02, 0x84, 0xC7) // Rich sky blue
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
        visuals.window_rounding = Rounding::same(10.0_f32);
        visuals.menu_rounding = Rounding::same(8.0_f32);
        visuals.extreme_bg_color = self.card_subtle();

        visuals.widgets.inactive.bg_fill = self.card_surface();
        visuals.widgets.inactive.bg_stroke = Stroke::new(1.0_f32, self.border_color());
        visuals.widgets.inactive.fg_stroke = Stroke::new(1.0_f32, self.text_primary());
        visuals.widgets.inactive.rounding = Rounding::same(6.0_f32);

        visuals.widgets.hovered.bg_fill = self.row_hover();
        visuals.widgets.hovered.bg_stroke = Stroke::new(1.0_f32, self.accent_terracotta());
        visuals.widgets.hovered.fg_stroke = Stroke::new(1.0_f32, self.text_primary());
        visuals.widgets.hovered.rounding = Rounding::same(6.0_f32);

        visuals.widgets.active.bg_fill = self.accent_terracotta();
        visuals.widgets.active.bg_stroke = Stroke::new(1.0_f32, self.accent_terracotta_hover());
        visuals.widgets.active.fg_stroke = Stroke::new(1.0_f32, Color32::WHITE);
        visuals.widgets.active.rounding = Rounding::same(6.0_f32);

        visuals.widgets.noninteractive.bg_fill = self.card_surface();
        visuals.widgets.noninteractive.bg_stroke = Stroke::new(1.0_f32, self.border_color());
        visuals.widgets.noninteractive.fg_stroke = Stroke::new(1.0_f32, self.text_primary());
        visuals.widgets.noninteractive.rounding = Rounding::same(6.0_f32);

        visuals.selection.bg_fill = self.row_selected();
        visuals.selection.stroke = Stroke::new(1.0_f32, self.accent_terracotta());

        ctx.set_visuals(visuals);
    }

    // Custom Styled Components
    pub fn primary_button(&self, ui: &mut egui::Ui, text: &str) -> Response {
        let (rect, response) = ui.allocate_exact_size(Vec2::new(116.0, 32.0), egui::Sense::click());
        let bg = if response.is_pointer_button_down_on() {
            self.accent_terracotta_hover()
        } else if response.hovered() {
            self.accent_terracotta_hover()
        } else {
            self.accent_terracotta()
        };

        let painter = ui.painter();
        painter.rect_filled(rect, Rounding::same(6.0_f32), bg);

        let font_id = egui::FontId::proportional(12.5);
        painter.text(
            rect.center(),
            egui::Align2::CENTER_CENTER,
            text,
            font_id,
            Color32::WHITE,
        );

        response
    }

    pub fn tool_button(&self, ui: &mut egui::Ui, text: &str, enabled: bool) -> Response {
        let (rect, response) = ui.allocate_exact_size(Vec2::new(94.0, 32.0), egui::Sense::click());
        if !enabled {
            let painter = ui.painter();
            painter.rect_filled(rect, Rounding::same(6.0_f32), self.card_subtle());
            painter.rect_stroke(rect, Rounding::same(6.0_f32), Stroke::new(1.0_f32, self.border_subtle()));
            let font_id = egui::FontId::proportional(12.0);
            painter.text(rect.center(), egui::Align2::CENTER_CENTER, text, font_id, self.border_color());
            return response;
        }

        let painter = ui.painter();
        let (bg, border, text_color) = if response.is_pointer_button_down_on() {
            (self.row_selected(), self.accent_terracotta(), self.accent_terracotta())
        } else if response.hovered() {
            (self.row_hover(), self.accent_terracotta(), self.text_primary())
        } else {
            (self.card_surface(), self.border_color(), self.text_primary())
        };

        painter.rect_filled(rect, Rounding::same(6.0_f32), bg);
        painter.rect_stroke(rect, Rounding::same(6.0_f32), Stroke::new(1.0_f32, border));
        let font_id = egui::FontId::proportional(12.0);
        painter.text(rect.center(), egui::Align2::CENTER_CENTER, text, font_id, text_color);

        response
    }

    pub fn status_badge(&self, ui: &mut egui::Ui, status: &DownloadStatus) {
        let (bg, fg, dot_col, text) = match status {
            DownloadStatus::Downloading => {
                if self.is_dark {
                    (Color32::from_rgb(0x13, 0x2A, 0x3E), Color32::from_rgb(0x38, 0xBD, 0xF8), Color32::from_rgb(0x38, 0xBD, 0xF8), "Downloading")
                } else {
                    (Color32::from_rgb(0xE0, 0xF2, 0xFE), Color32::from_rgb(0x02, 0x84, 0xC7), Color32::from_rgb(0x02, 0x84, 0xC7), "Downloading")
                }
            }
            DownloadStatus::Complete => {
                if self.is_dark {
                    (Color32::from_rgb(0x14, 0x33, 0x24), Color32::from_rgb(0x34, 0xD3, 0x99), Color32::from_rgb(0x34, 0xD3, 0x99), "Complete")
                } else {
                    (Color32::from_rgb(0xDC, 0xFC, 0xE7), Color32::from_rgb(0x15, 0x80, 0x3D), Color32::from_rgb(0x15, 0x80, 0x3D), "Complete")
                }
            }
            DownloadStatus::Paused => {
                if self.is_dark {
                    (Color32::from_rgb(0x3A, 0x2D, 0x14), Color32::from_rgb(0xFB, 0xBF, 0x24), Color32::from_rgb(0xFB, 0xBF, 0x24), "Paused")
                } else {
                    (Color32::from_rgb(0xFE, 0xF3, 0xC7), Color32::from_rgb(0xB4, 0x53, 0x09), Color32::from_rgb(0xB4, 0x53, 0x09), "Paused")
                }
            }
            DownloadStatus::Queued => {
                if self.is_dark {
                    (Color32::from_rgb(0x26, 0x25, 0x24), Color32::from_rgb(0x9E, 0x9B, 0x93), Color32::from_rgb(0x9E, 0x9B, 0x93), "Queued")
                } else {
                    (Color32::from_rgb(0xF3, 0xF4, 0xF6), Color32::from_rgb(0x6B, 0x72, 0x80), Color32::from_rgb(0x6B, 0x72, 0x80), "Queued")
                }
            }
            DownloadStatus::Connecting => {
                if self.is_dark {
                    (Color32::from_rgb(0x2D, 0x20, 0x3E), Color32::from_rgb(0xC0, 0x84, 0xFC), Color32::from_rgb(0xC0, 0x84, 0xFC), "Connecting")
                } else {
                    (Color32::from_rgb(0xF3, 0xE8, 0xFF), Color32::from_rgb(0x7E, 0x22, 0xCE), Color32::from_rgb(0x7E, 0x22, 0xCE), "Connecting")
                }
            }
            DownloadStatus::Error(_) => {
                if self.is_dark {
                    (Color32::from_rgb(0x3E, 0x18, 0x18), Color32::from_rgb(0xF8, 0x71, 0x71), Color32::from_rgb(0xF8, 0x71, 0x71), "Error")
                } else {
                    (Color32::from_rgb(0xFE, 0xE2, 0xE2), Color32::from_rgb(0xB9, 0x1C, 0x1C), Color32::from_rgb(0xB9, 0x1C, 0x1C), "Error")
                }
            }
        };

        let (rect, _) = ui.allocate_exact_size(Vec2::new(96.0, 22.0), egui::Sense::hover());
        let painter = ui.painter();
        painter.rect_filled(rect, Rounding::same(11.0_f32), bg);

        // Vector circle dot indicator
        let dot_center = egui::pos2(rect.min.x + 13.0, rect.center().y);
        painter.circle_filled(dot_center, 3.5_f32, dot_col);

        let font_id = egui::FontId::proportional(11.0);
        painter.text(rect.center() + Vec2::new(5.0, 0.0), egui::Align2::CENTER_CENTER, text, font_id, fg);
    }

    pub fn modern_progress_bar(&self, ui: &mut egui::Ui, ratio: f32, status: &DownloadStatus, width: f32) {
        let (rect, _) = ui.allocate_exact_size(Vec2::new(width, 16.0), egui::Sense::hover());
        let painter = ui.painter();

        // Background track
        painter.rect_filled(rect, Rounding::same(8.0_f32), self.card_subtle());
        painter.rect_stroke(rect, Rounding::same(8.0_f32), Stroke::new(1.0_f32, self.border_subtle()));

        // Filled track
        let clamped = ratio.clamp(0.0, 1.0);
        if clamped > 0.0 {
            let fill_width = rect.width() * clamped;
            let filled_rect = Rect::from_min_size(rect.min, Vec2::new(fill_width, rect.height()));
            let fill_color = match status {
                DownloadStatus::Complete => self.accent_emerald(),
                DownloadStatus::Downloading => self.accent_terracotta(),
                DownloadStatus::Paused => self.accent_amber(),
                _ => self.text_muted(),
            };
            painter.rect_filled(filled_rect, Rounding::same(8.0_f32), fill_color);
        }

        // Percentage text overlay
        let pct_str = format!("{:.0}%", clamped * 100.0);
        let text_color = if clamped > 0.55 {
            Color32::WHITE
        } else {
            self.text_primary()
        };
        let font_id = egui::FontId::proportional(10.0);
        painter.text(rect.center(), egui::Align2::CENTER_CENTER, pct_str, font_id, text_color);
    }
}
