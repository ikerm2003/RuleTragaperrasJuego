#!/usr/bin/env python3
"""
Aplicación principal del Casino RuleTragaperrasJuego

Este módulo contiene la interfaz principal de usuario que permite acceder
a todos los juegos de casino disponibles: Poker, Blackjack, Ruleta y Tragaperras.
Gestiona la navegación entre juegos y la configuración general de la aplicación.
"""
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (QMainWindow, QApplication, QPushButton, QLabel, 
                             QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, 
                             QGridLayout, QFrame, QMenuBar, QMenu)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QIcon
import sys
import importlib

from config import config_manager, get_text  # type: ignore[import-not-found]
from config_dialog import ConfigDialog  # type: ignore[import-not-found]


class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load config if available
        self.config = config_manager
        title = get_text('casino_title')

        self._poker_window = None
        self._slots_window = None
        self._blackjack_window = None
        self._roulette_window = None

        self.setWindowTitle(title)
        self.setGeometry(100, 100, 800, 600)
        
        # Apply display settings
        if self.config.is_fullscreen():
            self.showFullScreen()
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize the main UI"""
        # Create menu bar
        self.create_menu_bar()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title_label = QLabel(get_text('casino_title'))
        title_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #FFD700;
            margin: 20px;
        """)
        main_layout.addWidget(title_label)
        
        # Game buttons container
        games_frame = QFrame()
        games_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(17, 24, 39, 0.9),
                           stop:1 rgba(31, 41, 55, 0.9));
                border: 2px solid rgba(75, 85, 99, 0.6);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        games_layout = QGridLayout(games_frame)
        games_layout.setSpacing(20)
        
        # Game buttons
        self.create_game_buttons(games_layout)
        
        main_layout.addWidget(games_frame)
        main_layout.addStretch()
        
        # Set background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(21, 128, 61, 0.8),
                           stop:1 rgba(22, 101, 52, 0.8));
            }
        """)
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        if menubar is None:
            return
        
        # Settings menu
        settings_menu = menubar.addMenu(get_text('settings'))
        if isinstance(settings_menu, QMenu):
            config_action = settings_menu.addAction("Configuración...")
            if config_action is not None:
                config_action.triggered.connect(self.show_config_dialog)
        
        # Help menu
        help_menu = menubar.addMenu("Ayuda")
        if isinstance(help_menu, QMenu):
            about_action = help_menu.addAction("Acerca de...")
            if about_action is not None:
                about_action.triggered.connect(self.show_about)
    
    def create_game_buttons(self, layout):
        """Create game selection buttons"""
        games = [
            ("poker", get_text('poker'), self.launch_poker),
            ("blackjack", get_text('blackjack'), self.launch_blackjack),
            ("roulette", get_text('roulette'), self.launch_roulette),
            ("slot_machine", get_text('slot_machine'), self.launch_slots),
        ]
        
        for i, (game_id, game_name, handler) in enumerate(games):
            button = self.create_game_button(game_name, handler)
            row = i // 2
            col = i % 2
            layout.addWidget(button, row, col)
    
    def create_game_button(self, text, handler):
        """Create a styled game button"""
        button = QPushButton(text)
        button.setMinimumSize(200, 100)
        button.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(59, 130, 246, 0.9),
                           stop:1 rgba(37, 99, 235, 0.9));
                border: 2px solid rgba(147, 197, 253, 0.6);
                border-radius: 10px;
                color: white;
                font-weight: bold;
                padding: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(96, 165, 250, 0.9),
                           stop:1 rgba(59, 130, 246, 0.9));
                border: 2px solid rgba(147, 197, 253, 0.8);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(37, 99, 235, 0.9),
                           stop:1 rgba(29, 78, 216, 0.9));
            }
        """)
        button.clicked.connect(handler)
        return button
    
    def show_config_dialog(self):
        """Show configuration dialog"""
        dialog = ConfigDialog(self)
        dialog.config_changed.connect(self.apply_config_changes)
        dialog.exec()
    
    def apply_config_changes(self):
        """Apply configuration changes"""
        # Update window title
        self.setWindowTitle(get_text('casino_title'))
            
        # Apply display settings
        if self.config.is_fullscreen():
            self.showFullScreen()
        else:
            self.showNormal()
            resolution = self.config.get_resolution()
            if resolution != (-1, -1):
                self.resize(resolution[0], resolution[1])
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "Acerca de", 
                         "Casino de tu mama\n\n"
                         "Un juego de casino con múltiples juegos:\n"
                         "• Póker Texas Hold'em\n"
                         "• Blackjack\n"
                         "• Ruleta\n"
                         "• Tragaperras\n\n"
                         "Versión 2.0")
    
    def launch_poker(self):
        """Launch poker game"""
        try:
            poker_module = importlib.import_module("Poker.poker_main")
            open_poker_window = getattr(poker_module, "open_poker_window")

            self.hide()
            window, owns_app, app = open_poker_window(num_players=6, parent=self)
            self._poker_window = window
            window.destroyed.connect(self.on_poker_window_closed)

            if owns_app:
                app.exec()

        except ImportError:
            self.show()
            QMessageBox.warning(self, "Error", "El juego de póker no está disponible.")
        except Exception as e:
            self.show()
            print(e)
            QMessageBox.critical(self, "Error", f"Error al lanzar póker: {str(e)}")

    def on_poker_window_closed(self, _obj=None):
        """Restore main window when the poker window is closed."""
        self._poker_window = None
        self.show()
    
    def launch_blackjack(self):
        """Launch blackjack game"""
        try:
            blackjack_module = importlib.import_module("Blackjack.blackjack")
            open_blackjack_window = getattr(blackjack_module, "open_blackjack_window")

            self.hide()
            window, owns_app, app = open_blackjack_window(parent=self)
            self._blackjack_window = window
            window.destroyed.connect(self.on_blackjack_window_closed)

            if owns_app:
                app.exec()

        except ImportError as e:
            self.show()
            QMessageBox.warning(self, "Error", f"El juego de Blackjack no está disponible: {str(e)}")
        except Exception as e:
            self.show()
            print(e)
            QMessageBox.critical(self, "Error", f"Error al lanzar Blackjack: {str(e)}")

    def on_blackjack_window_closed(self, _obj=None):
        """Restore main window when the blackjack window is closed."""
        self._blackjack_window = None
        self.show()
    
    def launch_roulette(self):
        """Launch roulette game"""
        try:
            roulette_module = importlib.import_module("Ruleta.ruleta_main")
            open_roulette_window = getattr(roulette_module, "open_roulette_window")

            self.hide()
            window, owns_app, app = open_roulette_window(parent=self)
            self._roulette_window = window
            window.destroyed.connect(self.on_roulette_window_closed)

            if owns_app:
                app.exec()

        except ImportError as e:
            self.show()
            QMessageBox.warning(self, "Error", f"El juego de ruleta no está disponible: {str(e)}")
        except Exception as e:
            self.show()
            print(e)
            QMessageBox.critical(self, "Error", f"Error al lanzar ruleta: {str(e)}")

    def on_roulette_window_closed(self, _obj=None):
        """Restore main window when the roulette window is closed."""
        self._roulette_window = None
        self.show()
    
    def launch_slots(self):
        """Launch slot machine game"""
        try:
            slots_module = importlib.import_module("Tragaperras.tragaperras_main")
            open_slot_window = getattr(slots_module, "open_slot_window")

            self.hide()
            window, owns_app, app = open_slot_window(parent=self)
            self._slots_window = window
            window.destroyed.connect(self.on_slots_window_closed)

            if owns_app:
                app.exec()

        except ImportError:
            self.show()
            QMessageBox.warning(self, "Error", "El juego de tragaperras no está disponible.")
        except Exception as e:
            self.show()
            print(e)
            QMessageBox.critical(self, "Error", f"Error al lanzar tragaperras: {str(e)}")

    def on_slots_window_closed(self, _obj=None):
        """Restore main window when slot machine window is closed."""
        self._slots_window = None
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec())
