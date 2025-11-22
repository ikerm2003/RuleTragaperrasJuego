"""Main entry point for the Texas Hold'em Poker game."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple, cast

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

ROOT_DIR = Path(__file__).resolve().parents[1]
POKER_DIR = ROOT_DIR / "Poker"

for path in (ROOT_DIR, POKER_DIR):
    str_path = str(path)
    if str_path not in sys.path:
        sys.path.insert(0, str_path)

if __package__:
    from .poker_ui import PokerWindow  
else:
    from Poker.poker_ui import PokerWindow  




def _normalize_player_count(num_players: int) -> int:
    """Clamp the number of players to the supported range (2-9)."""
    return max(2, min(num_players, 9))


def create_poker_application() -> QApplication:
    """Create a QApplication configured for the poker module."""
    app = QApplication(sys.argv)
    app.setApplicationName("Texas Hold'em Poker")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("RuleTragaperrasJuego")
    return app


def ensure_poker_application() -> Tuple[QApplication, bool]:
    """Ensure that a QApplication exists, returning it and an ownership flag."""
    existing_app = QApplication.instance()
    if existing_app is not None:
        return cast(QApplication, existing_app), False
    return create_poker_application(), True


def _center_window_on_screen(window: PokerWindow, app: QApplication) -> None:
    """Center the given window on the primary screen when possible."""
    primary_screen = app.primaryScreen()
    if primary_screen is None:
        return
    screen_geometry = primary_screen.availableGeometry()
    window.move(
        (screen_geometry.width() - window.width()) // 2,
        (screen_geometry.height() - window.height()) // 2,
    )


def open_poker_window(
    num_players: int = 6,
    table_type: str = "nine_player",
    parent=None,
    show_immediately: bool = True,
) -> Tuple[PokerWindow, bool, QApplication]:
    """Create the poker window, reusing an existing QApplication when available."""
    app, owns_app = ensure_poker_application()
    normalized_players = _normalize_player_count(num_players)

    window = PokerWindow(table_type=table_type, num_players=normalized_players, parent=parent)
    window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

    if show_immediately:
        window.show()
        _center_window_on_screen(window, app)

    return window, owns_app, app


def main() -> int:
    """Main application entry point."""
    try:
        _, owns_app, app = open_poker_window(num_players=6)

        if owns_app:
            return app.exec()

        # Embedded callers (e.g., main menu) will handle the event loop themselves.
        return 0

    except Exception as exc:  # pragma: no cover - defensive logging
        print(f"Error creating poker window: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())