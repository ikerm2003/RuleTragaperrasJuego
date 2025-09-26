"""Main entry point for the Texas Hold'em Poker game."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

try:
    from PyQt6.QtWidgets import QApplication
    PYQT6_AVAILABLE = True
except ImportError:  # pragma: no cover - handled gracefully at runtime
    QApplication = None  # type: ignore[assignment]
    PYQT6_AVAILABLE = False


if __package__ in (None, ""):
    current_dir = Path(__file__).resolve().parent
    parent_dir = current_dir.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))


if PYQT6_AVAILABLE:
    from Poker.poker_ui import PokerWindow
else:  # pragma: no cover - fallback when PyQt6 is missing
    PokerWindow = None  # type: ignore[assignment]


def create_poker_application(num_players: int = 6) -> Optional[QApplication]:
    """
    Create the poker application with specified number of players.
    
    Args:
        num_players: Number of players (2-9, default 6)
    
    Returns:
        QApplication instance if PyQt6 is available, None otherwise
    """
    
    # Validate num_players
    num_players = max(2, min(num_players, 9))
    
    if not PYQT6_AVAILABLE or QApplication is None:
        raise RuntimeError("PyQt6 is required to create the application.")

    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Texas Hold'em Poker")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("RuleTragaperrasJuego")
    
    return app


def main():
    """Main application entry point"""
    if not PYQT6_AVAILABLE:
        print("Error: PyQt6 is required to run the poker game.")
        print("Please install PyQt6: pip install PyQt6")
        return 1
    
    # Create application
    app = create_poker_application(num_players=6)
    if not app:
        return 1
    assert app is not None  # for type checkers
    
    # Create and show main window
    try:
        if PokerWindow is None:
            raise RuntimeError("PokerWindow is unavailable because PyQt6 could not be imported.")

        window = PokerWindow(table_type="nine_player", num_players=6)
        window.show()
        
        # Set window to center of screen
        primary_screen = app.primaryScreen()
        if primary_screen is not None:
            screen_geometry = primary_screen.availableGeometry()
            window.move(
                (screen_geometry.width() - window.width()) // 2,
                (screen_geometry.height() - window.height()) // 2,
            )
        
        return app.exec()
        
    except Exception as e:
        print(f"Error creating poker window: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())