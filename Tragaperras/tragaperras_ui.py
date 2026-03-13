"""Componentes de interfaz PyQt6 para la máquina tragaperras.

La interfaz sigue la filosofía del módulo de póker, separando la lógica de la
presentación y proporcionando animaciones suaves para los rodillos.
"""

from __future__ import annotations

import sys
import time
import json
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QColor, QFont, QResizeEvent
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QFrame,
    QGridLayout,
    QSizePolicy,
)


ROOT_DIR = Path(__file__).resolve().parents[1]
PACKAGE_PARENT_DIR = ROOT_DIR.parent
for path_entry in (PACKAGE_PARENT_DIR, ROOT_DIR):
    str_path = str(path_entry)
    if str_path not in sys.path:
        sys.path.insert(0, str_path)

from RuleTragaperrasJuego.Tragaperras.tragaperras_table import (
    SlotMachineTable,
    SlotMachineTableFactory,
)
from RuleTragaperrasJuego.Tragaperras.tragaperras_logic import PAYLINES, SpinResult
from RuleTragaperrasJuego.config import config_manager, get_text
from RuleTragaperrasJuego.game_events import GameRoundEvent, get_game_event_service
from RuleTragaperrasJuego.sound_manager import get_sound_manager


# ---------------------------------------------------------------------------
# Utilidades de estilo


BASE_LABEL_STYLE = """
    QLabel {
        background-color: rgba(17, 24, 39, 0.85);
        color: #F9FAFB;
        border-radius: 14px;
        border: 2px solid rgba(59, 130, 246, 0.3);
        font-weight: bold;
    }
"""

HIGHLIGHT_LABEL_STYLE = """
    QLabel {
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:1,
            stop:0 rgba(59, 130, 246, 0.9),
            stop:1 rgba(14, 116, 144, 0.9));
        color: #FDF2F8;
        border-radius: 16px;
        border: 3px solid rgba(253, 224, 71, 0.9);
        font-weight: 800;
        box-shadow: 0 0 12px rgba(253, 224, 71, 0.5);
    }
"""


def clamp(value: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(value, maximum))


# ---------------------------------------------------------------------------
# Widgets auxiliares


class ReelColumn(QFrame):
    """Widget que representa una columna del carrete con animación vertical."""

    def __init__(self, rows: int, get_scaled_size, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.rows = rows
        self._get_scaled_size = get_scaled_size
        self.setObjectName("ReelColumn")
        self.setStyleSheet("""
            QFrame#ReelColumn {
                background-color: rgba(15, 23, 42, 0.85);
                border-radius: 18px;
                border: 2px solid rgba(148, 163, 184, 0.4);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 14, 14, 14)
        layout.setSpacing(self._get_scaled_size(12))

        self.labels: List[QLabel] = []
        for _ in range(rows):
            label = QLabel("❔", self)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setMinimumSize(self._get_scaled_size(96), self._get_scaled_size(96))
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            label.setStyleSheet(BASE_LABEL_STYLE)
            label.setFont(QFont("Arial", self._get_scaled_size(30), QFont.Weight.Bold))
            layout.addWidget(label)
            self.labels.append(label)

        self.highlighted: Dict[int, bool] = {}

    def _set_label_text_if_changed(self, label: QLabel, text: str) -> None:
        if label.text() != text:
            label.setText(text)

    def _set_label_style_if_changed(self, label: QLabel, style: str) -> None:
        if label.property("_last_style") != style:
            label.setStyleSheet(style)
            label.setProperty("_last_style", style)

    def set_symbols(self, symbols: Sequence[str]) -> None:
        for label, symbol in zip(self.labels, symbols):
            self._set_label_text_if_changed(label, symbol)

    def set_highlights(self, rows: Iterable[int]) -> None:
        self.highlighted = {row: True for row in rows}
        for index, label in enumerate(self.labels):
            if self.highlighted.get(index):
                self._set_label_style_if_changed(label, HIGHLIGHT_LABEL_STYLE)
            else:
                self._set_label_style_if_changed(label, BASE_LABEL_STYLE)

    def clear_highlights(self) -> None:
        self.highlighted.clear()
        for label in self.labels:
            self._set_label_style_if_changed(label, BASE_LABEL_STYLE)


# ---------------------------------------------------------------------------
# Ventana principal


class SlotMachineWindow(QMainWindow):
    """Ventana principal del juego de tragaperras."""

    ROWS = 3
    COLUMNS = 3
    UI_LATENCY_THRESHOLDS_MS: Dict[str, float] = {
        "ui.slots.render_result_ms": 25.0,
        "ui.slots.spin_end_to_end_ms": 2400.0,
    }

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.config = config_manager
        self.sound_manager = get_sound_manager(self.config)
        self.table: SlotMachineTable = SlotMachineTableFactory.create_table(
            balance=1000,
            bet_per_line=5,
        )
        self.table.set_active_lines(self.table.get_default_active_lines(3))

        self.base_width = 1280
        self.base_height = 800
        self.current_scale = 1.0

        self.pending_result: Optional[SpinResult] = None
        self.is_animating: bool = False
        self._spin_started_at: Optional[float] = None
        self._ui_perf_metrics: Dict[str, List[float]] = {}

        self.reel_columns: List[ReelColumn] = []
        self.reel_timers: List[QTimer] = []
        self.reveal_sequence: List[int] = []

        self.autoplay_timer = QTimer(self)
        self.autoplay_timer.setSingleShot(True)
        self.autoplay_timer.timeout.connect(self._handle_autoplay_timeout)

        self._register_callbacks()

        self._init_window()
        self._init_ui()
        self._update_info_labels()

    def _play_sound(self, method_name: str, *args, **kwargs) -> None:
        manager = self.sound_manager
        if manager is None:
            return
        callback = getattr(manager, method_name, None)
        if callable(callback):
            callback(*args, **kwargs)

    # ------------------------------------------------------------------
    # Configuración inicial

    def _init_window(self) -> None:
        self.setWindowTitle(f"{get_text('slot_machine')} - {get_text('casino_title')}")
        self.resize(1100, 760)
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 64, 175, 0.85),
                    stop:1 rgba(17, 24, 39, 0.95));
            }
            QLabel#InfoValue {
                color: #FACC15;
                font-weight: 700;
            }
            QLabel#InfoTitle {
                color: #CBD5F5;
                font-weight: 600;
                letter-spacing: 0.08em;
            }
            QListWidget {
                background-color: rgba(15, 23, 42, 0.85);
                border: 1px solid rgba(59, 130, 246, 0.25);
                border-radius: 12px;
                color: #E2E8F0;
            }
        """)

    def _register_callbacks(self) -> None:
        self.table.register_ui_callback("balance_changed", self._on_balance_changed)
        self.table.register_ui_callback("bet_changed", self._on_bet_changed)
        self.table.register_ui_callback("lines_changed", self._on_lines_changed)
        self.table.register_ui_callback("spin_started", self._on_spin_started)
        self.table.register_ui_callback("spin_completed", self._on_spin_completed)
        self.table.register_ui_callback("statistics_changed", self._on_statistics_changed)
        self.table.register_ui_callback("autoplay_changed", self._on_autoplay_changed)

    def _init_ui(self) -> None:
        central = QWidget(self)
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(28, 28, 28, 28)
        main_layout.setSpacing(self.get_scaled_size(16))

        self._create_menu_bar()

        info_frame = self._create_info_panel()
        main_layout.addWidget(info_frame)

        reels_frame = self._create_reels_panel()
        main_layout.addWidget(reels_frame)

        controls_frame = self._create_controls_panel()
        main_layout.addWidget(controls_frame)

        history_frame = self._create_history_panel()
        main_layout.addWidget(history_frame)

    # ------------------------------------------------------------------
    # Creación de secciones de UI

    def _create_menu_bar(self) -> None:
        menubar = self.menuBar()
        game_menu = menubar.addMenu(get_text('game_menu')) #type: ignore

        new_spin_action: QAction = game_menu.addAction(get_text('spin') + "!")
        new_spin_action.triggered.connect(self.start_spin)

        game_menu.addSeparator()

        exit_action: QAction = game_menu.addAction(get_text('exit'))
        exit_action.triggered.connect(self.close)

    def _create_info_panel(self) -> QFrame:
        frame = QFrame(self)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(self.get_scaled_size(24))

        self.balance_label = self._create_info_item(layout, get_text('balance'), "$0")
        self.bet_label = self._create_info_item(layout, get_text('bet'), "$0")
        self.total_bet_label = self._create_info_item(layout, get_text('total_bet'), "$0")
        self.last_win_label = self._create_info_item(layout, get_text('last_win'), "$0")
        self.stats_label = self._create_info_item(layout, get_text('statistics'), "-")

        return frame

    def _create_info_item(self, layout: QHBoxLayout, title: str, value: str) -> QLabel:
        container = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setObjectName("InfoTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        title_label.setFont(QFont("Montserrat", self.get_scaled_size(12), QFont.Weight.Bold))

        value_label = QLabel(value)
        value_label.setObjectName("InfoValue")
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        value_label.setFont(QFont("Montserrat", self.get_scaled_size(18), QFont.Weight.Bold))

        container.addWidget(title_label)
        container.addWidget(value_label)
        layout.addLayout(container)

        return value_label

    def _create_reels_panel(self) -> QFrame:
        frame = QFrame(self)
        frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 rgba(15, 23, 42, 0.85),
                    stop:1 rgba(30, 58, 138, 0.75));
                border-radius: 26px;
                border: 3px solid rgba(96, 165, 250, 0.35);
            }
        """)
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(40, 28, 40, 28)
        layout.setSpacing(self.get_scaled_size(24))

        self.symbol_labels: List[List[QLabel]] = []
        self.reel_columns = []
        self.reel_timers = []

        for column in range(self.COLUMNS):
            reel = ReelColumn(self.ROWS, self.get_scaled_size, self)
            self.reel_columns.append(reel)
            layout.addWidget(reel)

            column_labels: List[QLabel] = []
            for row in range(self.ROWS):
                column_labels.append(reel.labels[row])
            self.symbol_labels.append(column_labels)

            timer = QTimer(self)
            timer.timeout.connect(self._make_shuffle_handler(column))
            self.reel_timers.append(timer)

        self.message_label = QLabel(get_text('ready_to_spin'))
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("Montserrat", self.get_scaled_size(14), QFont.Weight.Medium))
        self.message_label.setStyleSheet("color: #E2E8F0;")
        layout.addWidget(self.message_label)

        return frame

    def _create_controls_panel(self) -> QFrame:
        frame = QFrame(self)
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 23, 42, 0.85);
                border-radius: 20px;
                border: 2px solid rgba(59, 130, 246, 0.25);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(59, 130, 246, 0.95),
                    stop:1 rgba(37, 99, 235, 0.95));
                border-radius: 14px;
                border: 2px solid rgba(191, 219, 254, 0.45);
                color: #F8FAFC;
                font-size: 17px;
                font-weight: bold;
                padding: 12px 28px;
            }
            QPushButton:disabled {
                background-color: rgba(59, 130, 246, 0.4);
                border-color: rgba(191, 219, 254, 0.3);
                color: rgba(226, 232, 240, 0.6);
            }
            QPushButton#AutoplayButton:checked {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(16, 185, 129, 0.95),
                    stop:1 rgba(5, 150, 105, 0.95));
            }
        """)

        layout = QGridLayout(frame)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setHorizontalSpacing(self.get_scaled_size(18))
        layout.setVerticalSpacing(self.get_scaled_size(12))

        self.spin_button = QPushButton(get_text('spin').upper(), frame)
        self.spin_button.clicked.connect(self.start_spin)
        layout.addWidget(self.spin_button, 0, 0, 2, 1)

        self.autoplay_button = QPushButton(get_text('auto_play').upper(), frame)
        self.autoplay_button.setCheckable(True)
        self.autoplay_button.setObjectName("AutoplayButton")
        self.autoplay_button.clicked.connect(self._on_autoplay_button_clicked)
        layout.addWidget(self.autoplay_button, 0, 1)

        self.bet_spinbox = QSpinBox(frame)
        self.bet_spinbox.setRange(1, 200)
        self.bet_spinbox.setValue(self.table.bet_per_line)
        self.bet_spinbox.valueChanged.connect(self._on_bet_spinbox_changed)
        layout.addWidget(self._wrap_labeled_widget(get_text('bet_per_line'), self.bet_spinbox), 0, 2)

        self.lines_spinbox = QSpinBox(frame)
        self.lines_spinbox.setRange(1, len(PAYLINES))
        self.lines_spinbox.setValue(len(self.table.get_active_lines()))
        self.lines_spinbox.valueChanged.connect(self._on_lines_spinbox_changed)
        layout.addWidget(self._wrap_labeled_widget(get_text('lines'), self.lines_spinbox), 0, 3)

        self.add_credits_button = QPushButton(get_text('add_credits'), frame)
        self.add_credits_button.clicked.connect(self._on_add_credits_clicked)
        layout.addWidget(self.add_credits_button, 1, 1)

        self.reset_stats_button = QPushButton(get_text('reset_statistics'), frame)
        self.reset_stats_button.clicked.connect(self._on_reset_statistics_clicked)
        layout.addWidget(self.reset_stats_button, 1, 3)

        return frame

    def _wrap_labeled_widget(self, label: str, widget: QWidget) -> QWidget:
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #E2E8F0; font-weight: 600;")
        lbl.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(lbl)
        layout.addWidget(widget)
        return container

    def _create_history_panel(self) -> QFrame:
        frame = QFrame(self)
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(15, 23, 42, 0.75);
                border-radius: 18px;
                border: 2px solid rgba(59, 130, 246, 0.2);
            }
        """)
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(10)

        title = QLabel(get_text('history'))
        title.setStyleSheet("color: #F8FAFC; font-size: 16px; font-weight: 700;")
        layout.addWidget(title)

        self.history_list = QListWidget(frame)
        layout.addWidget(self.history_list)

        return frame

    # ------------------------------------------------------------------
    # Gestión de eventos UI

    def start_spin(self) -> None:
        if self.is_animating or self.table.is_spinning():
            return

        try:
            self._play_sound("play_slot_spin")
            self._begin_animation()
            # Ejecuta la tirada (los callbacks actualizarán el estado)
            self.table.spin()
        except ValueError as exc:
            self._end_animation(force=True)
            QMessageBox.warning(self, get_text('not_enough_balance_title'), str(exc))
        except RuntimeError as exc:
            self._end_animation(force=True)
            QMessageBox.information(self, get_text('action_not_available'), str(exc))

    def _begin_animation(self) -> None:
        self.is_animating = True
        self.pending_result = None
        self.spin_button.setEnabled(False)
        self.bet_spinbox.setEnabled(False)
        self.lines_spinbox.setEnabled(False)
        self.add_credits_button.setEnabled(False)
        self.reset_stats_button.setEnabled(False)

        speed_multiplier = self.config.get_animation_speed()
        base_interval = clamp(int(70 * speed_multiplier), 30, 160)
        base_duration = clamp(int(900 * speed_multiplier), 400, 1800)

        self.reveal_sequence = []

        for column, timer in enumerate(self.reel_timers):
            timer.setInterval(base_interval)
            timer.start()
            QTimer.singleShot(base_duration + column * 180, self._make_stop_handler(column))

    def _end_animation(self, force: bool = False) -> None:
        for timer in self.reel_timers:
            timer.stop()

        self.is_animating = False
        self.spin_button.setEnabled(True)
        self.bet_spinbox.setEnabled(True)
        self.lines_spinbox.setEnabled(True)
        self.add_credits_button.setEnabled(True)
        self.reset_stats_button.setEnabled(True)

        if self.autoplay_button.isChecked() and not force:
            self._schedule_autoplay()

    def _make_shuffle_handler(self, column: int):
        def handler() -> None:
            for row in range(self.ROWS):
                symbol = self.table.sample_symbol()
                self._set_label_text_if_changed(self.symbol_labels[column][row], symbol)

        return handler

    def _make_stop_handler(self, column: int):
        def handler() -> None:
            if not self.is_animating:
                return
            self.reel_timers[column].stop()
            if self.pending_result:
                column_symbols = [self.pending_result.grid[row][column] for row in range(self.ROWS)]
                for row, symbol in enumerate(column_symbols):
                    self._set_label_text_if_changed(self.symbol_labels[column][row], symbol)
            self._reveal_if_ready()

        return handler

    def _reveal_if_ready(self) -> None:
        if not self.pending_result:
            return
        if any(timer.isActive() for timer in self.reel_timers):
            return
        self._display_spin_result(self.pending_result)
        self.pending_result = None
        self._end_animation()

    def _display_spin_result(self, result: SpinResult) -> None:
        render_started_at = time.perf_counter()
        self._clear_highlights()
        winning_positions: Dict[Tuple[int, int], bool] = {}
        for line_win in result.line_wins:
            for row, col in line_win.positions:
                winning_positions[(row, col)] = True

        for col in range(self.COLUMNS):
            highlight_rows = [row for row in range(self.ROWS) if winning_positions.get((row, col))]
            if highlight_rows:
                self.reel_columns[col].set_highlights(highlight_rows)
            else:
                self.reel_columns[col].clear_highlights()

        self._set_label_text_if_changed(self.last_win_label, f"{result.total_payout} ⚡")
        self._set_label_text_if_changed(self.total_bet_label, f"{result.total_bet}")
        if result.net_win >= 0:
            self._set_label_text_if_changed(
                self.message_label,
                get_text('win_message').format(total=result.total_payout),
            )
        else:
            self._set_label_text_if_changed(self.message_label, get_text('loss_message'))

        self._append_history(result)
        self._record_ui_metric("ui.slots.render_result_ms", render_started_at)

        if self._spin_started_at is not None:
            self._record_ui_metric("ui.slots.spin_end_to_end_ms", self._spin_started_at)
            self._spin_started_at = None

    def _clear_highlights(self) -> None:
        for reel in self.reel_columns:
            reel.clear_highlights()

    # ------------------------------------------------------------------
    # Callbacks desde la mesa

    def _on_balance_changed(self, balance: int) -> None:
        self._set_label_text_if_changed(self.balance_label, f"{balance}")

    def _on_bet_changed(self, bet_per_line: int) -> None:
        if self.bet_spinbox.value() != bet_per_line:
            self.bet_spinbox.blockSignals(True)
            self.bet_spinbox.setValue(bet_per_line)
            self.bet_spinbox.blockSignals(False)
        self._set_label_text_if_changed(self.bet_label, f"{bet_per_line}")
        self._update_total_bet()

    def _on_lines_changed(self, lines: Sequence[int]) -> None:
        num_lines = len(tuple(lines))
        if self.lines_spinbox.value() != num_lines:
            self.lines_spinbox.blockSignals(True)
            self.lines_spinbox.setValue(num_lines)
            self.lines_spinbox.blockSignals(False)
        self._update_total_bet()

    def _on_spin_started(self, total_bet: int, **_kwargs) -> None:
        self._spin_started_at = time.perf_counter()
        self._set_label_text_if_changed(self.total_bet_label, str(total_bet))
        self._set_label_text_if_changed(self.message_label, get_text('spinning_message'))

    def _on_spin_completed(self, result: SpinResult) -> None:
        self.pending_result = result
        self._update_info_labels(result)
        if result.total_payout >= result.total_bet * 10 and result.total_payout > 0:
            self._play_sound("play_jackpot")
        elif result.net_win > 0:
            self._play_sound("play_win", big_win=result.net_win >= max(200, result.total_bet * 5))
        elif result.net_win < 0:
            self._play_sound("play_lose")
        else:
            self._play_sound("play_notification")
        try:
            get_game_event_service().record_round(
                GameRoundEvent(
                    game_type="slots",
                    rounds_played=1,
                    wagered=int(result.total_bet),
                    net_win=int(result.net_win),
                )
            )
        except Exception:
            pass
        self._reveal_if_ready()

    def _on_statistics_changed(self, statistics) -> None:
        rtp_percent = statistics.rtp * 100 if statistics.total_bet else 0.0
        self._set_label_text_if_changed(
            self.stats_label,
            f"{statistics.total_spins} | RTP {rtp_percent:.1f}% | Δ {statistics.net_profit}",
        )

    def _on_autoplay_changed(self, enabled: bool) -> None:
        if self.autoplay_button.isChecked() != enabled:
            self.autoplay_button.blockSignals(True)
            self.autoplay_button.setChecked(enabled)
            self.autoplay_button.blockSignals(False)
        if enabled and not self.is_animating:
            self._schedule_autoplay()
        else:
            self.autoplay_timer.stop()

    # ------------------------------------------------------------------
    # Slots de widgets

    def _on_bet_spinbox_changed(self, value: int) -> None:
        try:
            self.table.set_bet_per_line(value)
        except ValueError as exc:
            QMessageBox.warning(self, get_text('invalid_bet_title'), str(exc))

    def _on_lines_spinbox_changed(self, value: int) -> None:
        lines = self.table.get_default_active_lines(value)
        try:
            self.table.set_active_lines(lines)
        except ValueError as exc:
            QMessageBox.warning(self, get_text('invalid_lines_title'), str(exc))

    def _on_add_credits_clicked(self) -> None:
        self.table.add_credits(200)
        self._set_label_text_if_changed(self.message_label, get_text('credits_added'))

    def _on_reset_statistics_clicked(self) -> None:
        self.table.reset_statistics()
        self._set_label_text_if_changed(self.message_label, get_text('statistics_reset'))

    def _on_autoplay_button_clicked(self) -> None:
        enabled = self.autoplay_button.isChecked()
        self.table.enable_autoplay(enabled)
        if enabled and not self.is_animating:
            self._schedule_autoplay(initial_delay=True)

    # ------------------------------------------------------------------
    # Autoplay

    def _schedule_autoplay(self, initial_delay: bool = False) -> None:
        if not self.table.autoplay_enabled:
            return
        delay = self.table.autoplay_interval_ms
        if initial_delay:
            delay = max(400, int(delay * 0.6))
        self.autoplay_timer.start(delay)

    def _handle_autoplay_timeout(self) -> None:
        if not self.is_animating and self.table.autoplay_enabled:
            self.start_spin()

    # ------------------------------------------------------------------
    # Utilidades

    def _update_info_labels(self, result: Optional[SpinResult] = None) -> None:
        self._set_label_text_if_changed(self.balance_label, f"{self.table.balance}")
        self._set_label_text_if_changed(self.bet_label, f"{self.table.bet_per_line}")
        self._update_total_bet()
        if result is not None:
            self._set_label_text_if_changed(self.last_win_label, f"{result.total_payout} ⚡")

    def _update_total_bet(self) -> None:
        total_bet = self.table.bet_per_line * len(self.table.get_active_lines())
        self._set_label_text_if_changed(self.total_bet_label, f"{total_bet}")

    def _set_label_text_if_changed(self, label: QLabel, text: str) -> None:
        if label.text() != text:
            label.setText(text)

    def _record_ui_metric(self, metric_name: str, started_at: float) -> None:
        elapsed_ms = (time.perf_counter() - started_at) * 1000.0
        if metric_name not in self._ui_perf_metrics:
            self._ui_perf_metrics[metric_name] = []
        self._ui_perf_metrics[metric_name].append(elapsed_ms)
        if len(self._ui_perf_metrics[metric_name]) > 100:
            self._ui_perf_metrics[metric_name] = self._ui_perf_metrics[metric_name][-100:]

    def _build_metric_summary(self, metric_name: str, samples: List[float]) -> Dict[str, object]:
        ordered = sorted(samples)
        count = len(ordered)
        p95_index = max(0, min(count - 1, int(count * 0.95) - 1))
        avg_ms = sum(ordered) / count
        threshold_ms = self.UI_LATENCY_THRESHOLDS_MS.get(metric_name)

        return {
            "count": count,
            "avg_ms": round(avg_ms, 3),
            "min_ms": round(ordered[0], 3),
            "max_ms": round(ordered[-1], 3),
            "p95_ms": round(ordered[p95_index], 3),
            "threshold_ms": threshold_ms,
            "within_threshold": (
                None
                if threshold_ms is None
                else round(avg_ms, 3) <= threshold_ms
            ),
        }

    def _export_ui_metrics_baseline(self) -> None:
        if not self._ui_perf_metrics:
            return

        report_path = ROOT_DIR / "performance_baseline.json"
        summary = {
            metric: self._build_metric_summary(metric, samples)
            for metric, samples in self._ui_perf_metrics.items()
            if samples
        }

        if not summary:
            return

        snapshot = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "source": "tragaperras",
            "metrics": summary,
        }

        data = {"snapshots": []}
        if report_path.exists():
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict) and isinstance(loaded.get("snapshots"), list):
                    data = loaded
            except (OSError, json.JSONDecodeError):
                data = {"snapshots": []}

        data["snapshots"].append(snapshot)
        data["snapshots"] = data["snapshots"][-200:]

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def _append_history(self, result: SpinResult) -> None:
        summary = (
            f"{result.grid[0][0]} {result.grid[0][1]} {result.grid[0][2]} | "
            f"Apuesta {result.total_bet} → Premio {result.total_payout}"
        )
        item = QListWidgetItem(summary)
        if result.total_payout > 0:
            item.setForeground(QColor("#FACC15"))
        else:
            item.setForeground(QColor("#94A3B8"))
        self.history_list.insertItem(0, item)
        while self.history_list.count() > 20:
            self.history_list.takeItem(self.history_list.count() - 1)

    def _handle_resize(self, event: QResizeEvent) -> None:
        width_scale = event.size().width() / self.base_width
        height_scale = event.size().height() / self.base_height
        self.current_scale = max(0.5, min(width_scale, height_scale))

    def get_scaled_size(self, value: int) -> int:
        return max(1, int(value * self.current_scale))

    # ------------------------------------------------------------------
    # Eventos Qt

    def resizeEvent(self, a0: Optional[QResizeEvent]) -> None:
        if a0 is not None:
            super().resizeEvent(a0)
            self._handle_resize(a0)
        else:
            return

    def closeEvent(self, a0) -> None:
        self._export_ui_metrics_baseline()
        a0.accept()


def launch_slot_machine() -> int:
    """Función rápida para lanzar la ventana de tragaperras."""

    app = QApplication.instance() or QApplication(sys.argv)
    window = SlotMachineWindow()
    window.show()
    if QApplication.instance() is app:
        return app.exec()
    return 0


if __name__ == "__main__":
    sys.exit(launch_slot_machine())


