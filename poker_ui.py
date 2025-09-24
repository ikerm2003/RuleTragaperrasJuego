"""
PyQt6 UI Components for Texas Hold'em Poker

This module contains the UI implementation for the poker game,
separated from the game logic.
"""
from typing import List, Optional, Dict, Any
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

from poker_table import NinePlayerTable, BasePokerTable
from poker_logic import PlayerAction, GamePhase, Player
from cardCommon import PokerCard
from ui.base_table import BaseFourPlayerTable


class PokerWindow(QMainWindow):
    """
    Main poker window supporting scalable UI for up to 9 players.
    Inherits responsive scaling capabilities.
    """
    
    def __init__(self, table_type: str = "nine_player", num_players: int = 6):
        super().__init__()
        
        # Base dimensions for scaling
        self.base_width = 1400
        self.base_height = 900
        self.current_scale = 1.0
        
        self.setWindowTitle("Texas Hold'em Poker")
        self.setGeometry(100, 100, 1200, 800)
        
        # Initialize game table
        self.table = NinePlayerTable(small_blind=10, big_blind=20)
        self.table.setup_standard_game(num_human_players=1, total_players=num_players)
        
        # UI components
        self.community_card_labels: List[QLabel] = []
        self.player_displays: List[QFrame] = []
        self.action_buttons: List[QPushButton] = []
        self.pot_label: Optional[QLabel] = None
        self.phase_label: Optional[QLabel] = None
        
        # Timer for bot actions
        self.bot_timer = QTimer()
        self.bot_timer.timeout.connect(self.handle_bot_action)
        
        # Register UI callbacks with table
        self.table.register_ui_callback('hand_started', self.on_hand_started)
        self.table.register_ui_callback('action_executed', self.on_action_executed)
        self.table.register_ui_callback('hand_ended', self.on_hand_ended)
        
        self.init_ui()
        self.start_new_game()
    
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
        info_frame.setFixedHeight(self.get_scaled_size(80))
        info_frame.setStyleSheet(self.get_info_bar_style())
        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(20, 10, 20, 10)
        
        # Pot display
        pot_container = QFrame()
        pot_layout = QVBoxLayout(pot_container)
        pot_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pot_layout.setSpacing(2)
        
        pot_title = QLabel("POT")
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
        phase_layout.setSpacing(2)
        
        phase_title = QLabel("PHASE")
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
        title = QLabel("Community Cards")
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
        frame.cards_frame = cards_frame
        frame.cards_layout = cards_layout
        frame.card_labels = card_labels
        frame.name_label = name_label
        frame.chips_label = chips_label
        
        layout.addWidget(cards_frame)
        
        # Current bet display
        bet_label = QLabel("Bet: $0")
        bet_label.setFont(self.get_scaled_font(11, QFont.Weight.Bold))
        bet_label.setStyleSheet("color: #D1D5DB; text-align: center;")
        bet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        frame.bet_label = bet_label
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
        self.fold_button = self.create_action_button("Fold", PlayerAction.FOLD)
        self.check_call_button = self.create_action_button("Check", PlayerAction.CHECK)
        self.raise_button = self.create_action_button("Raise", PlayerAction.RAISE)
        
        # Raise amount controls
        self.raise_slider = QSlider(Qt.Orientation.Horizontal)
        self.raise_slider.setFixedWidth(self.get_scaled_size(200))
        self.raise_amount_label = QLabel("$0")
        self.raise_amount_label.setFont(self.get_scaled_font(12, QFont.Weight.Bold))
        
        action_layout.addWidget(self.fold_button)
        action_layout.addWidget(self.check_call_button)
        action_layout.addWidget(self.raise_button)
        action_layout.addWidget(QLabel("Amount:"))
        action_layout.addWidget(self.raise_slider)
        action_layout.addWidget(self.raise_amount_label)
        
        # New hand button
        self.new_hand_button = QPushButton("New Hand")
        self.new_hand_button.setFont(self.get_scaled_font(14, QFont.Weight.Bold))
        self.new_hand_button.clicked.connect(self.start_new_game)
        action_layout.addWidget(self.new_hand_button)
        
        # Initially hide action buttons
        self.hide_action_buttons()
        
        main_layout.addWidget(action_frame)
    
    def create_action_button(self, text: str, action: PlayerAction) -> QPushButton:
        """Create a styled action button"""
        button = QPushButton(text)
        button.setFont(self.get_scaled_font(14, QFont.Weight.Bold))
        button.setFixedSize(self.get_scaled_size(120), self.get_scaled_size(45))
        button.setStyleSheet(self.get_button_style())
        button.clicked.connect(lambda: self.execute_player_action(action))
        self.action_buttons.append(button)
        return button
    
    def start_new_game(self):
        """Start a new poker hand"""
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
        
        success = self.table.execute_action(self.table.current_player, action, amount)
        if success:
            self.hide_action_buttons()
            
            # Handle bot actions after a delay
            if not self.table.is_hand_over():
                self.bot_timer.start(1000)  # 1 second delay
    
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
            # Continue with next player after delay
            self.bot_timer.start(1500)
    
    def show_available_actions(self):
        """Show available action buttons for human player"""
        if self.table.current_player >= len(self.table.players):
            return
            
        current_player = self.table.players[self.table.current_player]
        if not current_player.is_human:
            return
        
        valid_actions = self.table.get_valid_actions(self.table.current_player)
        
        # Update button visibility and text
        self.fold_button.setVisible(PlayerAction.FOLD in valid_actions)
        
        if PlayerAction.CHECK in valid_actions:
            self.check_call_button.setText("Check")
            self.check_call_button.setVisible(True)
        elif PlayerAction.CALL in valid_actions:
            call_amount = self.table.current_bet - current_player.current_bet
            self.check_call_button.setText(f"Call ${call_amount}")
            self.check_call_button.setVisible(True)
        else:
            self.check_call_button.setVisible(False)
        
        # Raise button and slider
        if PlayerAction.RAISE in valid_actions:
            self.raise_button.setVisible(True)
            self.raise_slider.setVisible(True)
            self.raise_amount_label.setVisible(True)
            
            # Set slider range
            min_raise = self.table.current_bet + self.table.min_raise
            max_raise = current_player.chips + current_player.current_bet
            self.raise_slider.setRange(min_raise, max_raise)
            self.raise_slider.setValue(min_raise)
            self.raise_amount_label.setText(f"${min_raise}")
            
            # Connect slider to label
            self.raise_slider.valueChanged.connect(
                lambda v: self.raise_amount_label.setText(f"${v}")
            )
        else:
            self.raise_button.setVisible(False)
            self.raise_slider.setVisible(False)
            self.raise_amount_label.setVisible(False)
    
    def hide_action_buttons(self):
        """Hide all action buttons"""
        for button in self.action_buttons:
            button.setVisible(False)
        self.raise_slider.setVisible(False)
        self.raise_amount_label.setVisible(False)
    
    def update_display(self):
        """Update all UI elements with current game state"""
        # Update pot and phase
        if self.pot_label:
            self.pot_label.setText(f"${self.table.pot}")
        if self.phase_label:
            self.phase_label.setText(self.table.phase.value)
        
        # Update community cards
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
        for i, frame in enumerate(self.player_displays):
            if i < len(self.table.players):
                player = self.table.players[i]
                
                # Update chips and bet
                frame.chips_label.setText(f"${player.chips}")
                frame.bet_label.setText(f"Bet: ${player.current_bet}")
                
                # Update player state styling
                if i == self.table.current_player and not self.table.is_hand_over():
                    frame.setStyleSheet(self.get_player_frame_style("highlight"))
                elif player.is_folded:
                    frame.setStyleSheet(self.get_player_frame_style("folded"))
                else:
                    frame.setStyleSheet(self.get_player_frame_style())
                
                # Update cards for human player
                if player.is_human and len(player.hand) >= 2:
                    for j, card_label in enumerate(frame.card_labels):
                        if j < len(player.hand):
                            card = player.hand[j]
                            pixmap = self.load_card_image(card)
                            card_label.setPixmap(pixmap)
                            card_label.setText("")
                            card_label.setStyleSheet("")
    
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
        self.update_display()
    
    def on_action_executed(self, player: int, action: PlayerAction, amount: int):
        """Called when an action is executed"""
        self.update_display()
    
    def on_hand_ended(self):
        """Called when a hand ends"""
        self.update_display()
        self.hide_action_buttons()
    
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
                border-radius: 12px;
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
    
    def resizeEvent(self, event):
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