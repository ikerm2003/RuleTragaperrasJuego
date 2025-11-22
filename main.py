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
from PyQt6.QtGui import QFont, QPixmap, QIcon, QKeySequence, QShortcut
import sys
import importlib
from PyQt6.QtWidgets import QDialog, QProgressBar
from .config import config_manager
from PyQt6.QtWidgets import QDialog, QScrollArea, QVBoxLayout as QVBox
from .config import config_manager

from config import config_manager, get_text
from config_dialog import ConfigDialog  
from achievements import AchievementManager  
from missions import MissionManager


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
        
        # Initialize achievement and mission managers
        self.achievement_manager = AchievementManager(self.config)
        self.mission_manager = MissionManager(self.config)
        
        # Add achievement unlock listener
        self.achievement_manager.add_listener(self.on_achievement_unlocked)

        self.setWindowTitle(title)
        self.setGeometry(100, 100, 800, 600)
        
        # Apply display settings
        if self.config.is_fullscreen():
            self.showFullScreen()
        
        self.init_ui()
        self.setup_shortcuts()
        
        # Check for daily refill
        self.check_daily_refill()
    
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
        
        # Balance and mode display
        self.status_frame = QFrame()
        self.status_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 215, 0, 0.5);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        status_layout = QHBoxLayout(self.status_frame)
        
        # Balance label
        self.balance_label = QLabel()
        self.balance_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.balance_label.setStyleSheet("color: #FFD700;")
        self.update_balance_display()
        status_layout.addWidget(self.balance_label)
        
        status_layout.addStretch()
        
        # Practice mode indicator
        self.mode_label = QLabel()
        self.mode_label.setFont(QFont("Arial", 12))
        self.update_mode_display()
        status_layout.addWidget(self.mode_label)
        
        main_layout.addWidget(self.status_frame)
        
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
    
    def setup_shortcuts(self):
        """Setup keyboard shortcuts for the main menu"""
        # Number keys for launching games
        QShortcut(QKeySequence("1"), self).activated.connect(self.launch_poker)
        QShortcut(QKeySequence("2"), self).activated.connect(self.launch_blackjack)
        QShortcut(QKeySequence("3"), self).activated.connect(self.launch_roulette)
        QShortcut(QKeySequence("4"), self).activated.connect(self.launch_slots)
        
        # F11 for fullscreen toggle
        QShortcut(QKeySequence("F11"), self).activated.connect(self.toggle_fullscreen)
        
        # Escape to quit
        QShortcut(QKeySequence("Esc"), self).activated.connect(self.close)
        
        # Ctrl+Q to quit
        QShortcut(QKeySequence("Ctrl+Q"), self).activated.connect(self.close)
        
        # Ctrl+S for settings
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.show_config_dialog)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
            self.config.set('display', 'fullscreen', False)
        else:
            self.showFullScreen()
            self.config.set('display', 'fullscreen', True)
        self.config.save_config()
    
    def check_daily_refill(self):
        """Check and apply daily refill if applicable"""
        if self.config.check_daily_refill():
            balance = self.config.get_player_balance()
            message = get_text('daily_refill_message').format(balance=balance)
            QMessageBox.information(
                self,
                get_text('daily_refill_title'),
                message
            )
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        if menubar is None:
            return
        
        # Game menu
        game_menu = menubar.addMenu(get_text('game_menu'))
        if isinstance(game_menu, QMenu):
            # Practice mode toggle
            self.practice_mode_action = game_menu.addAction(get_text('practice_mode'))
            if self.practice_mode_action is not None:
                self.practice_mode_action.setCheckable(True)
                self.practice_mode_action.setChecked(self.config.is_practice_mode())
                self.practice_mode_action.triggered.connect(self.toggle_practice_mode)
            
            game_menu.addSeparator()
            
            # Statistics
            stats_action = game_menu.addAction(get_text('view_statistics'))
            if stats_action is not None:
                stats_action.triggered.connect(self.show_statistics)
            
            # Achievements
            achievements_action = game_menu.addAction(get_text('view_achievements'))
            if achievements_action is not None:
                achievements_action.triggered.connect(self.show_achievements)
            
            # Missions
            missions_action = game_menu.addAction(get_text('view_missions'))
            if missions_action is not None:
                missions_action.triggered.connect(self.show_missions)
        
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
            ("poker", f"{get_text('poker')} (1)", self.launch_poker),
            ("blackjack", f"{get_text('blackjack')} (2)", self.launch_blackjack),
            ("roulette", f"{get_text('roulette')} (3)", self.launch_roulette),
            ("slot_machine", f"{get_text('slot_machine')} (4)", self.launch_slots),
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
        shortcuts_help = get_text('shortcuts_help')
        QMessageBox.about(self, "Acerca de", 
                         f"Casino de tu mama\n\n"
                         f"Un juego de casino con múltiples juegos:\n"
                         f"• Póker Texas Hold'em\n"
                         f"• Blackjack\n"
                         f"• Ruleta\n"
                         f"• Tragaperras\n\n"
                         f"Versión 2.0\n\n"
                         f"{get_text('keyboard_shortcuts')}:\n"
                         f"{shortcuts_help}")
    
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
    
    def update_balance_display(self):
        """Update the balance display"""
        balance = self.config.get_effective_balance()
        balance_type = get_text('practice_balance') if self.config.is_practice_mode() else get_text('real_balance')
        self.balance_label.setText(f"{balance_type}: {balance} créditos")
    
    def update_mode_display(self):
        """Update the practice mode indicator"""
        if self.config.is_practice_mode():
            self.mode_label.setText(get_text('practice_mode_on'))
            self.mode_label.setStyleSheet("color: #FFA500; font-weight: bold;")
        else:
            self.mode_label.setText(get_text('practice_mode_off'))
            self.mode_label.setStyleSheet("color: #90EE90;")
    
    def toggle_practice_mode(self):
        """Toggle practice mode"""
        current = self.config.is_practice_mode()
        self.config.set_practice_mode(not current)
        self.update_balance_display()
        self.update_mode_display()
        
        mode_str = get_text('practice_mode_on') if not current else get_text('practice_mode_off')
        QMessageBox.information(self, get_text('practice_mode'), mode_str)
    
    def on_achievement_unlocked(self, achievement):
        """Handle achievement unlock notification"""
        from .config import config_manager
        lang = config_manager.get_language().value
        
        message = f"{achievement.get_name(lang)}\n\n{achievement.get_description(lang)}\n\n{get_text('mission_reward').format(reward=achievement.reward)}"
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(get_text('achievement_unlocked'))
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()
        
        self.update_balance_display()
    
    def show_statistics(self):
        """Show statistics dialog"""
        from PyQt6.QtWidgets import QDialog, QTextBrowser
        
        dialog = QDialog(self)
        dialog.setWindowTitle(get_text('statistics'))
        dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Create statistics text
        stats_text = f"""
        <h2>{get_text('statistics')}</h2>
        <table style="width:100%; border-collapse: collapse;">
            <tr><td style="padding: 5px;"><b>{get_text('total_hands')}:</b></td><td style="padding: 5px;">{self.config.get_statistic('total_hands_played')}</td></tr>
            <tr><td style="padding: 5px;"><b>{get_text('total_wins')}:</b></td><td style="padding: 5px;">{self.config.get_statistic('total_wins')}</td></tr>
            <tr><td style="padding: 5px;"><b>{get_text('total_losses')}:</b></td><td style="padding: 5px;">{self.config.get_statistic('total_losses')}</td></tr>
            <tr><td style="padding: 5px;"><b>{get_text('biggest_win')}:</b></td><td style="padding: 5px;">{self.config.get_statistic('biggest_win')} créditos</td></tr>
        </table>
        <br>
        <h3>{get_text('game_menu')}</h3>
        <table style="width:100%; border-collapse: collapse;">
            <tr><td style="padding: 5px;"><b>Poker:</b></td><td style="padding: 5px;">{self.config.get_statistic('poker_hands')} manos</td></tr>
            <tr><td style="padding: 5px;"><b>Blackjack:</b></td><td style="padding: 5px;">{self.config.get_statistic('blackjack_hands')} manos</td></tr>
            <tr><td style="padding: 5px;"><b>Ruleta:</b></td><td style="padding: 5px;">{self.config.get_statistic('roulette_spins')} giros</td></tr>
            <tr><td style="padding: 5px;"><b>Tragaperras:</b></td><td style="padding: 5px;">{self.config.get_statistic('slots_spins')} giros</td></tr>
        </table>
        """
        
        text_browser = QTextBrowser()
        text_browser.setHtml(stats_text)
        layout.addWidget(text_browser)
        
        # Reset button
        reset_btn = QPushButton(get_text('reset_stats'))
        reset_btn.clicked.connect(lambda: self.reset_statistics(dialog))
        layout.addWidget(reset_btn)
        
        # Close button
        close_btn = QPushButton(get_text('cancel'))
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def reset_statistics(self, parent_dialog):
        """Reset all statistics"""
        reply = QMessageBox.question(
            self, 
            get_text('reset_stats'),
            get_text('reset_stats_confirm'),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config.reset_statistics()
            QMessageBox.information(self, get_text('statistics'), "Estadísticas reiniciadas")
            parent_dialog.close()
            self.show_statistics()
    
    def show_achievements(self):
        """Show achievements dialog"""
        
        lang = config_manager.get_language().value
        
        dialog = QDialog(self)
        dialog.setWindowTitle(get_text('achievements'))
        dialog.setMinimumSize(500, 400)
        
        main_layout = QVBoxLayout(dialog)
        
        # Scroll area for achievements
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBox(scroll_widget)
        
        # Show unlocked achievements
        unlocked = self.achievement_manager.get_unlocked_achievements()
        if unlocked:
            unlocked_label = QLabel(f"<h3>{get_text('unlocked')} ({len(unlocked)})</h3>")
            scroll_layout.addWidget(unlocked_label)
            
            for ach in unlocked:
                ach_frame = QFrame()
                ach_frame.setStyleSheet("""
                    QFrame {
                        background: rgba(0, 255, 0, 0.1);
                        border: 1px solid rgba(0, 255, 0, 0.3);
                        border-radius: 5px;
                        padding: 10px;
                        margin: 5px;
                    }
                """)
                ach_layout = QVBox(ach_frame)
                
                name_label = QLabel(f"<b>{ach.get_name(lang)}</b>")
                ach_layout.addWidget(name_label)
                
                desc_label = QLabel(ach.get_description(lang))
                desc_label.setWordWrap(True)
                ach_layout.addWidget(desc_label)
                
                reward_label = QLabel(f"🏆 {get_text('mission_reward').format(reward=ach.reward)}")
                ach_layout.addWidget(reward_label)
                
                scroll_layout.addWidget(ach_frame)
        
        # Show locked achievements
        locked = self.achievement_manager.get_locked_achievements()
        if locked:
            locked_label = QLabel(f"<h3>{get_text('locked')} ({len(locked)})</h3>")
            scroll_layout.addWidget(locked_label)
            
            for ach in locked:
                ach_frame = QFrame()
                ach_frame.setStyleSheet("""
                    QFrame {
                        background: rgba(128, 128, 128, 0.1);
                        border: 1px solid rgba(128, 128, 128, 0.3);
                        border-radius: 5px;
                        padding: 10px;
                        margin: 5px;
                    }
                """)
                ach_layout = QVBox(ach_frame)
                
                name_label = QLabel(f"<b>{ach.get_name(lang)}</b>")
                ach_layout.addWidget(name_label)
                
                desc_label = QLabel(ach.get_description(lang))
                desc_label.setWordWrap(True)
                ach_layout.addWidget(desc_label)
                
                # Progress bar
                progress = self.achievement_manager.get_achievement_progress_percent(ach.id)
                progress_label = QLabel(f"{get_text('progress')}: {int(progress)}%")
                ach_layout.addWidget(progress_label)
                
                scroll_layout.addWidget(ach_frame)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
        
        # Close button
        close_btn = QPushButton(get_text('cancel'))
        close_btn.clicked.connect(dialog.close)
        main_layout.addWidget(close_btn)
        
        dialog.exec()
    
    def show_missions(self):
        """Show daily missions dialog"""
        lang = config_manager.get_language().value
        
        dialog = QDialog(self)
        dialog.setWindowTitle(get_text('missions'))
        dialog.setMinimumSize(450, 350)
        
        layout = QVBoxLayout(dialog)
        
        # Title
        title_label = QLabel(f"<h2>{get_text('missions')}</h2>")
        layout.addWidget(title_label)
        
        # Get missions
        missions = self.mission_manager.get_current_missions()
        
        for mission in missions:
            mission_frame = QFrame()
            is_completed = self.config.is_mission_completed(mission.id)
            
            if is_completed:
                mission_frame.setStyleSheet("""
                    QFrame {
                        background: rgba(0, 255, 0, 0.2);
                        border: 2px solid rgba(0, 255, 0, 0.5);
                        border-radius: 5px;
                        padding: 10px;
                        margin: 5px;
                    }
                """)
            else:
                mission_frame.setStyleSheet("""
                    QFrame {
                        background: rgba(255, 255, 255, 0.1);
                        border: 1px solid rgba(255, 255, 255, 0.3);
                        border-radius: 5px;
                        padding: 10px;
                        margin: 5px;
                    }
                """)
            
            mission_layout = QVBoxLayout(mission_frame)
            
            # Name and status
            name_text = mission.get_name(lang)
            if is_completed:
                name_text += f" ✓ {get_text('completed')}"
            name_label = QLabel(f"<b>{name_text}</b>")
            mission_layout.addWidget(name_label)
            
            # Description
            desc_label = QLabel(mission.get_description(lang))
            desc_label.setWordWrap(True)
            mission_layout.addWidget(desc_label)
            
            # Progress bar
            if not is_completed:
                progress_bar = QProgressBar()
                progress_percent = self.mission_manager.get_mission_progress_percent(mission)
                progress_bar.setValue(int(progress_percent))
                
                current_progress = self.mission_manager.get_mission_progress(mission)
                progress_bar.setFormat(f"{current_progress}/{mission.target}")
                mission_layout.addWidget(progress_bar)
            
            # Reward
            reward_label = QLabel(f"🎁 {get_text('mission_reward').format(reward=mission.reward)}")
            mission_layout.addWidget(reward_label)
            
            layout.addWidget(mission_frame)
        
        layout.addStretch()
        
        # Close button
        close_btn = QPushButton(get_text('cancel'))
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainUI()
    window.show()
    sys.exit(app.exec())
