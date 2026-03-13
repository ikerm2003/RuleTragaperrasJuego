"""
Aplicación principal del Casino RuleTragaperrasJuego

Este módulo contiene la interfaz principal de usuario que permite acceder
a todos los juegos de casino disponibles: Poker, Blackjack, Ruleta y Tragaperras.
Gestiona la navegación entre juegos y la configuración general de la aplicación.
"""

import importlib
import os
import sys
import time
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
PACKAGE_PARENT_DIR = ROOT_DIR.parent
if str(PACKAGE_PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PARENT_DIR))

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QKeySequence, QPixmap, QShortcut
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
)
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtWidgets import QVBoxLayout as QVBox
from PyQt6.QtWidgets import (
    QWidget,
)

from RuleTragaperrasJuego.achievements import AchievementManager
from RuleTragaperrasJuego.config import config_manager, get_text
from RuleTragaperrasJuego.config_dialog import ConfigDialog
from RuleTragaperrasJuego.missions import MissionManager
from RuleTragaperrasJuego.performance_debug import PerformanceDebugManager
from RuleTragaperrasJuego.sound_manager import MusicContext, get_sound_manager


class MainUI(QMainWindow):
    UI_LATENCY_THRESHOLDS_MS: dict[str, float] = PerformanceDebugManager.DEFAULT_THRESHOLDS_MS

    def __init__(self, startup_started_at=None, bootstrap_metrics=None):
        super().__init__()

        # Load config if available
        self.config = config_manager

        # Include logged-in username in the window title
        username = self.config.get_logged_username()
        title = get_text("casino_title")
        if username:
            title = f"{title}  –  {username}"

        self._poker_window = None
        self._slots_window = None
        self._blackjack_window = None
        self._roulette_window = None
        self._startup_started_at = startup_started_at
        self._bootstrap_metrics = bootstrap_metrics if isinstance(bootstrap_metrics, dict) else {}
        self._ui_perf_metrics: dict[str, list[float]] = {}
        self._perf_debug_enabled = self._is_debug_mode()
        self.perf_debug = PerformanceDebugManager(
            enabled=self._perf_debug_enabled,
            base_dir=Path(__file__).resolve().parent,
            thresholds=self.UI_LATENCY_THRESHOLDS_MS,
        )
        self.sound_manager = get_sound_manager(self.config)

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

        self._start_menu_music()

        # Check for daily refill
        self.check_daily_refill()

        if isinstance(self._startup_started_at, (int, float)):
            self._record_ui_metric("ui.main.startup_ms", self._startup_started_at)

        self._record_bootstrap_metrics(self._bootstrap_metrics)

    def _is_debug_mode(self) -> bool:
        config_debug = bool(self.config.get("interface", "debug_mode", False))
        env_debug = os.getenv("CASINO_DEBUG_PERF", "0") == "1"
        return config_debug or env_debug

    def _start_menu_music(self) -> None:
        manager = self.sound_manager
        if manager is None:
            return
        try:
            manager.play_music_for_context(MusicContext.MENU)
        except Exception:
            pass

    def _start_game_music(self, metric_suffix: str) -> None:
        manager = self.sound_manager
        if manager is None:
            return
        context_by_game = {
            "poker": MusicContext.POKER,
            "blackjack": MusicContext.BLACKJACK,
            "roulette": MusicContext.ROULETTE,
            "slots": MusicContext.SLOTS,
        }
        context = context_by_game.get(metric_suffix)
        if context is None:
            return
        try:
            manager.play_music_for_context(context)
        except Exception:
            pass

    def _play_sound(self, method_name: str, *args, **kwargs) -> None:
        manager = self.sound_manager
        if manager is None:
            return
        callback = getattr(manager, method_name, None)
        if callable(callback):
            callback(*args, **kwargs)

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
        title_label = QLabel(get_text("casino_title"))
        title_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet(
            """
            color: #FFD700;
            margin: 20px;
        """
        )
        main_layout.addWidget(title_label)

        # Balance and mode display
        self.status_frame = QFrame()
        self.status_frame.setStyleSheet(
            """
            QFrame {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid rgba(255, 215, 0, 0.5);
                border-radius: 10px;
                padding: 10px;
            }
        """
        )
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
        games_frame.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(17, 24, 39, 0.9),
                           stop:1 rgba(31, 41, 55, 0.9));
                border: 2px solid rgba(75, 85, 99, 0.6);
                border-radius: 15px;
                padding: 20px;
            }
        """
        )
        games_layout = QGridLayout(games_frame)
        games_layout.setSpacing(20)

        # Game buttons
        self.create_game_buttons(games_layout)

        main_layout.addWidget(games_frame)
        main_layout.addStretch()

        # Set background
        self.setStyleSheet(
            """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(21, 128, 61, 0.8),
                           stop:1 rgba(22, 101, 52, 0.8));
            }
        """
        )

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
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(
            self.show_config_dialog
        )

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.isFullScreen():
            self.showNormal()
            self.config.set("display", "fullscreen", False)
        else:
            self.showFullScreen()
            self.config.set("display", "fullscreen", True)
        self.config.save_config()

    def _logout(self) -> None:
        """Log out the current user and close the application."""
        reply = QMessageBox.question(
            self,
            "Cerrar sesión",
            "¿Deseas cerrar sesión y salir del casino?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.config.logout()
            QApplication.instance().quit()  # type: ignore[union-attr]

    def check_daily_refill(self):
        """Check and apply daily refill if applicable"""
        if self.config.check_daily_refill():
            balance = self.config.get_player_balance()
            message = get_text("daily_refill_message").format(balance=balance)
            QMessageBox.information(self, get_text("daily_refill_title"), message)

    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        if menubar is None:
            return

        # Game menu
        game_menu = menubar.addMenu(get_text("game_menu"))
        if isinstance(game_menu, QMenu):
            # Practice mode toggle
            self.practice_mode_action = game_menu.addAction(get_text("practice_mode"))
            if self.practice_mode_action is not None:
                self.practice_mode_action.setCheckable(True)
                self.practice_mode_action.setChecked(self.config.is_practice_mode())
                self.practice_mode_action.triggered.connect(self.toggle_practice_mode)

            game_menu.addSeparator()

            # Statistics
            stats_action = game_menu.addAction(get_text("view_statistics"))
            if stats_action is not None:
                stats_action.triggered.connect(self.show_statistics)

            if self._perf_debug_enabled:
                perf_action = game_menu.addAction("Rendimiento UI")
                if perf_action is not None:
                    perf_action.triggered.connect(self.show_performance_baseline)

            # Achievements
            achievements_action = game_menu.addAction(get_text("view_achievements"))
            if achievements_action is not None:
                achievements_action.triggered.connect(self.show_achievements)

            # Missions
            missions_action = game_menu.addAction(get_text("view_missions"))
            if missions_action is not None:
                missions_action.triggered.connect(self.show_missions)

        # Settings menu
        settings_menu = menubar.addMenu(get_text("settings"))
        if isinstance(settings_menu, QMenu):
            config_action = settings_menu.addAction("Configuración...")
            if config_action is not None:
                config_action.triggered.connect(self.show_config_dialog)

        # Account menu (only visible when logged in)
        if self.config.is_logged_in():
            account_menu = menubar.addMenu(
                f"👤 {self.config.get_logged_username()}"
            )
            if isinstance(account_menu, QMenu):
                logout_action = account_menu.addAction("Cerrar sesión")
                if logout_action is not None:
                    logout_action.triggered.connect(self._logout)

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
        button.setStyleSheet(
            """
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
        """
        )
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
        self.setWindowTitle(get_text("casino_title"))

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
        shortcuts_help = get_text("shortcuts_help")
        QMessageBox.about(
            self,
            "Acerca de",
            f"Casino de tu mama\n\n"
            f"Un juego de casino con múltiples juegos:\n"
            f"• Póker Texas Hold'em\n"
            f"• Blackjack\n"
            f"• Ruleta\n"
            f"• Tragaperras\n\n"
            f"Versión 2.0\n\n"
            f"{get_text('keyboard_shortcuts')}:\n"
            f"{shortcuts_help}",
        )

    def _launch_game(
        self,
        module_path: str,
        open_function_name: str,
        window_attr: str,
        metric_suffix: str,
        on_closed_handler,
        import_error_message: str,
        generic_error_message: str,
        *,
        open_kwargs: dict | None = None,
        raise_import_error: bool = False,
    ) -> None:
        """Lanza un juego mediante import dinámico y maneja estado/errores comunes."""
        started_at = time.perf_counter()
        try:
            import_started_at = time.perf_counter()
            game_module = importlib.import_module(module_path)
            open_window = getattr(game_module, open_function_name)
            self._record_ui_metric(f"ui.main.import_{metric_suffix}_ms", import_started_at)

            transition_started_at = time.perf_counter()
            self.hide()
            kwargs = open_kwargs or {}
            open_started_at = time.perf_counter()
            window, owns_app, app = open_window(parent=self, **kwargs)
            self._record_ui_metric(f"ui.main.open_{metric_suffix}_ms", open_started_at)
            setattr(self, window_attr, window)
            window.destroyed.connect(on_closed_handler)
            QApplication.processEvents()
            self._start_game_music(metric_suffix)
            self._record_ui_metric(
                f"ui.main.transition_to_{metric_suffix}_ms", transition_started_at
            )
            self._record_ui_metric(f"ui.main.launch_{metric_suffix}_ms", started_at)

            if owns_app:
                app.exec()

        except ImportError as e:
            self.show()
            if raise_import_error:
                raise ImportError(e)
            QMessageBox.warning(self, "Error", import_error_message)
        except Exception as e:
            self.show()
            print(e)
            QMessageBox.critical(self, "Error", f"{generic_error_message}: {str(e)}")

    def _restore_main_window(self, window_attr: str, metric_suffix: str) -> None:
        """Restaura la ventana principal al cerrar un sub-juego."""
        started_at = time.perf_counter()
        transition_started_at = time.perf_counter()
        setattr(self, window_attr, None)
        self.show()
        QApplication.processEvents()
        self._start_menu_music()
        self._record_ui_metric(
            f"ui.main.restore_transition_{metric_suffix}_ms", transition_started_at
        )
        self._record_ui_metric(f"ui.main.restore_{metric_suffix}_ms", started_at)

    def launch_poker(self):
        """Launch poker game"""
        self._launch_game(
            module_path="Poker.poker_main",
            open_function_name="open_poker_window",
            window_attr="_poker_window",
            metric_suffix="poker",
            on_closed_handler=self.on_poker_window_closed,
            import_error_message="El juego de póker no está disponible.",
            generic_error_message="Error al lanzar póker",
            open_kwargs={"num_players": 6},
            raise_import_error=True,
        )

    def on_poker_window_closed(self, _obj=None):
        """Restore main window when the poker window is closed."""
        self._restore_main_window("_poker_window", "poker")

    def launch_blackjack(self):
        """Launch blackjack game"""
        self._launch_game(
            module_path="Blackjack.blackjack",
            open_function_name="open_blackjack_window",
            window_attr="_blackjack_window",
            metric_suffix="blackjack",
            on_closed_handler=self.on_blackjack_window_closed,
            import_error_message="El juego de Blackjack no está disponible.",
            generic_error_message="Error al lanzar Blackjack",
        )

    def on_blackjack_window_closed(self, _obj=None):
        """Restore main window when the blackjack window is closed."""
        self._restore_main_window("_blackjack_window", "blackjack")

    def launch_roulette(self):
        """Launch roulette game"""
        self._launch_game(
            module_path="Ruleta.ruleta_main",
            open_function_name="open_roulette_window",
            window_attr="_roulette_window",
            metric_suffix="roulette",
            on_closed_handler=self.on_roulette_window_closed,
            import_error_message="El juego de ruleta no está disponible.",
            generic_error_message="Error al lanzar ruleta",
        )

    def on_roulette_window_closed(self, _obj=None):
        """Restore main window when the roulette window is closed."""
        self._restore_main_window("_roulette_window", "roulette")

    def launch_slots(self):
        """Launch slot machine game"""
        self._launch_game(
            module_path="Tragaperras.tragaperras_main",
            open_function_name="open_slot_window",
            window_attr="_slots_window",
            metric_suffix="slots",
            on_closed_handler=self.on_slots_window_closed,
            import_error_message="El juego de tragaperras no está disponible.",
            generic_error_message="Error al lanzar tragaperras",
        )

    def on_slots_window_closed(self, _obj=None):
        """Restore main window when slot machine window is closed."""
        self._restore_main_window("_slots_window", "slots")

    def update_balance_display(self):
        """Update the balance display"""
        balance = self.config.get_effective_balance()
        balance_type = (
            get_text("practice_balance")
            if self.config.is_practice_mode()
            else get_text("real_balance")
        )
        self.balance_label.setText(f"{balance_type}: {balance} créditos")

    def update_mode_display(self):
        """Update the practice mode indicator"""
        if self.config.is_practice_mode():
            self.mode_label.setText(get_text("practice_mode_on"))
            self.mode_label.setStyleSheet("color: #FFA500; font-weight: bold;")
        else:
            self.mode_label.setText(get_text("practice_mode_off"))
            self.mode_label.setStyleSheet("color: #90EE90;")

    def toggle_practice_mode(self):
        """Toggle practice mode"""
        current = self.config.is_practice_mode()
        self.config.set_practice_mode(not current)
        self.update_balance_display()
        self.update_mode_display()

        mode_str = (
            get_text("practice_mode_on")
            if not current
            else get_text("practice_mode_off")
        )
        QMessageBox.information(self, get_text("practice_mode"), mode_str)

    def on_achievement_unlocked(self, achievement):
        """Handle achievement unlock notification"""
        from .config import config_manager

        lang = config_manager.get_language().value

        message = f"{achievement.get_name(lang)}\n\n{achievement.get_description(lang)}\n\n{get_text('mission_reward').format(reward=achievement.reward)}"
        self._play_sound("play_achievement_unlock")

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(get_text("achievement_unlocked"))
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.exec()

        self.update_balance_display()

    def show_statistics(self):
        """Show statistics dialog"""
        from PyQt6.QtWidgets import QDialog, QTextBrowser

        dialog = QDialog(self)
        dialog.setWindowTitle(get_text("statistics"))
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
        reset_btn = QPushButton(get_text("reset_stats"))
        reset_btn.clicked.connect(lambda: self.reset_statistics(dialog))
        layout.addWidget(reset_btn)

        # Close button
        close_btn = QPushButton(get_text("cancel"))
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()

    def _record_ui_metric(self, metric_name: str, started_at: float) -> None:
        if hasattr(self, "perf_debug"):
            self.perf_debug.record_ui_metric(metric_name, started_at)

    def _record_ui_metric_value(self, metric_name: str, elapsed_ms: float) -> None:
        if hasattr(self, "perf_debug"):
            self.perf_debug.record_ui_metric_value(metric_name, elapsed_ms)
            return

        if not isinstance(elapsed_ms, (int, float)):
            return
        elapsed = float(elapsed_ms)
        if elapsed < 0:
            return
        if metric_name not in self._ui_perf_metrics:
            self._ui_perf_metrics[metric_name] = []
        self._ui_perf_metrics[metric_name].append(elapsed)
        if len(self._ui_perf_metrics[metric_name]) > 100:
            self._ui_perf_metrics[metric_name] = self._ui_perf_metrics[metric_name][-100:]

    def _record_bootstrap_metrics(self, bootstrap_metrics) -> None:
        if hasattr(self, "perf_debug"):
            self.perf_debug.record_bootstrap_metrics(bootstrap_metrics)
            return

        if not isinstance(bootstrap_metrics, dict):
            return
        for metric_name, elapsed_ms in bootstrap_metrics.items():
            if not isinstance(metric_name, str) or not metric_name:
                continue
            self._record_ui_metric_value(metric_name, elapsed_ms)

    def _build_metric_summary(self, metric_name: str, samples: list[float]) -> dict:
        if hasattr(self, "perf_debug"):
            return self.perf_debug.build_metric_summary(metric_name, samples)
        return PerformanceDebugManager(True, Path(__file__).resolve().parent, self.UI_LATENCY_THRESHOLDS_MS).build_metric_summary(metric_name, samples)

    def _export_ui_metrics_baseline(self) -> None:
        if hasattr(self, "perf_debug"):
            self.perf_debug.export_ui_metrics_baseline_async("main")

    @staticmethod
    def _compute_metric_alert_level(status, avg_ms, threshold_ms, delta_avg_ms):
        return PerformanceDebugManager._compute_metric_alert_level(status, avg_ms, threshold_ms, delta_avg_ms)

    @staticmethod
    def _delta_visual(delta_avg_ms):
        return PerformanceDebugManager._delta_visual(delta_avg_ms)

    @classmethod
    def _build_performance_csv_rows(cls, snapshots):
        return PerformanceDebugManager._build_performance_csv_rows(snapshots)

    @staticmethod
    def _parse_snapshot_timestamp(value):
        return PerformanceDebugManager._parse_snapshot_timestamp(value)

    @staticmethod
    def _format_iso_timestamp(value):
        return PerformanceDebugManager._format_iso_timestamp(value)

    @classmethod
    def _get_time_preset_bounds(cls, preset_name, now=None):
        return PerformanceDebugManager._get_time_preset_bounds(preset_name, now=now)

    @classmethod
    def _filter_performance_snapshots(
        cls,
        snapshots,
        source_filter="Todas",
        metric_filter="Todas",
        start_ts=None,
        end_ts=None,
    ):
        return PerformanceDebugManager._filter_performance_snapshots(
            snapshots,
            source_filter=source_filter,
            metric_filter=metric_filter,
            start_ts=start_ts,
            end_ts=end_ts,
        )

    @classmethod
    def _build_metric_trend_rows(cls, snapshots):
        return PerformanceDebugManager._build_metric_trend_rows(snapshots)

    @classmethod
    def _build_source_trend_rows(cls, snapshots):
        return PerformanceDebugManager._build_source_trend_rows(snapshots)

    @staticmethod
    def _classify_main_metric_phase(metric_name):
        return PerformanceDebugManager._classify_main_metric_phase(metric_name)

    @staticmethod
    def _compute_phase_alert_level(threshold_breaches, threshold_checks, delta_avg_ms):
        return PerformanceDebugManager._compute_phase_alert_level(threshold_breaches, threshold_checks, delta_avg_ms)

    @classmethod
    def _build_phase_trend_rows(cls, snapshots):
        return PerformanceDebugManager._build_phase_trend_rows(snapshots)

    @staticmethod
    def _parse_delta_value(value):
        return PerformanceDebugManager._parse_delta_value(value)

    @staticmethod
    def _parse_breach_ratio(value):
        return PerformanceDebugManager._parse_breach_ratio(value)

    @classmethod
    def _sort_performance_rows(cls, rows, sort_mode, row_type):
        return PerformanceDebugManager._sort_performance_rows(rows, sort_mode, row_type)

    @staticmethod
    def _sortable_number(value):
        return PerformanceDebugManager._sortable_number(value)

    @classmethod
    def _export_performance_csv(cls, snapshots, csv_path: Path):
        return PerformanceDebugManager._export_performance_csv(snapshots, csv_path)

    def show_performance_baseline(self):
        if hasattr(self, "perf_debug"):
            self.perf_debug.show_performance_baseline(self, get_text)

    def reset_statistics(self, parent_dialog):
        """Reset all statistics"""
        reply = QMessageBox.question(
            self,
            get_text("reset_stats"),
            get_text("reset_stats_confirm"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.config.reset_statistics()
            QMessageBox.information(
                self, get_text("statistics"), "Estadísticas reiniciadas"
            )
            parent_dialog.close()
            self.show_statistics()

    def show_achievements(self):
        """Show achievements dialog"""

        lang = config_manager.get_language().value

        dialog = QDialog(self)
        dialog.setWindowTitle(get_text("achievements"))
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
            unlocked_label = QLabel(
                f"<h3>{get_text('unlocked')} ({len(unlocked)})</h3>"
            )
            scroll_layout.addWidget(unlocked_label)

            for ach in unlocked:
                ach_frame = QFrame()
                ach_frame.setStyleSheet(
                    """
                    QFrame {
                        background: rgba(0, 255, 0, 0.1);
                        border: 1px solid rgba(0, 255, 0, 0.3);
                        border-radius: 5px;
                        padding: 10px;
                        margin: 5px;
                    }
                """
                )
                ach_layout = QVBox(ach_frame)

                name_label = QLabel(f"<b>{ach.get_name(lang)}</b>")
                ach_layout.addWidget(name_label)

                desc_label = QLabel(ach.get_description(lang))
                desc_label.setWordWrap(True)
                ach_layout.addWidget(desc_label)

                reward_label = QLabel(
                    f"🏆 {get_text('mission_reward').format(reward=ach.reward)}"
                )
                ach_layout.addWidget(reward_label)

                scroll_layout.addWidget(ach_frame)

        # Show locked achievements
        locked = self.achievement_manager.get_locked_achievements()
        if locked:
            locked_label = QLabel(f"<h3>{get_text('locked')} ({len(locked)})</h3>")
            scroll_layout.addWidget(locked_label)

            for ach in locked:
                ach_frame = QFrame()
                ach_frame.setStyleSheet(
                    """
                    QFrame {
                        background: rgba(128, 128, 128, 0.1);
                        border: 1px solid rgba(128, 128, 128, 0.3);
                        border-radius: 5px;
                        padding: 10px;
                        margin: 5px;
                    }
                """
                )
                ach_layout = QVBox(ach_frame)

                name_label = QLabel(f"<b>{ach.get_name(lang)}</b>")
                ach_layout.addWidget(name_label)

                desc_label = QLabel(ach.get_description(lang))
                desc_label.setWordWrap(True)
                ach_layout.addWidget(desc_label)

                # Progress bar
                progress = self.achievement_manager.get_achievement_progress_percent(
                    ach.id
                )
                progress_label = QLabel(f"{get_text('progress')}: {int(progress)}%")
                ach_layout.addWidget(progress_label)

                scroll_layout.addWidget(ach_frame)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

        # Close button
        close_btn = QPushButton(get_text("cancel"))
        close_btn.clicked.connect(dialog.close)
        main_layout.addWidget(close_btn)

        dialog.exec()

    def show_missions(self):
        """Show daily missions dialog"""
        lang = config_manager.get_language().value

        dialog = QDialog(self)
        dialog.setWindowTitle(get_text("missions"))
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
                mission_frame.setStyleSheet(
                    """
                    QFrame {
                        background: rgba(0, 255, 0, 0.2);
                        border: 2px solid rgba(0, 255, 0, 0.5);
                        border-radius: 5px;
                        padding: 10px;
                        margin: 5px;
                    }
                """
                )
            else:
                mission_frame.setStyleSheet(
                    """
                    QFrame {
                        background: rgba(255, 255, 255, 0.1);
                        border: 1px solid rgba(255, 255, 255, 0.3);
                        border-radius: 5px;
                        padding: 10px;
                        margin: 5px;
                    }
                """
                )

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
                progress_percent = self.mission_manager.get_mission_progress_percent(
                    mission
                )
                progress_bar.setValue(int(progress_percent))

                current_progress = self.mission_manager.get_mission_progress(mission)
                progress_bar.setFormat(f"{current_progress}/{mission.target}")
                mission_layout.addWidget(progress_bar)

            # Reward
            reward_label = QLabel(
                f"🎁 {get_text('mission_reward').format(reward=mission.reward)}"
            )
            mission_layout.addWidget(reward_label)

            layout.addWidget(mission_frame)

        layout.addStretch()

        # Close button
        close_btn = QPushButton(get_text("cancel"))
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        dialog.exec()

    def closeEvent(self, a0) -> None:
        manager = self.sound_manager
        if manager is not None:
            try:
                manager.stop_background_music()
            except Exception:
                pass
        self._export_ui_metrics_baseline()
        a0.accept()


if __name__ == "__main__":
    startup_started_at = time.perf_counter()
    bootstrap_metrics: dict[str, float] = {}

    def _mark_bootstrap_metric(metric_name: str, started_at: float) -> None:
        bootstrap_metrics[metric_name] = round(
            (time.perf_counter() - started_at) * 1000.0, 3
        )

    app = QApplication(sys.argv)

    # ── Initialise PostgreSQL (non-blocking; falls back to offline mode) ──
    auth_database_import_started_at = time.perf_counter()
    from RuleTragaperrasJuego.auth.database import init_db, create_tables
    _mark_bootstrap_metric(
        "ui.main.bootstrap.import_auth_database_ms", auth_database_import_started_at
    )

    db_init_started_at = time.perf_counter()
    if init_db():
        create_tables()  # idempotent: create tables if they don't exist yet
    _mark_bootstrap_metric("ui.main.bootstrap.db_init_ms", db_init_started_at)

    # ── Show login dialog ─────────────────────────────────────────────────
    login_import_started_at = time.perf_counter()
    from RuleTragaperrasJuego.auth.login_dialog import LoginDialog
    from PyQt6.QtWidgets import QDialog
    _mark_bootstrap_metric(
        "ui.main.bootstrap.import_login_dialog_ms", login_import_started_at
    )

    login_dialog = LoginDialog()
    if login_dialog.exec() != QDialog.DialogCode.Accepted:
        sys.exit(0)  # user closed the dialog without choosing

    # Apply per-user PostgreSQL config when logged in
    if login_dialog.user_data:
        user_load_started_at = time.perf_counter()
        config_manager.load_as_user(
            login_dialog.user_data["id"],
            login_dialog.user_data["username"],
        )
        _mark_bootstrap_metric(
            "ui.main.bootstrap.load_user_config_ms", user_load_started_at
        )

    # ── Launch main UI ────────────────────────────────────────────────────
    window_init_started_at = time.perf_counter()
    window = MainUI(
        startup_started_at=startup_started_at,
        bootstrap_metrics=bootstrap_metrics,
    )
    _mark_bootstrap_metric("ui.main.bootstrap.window_init_ms", window_init_started_at)
    window._record_bootstrap_metrics(
        {
            "ui.main.bootstrap.window_init_ms": bootstrap_metrics[
                "ui.main.bootstrap.window_init_ms"
            ]
        }
    )
    window.show()
    sys.exit(app.exec())
