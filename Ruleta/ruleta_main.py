"""Punto de entrada principal para el juego de Ruleta.

Este módulo proporciona la función de entrada para lanzar el juego de ruleta
desde el menú principal o como aplicación independiente.
"""

from PyQt6.QtWidgets import QApplication
import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from Ruleta.ruleta_ui import RouletteWindow


def main():
    """Entry point for standalone roulette game"""
    app = QApplication.instance()
    owns_app = app is None
    
    if owns_app:
        app = QApplication(sys.argv)
    
    window = RouletteWindow()
    window.show()
    
    if owns_app:
        sys.exit(app.exec())
    
    return window, owns_app, app


def open_roulette_window(parent=None):
    """Open roulette window from main UI"""
    if parent is None:
        return main()
    else:
        return (RouletteWindow(parent), False, None)


if __name__ == "__main__":
    main()
