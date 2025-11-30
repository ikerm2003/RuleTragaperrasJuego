
"""
Theme System for Casino Game
Provides customizable visual themes
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional


class ThemeType(Enum):
    """Available themes"""

    CLASSIC_GREEN = "classic_green"
    DARK = "dark"
    LIGHT = "light"
    BLUE_OCEAN = "blue_ocean"
    GOLD_LUXURY = "gold_luxury"


@dataclass
class ThemeColors:
    """Theme color scheme"""

    # Background colors
    bg_primary: str
    bg_secondary: str
    bg_tertiary: str

    # Text colors
    text_primary: str
    text_secondary: str
    text_accent: str

    # UI element colors
    button_bg: str
    button_hover: str
    button_pressed: str
    button_text: str

    # Border and accent colors
    border_primary: str
    border_secondary: str
    accent_color: str

    # Game-specific colors
    card_bg: str
    table_felt: str
    chip_primary: str


class ThemeManager:
    """Manages visual themes"""

    def __init__(self, config_manager):
        self.config = config_manager
        self.themes = self._initialize_themes()

    def _initialize_themes(self) -> Dict[ThemeType, ThemeColors]:
        """Initialize all available themes"""
        themes = {}

        # Classic Green Theme (Casino default)
        themes[ThemeType.CLASSIC_GREEN] = ThemeColors(
            bg_primary="rgba(21, 128, 61, 0.8)",
            bg_secondary="rgba(22, 101, 52, 0.8)",
            bg_tertiary="rgba(17, 24, 39, 0.9)",
            text_primary="#FFD700",
            text_secondary="#FFFFFF",
            text_accent="#90EE90",
            button_bg="rgba(59, 130, 246, 0.9)",
            button_hover="rgba(96, 165, 250, 0.9)",
            button_pressed="rgba(37, 99, 235, 0.9)",
            button_text="#FFFFFF",
            border_primary="rgba(75, 85, 99, 0.6)",
            border_secondary="rgba(147, 197, 253, 0.6)",
            accent_color="#FFD700",
            card_bg="#FFFFFF",
            table_felt="#1B5E20",
            chip_primary="#FF5722",
        )

        # Dark Theme
        themes[ThemeType.DARK] = ThemeColors(
            bg_primary="rgba(17, 24, 39, 1.0)",
            bg_secondary="rgba(31, 41, 55, 1.0)",
            bg_tertiary="rgba(55, 65, 81, 1.0)",
            text_primary="#F3F4F6",
            text_secondary="#D1D5DB",
            text_accent="#60A5FA",
            button_bg="rgba(55, 65, 81, 0.9)",
            button_hover="rgba(75, 85, 99, 0.9)",
            button_pressed="rgba(31, 41, 55, 0.9)",
            button_text="#F3F4F6",
            border_primary="rgba(75, 85, 99, 0.8)",
            border_secondary="rgba(107, 114, 128, 0.8)",
            accent_color="#60A5FA",
            card_bg="#374151",
            table_felt="#1F2937",
            chip_primary="#EF4444",
        )

        # Light Theme
        themes[ThemeType.LIGHT] = ThemeColors(
            bg_primary="rgba(243, 244, 246, 1.0)",
            bg_secondary="rgba(229, 231, 235, 1.0)",
            bg_tertiary="rgba(209, 213, 219, 1.0)",
            text_primary="#1F2937",
            text_secondary="#4B5563",
            text_accent="#2563EB",
            button_bg="rgba(59, 130, 246, 0.9)",
            button_hover="rgba(96, 165, 250, 0.9)",
            button_pressed="rgba(37, 99, 235, 0.9)",
            button_text="#FFFFFF",
            border_primary="rgba(209, 213, 219, 1.0)",
            border_secondary="rgba(156, 163, 175, 1.0)",
            accent_color="#2563EB",
            card_bg="#FFFFFF",
            table_felt="#E5E7EB",
            chip_primary="#3B82F6",
        )

        # Blue Ocean Theme
        themes[ThemeType.BLUE_OCEAN] = ThemeColors(
            bg_primary="rgba(12, 74, 110, 0.9)",
            bg_secondary="rgba(15, 23, 42, 0.9)",
            bg_tertiary="rgba(30, 41, 59, 0.9)",
            text_primary="#7DD3FC",
            text_secondary="#BFDBFE",
            text_accent="#38BDF8",
            button_bg="rgba(14, 116, 144, 0.9)",
            button_hover="rgba(6, 182, 212, 0.9)",
            button_pressed="rgba(8, 145, 178, 0.9)",
            button_text="#FFFFFF",
            border_primary="rgba(6, 182, 212, 0.5)",
            border_secondary="rgba(56, 189, 248, 0.5)",
            accent_color="#38BDF8",
            card_bg="#F0F9FF",
            table_felt="#0C4A6E",
            chip_primary="#06B6D4",
        )

        # Gold Luxury Theme
        themes[ThemeType.GOLD_LUXURY] = ThemeColors(
            bg_primary="rgba(120, 53, 15, 0.9)",
            bg_secondary="rgba(69, 26, 3, 0.9)",
            bg_tertiary="rgba(41, 37, 36, 0.9)",
            text_primary="#FDE047",
            text_secondary="#FEF08A",
            text_accent="#FACC15",
            button_bg="rgba(161, 98, 7, 0.9)",
            button_hover="rgba(202, 138, 4, 0.9)",
            button_pressed="rgba(133, 77, 14, 0.9)",
            button_text="#FFFFFF",
            border_primary="rgba(202, 138, 4, 0.6)",
            border_secondary="rgba(250, 204, 21, 0.6)",
            accent_color="#FACC15",
            card_bg="#FFFBEB",
            table_felt="#78350F",
            chip_primary="#EAB308",
        )

        return themes

    def get_current_theme(self) -> ThemeType:
        """Get the currently selected theme"""
        theme_str = self.config.get("interface", "theme", ThemeType.CLASSIC_GREEN.value)
        try:
            return ThemeType(theme_str)
        except ValueError:
            return ThemeType.CLASSIC_GREEN

    def set_theme(self, theme: ThemeType) -> None:
        """Set the current theme"""
        self.config.set("interface", "theme", theme.value)
        self.config.save_config()

    def get_theme_colors(self, theme: Optional[ThemeType] = None) -> ThemeColors:
        """Get colors for specified theme (or current theme)"""
        if theme is None:
            theme = self.get_current_theme()
        return self.themes.get(theme, self.themes[ThemeType.CLASSIC_GREEN])

    def get_window_stylesheet(self, theme: Optional[ThemeType] = None) -> str:
        """Get main window stylesheet for theme"""
        colors = self.get_theme_colors(theme)

        return f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 {colors.bg_primary},
                           stop:1 {colors.bg_secondary});
            }}
        """

    def get_button_stylesheet(self, theme: Optional[ThemeType] = None) -> str:
        """Get button stylesheet for theme"""
        colors = self.get_theme_colors(theme)

        return f"""
            QPushButton {{
                background: {colors.button_bg};
                border: 2px solid {colors.border_secondary};
                border-radius: 10px;
                color: {colors.button_text};
                font-weight: bold;
                padding: 15px;
            }}
            QPushButton:hover {{
                background: {colors.button_hover};
                border: 2px solid {colors.accent_color};
            }}
            QPushButton:pressed {{
                background: {colors.button_pressed};
            }}
        """

    def get_frame_stylesheet(self, theme: Optional[ThemeType] = None) -> str:
        """Get frame stylesheet for theme"""
        colors = self.get_theme_colors(theme)

        return f"""
            QFrame {{
                background: {colors.bg_tertiary};
                border: 2px solid {colors.border_primary};
                border-radius: 15px;
                padding: 20px;
            }}
        """

    def get_label_stylesheet(
        self, theme: Optional[ThemeType] = None, accent: bool = False
    ) -> str:
        """Get label stylesheet for theme"""
        colors = self.get_theme_colors(theme)
        color = colors.text_accent if accent else colors.text_primary

        return f"""
            QLabel {{
                color: {color};
            }}
        """

    def apply_theme_to_widget(self, widget, theme: Optional[ThemeType] = None) -> None:
        """Apply theme to a widget"""
        colors = self.get_theme_colors(theme)

        # Apply appropriate stylesheet based on widget type
        widget_type = type(widget).__name__

        if "MainWindow" in widget_type or "QMainWindow" in widget_type:
            widget.setStyleSheet(self.get_window_stylesheet(theme))
        elif "Button" in widget_type:
            widget.setStyleSheet(self.get_button_stylesheet(theme))
        elif "Frame" in widget_type:
            widget.setStyleSheet(self.get_frame_stylesheet(theme))


# Create global theme manager instance
_theme_manager = None


def get_theme_manager(config_manager=None):
    """Get the global theme manager instance"""
    global _theme_manager
    if _theme_manager is None and config_manager is not None:
        _theme_manager = ThemeManager(config_manager)
    return _theme_manager
