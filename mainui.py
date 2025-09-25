from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (QMainWindow, QApplication, QPushButton, QLabel, 
                             QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, 
                             QGridLayout, QFrame, QMenuBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap, QIcon
import sys

try:
    from config import config_manager, get_text
    from config_dialog import ConfigDialog
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load config if available
        if CONFIG_AVAILABLE:
            self.config = config_manager
            title = get_text('casino_title')
        else:
            self.config = None
            title = "Casino de tu mama"
            
        self.setWindowTitle(title)
        self.setGeometry(100, 100, 800, 600)
        
        # Apply display settings
        if self.config and self.config.is_fullscreen():
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
        title_label = QLabel(get_text('casino_title') if CONFIG_AVAILABLE else "Casino de tu mama")
        title_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #FFD700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
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
        
        # Settings menu
        if CONFIG_AVAILABLE:
            settings_menu = menubar.addMenu(get_text('settings'))
            config_action = settings_menu.addAction("Configuración...")
            config_action.triggered.connect(self.show_config_dialog)
        
        # Help menu
        help_menu = menubar.addMenu("Ayuda")
        about_action = help_menu.addAction("Acerca de...")
        about_action.triggered.connect(self.show_about)
    
    def create_game_buttons(self, layout):
        """Create game selection buttons"""
        games = [
            ("poker", get_text('poker') if CONFIG_AVAILABLE else "Póker", self.launch_poker),
            ("blackjack", get_text('blackjack') if CONFIG_AVAILABLE else "Blackjack", self.launch_blackjack),
            ("roulette", get_text('roulette') if CONFIG_AVAILABLE else "Ruleta", self.launch_roulette),
            ("slot_machine", get_text('slot_machine') if CONFIG_AVAILABLE else "Tragaperras", self.launch_slots),
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
        if CONFIG_AVAILABLE:
            dialog = ConfigDialog(self)
            dialog.config_changed.connect(self.apply_config_changes)
            dialog.exec()
        else:
            QMessageBox.information(self, "Info", "Configuración no disponible.")
    
    def apply_config_changes(self):
        """Apply configuration changes"""
        if CONFIG_AVAILABLE:
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
            from poker_main import main as poker_main
            self.hide()  # Hide main window
            poker_main()
            self.show()  # Show main window when poker closes
        except ImportError:
            QMessageBox.warning(self, "Error", "El juego de póker no está disponible.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al lanzar póker: {str(e)}")
    
    def launch_blackjack(self):
        """Launch blackjack game"""
        QMessageBox.information(self, "Próximamente", "Blackjack estará disponible próximamente.")
    
    def launch_roulette(self):
        """Launch roulette game"""
        QMessageBox.information(self, "Próximamente", "La ruleta estará disponible próximamente.")
    
    def launch_slots(self):
        """Launch slot machine game"""
        QMessageBox.information(self, "Próximamente", "Las tragaperras estarán disponibles próximamente.")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec())
