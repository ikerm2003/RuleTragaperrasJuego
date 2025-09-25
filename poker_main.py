"""
Main entry point for the Texas Hold'em Poker game.

This module integrates the modular poker components and provides
the main application entry point.
"""
import sys
from typing import Optional

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from poker_ui import PokerWindow
    PYQT6_AVAILABLE = True
except ImportError:
    PYQT6_AVAILABLE = False


def create_poker_application(num_players: int = 6) -> Optional[QApplication]:
    """
    Create the poker application with specified number of players.
    
    Args:
        num_players: Number of players (2-9, default 6)
    
    Returns:
        QApplication instance if PyQt6 is available, None otherwise
    """
    if not PYQT6_AVAILABLE:
        print("PyQt6 is not available. Cannot create GUI application.")
        return None
    
    # Validate num_players
    num_players = max(2, min(num_players, 9))
    
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
    
    # Create and show main window
    try:
        window = PokerWindow(table_type="nine_player", num_players=6)
        window.show()
        
        # Set window to center of screen
        screen = app.primaryScreen().availableGeometry()
        window.move(
            (screen.width() - window.width()) // 2,
            (screen.height() - window.height()) // 2
        )
        
        return app.exec()
        
    except Exception as e:
        print(f"Error creating poker window: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())