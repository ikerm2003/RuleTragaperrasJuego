from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu
"""
PyQt6 UI Components for Texas Hold'em Poker

This module contains the UI implementation for the poker game,
separated from the game logic.
"""
from typing import List, Optional, Dict, Any, Callable
from PyQt6.QtWidgets import QMenuBar
from PyQt6.QtWidgets import (
    QApplication,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSlider,
    QSpinBox,
    QGridLayout,
    QFrame,
    QGraphicsDropShadowEffect,
    QSizePolicy,
    QWidget,
    QMainWindow,
    QMessageBox,
)
from PyQt6.QtGui import (
    QPixmap,
    QPainter,
    QFont,
    QColor,
    QPalette,
    QLinearGradient,
    QBrush,
    QPen,
    QFontMetrics,
    QResizeEvent,
)
from PyQt6.QtCore import (
    Qt,
    QTimer,
    QPropertyAnimation,
    QEasingCurve,
    QRect,
    QSize,
    pyqtSignal,
)

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from .poker_table import NinePlayerTable, BasePokerTable
from .poker_logic import PlayerAction, GamePhase, Player
import cardCommon
PokerCard = cardCommon.PokerCard
import config
config_manager = config.config_manager
get_text = config.get_text


class PokerWindow(QMainWindow):
    """
    Main poker window supporting scalable UI for up to 9 players.
    Inherits responsive scaling capabilities.
    """
    
    def __init__(self, table_type: str = "nine_player", num_players: int = 6, parent: Optional[QWidget] = None):
        super().__init__(parent)
        
        # Initialize config system
        self.config = config_manager
        
        # Base dimensions for scaling
        self.base_width = 1400
        self.base_height = 900
        self.current_scale = 1.0
        
        self.setWindowTitle(get_text('poker') + " - " + get_text('casino_title'))
        self.setGeometry(100, 100, 1200, 800)
        
        # Apply initial display settings
        self.apply_display_settings()
        
        # Initialize game table
        self.table = NinePlayerTable(small_blind=10, big_blind=20)
        self.table.setup_standard_game(num_human_players=1, total_players=num_players)
        
        # UI components
        self.community_card_labels: List[QLabel] = []
        self.player_displays: List[QFrame] = []
        self.action_buttons: List[QPushButton] = []
        self.pot_label: Optional[QLabel] = None
        self.phase_label: Optional[QLabel] = None
        self.reveal_all_hands: bool = False
        self.check_call_current_action: PlayerAction = PlayerAction.CHECK
        
        # Timer for bot actions
        self.bot_timer = QTimer()
        self.bot_timer.timeout.connect(self.handle_bot_action)
        
        # Register UI callbacks with table
        self.table.register_ui_callback('hand_started', self.on_hand_started)
        self.table.register_ui_callback('action_executed', self.on_action_executed)
        self.table.register_ui_callback('hand_ended', self.on_hand_ended)
        self.table.register_ui_callback('update_display', lambda: self.update_display())
        self.table.register_ui_callback('highlight_player', lambda player_position: self.highlight_current_player(player_position))
        self.table.register_ui_callback('show_actions', lambda player_position, actions: self.show_action_buttons(player_position, actions))
        
        self.create_menu_bar()
        self.init_ui()
        self.start_new_game()
    
    def create_menu_bar(self):
        """Create menu bar with settings option"""
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        
        # Game menu
        game_menu = QMenu("Juego", self)
        menubar.addMenu(game_menu)
        
        new_hand_action = QAction(get_text('new_hand'), self)
        new_hand_action.triggered.connect(self.start_new_game)
        game_menu.addAction(new_hand_action)
        
        game_menu.addSeparator()
        
        exit_action = game_menu.addAction("Salir")
        if isinstance(exit_action, QAction):
            exit_action.triggered.connect(self.close)
        
        # Settings menu
        settings_menu = QMenu(get_text('settings'), self)
        menubar.addMenu(settings_menu)

        config_action = QAction("Configuración...", self)
        config_action.triggered.connect(self.show_config_dialog)
        settings_menu.addAction(config_action)
        
    def show_config_dialog(self):
        """Show configuration dialog"""
        try:
            from ..config_dialog import ConfigDialog
            dialog = ConfigDialog(self)
            dialog.config_changed.connect(self.apply_config_changes)
            dialog.exec()
        except ImportError:
            QMessageBox.information(self, "Info", "Configuración no disponible en este momento.")
    
    def apply_config_changes(self):
        """Apply configuration changes"""
        print("Applying configuration changes...")
        self.apply_display_settings()
        self.update_interface_language()
        self.update_animation_settings()
    
    def apply_display_settings(self):
        """Apply display settings from config"""
        if self.config.is_fullscreen():
            self.showFullScreen()
        else:
            self.showNormal()
            resolution = self.config.get_resolution()
            if resolution != (-1, -1):  # Not auto
                self.resize(resolution[0], resolution[1])
    
    def update_interface_language(self):
        """Update interface language"""
        self.setWindowTitle(get_text('poker') + " - " + get_text('casino_title'))
        # Update other text elements as needed
        if hasattr(self, 'new_hand_button'):
            self.new_hand_button.setText(get_text('new_hand'))
    
    def update_animation_settings(self):
        """Update animation settings"""
        # Animation settings will be applied to existing animation methods
        pass
    
    def init_ui(self):
        """Initialize the main UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(self.get_scaled_size(15))
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create info bar
        self.create_info_bar(main_layout)
        
        # Create main game area
        self.create_game_area(main_layout)
        
        # Create action panel
        self.create_action_panel(main_layout)
    
    def create_info_bar(self, main_layout: QVBoxLayout):
        """Create the info bar showing pot, phase, etc."""
        info_frame = QFrame()
        info_frame.setFixedHeight(self.get_scaled_size(130))
        info_frame.setStyleSheet(self.get_info_bar_style())
        info_layout = QHBoxLayout(info_frame)
        
        # Pot display
        pot_container = QFrame()
        pot_layout = QVBoxLayout(pot_container)
        pot_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pot_layout.setSpacing(1)
        
        pot_title = QLabel(get_text('pot'))
        pot_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pot_title.setFont(self.get_scaled_font(12, QFont.Weight.Bold))
        pot_title.setStyleSheet("color: #F59E0B; font-weight: bold;")
        
        self.pot_label = QLabel("$0")
        self.pot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pot_label.setFont(self.get_scaled_font(24, QFont.Weight.Bold))
        self.pot_label.setStyleSheet("color: #FBBF24; font-weight: bold;")
        
        pot_layout.addWidget(pot_title)
        pot_layout.addWidget(self.pot_label)
        info_layout.addWidget(pot_container)
        
        # Phase display
        phase_container = QFrame()
        phase_layout = QVBoxLayout(phase_container)
        phase_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        phase_layout.setSpacing(1)
        
        phase_title = QLabel(get_text('phase'))
        phase_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        phase_title.setFont(self.get_scaled_font(12, QFont.Weight.Bold))
        phase_title.setStyleSheet("color: #10B981; font-weight: bold;")
        
        self.phase_label = QLabel("Waiting")
        self.phase_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.phase_label.setFont(self.get_scaled_font(18, QFont.Weight.Bold))
        self.phase_label.setStyleSheet("color: #34D399; font-weight: bold;")
        
        phase_layout.addWidget(phase_title)
        phase_layout.addWidget(self.phase_label)
        info_layout.addWidget(phase_container)
        
        main_layout.addWidget(info_frame)
    
    def create_game_area(self, main_layout: QVBoxLayout):
        """Create the main poker table area"""
        table_frame = QFrame()
        table_frame.setMinimumHeight(self.get_scaled_size(550))
        table_frame.setStyleSheet(self.get_table_style())
        
        # Use grid layout for flexible player positioning
        self.table_layout = QGridLayout(table_frame)
        self.table_layout.setSpacing(self.get_scaled_size(20))
        self.table_layout.setContentsMargins(40, 40, 40, 40)
        for row in range(5):
            self.table_layout.setRowStretch(row, 1)
        for col in range(3):
            self.table_layout.setColumnStretch(col, 1)
        
        # Create community cards area
        self.create_community_cards_section()
        
        # Create player displays
        self.create_player_displays()
        
        main_layout.addWidget(table_frame)
    
    def create_community_cards_section(self):
        """Create the community cards display area"""
        community_frame = QFrame()
        community_frame.setFixedSize(self.get_scaled_size(400), self.get_scaled_size(140))
        community_frame.setStyleSheet(self.get_community_cards_style())
        
        community_layout = QVBoxLayout(community_frame)
        community_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        community_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel(get_text('community_cards'))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(self.get_scaled_font(14, QFont.Weight.Bold))
        title.setStyleSheet("color: #F9FAFB; margin-bottom: 8px;")
        community_layout.addWidget(title)
        
        # Cards container
        cards_container = QHBoxLayout()
        cards_container.setSpacing(self.get_scaled_size(8))
        cards_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create 5 card labels
        self.community_card_labels = []
        for i in range(5):
            card_label = QLabel()
            card_width = self.get_scaled_size(70)
            card_height = self.get_scaled_size(100)
            card_label.setFixedSize(card_width, card_height)
            card_label.setStyleSheet(self.get_card_back_style())
            card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_label.setText("?")
            card_label.setFont(self.get_scaled_font(24, QFont.Weight.Bold))
            
            # Add shadow effect
            shadow = QGraphicsDropShadowEffect()
            shadow.setBlurRadius(self.get_scaled_size(15))
            shadow.setColor(QColor(0, 0, 0, 100))
            shadow.setOffset(self.get_scaled_size(2), self.get_scaled_size(3))
            card_label.setGraphicsEffect(shadow)
            
            self.community_card_labels.append(card_label)
            cards_container.addWidget(card_label)
        
        community_layout.addLayout(cards_container)
        
        # Add to center of table
        self.table_layout.addWidget(community_frame, 2, 1, Qt.AlignmentFlag.AlignCenter)
    
    def create_player_displays(self):
        """Create displays for all players based on table layout"""
        self.player_displays = []
        seat_layout = self.table.get_seat_layout()
        
        for i, (row, col, position) in enumerate(seat_layout):
            if i < len(self.table.players):
                player_frame = self.create_player_display(i, position)
                self.player_displays.append(player_frame)
                self.table_layout.addWidget(player_frame, row, col, Qt.AlignmentFlag.AlignCenter)
    
    def create_player_display(self, player_index: int, position: str) -> QFrame:
        """Create a display widget for a player"""
        player = self.table.players[player_index]
        
        frame = QFrame()
        frame.setFixedSize(self.get_scaled_size(340), self.get_scaled_size(170))
        frame.setStyleSheet(self.get_player_frame_style())
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(self.get_scaled_size(10))
        layout.setContentsMargins(18, 16, 18, 16)
        
        # Player name and chips
        info_layout = QHBoxLayout()
        
        name_label = QLabel(player.name)
        name_label.setFont(self.get_scaled_font(14, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #F9FAFB; font-weight: bold;")
        
        chips_label = QLabel(f"${player.chips}")
        chips_label.setFont(self.get_scaled_font(12, QFont.Weight.Bold))
        chips_label.setStyleSheet("color: #FBBF24; font-weight: bold;")
        chips_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        info_layout.addWidget(name_label)
        info_layout.addStretch()
        info_layout.addWidget(chips_label)
        layout.addLayout(info_layout)
        
        # Cards area
        cards_frame = QFrame()
        cards_frame.setFixedHeight(self.get_scaled_size(75))
        cards_layout = QHBoxLayout(cards_frame)
        cards_layout.setContentsMargins(10, 10, 10, 10)
        cards_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cards_layout.setSpacing(self.get_scaled_size(8))
        
        # Create card labels
        card_labels = []
        for i in range(2):
            card_label = QLabel()
            card_label.setFixedSize(self.get_scaled_size(45), self.get_scaled_size(65))
            card_label.setStyleSheet(self.get_card_back_style())
            card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_label.setText("?")
            card_label.setFont(self.get_scaled_font(16, QFont.Weight.Bold))
            card_labels.append(card_label)
            cards_layout.addWidget(card_label)
        
        # Store references for updates
        setattr(frame, "cards_frame", cards_frame)
        setattr(frame, "cards_layout", cards_layout)
        setattr(frame, "card_labels", card_labels)
        setattr(frame, "name_label", name_label)
        setattr(frame, "chips_label", chips_label)
        
        layout.addWidget(cards_frame)
        
        # Current bet display with better styling
        bet_label = QLabel("Bet: $0")
        bet_label.setFont(self.get_scaled_font(12, QFont.Weight.Bold))
        bet_label.setStyleSheet("""
            color: #FBBF24; 
            background-color: rgba(0, 0, 0, 0.3);
            border: 1px solid rgba(251, 191, 36, 0.5);
            border-radius: 8px;
            padding: 4px 8px;
            text-align: center;
        """)
        bet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        setattr(frame, "bet_label", bet_label)
        layout.addWidget(bet_label)
        
        return frame
    
    def create_action_panel(self, main_layout: QVBoxLayout):
        """Create the action panel with buttons"""
        action_frame = QFrame()
        action_frame.setFixedHeight(self.get_scaled_size(100))
        action_frame.setStyleSheet(self.get_action_panel_style())
        
        action_layout = QHBoxLayout(action_frame)
        action_layout.setContentsMargins(20, 15, 20, 15)
        action_layout.setSpacing(self.get_scaled_size(15))
        action_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Create action buttons (initially hidden)
        self.fold_button = self.create_action_button(get_text('fold'), action=PlayerAction.FOLD)
        self.check_call_button = self.create_action_button(get_text('check'), click_handler=self.on_check_call_clicked)
        self.raise_button = self.create_action_button(get_text('raise'), action=PlayerAction.RAISE)
        
        # Raise amount controls
        self.raise_slider = QSlider(Qt.Orientation.Horizontal)
        self.raise_slider.setFixedWidth(self.get_scaled_size(200))
        self.raise_slider.valueChanged.connect(self.on_raise_slider_changed)
        self.raise_amount_label = QLabel("$0")
        self.raise_amount_label.setFont(self.get_scaled_font(12, QFont.Weight.Bold))
        
        action_layout.addWidget(self.fold_button)
        action_layout.addWidget(self.check_call_button)
        action_layout.addWidget(self.raise_button)
        self.raise_amount_title = QLabel("Cantidad:")
        self.raise_amount_title.setFont(self.get_scaled_font(12, QFont.Weight.Bold))
        action_layout.addWidget(self.raise_amount_title)
        action_layout.addWidget(self.raise_slider)
        action_layout.addWidget(self.raise_amount_label)
        
        # New hand button
        self.new_hand_button = QPushButton(get_text('new_hand'))
        self.new_hand_button.setFont(self.get_scaled_font(14, QFont.Weight.Bold))
        self.new_hand_button.clicked.connect(self.start_new_game)
        action_layout.addWidget(self.new_hand_button)

        main_layout.addWidget(action_frame)

        # Ocultar controles hasta que sea el turno del jugador humano
        self.hide_action_buttons()
    
    def create_action_button(
        self,
        text: str,
        action: Optional[PlayerAction] = None,
        click_handler: Optional[Callable[[], None]] = None,
    ) -> QPushButton:
        """Create a styled action button"""
        button = QPushButton(text)
        button.setFont(self.get_scaled_font(14, QFont.Weight.Bold))
        button.setFixedSize(self.get_scaled_size(120), self.get_scaled_size(45))
        button.setStyleSheet(self.get_button_style())
        if click_handler is not None:
            button.clicked.connect(click_handler)
        elif action is not None:
            button.clicked.connect(lambda: self.execute_player_action(action))
        self.action_buttons.append(button)
        return button

    def on_check_call_clicked(self):
        action = getattr(self, "check_call_current_action", PlayerAction.CHECK)
        self.execute_player_action(action)
    
    def start_new_game(self):
        """Start a new poker hand"""
        self.bot_timer.stop()
        self.reveal_all_hands = False
        self.hide_action_buttons()
        self.table.start_new_hand()
    
    def execute_player_action(self, action: PlayerAction):
        """Execute a player action"""
        if not self.table.players or self.table.current_player >= len(self.table.players):
            return
            
        current_player = self.table.players[self.table.current_player]
        if not current_player.is_human:
            return
        
        amount = 0
        if action == PlayerAction.RAISE:
            amount = self.raise_slider.value()
        
        # Evita dobles clics mientras se procesa la acción
        self.hide_action_buttons()

        success = self.table.execute_action(self.table.current_player, action, amount)
        if success:
            self.schedule_bot_action_if_needed()
        else:
            # Si la acción no fue válida, vuelve a mostrar las opciones disponibles
            self.show_available_actions(self.table.current_player)
    
    def handle_bot_action(self):
        """Handle bot player actions"""
        self.bot_timer.stop()
        
        if self.table.is_hand_over():
            return
            
        current_player = self.table.players[self.table.current_player]
        if current_player.is_human:
            # Show action buttons for human player
            self.show_available_actions()
            return
        
        # Execute bot action
        action, amount = self.table.get_bot_action(self.table.current_player)
        success = self.table.execute_action(self.table.current_player, action, amount)
        
        if success and not self.table.is_hand_over():
            self.schedule_bot_action_if_needed(delay=1500)
    
    def show_available_actions(
        self,
        player_position: Optional[int] = None,
        actions: Optional[List[PlayerAction]] = None,
    ):
        """Show available action buttons for the specified player (defaults to current)."""
        if player_position is None:
            player_position = self.table.current_player

        if player_position >= len(self.table.players):
            self.hide_action_buttons()
            return

        current_player = self.table.players[player_position]
        if not current_player.is_human:
            self.hide_action_buttons()
            return

        if actions is None:
            actions = self.table.get_valid_actions(player_position)

        if not actions:
            self.hide_action_buttons()
            return

        # Fold button
        can_fold = PlayerAction.FOLD in actions
        self.fold_button.setVisible(can_fold)
        self.fold_button.setEnabled(can_fold)

        # Check / Call button
        if PlayerAction.CHECK in actions:
            self.check_call_button.setText("Check")
            self.check_call_button.setVisible(True)
            self.check_call_button.setEnabled(True)
            self.check_call_current_action = PlayerAction.CHECK
        elif PlayerAction.CALL in actions:
            call_amount = self.table.current_bet - current_player.current_bet
            self.check_call_button.setText(f"Call ${call_amount}")
            self.check_call_button.setVisible(True)
            self.check_call_button.setEnabled(True)
            self.check_call_current_action = PlayerAction.CALL
        else:
            self.check_call_button.setVisible(False)
            self.check_call_current_action = PlayerAction.CHECK

        # Raise controls
        can_raise = (PlayerAction.RAISE in actions) and (current_player.chips > 0)
        min_raise = self.table.current_bet + self.table.min_raise if hasattr(self.table, 'min_raise') else 0
        max_raise = current_player.chips + current_player.current_bet if hasattr(current_player, 'chips') and hasattr(current_player, 'current_bet') else 0
        if can_raise:
            min_raise = self.table.current_bet + self.table.min_raise
            max_raise = current_player.chips + current_player.current_bet
            if min_raise > max_raise:
                can_raise = False

        if can_raise:
            self.raise_button.setText("Raise")
            self.raise_button.setVisible(True)
            self.raise_button.setEnabled(True)
            self.raise_slider.setVisible(True)
            self.raise_slider.setEnabled(True)
            self.raise_amount_title.setVisible(True)
            self.raise_amount_title.setEnabled(True)
            self.raise_amount_label.setVisible(True)
            self.raise_amount_label.setEnabled(True)

            self.raise_slider.setRange(min_raise, max_raise)
            self.raise_slider.setValue(min_raise)
            self.on_raise_slider_changed(min_raise)
        else:
            self.raise_button.setVisible(False)
            self.raise_button.setEnabled(False)
            self.raise_slider.setVisible(False)
            self.raise_slider.setEnabled(False)
            self.raise_amount_title.setVisible(False)
            self.raise_amount_title.setEnabled(False)
            self.raise_amount_label.setVisible(False)
            self.raise_amount_label.setEnabled(False)

    def show_action_buttons(self, player_position: int, actions: List[PlayerAction]):
        """Callback bridge from the table to display available actions."""
        self.show_available_actions(player_position, actions)

    def highlight_current_player(self, player_position: int):
        """Callback bridge to refresh highlighting for the current player."""
        self.animate_player_highlight(player_position)
        self.update_player_displays()
        self.schedule_bot_action_if_needed()
    
    def animate_bet_change(self, bet_label: QLabel):
        """Animate bet label when amount changes"""
        if not self.config.are_animations_enabled():
            return
            
        if not hasattr(self, '_bet_animations'):
            self._bet_animations = {}
        
        # Stop existing animation if any
        if bet_label in self._bet_animations:
            self._bet_animations[bet_label].stop()
        
        # Create scale animation
        animation = QPropertyAnimation(bet_label, b"geometry")
        duration = int(300 / self.config.get_animation_speed()) if self.config.get_animation_speed() > 0 else 300
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        original_geometry = bet_label.geometry()
        expanded_geometry = QRect(
            original_geometry.x() - 5,
            original_geometry.y() - 2, 
            original_geometry.width() + 10,
            original_geometry.height() + 4
        )
        
        animation.setStartValue(original_geometry)
        animation.setKeyValueAt(0.5, expanded_geometry)
        animation.setEndValue(original_geometry)
        animation.finished.connect(lambda: self._bet_animations.pop(bet_label, None))
        
        self._bet_animations[bet_label] = animation
        animation.start()
        
    def animate_player_highlight(self, player_position: int):
        """Animate highlighting transition between players"""
        if not self.config.are_animations_enabled():
            return
            
        if not hasattr(self, '_highlight_animations'):
            self._highlight_animations = {}
        
        # Stop all existing highlight animations
        for anim in self._highlight_animations.values():
            if anim.state() == QPropertyAnimation.State.Running:
                anim.stop()
        self._highlight_animations.clear()
        
        # Animate current player highlight
        if player_position < len(self.player_displays):
            frame = self.player_displays[player_position]
            animation = QPropertyAnimation(frame, b"pos")
            duration = int(200 / self.config.get_animation_speed()) if self.config.get_animation_speed() > 0 else 200
            animation.setDuration(duration)
            animation.setEasingCurve(QEasingCurve.Type.OutCubic)
            
            original_pos = frame.pos()
            parent_widget = frame.parentWidget()
            if parent_widget is not None:
                global_pos = frame.mapToGlobal(original_pos)
                mapped_pos = parent_widget.mapFromGlobal(global_pos)
                lifted_pos = mapped_pos
            else:
                lifted_pos = original_pos
            lifted_pos.setY(lifted_pos.y() - 3)
            
            animation.setStartValue(original_pos)
            animation.setKeyValueAt(0.5, lifted_pos)
            animation.setEndValue(original_pos)
            
            self._highlight_animations[player_position] = animation
            animation.start()
    
    def animate_card_deal(self, card_label: QLabel, delay: int = 0):
        """Animate dealing a card"""
        if not self.config.are_animations_enabled():
            return
            
        if not hasattr(self, '_card_animations'):
            self._card_animations = []
        
        # Start position (from deck)
        start_pos = self.geometry().center()
        end_pos = card_label.pos()
        
        # Create movement animation
        animation = QPropertyAnimation(card_label, b"pos")
        duration = int(400 / self.config.get_animation_speed()) if self.config.get_animation_speed() > 0 else 400
        animation.setDuration(duration)
        animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        animation.setStartValue(start_pos)
        animation.setEndValue(end_pos)
        
        if delay > 0:
            QTimer.singleShot(delay, animation.start)
        else:
            animation.start()
        
        self._card_animations.append(animation)
        animation.finished.connect(lambda: self._card_animations.remove(animation) if animation in self._card_animations else None)
        
    def animate_pot_update(self):
        """Animate pot value changes"""
        if not self.config.are_animations_enabled() or not self.pot_label:
            return
            
        if not hasattr(self, '_pot_animation'):
            self._pot_animation = QPropertyAnimation(self.pot_label, b"geometry")
        
        if self._pot_animation.state() == QPropertyAnimation.State.Running:
            self._pot_animation.stop()
        
        duration = int(250 / self.config.get_animation_speed()) if self.config.get_animation_speed() > 0 else 250
        self._pot_animation.setDuration(duration)
        self._pot_animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        
        original_geometry = self.pot_label.geometry()
        if original_geometry.width() == 0 or original_geometry.height() == 0:
            return
        expanded_geometry = QRect(
            original_geometry.x() - 10,
            original_geometry.y() - 5,
            original_geometry.width() + 20,
            original_geometry.height() + 10
        )
        
        self._pot_animation.setStartValue(original_geometry)
        self._pot_animation.setKeyValueAt(0.5, expanded_geometry)
        self._pot_animation.setEndValue(original_geometry)
        self._pot_animation.start()

    def on_raise_slider_changed(self, value: int):
        """Keep the raise amount label in sync with the slider."""
        self.raise_amount_label.setText(f"${value}")
    
    def hide_action_buttons(self):
        """Hide all action buttons and raise controls."""
        for button in self.action_buttons:
            button.setVisible(False)
            button.setEnabled(False)
        self.raise_slider.setVisible(False)
        self.raise_slider.setEnabled(False)
        self.raise_amount_title.setVisible(False)
        self.raise_amount_title.setEnabled(False)
        self.raise_amount_label.setVisible(False)
        self.raise_amount_label.setEnabled(False)

    def schedule_bot_action_if_needed(self, delay: int = 1000):
        """Programar la acción del bot si el turno actual pertenece a un bot."""
        if not self.table.players or self.table.is_hand_over():
            self.bot_timer.stop()
            return

        if self.table.current_player >= len(self.table.players):
            self.bot_timer.stop()
            return

        current_player = self.table.players[self.table.current_player]
        if current_player.is_human:
            self.bot_timer.stop()
        else:
            self.hide_action_buttons()
            self.bot_timer.stop()
            self.bot_timer.start(delay)
    
    def update_display(self):
        """Update all UI elements with current game state"""
        # Update pot and phase with animations
        if self.pot_label:
            old_pot_text = self.pot_label.text()
            new_pot_text = f"${self.table.pot}"
            if old_pot_text != new_pot_text:
                self.pot_label.setText(new_pot_text)
                self.animate_pot_update()
            
        if self.phase_label:
            self.phase_label.setText(self.table.phase.value)
        
        # Update community cards with animations
        self.update_community_cards()
        
        # Update player displays
        self.update_player_displays()
    
    def update_community_cards(self):
        """Update community card displays"""
        for i, card_label in enumerate(self.community_card_labels):
            if i < len(self.table.community_cards):
                card = self.table.community_cards[i]
                pixmap = self.load_card_image(card)
                card_label.setPixmap(pixmap)
                card_label.setText("")
                card_label.setStyleSheet("")
            else:
                card_label.setPixmap(QPixmap())
                card_label.setText("?")
                card_label.setStyleSheet(self.get_card_back_style())
    
    def update_player_displays(self):
        """Update all player displays"""
        # If the number of player displays does not match the number of players, re-create them
        if len(self.player_displays) != len(self.table.players):
            # Remove old widgets from layout
            for frame in self.player_displays:
                frame.setParent(None)
            self.player_displays = []
            self.create_player_displays()

        for i, frame in enumerate(self.player_displays):
            if i < len(self.table.players):
                player = self.table.players[i]
                
                # Update chips and bet with enhanced display
                if hasattr(frame, "chips_label"):
                    frame.chips_label.setText(f"${player.chips}")
                
                # Enhanced bet display with total bet information
                current_bet = player.current_bet
                total_bet = getattr(player, 'total_bet_this_hand', current_bet)
                
                if current_bet > 0:
                    if total_bet > current_bet:
                        bet_text = f"Bet: ${current_bet} (Total: ${total_bet})"
                    else:
                        bet_text = f"Bet: ${current_bet}"
                    
                    # Add visual emphasis for new bets
                    if hasattr(frame, "bet_label"):
                        if hasattr(frame.bet_label, '_last_bet') and frame.bet_label._last_bet != current_bet:
                            self.animate_bet_change(frame.bet_label)
                        frame.bet_label._last_bet = current_bet
                else:
                    bet_text = "Bet: $0"
                    
                if hasattr(frame, "bet_label"):
                    frame.bet_label.setText(bet_text)
                
                # Update player state styling
                if i == self.table.current_player and not self.table.is_hand_over():
                    frame.setStyleSheet(self.get_player_frame_style("highlight"))
                elif player.is_folded:
                    frame.setStyleSheet(self.get_player_frame_style("folded"))
                else:
                    frame.setStyleSheet(self.get_player_frame_style())
                
                # Update cards
                reveal_cards = len(player.hand) >= 2 and (player.is_human or self.reveal_all_hands)
                if hasattr(frame, "card_labels"):
                    for j, card_label in enumerate(frame.card_labels):
                        if reveal_cards and j < len(player.hand):
                            card = player.hand[j]
                            pixmap = self.load_card_image(card)
                            card_label.setPixmap(pixmap)
                            card_label.setText("")
                            card_label.setStyleSheet("")
                        else:
                            card_label.setPixmap(QPixmap())
                            card_label.setText("?")
                            card_label.setStyleSheet(self.get_card_back_style())
    
    def load_card_image(self, card: PokerCard) -> QPixmap:
        """Create a visual representation of a card"""
        card_width = self.get_scaled_size(70)
        card_height = self.get_scaled_size(100)
        
        pixmap = QPixmap(card_width, card_height)
        pixmap.fill(QColor(255, 255, 255))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw card border
        border_pen = QPen(QColor(0, 0, 0), 2)
        painter.setPen(border_pen)
        painter.drawRoundedRect(1, 1, card_width-2, card_height-2, 8, 8)
        
        # Determine card color
        if card.suit in ['Corazones', 'Diamantes']:
            color = QColor(220, 20, 60)  # Red
            symbol = '♥' if card.suit == 'Corazones' else '♦'
        else:
            color = QColor(0, 0, 0)  # Black
            symbol = '♠' if card.suit == 'Picas' else '♣'
        
        painter.setPen(QPen(color))
        
        # Draw value in top-left
        font = QFont("Arial", self.get_scaled_size(12), QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(8, 20, card.value)
        
        # Draw suit symbol in top-left
        font_symbol = QFont("Arial", self.get_scaled_size(10))
        painter.setFont(font_symbol)
        painter.drawText(8, 35, symbol)
        
        # Draw large value in center
        font_large = QFont("Arial", self.get_scaled_size(20), QFont.Weight.Bold)
        painter.setFont(font_large)
        fm = QFontMetrics(font_large)
        value_width = fm.horizontalAdvance(card.value)
        painter.drawText(card_width // 2 - value_width // 2, card_height // 2, card.value)
        
        # Draw large symbol in center-bottom
        font_symbol_large = QFont("Arial", self.get_scaled_size(16), QFont.Weight.Bold)
        painter.setFont(font_symbol_large)
        fm_symbol = QFontMetrics(font_symbol_large)
        symbol_width = fm_symbol.horizontalAdvance(symbol)
        painter.drawText(card_width // 2 - symbol_width // 2, int(card_height * 0.75), symbol)
        
        painter.end()
        return pixmap
    
    # Event callbacks
    def on_hand_started(self):
        """Called when a new hand starts"""
        self.reveal_all_hands = False
        self.update_display()
        self.schedule_bot_action_if_needed()
    
    def on_action_executed(self, player: int, action: PlayerAction, amount: int):
        """Called when an action is executed"""
        self.update_display()
        self.schedule_bot_action_if_needed()
    
    def on_hand_ended(self, results=None):
        """Called when a hand ends"""
        self.bot_timer.stop()
        self.reveal_all_hands = True
        self.update_display()
        QApplication.processEvents()
        self.hide_action_buttons()

        if results:
            winner_lines = []
            for info in results:
                if isinstance(info, dict):
                    name = info.get("name")
                    player_obj = info.get("player")
                    if not name and player_obj is not None:
                        name = getattr(player_obj, "name", "Jugador")
                    amount = info.get("amount", 0)
                    ranking_name = info.get("ranking_name")
                else:
                    # Compatibilidad básica si llega otro tipo
                    name = getattr(info, "name", "Jugador")
                    amount = getattr(info, "amount", 0)
                    ranking_name = getattr(info, "ranking_name", None)

                if name is None:
                    name = "Jugador"
                if ranking_name:
                    winner_lines.append(f"{name} gana ${amount} con {ranking_name}")
                else:
                    winner_lines.append(f"{name} gana ${amount}")

            if len(winner_lines) == 1:
                message = winner_lines[0]
            else:
                message = "El bote se repartió entre:\n- " + "\n- ".join(winner_lines)
        else:
            message = "La mano ha terminado."

        QMessageBox.information(self, "Mano finalizada", message)
    
    # Styling methods
    def get_scaled_size(self, base_size: int) -> int:
        """Get scaled size based on current window size"""
        current_size = self.size()
        width_scale = current_size.width() / self.base_width
        height_scale = current_size.height() / self.base_height
        scale = max(0.65, min(width_scale, height_scale, 2.0))
        return max(1, int(base_size * scale))
    
    def get_scaled_font(self, base_size: int, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
        """Get scaled font"""
        scaled_size = max(10, int(base_size * self.current_scale))
        return QFont("Arial", scaled_size, weight)
    
    def get_info_bar_style(self) -> str:
        return """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(17, 24, 39, 0.95),
                           stop:1 rgba(31, 41, 55, 0.95));
                border: 2px solid rgba(75, 85, 99, 0.6);
                border-radius: 10px;
            }
        """
    
    def get_table_style(self) -> str:
        return """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(21, 128, 61, 0.9),
                           stop:1 rgba(22, 101, 52, 0.9));
                border: 3px solid rgba(34, 197, 94, 0.4);
                border-radius: 20px;
            }
        """
    
    def get_community_cards_style(self) -> str:
        return """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(55, 65, 81, 0.9),
                           stop:1 rgba(75, 85, 99, 0.9));
                border: 2px solid rgba(156, 163, 175, 0.4);
                border-radius: 15px;
            }
        """
    
    def get_player_frame_style(self, state: str = "base") -> str:
        border_radius = self.get_scaled_size(18)
        border_width = max(2, self.get_scaled_size(2))
        
        if state == "highlight":
            background = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(255, 215, 0, 0.92), stop:1 rgba(240, 180, 0, 0.88))"
            border_color = "#FFE066"
            text_color = "#1A1A1A"
        elif state == "folded":
            background = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(70, 70, 70, 0.8), stop:1 rgba(45, 45, 45, 0.8))"
            border_color = "rgba(200, 200, 200, 0.3)"
            text_color = "#D1D5DB"
        else:
            background = "qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 rgba(139, 69, 19, 0.9), stop:1 rgba(101, 67, 33, 0.9))"
            border_color = "rgba(255, 215, 0, 0.35)"
            text_color = "#F9FAFB"
        
        return f"""
            QFrame {{
                background: {background};
                border: {border_width}px solid {border_color};
                border-radius: {border_radius}px;
                color: {text_color};
            }}
        """
    
    def get_card_back_style(self) -> str:
        return """
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(37, 99, 235, 0.9),
                           stop:1 rgba(29, 78, 216, 0.9));
                border: 2px solid rgba(147, 197, 253, 0.6);
                border-radius: 8px;
                color: white;
                font-weight: bold;
            }
        """
    
    def get_action_panel_style(self) -> str:
        return """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(17, 24, 39, 0.95),
                           stop:1 rgba(31, 41, 55, 0.95));
                border: 2px solid rgba(75, 85, 99, 0.6);
                border-radius: 12px;
            }
        """
    
    def get_button_style(self) -> str:
        return """
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(59, 130, 246, 0.9),
                           stop:1 rgba(37, 99, 235, 0.9));
                border: 2px solid rgba(147, 197, 253, 0.6);
                border-radius: 8px;
                color: white;
                font-weight: bold;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(96, 165, 250, 0.9),
                           stop:1 rgba(59, 130, 246, 0.9));
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(37, 99, 235, 0.9),
                           stop:1 rgba(29, 78, 216, 0.9));
            }
        """
    
    def resizeEvent(self, event: QResizeEvent):
        """Handle window resize for responsive scaling"""
        super().resizeEvent(event)
        current_size = self.size()
        width_scale = current_size.width() / self.base_width
        height_scale = current_size.height() / self.base_height
        new_scale = max(0.65, min(width_scale, height_scale, 2.0))
        
        if abs(new_scale - self.current_scale) > 0.05:
            self.current_scale = new_scale
            self.update_ui_scaling()
    
    def update_ui_scaling(self):
        """Update UI elements when scale changes"""
        # This would update all scalable elements
        # Implementation depends on specific scaling needs
        pass