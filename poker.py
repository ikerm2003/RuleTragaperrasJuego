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
)

import sys
import random
from enum import Enum
from dataclasses import dataclass
from typing import Any, List, Optional, cast

from cardCommon import PokerDeck
from ui.base_table import BaseFourPlayerTable
    
class GamePhase(Enum):
    WAITING = "Esperando jugadores"
    PRE_FLOP = "Pre-flop"
    FLOP = "Flop"
    TURN = "Turn"
    RIVER = "River"
    SHOWDOWN = "Showdown"
    FINISHED = "Mano terminada"

class PlayerAction(Enum):
    FOLD = "fold"
    CALL = "call"
    RAISE = "raise"
    CHECK = "check"
    ALL_IN = "all_in"

@dataclass
class Player:
    name: str
    chips: int
    position: int
    hand: List = None  # type: ignore
    current_bet: int = 0
    total_bet_in_hand: int = 0
    is_active: bool = True
    is_folded: bool = False
    is_all_in: bool = False
    is_human: bool = False
    
    def __post_init__(self):
        if self.hand is None:
            self.hand = []
    
    def can_act(self) -> bool:
        return self.is_active and not self.is_folded and not self.is_all_in
    
    def reset_for_new_hand(self):
        self.hand = []
        self.current_bet = 0
        self.total_bet_in_hand = 0
        self.is_folded = False
        self.is_all_in = False
        self.is_active = True

class PokerGame:
    def __init__(self, num_players: int = 4, small_blind: int = 10, big_blind: int = 20):
        self.deck = PokerDeck()
        self.players: List[Player] = []
        self.community_cards = []
        self.pot = 0
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.dealer_position = 0
        self.current_player = 0
        self.current_bet = 0
        self.phase = GamePhase.WAITING
        self.min_raise = big_blind
        
        # Initialize players
        for i in range(num_players):
            is_human = (i == 0)  # First player is human
            player_name = "Tú" if is_human else f"Bot {i}"
            self.players.append(Player(
                name=player_name,
                chips=1000,  # Starting chips
                position=i,
                is_human=is_human
            ))
    
    def start_new_hand(self):
        """Inicia una nueva mano de poker"""
        # Reset game state
        self.deck = PokerDeck()
        self.deck.shuffle()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.min_raise = self.big_blind
        self.phase = GamePhase.PRE_FLOP
        
        # Reset players
        for player in self.players:
            player.reset_for_new_hand()
        
        # Deal hole cards
        for _ in range(2):
            for player in self.players:
                if player.chips > 0:  # Only deal to players with chips
                    player.hand.extend(self.deck.deal(1))
        
        # Post blinds
        self._post_blinds()
        
        # Set current player (left of big blind)
        self.current_player = (self.dealer_position + 3) % len(self.players)
        while not self.players[self.current_player].can_act():
            self.current_player = (self.current_player + 1) % len(self.players)
    
    def _post_blinds(self):
        """Postea las ciegas pequeña y grande"""
        sb_pos = (self.dealer_position + 1) % len(self.players)
        bb_pos = (self.dealer_position + 2) % len(self.players)
    def create_info_bar(self, main_layout: QVBoxLayout) -> None:
        """Creates an elegant info bar at the top with responsive scaling"""
        info_frame = QFrame()
        info_frame.setFixedHeight(self.get_scaled_size(80))
        info_frame.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(45, 90, 39, 0.95), stop:0.5 rgba(75, 120, 69, 0.95), stop:1 rgba(45, 90, 39, 0.95));
                border: 2px solid rgba(255, 215, 0, 0.3);
                border-radius: 15px;
                margin: 5px;
            }
            """
        )

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(self.get_scaled_size(20))
        shadow.setColor(QColor(0, 0, 0, 100))
        shadow.setOffset(0, self.get_scaled_size(5))
        info_frame.setGraphicsEffect(shadow)

        info_layout = QHBoxLayout(info_frame)
        info_layout.setContentsMargins(
            self.get_scaled_size(25),
            self.get_scaled_size(15),
            self.get_scaled_size(25),
            self.get_scaled_size(15),
        )

        self.pot_label = QLabel("POT: $0")
        self.pot_label.setFont(self.get_scaled_font(18, QFont.Weight.Bold))
        self.pot_label.setStyleSheet(
            f"""
            QLabel {{
                color: #FFD700;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 215, 0, 0.2), stop:1 rgba(255, 215, 0, 0.1));
                border: 2px solid rgba(255, 215, 0, 0.5);
                border-radius: 12px;
                padding: {self.get_scaled_size(8)}px {self.get_scaled_size(20)}px;
                font-weight: bold;
            }}
            """
        )

        self.phase_label = QLabel("ESPERANDO JUGADORES")
        self.phase_label.setFont(self.get_scaled_font(14, QFont.Weight.Bold))
        self.phase_label.setStyleSheet(
            f"""
            QLabel {{
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 144, 255, 0.8), stop:1 rgba(30, 144, 255, 0.6));
                border: 2px solid rgba(30, 144, 255, 0.3);
                border-radius: 10px;
                padding: {self.get_scaled_size(6)}px {self.get_scaled_size(15)}px;
            }}
            """
        )

        self.current_player_label = QLabel("TURNO: -")
        self.current_player_label.setFont(self.get_scaled_font(14, QFont.Weight.Bold))
        self.current_player_label.setStyleSheet(
            f"""
            QLabel {{
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 69, 0, 0.8), stop:1 rgba(255, 69, 0, 0.6));
                border: 2px solid rgba(255, 69, 0, 0.3);
                border-radius: 10px;
                padding: {self.get_scaled_size(6)}px {self.get_scaled_size(15)}px;
            }}
            """
        )

        info_layout.addWidget(self.pot_label)
        info_layout.addStretch()
        info_layout.addWidget(self.phase_label)
        info_layout.addStretch()
        info_layout.addWidget(self.current_player_label)

        main_layout.addWidget(info_frame)

    def create_game_area(self, main_layout: QVBoxLayout) -> None:
        """Creates the main poker table area with professional design"""
        game_widget = self.create_table_frame(
            min_height=self.get_scaled_size(550),
            spacing=self.get_scaled_size(20),
            margins=(
                self.get_scaled_size(40),
                self.get_scaled_size(40),
                self.get_scaled_size(40),
                self.get_scaled_size(40),
            ),
        )
        game_widget.setStyleSheet(
            """
            QFrame {
                background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                    fx:0.5, fy:0.5, stop:0 #1a5d34, stop:0.7 #0e5c2f, stop:1 #0a4d20);
                border: 4px solid rgba(139, 69, 19, 0.8);
                border-radius: 25px;
                margin: 10px;
            }
            """
        )

        table_shadow = QGraphicsDropShadowEffect()
        table_shadow.setBlurRadius(self.get_scaled_size(30))
        table_shadow.setColor(QColor(0, 0, 0, 150))
        table_shadow.setOffset(0, self.get_scaled_size(10))
        game_widget.setGraphicsEffect(table_shadow)

        self.populate_player_positions()
        layout = self.table_layout
        if layout is not None:
            self.create_community_cards_section(layout)

        main_layout.addWidget(game_widget)

    def create_community_cards_section(self, game_layout: QGridLayout) -> None:
        """Creates the community cards area with responsive scaling"""
        self.community_card_labels.clear()

        community_frame = QFrame()
        card_width = self.get_scaled_size(70)
        card_height = self.get_scaled_size(100)
        frame_width = self.get_scaled_size(400)
        frame_height = self.get_scaled_size(140)

        community_frame.setFixedSize(frame_width, frame_height)
        community_frame.setStyleSheet(
            """
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.15), stop:1 rgba(255, 255, 255, 0.05));
                border: 2px solid rgba(255, 215, 0, 0.4);
                border-radius: 15px;
                padding: 10px;
            }
            """
        )

        community_layout = QVBoxLayout(community_frame)
        community_layout.setSpacing(self.get_scaled_size(8))

        title_label = QLabel("COMMUNITY CARDS")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.get_scaled_font(12, QFont.Weight.Bold))
        title_label.setStyleSheet(
            """
            QLabel {
                color: rgba(255, 215, 0, 0.9);
                background: transparent;
                padding: 2px;
            }
            """
        )
        community_layout.addWidget(title_label)

        cards_container = QHBoxLayout()
        cards_container.setSpacing(self.get_scaled_size(8))

        for _ in range(5):
            card_label = QLabel()
            card_label.setFixedSize(card_width, card_height)
            card_label.setStyleSheet(
                """
                QLabel {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f8f8f8, stop:1 #e8e8e8);
                    border: 2px solid rgba(255, 215, 0, 0.6);
                    border-radius: 10px;
                    margin: 2px;
                }
                """
            )
            card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_label.setText("?")
            card_label.setFont(self.get_scaled_font(24, QFont.Weight.Bold))

            card_shadow = QGraphicsDropShadowEffect()
            card_shadow.setBlurRadius(self.get_scaled_size(8))
            card_shadow.setColor(QColor(0, 0, 0, 80))
            card_shadow.setOffset(self.get_scaled_size(2), self.get_scaled_size(3))
            card_label.setGraphicsEffect(card_shadow)

            self.community_card_labels.append(card_label)
            cards_container.addWidget(card_label)

        community_layout.addLayout(cards_container)
        game_layout.addWidget(community_frame, 2, 1, Qt.AlignmentFlag.AlignCenter)

    def get_player_frame_style(self, state: str = "base") -> str:
        """Construye estilos responsivos para los paneles de jugador"""
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



class PokerWindow(BaseFourPlayerTable):
    def __init__(self) -> None:
        super().__init__(base_width=1400, base_height=900)
        self.setWindowTitle("Texas Hold'em Poker")
        self.setGeometry(100, 100, 1200, 800)

        # Inicializa el juego con 4 jugadores
        self.game = PokerGame(num_players=4, small_blind=10, big_blind=20)

        # Temporizador para las acciones de los bots
        self.bot_timer = QTimer()
        self.bot_timer.timeout.connect(self.handle_bot_action)

        self.init_ui()
        self.start_new_game()

    def update_ui_scaling(self):
        """Updates UI elements with new scaling factors"""
        # Update fonts for main labels
        if hasattr(self, 'pot_label'):
            self.pot_label.setFont(self.get_scaled_font(18, QFont.Weight.Bold))
        if hasattr(self, 'phase_label'):
            self.phase_label.setFont(self.get_scaled_font(14, QFont.Weight.Bold))
        if hasattr(self, 'current_player_label'):
            self.current_player_label.setFont(self.get_scaled_font(14, QFont.Weight.Bold))
        if hasattr(self, 'status_label'):
            self.status_label.setFont(self.get_scaled_font(12, QFont.Weight.Bold))
        
        # Update player display fonts
        for player_frame in self.player_displays:
            if hasattr(player_frame, 'name_label'):
                player_frame.name_label.setFont(self.get_scaled_font(16, QFont.Weight.Bold))
            if hasattr(player_frame, 'chips_label'):
                player_frame.chips_label.setFont(self.get_scaled_font(14, QFont.Weight.Bold))
            if hasattr(player_frame, 'bet_label'):
                player_frame.bet_label.setFont(self.get_scaled_font(13, QFont.Weight.Bold))
            # Ajustar tamaños y estilos responsivos
            player_frame.setFixedSize(self.get_scaled_size(340), self.get_scaled_size(170))
            layout = player_frame.layout()
            if isinstance(layout, QVBoxLayout):
                layout.setSpacing(self.get_scaled_size(10))
                layout.setContentsMargins(self.get_scaled_size(18), self.get_scaled_size(16),
                                           self.get_scaled_size(18), self.get_scaled_size(16))
            if hasattr(player_frame, 'cards_frame'):
                player_frame.cards_frame.setFixedHeight(self.get_scaled_size(75))  # type: ignore[attr-defined]
            if hasattr(player_frame, 'cards_layout'):
                player_frame.cards_layout.setContentsMargins(self.get_scaled_size(10), self.get_scaled_size(10),
                                                           self.get_scaled_size(10), self.get_scaled_size(10))  # type: ignore[attr-defined]
            front_style, back_style = self.get_player_card_styles()
            if hasattr(player_frame, 'card_labels'):
                for card_label in player_frame.card_labels:  # type: ignore[attr-defined]
                    card_label.setFixedSize(self.get_scaled_size(56), self.get_scaled_size(80))
                    card_label.setFont(self.get_scaled_font(11, QFont.Weight.Bold))
                    card_label.front_style = front_style  # type: ignore[attr-defined]
                    card_label.back_style = back_style  # type: ignore[attr-defined]
                    if card_label.pixmap() and not card_label.pixmap().isNull():
                        card_label.setStyleSheet(front_style)
                    elif card_label.text() == "?" and hasattr(player_frame, 'player_index'):
                        player = self.game.players[getattr(player_frame, 'player_index')]
                        card_label.setStyleSheet(back_style if not player.is_human else front_style)
                    else:
                        card_label.setStyleSheet(front_style)
            state = getattr(player_frame, 'current_state', 'base')
            self.set_player_frame_state(player_frame, state)

        # Update community cards fonts
        for card_label in self.community_card_labels:
            card_label.setFont(self.get_scaled_font(24, QFont.Weight.Bold))

    def init_ui(self) -> None:
        """Construye la interfaz principal reutilizando la estructura base."""
        self.setMinimumSize(self.base_width, self.base_height)
        self.setStyleSheet(
            """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a4d20, stop:0.5 #0e5c2f, stop:1 #0a4d20);
            }
            """
        )

        self.configure_main_layout(spacing=15, margins=(20, 20, 20, 20))
        self.community_card_labels.clear()
        self.player_displays.clear()

        # Crear secciones principales
        self.create_info_bar(self.main_layout)
        self.create_game_area(self.main_layout)
        self.create_modern_action_panel(self.main_layout)
        def create_game_area(self, main_layout: QVBoxLayout) -> None:
            """Creates the main poker table area with professional design"""
            game_widget = self.create_table_frame(
                min_height=self.get_scaled_size(550),
                spacing=self.get_scaled_size(20),
                margins=(
                    self.get_scaled_size(40),
                    self.get_scaled_size(40),
                    self.get_scaled_size(40),
                    self.get_scaled_size(40),
                ),
            )
            game_widget.setStyleSheet(
                """
                QFrame {
                    background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                        fx:0.5, fy:0.5, stop:0 #1a5d34, stop:0.7 #0e5c2f, stop:1 #0a4d20);
                    border: 4px solid rgba(139, 69, 19, 0.8);
                    border-radius: 25px;
                    margin: 10px;
                }
                """
            )

            table_shadow = QGraphicsDropShadowEffect()
            table_shadow.setBlurRadius(self.get_scaled_size(30))
            table_shadow.setColor(QColor(0, 0, 0, 150))
            table_shadow.setOffset(0, self.get_scaled_size(10))
            game_widget.setGraphicsEffect(table_shadow)

            self.populate_player_positions()
            if self.table_layout is not None:
                self.create_community_cards_section(self.table_layout)

            main_layout.addWidget(game_widget)

        def create_community_cards_section(self, game_layout: QGridLayout | None) -> None:
            """Creates the community cards area with responsive scaling"""
            if game_layout is None:
                return

            community_frame = QFrame()
            card_width = self.get_scaled_size(70)
            card_height = self.get_scaled_size(100)
            frame_width = self.get_scaled_size(400)
            frame_height = self.get_scaled_size(140)
        self.phase_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 144, 255, 0.8), stop:1 rgba(30, 144, 255, 0.6));
                border: 2px solid rgba(30, 144, 255, 0.3);
                border-radius: 10px;
                padding: {self.get_scaled_size(6)}px {self.get_scaled_size(15)}px;
            }}
        """)
        
        # Current player indicator with responsive font
        self.current_player_label = QLabel("TURNO: -")
        self.current_player_label.setFont(self.get_scaled_font(14, QFont.Weight.Bold))
        self.current_player_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 69, 0, 0.8), stop:1 rgba(255, 69, 0, 0.6));
                border: 2px solid rgba(255, 69, 0, 0.3);
                border-radius: 10px;
                padding: {self.get_scaled_size(6)}px {self.get_scaled_size(15)}px;
            }}
        """)
        
        info_layout.addWidget(self.pot_label)
        info_layout.addStretch()
        info_layout.addWidget(self.phase_label)
        info_layout.addStretch()
        info_layout.addWidget(self.current_player_label)
        
        main_layout.addWidget(info_frame)
        
    def create_game_area(self, main_layout):
        """Creates the main poker table area with professional design"""
        # Main game frame with poker table look
        game_widget = QFrame()
        game_widget.setMinimumHeight(550)
        game_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        game_widget.setStyleSheet("""
            QFrame {
                background: qradialgradient(cx:0.5, cy:0.5, radius:1,
                    fx:0.5, fy:0.5, stop:0 #1a5d34, stop:0.7 #0e5c2f, stop:1 #0a4d20);
                border: 4px solid rgba(139, 69, 19, 0.8);
                border-radius: 25px;
                margin: 10px;
            }
        """)

        # Add table shadow
        table_shadow = QGraphicsDropShadowEffect()
        table_shadow.setBlurRadius(30)
        table_shadow.setColor(QColor(0, 0, 0, 150))
        table_shadow.setOffset(0, 10)
        game_widget.setGraphicsEffect(table_shadow)
        
        game_layout = QGridLayout(game_widget)
        game_layout.setSpacing(20)
        game_layout.setContentsMargins(40, 40, 40, 40)
        
        # Create player positions in a more natural poker table arrangement
        player_positions = [
            (3, 1, "bottom"),    # Human player (bottom)
            (2, 0, "left"),      # Bot 1 (left)
            (1, 1, "top"),       # Bot 2 (top)
            (2, 2, "right"),     # Bot 3 (right)
        ]
        
        # Create modern player displays
        for i, (row, col, position) in enumerate(player_positions):
            player_frame = self.create_modern_player_display(i, position)
            self.player_displays.append(player_frame)
            game_layout.addWidget(player_frame, row, col, Qt.AlignmentFlag.AlignCenter)
        
        # Community cards section with elegant design
        self.create_community_cards_section(game_layout)

        main_layout.addWidget(game_widget)

    def create_community_cards_section(self, game_layout):
        """Creates the community cards area with responsive scaling"""
        community_frame = QFrame()
        card_width = self.get_scaled_size(70)
        card_height = self.get_scaled_size(100)
        frame_width = self.get_scaled_size(400)
        frame_height = self.get_scaled_size(140)

        community_frame.setFixedSize(frame_width, frame_height)
        community_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.15), stop:1 rgba(255, 255, 255, 0.05));
                border: 2px solid rgba(255, 215, 0, 0.4);
                border-radius: 15px;
                padding: 10px;
            }
        """)

        community_layout = QVBoxLayout(community_frame)
        community_layout.setSpacing(self.get_scaled_size(8))

        # Title for community cards with responsive font
        title_label = QLabel("COMMUNITY CARDS")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.get_scaled_font(12, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 215, 0, 0.9);
                background: transparent;
                padding: 2px;
            }
        """)
        community_layout.addWidget(title_label)

        # Cards container with responsive spacing
        cards_container = QHBoxLayout()
        cards_container.setSpacing(self.get_scaled_size(8))
        
        for i in range(5):
            card_label = QLabel()
            card_label.setFixedSize(card_width, card_height)
            card_label.setStyleSheet(f"""
                QLabel {{
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f8f8f8, stop:1 #e8e8e8);
                    border: 2px solid rgba(255, 215, 0, 0.6);
                    border-radius: 10px;
                    margin: 2px;
                }}
            """)
            card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_label.setText("?")
            card_label.setFont(self.get_scaled_font(24, QFont.Weight.Bold))

            # Add subtle card shadow with scaled blur
            card_shadow = QGraphicsDropShadowEffect()
            card_shadow.setBlurRadius(self.get_scaled_size(8))
            card_shadow.setColor(QColor(0, 0, 0, 80))
            card_shadow.setOffset(self.get_scaled_size(2), self.get_scaled_size(3))
            card_label.setGraphicsEffect(card_shadow)

            self.community_card_labels.append(card_label)
            cards_container.addWidget(card_label)
        
        community_layout.addLayout(cards_container)
        game_layout.addWidget(community_frame, 2, 1, Qt.AlignmentFlag.AlignCenter)
    
    def get_player_frame_style(self, state: str = "base") -> str:
        """Construye estilos responsivos para los paneles de jugador"""
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

    def get_player_card_styles(self) -> tuple[str, str]:
        """Devuelve estilos responsivos para cartas boca arriba y boca abajo"""
        border_radius = self.get_scaled_size(8)
        front_style = f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f8f8, stop:1 #e0e0e0);
                border: 1px solid rgba(255, 215, 0, 0.45);
                border-radius: {border_radius}px;
                margin: 1px;
                color: black;
            }}
        """
        back_style = f"""
            QLabel {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1B254B, stop:1 #0C1631);
                border: 1px solid rgba(255, 255, 255, 0.35);
                border-radius: {border_radius}px;
                margin: 1px;
                color: white;
                letter-spacing: 1px;
            }}
        """
        return front_style, back_style

    def set_player_frame_state(self, frame: QFrame, state: str):
        """Aplica el estilo correspondiente al estado del jugador"""
        frame.current_state = state  # type: ignore[attr-defined]
        frame.setStyleSheet(self.get_player_frame_style(state))

    def create_modern_player_display(self, player_index: int, position: str) -> QFrame:
        """Creates a modern, elegant player display with responsive design"""
        player = self.game.players[player_index]
        
        frame = QFrame()
        frame.setFixedSize(self.get_scaled_size(340), self.get_scaled_size(170))
        self.set_player_frame_state(frame, "base")

        # Add player frame shadow
        player_shadow = QGraphicsDropShadowEffect()
        player_shadow.setBlurRadius(self.get_scaled_size(18))
        player_shadow.setColor(QColor(0, 0, 0, 120))
        player_shadow.setOffset(self.get_scaled_size(3), self.get_scaled_size(5))
        frame.setGraphicsEffect(player_shadow)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(self.get_scaled_size(10))
        layout.setContentsMargins(self.get_scaled_size(18), self.get_scaled_size(16),
                                  self.get_scaled_size(18), self.get_scaled_size(16))

        # Player header with name and position indicator
        header_layout = QHBoxLayout()
        
        name_label = QLabel(player.name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        name_label.setFont(self.get_scaled_font(16, QFont.Weight.Bold))
        name_label.setStyleSheet("""
            QLabel {
                color: #FFD700;
                background: transparent;
                padding: 2px 5px;
            }
        """)
        
        # Position indicator
        position_indicator = QLabel("●")
        position_indicator.setAlignment(Qt.AlignmentFlag.AlignRight)
        position_indicator.setFont(self.get_scaled_font(12))
        position_indicator.setStyleSheet("color: #32CD32; background: transparent;")

        header_layout.addWidget(name_label)
        header_layout.addStretch()
        header_layout.addWidget(position_indicator)
        layout.addLayout(header_layout)

        # Chips display with progress bar style
        chips_container = QHBoxLayout()
        chips_label = QLabel(f"${player.chips}")
        chips_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chips_label.setFont(self.get_scaled_font(14, QFont.Weight.Bold))
        chips_style = """
            QLabel {
                color: #90EE90;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 100, 0, 0.3), stop:1 rgba(0, 150, 0, 0.3));
                border: 1px solid rgba(0, 150, 0, 0.5);
                border-radius: 8px;
                padding: 4px 10px;
            }
        """
        chips_label.setStyleSheet(chips_style)
        chips_label.default_style = chips_style  # type: ignore[attr-defined]
        chips_container.addWidget(chips_label)
        layout.addLayout(chips_container)

        # Cards display area
        cards_frame = QFrame()
        cards_frame.setFixedHeight(self.get_scaled_size(75))
        cards_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 8px;
            }
        """)
        cards_layout = QHBoxLayout(cards_frame)
        cards_layout.setContentsMargins(self.get_scaled_size(10), self.get_scaled_size(10),
                                        self.get_scaled_size(10), self.get_scaled_size(10))

        card_labels = []
        front_style, back_style = self.get_player_card_styles()
        for i in range(2):
            card_label = QLabel()
            card_label.setFixedSize(self.get_scaled_size(48), self.get_scaled_size(68))
            card_label.setStyleSheet(front_style)
            card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_label.setText("?")
            card_label.setFont(self.get_scaled_font(10, QFont.Weight.Bold))
            card_label.front_style = front_style  # type: ignore
            card_label.back_style = back_style  # type: ignore
            card_labels.append(card_label)
            cards_layout.addWidget(card_label)
        
        cards_layout.addStretch()
        layout.addWidget(cards_frame)

        # Betting info
        bet_container = QHBoxLayout()
        bet_label = QLabel("$0")
        bet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bet_label.setFont(self.get_scaled_font(13, QFont.Weight.Bold))
        bet_style = """
            QLabel {
                color: #FFD700;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(255, 215, 0, 0.2), stop:1 rgba(255, 215, 0, 0.1));
                border: 1px solid rgba(255, 215, 0, 0.4);
                border-radius: 6px;
                padding: 3px 8px;
            }
        """
        bet_label.setStyleSheet(bet_style)
        bet_label.default_style = bet_style  # type: ignore[attr-defined]
        bet_container.addWidget(bet_label)
        layout.addLayout(bet_container)

        # Store references for updates (ignore type checking warnings)
        frame.name_label = name_label  # type: ignore
        frame.chips_label = chips_label  # type: ignore
        frame.bet_label = bet_label  # type: ignore
        frame.card_labels = card_labels  # type: ignore
        frame.position_indicator = position_indicator  # type: ignore
        frame.cards_frame = cards_frame  # type: ignore
        frame.cards_layout = cards_layout  # type: ignore
        frame.player_index = player_index  # type: ignore

        return frame
    
    # Old create_player_display method removed - using create_modern_player_display instead

    def create_modern_action_panel(self, main_layout):
        """Creates a modern, intuitive action panel with responsive scaling"""
        action_frame = QFrame()
        action_frame.setFixedHeight(self.get_scaled_size(150))
        action_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(45, 90, 39, 0.95), stop:1 rgba(35, 70, 29, 0.95));
                border: 3px solid rgba(255, 215, 0, 0.4);
                border-radius: 20px;
                margin: 10px;
            }
        """)
        
        # Add action panel shadow with scaled blur
        action_shadow = QGraphicsDropShadowEffect()
        action_shadow.setBlurRadius(self.get_scaled_size(25))
        action_shadow.setColor(QColor(0, 0, 0, 120))
        action_shadow.setOffset(0, self.get_scaled_size(8))
        action_frame.setGraphicsEffect(action_shadow)
        
        action_layout = QVBoxLayout(action_frame)
        action_layout.setSpacing(self.get_scaled_size(15))
        action_layout.setContentsMargins(self.get_scaled_size(25), self.get_scaled_size(20),
                                        self.get_scaled_size(25), self.get_scaled_size(20))

        # Title for action panel with responsive font
        title_label = QLabel("YOUR ACTIONS")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(self.get_scaled_font(12, QFont.Weight.Bold))
        title_label.setStyleSheet("""
            QLabel {
                color: rgba(255, 215, 0, 0.9);
                background: transparent;
                padding: 2px;
            }
        """)
        action_layout.addWidget(title_label)

        # Betting controls with responsive design
        bet_frame = QFrame()
        bet_frame.setStyleSheet(f"""
            QFrame {{
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                padding: {self.get_scaled_size(8)}px;
            }}
        """)
        bet_layout = QHBoxLayout(bet_frame)

        bet_label = QLabel("Cantidad a apostar:")
        bet_label.setFont(self.get_scaled_font(10, QFont.Weight.Bold))
        bet_label.setStyleSheet("color: white; background: transparent;")
        bet_layout.addWidget(bet_label)
        
        # Modern slider with responsive styling
        self.bet_slider = QSlider(Qt.Orientation.Horizontal)
        self.bet_slider.setMinimum(0)
        self.bet_slider.setMaximum(1000)
        self.bet_slider.setValue(20)
        handle_size = self.get_scaled_size(18)
        groove_height = self.get_scaled_size(8)
        self.bet_slider.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid rgba(255, 255, 255, 0.3);
                height: {groove_height}px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2a2a2a, stop:1 #1a1a1a);
                border-radius: {groove_height//2}px;
            }}
            QSlider::handle:horizontal {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFD700, stop:1 #FFA500);
                border: 2px solid #FFD700;
                width: {handle_size}px;
                margin: -{(handle_size-groove_height)//2}px 0;
                border-radius: {handle_size//2}px;
            }}
            QSlider::handle:horizontal:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #FFED4A, stop:1 #FFD700);
            }}
        """)
        self.bet_slider.valueChanged.connect(self.update_bet_spinbox)
        
        # Modern spinbox with responsive sizing
        self.bet_spinbox = QSpinBox()
        self.bet_spinbox.setMinimum(0)
        self.bet_spinbox.setMaximum(10000)
        self.bet_spinbox.setValue(20)
        self.bet_spinbox.setFixedWidth(self.get_scaled_size(80))
        spinbox_padding = self.get_scaled_size(4)
        self.bet_spinbox.setStyleSheet(f"""
            QSpinBox {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f0f0f0, stop:1 #e0e0e0);
                border: 2px solid rgba(255, 215, 0, 0.5);
                border-radius: 8px;
                padding: {spinbox_padding}px;
                color: black;
                font-weight: bold;
                font-size: {self.get_scaled_font(10).pointSize()}px;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                background: rgba(255, 215, 0, 0.3);
                border: 1px solid rgba(255, 215, 0, 0.5);
                border-radius: 3px;
            }}
        """)
        self.bet_spinbox.valueChanged.connect(self.update_bet_slider)
        
        bet_layout.addWidget(self.bet_slider, 1)
        bet_layout.addWidget(self.bet_spinbox)
        action_layout.addWidget(bet_frame)
        
        # Modern action buttons with responsive sizing
        button_layout = QHBoxLayout()
        button_layout.setSpacing(self.get_scaled_size(12))
        button_height = self.get_scaled_size(45)
        
        self.fold_button = QPushButton("RETIRARSE")
        self.fold_button.setFixedHeight(button_height)
        self.fold_button.setFont(self.get_scaled_font(13, QFont.Weight.Bold))
        self.fold_button.setStyleSheet(self.get_modern_button_style("#E53E3E", "#C53030"))
        self.fold_button.clicked.connect(self.fold_action)
        
        self.check_call_button = QPushButton("IGUALAR")
        self.check_call_button.setFixedHeight(button_height)
        self.check_call_button.setFont(self.get_scaled_font(13, QFont.Weight.Bold))
        self.check_call_button.setStyleSheet(self.get_modern_button_style("#38A169", "#2F855A"))
        self.check_call_button.clicked.connect(self.check_call_action)
        
        self.raise_button = QPushButton("SUBIR")
        self.raise_button.setFixedHeight(button_height)
        self.raise_button.setFont(self.get_scaled_font(13, QFont.Weight.Bold))
        self.raise_button.setStyleSheet(self.get_modern_button_style("#DD6B20", "#C05621"))
        self.raise_button.clicked.connect(self.raise_action)
        
        self.new_hand_button = QPushButton("NUEVA MANO")
        self.new_hand_button.setFixedHeight(button_height)
        self.new_hand_button.setFont(self.get_scaled_font(13, QFont.Weight.Bold))
        self.new_hand_button.setStyleSheet(self.get_modern_button_style("#3182CE", "#2C5282"))
        self.new_hand_button.clicked.connect(self.start_new_game)
        
        button_layout.addWidget(self.fold_button)
        button_layout.addWidget(self.check_call_button)
        button_layout.addWidget(self.raise_button)
        button_layout.addWidget(self.new_hand_button)
        
        action_layout.addLayout(button_layout)
        main_layout.addWidget(action_frame)    # Old create_action_panel method removed - using create_modern_action_panel instead

    def create_status_section(self, main_layout):
        """Creates an elegant status section at the bottom with responsive scaling"""
        status_frame = QFrame()
        status_frame.setFixedHeight(self.get_scaled_size(60))
        status_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(0, 0, 0, 0.7), stop:0.5 rgba(30, 30, 30, 0.8), stop:1 rgba(0, 0, 0, 0.7));
                border: 2px solid rgba(255, 215, 0, 0.3);
                border-radius: 12px;
                margin: 5px;
            }
        """)

        status_layout = QHBoxLayout(status_frame)
        status_layout.setContentsMargins(self.get_scaled_size(20), self.get_scaled_size(15),
                                        self.get_scaled_size(20), self.get_scaled_size(15))

        self.status_label = QLabel("¡Bienvenido al Texas Hold'em Poker Profesional! Haz clic en 'NUEVA MANO' para comenzar.")
        self.status_label.setFont(self.get_scaled_font(12, QFont.Weight.Bold))
        self.status_label.setStyleSheet("""
            QLabel {
                color: #F7FAFC;
                background: transparent;
                padding: 5px;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        status_layout.addWidget(self.status_label)
        main_layout.addWidget(status_frame)

    def get_modern_button_style(self, base_color: str, hover_color: str) -> str:
        """Returns modern button styling with hover effects and responsive sizing"""
        padding_v = self.get_scaled_size(8)
        padding_h = self.get_scaled_size(16)
        border_radius = self.get_scaled_size(12)
        min_width = self.get_scaled_size(80)

        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {base_color}, stop:1 {hover_color});
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: {border_radius}px;
                padding: {padding_v}px {padding_h}px;
                min-width: {min_width}px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {hover_color}, stop:1 {base_color});
                border: 2px solid rgba(255, 255, 255, 0.4);
                transform: translateY(-2px);
            }}
            QPushButton:pressed {{
                background: {hover_color};
                transform: translateY(1px);
            }}
            QPushButton:disabled {{
                background: rgba(100, 100, 100, 0.5);
                color: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(100, 100, 100, 0.3);
            }}
        """

    # Old get_button_style method removed - using get_modern_button_style instead
    def update_bet_slider(self, value):
        """Actualiza el slider cuando cambia el spinbox"""
        self.bet_slider.setValue(value)
    
    def update_bet_spinbox(self, value):
        """Actualiza el spinbox cuando cambia el slider"""
        self.bet_spinbox.setValue(value)
    
    def start_new_game(self):
        """Inicia una nueva mano"""
        self.game.start_new_hand()
        self.update_display()
        self.update_action_buttons()
        self.status_label.setText("Nueva mano iniciada. ¡Es tu turno!")
        
        # If it's a bot's turn, start bot timer
        current_player = self.game.get_current_player()
        if current_player and not current_player.is_human:
            self.bot_timer.start(2000)  # 2 second delay
    
    def update_display(self):
        """Actualiza toda la visualización del juego"""
        # Update pot
        self.pot_label.setText(f"Pot: ${self.game.pot}")
        
        # Update phase
        self.phase_label.setText(f"Fase: {self.game.phase.value}")
        
        # Update current player
        current_player = self.game.get_current_player()
        if current_player:
            self.current_player_label.setText(f"Turno: {current_player.name}")
        
        # Update community cards
        for i, card_label in enumerate(self.community_card_labels):
            if i < len(self.game.community_cards) and self.game.community_cards[i] is not None:
                pixmap = self.load_card_image(self.game.community_cards[i])
                if pixmap:
                    scaled_width = self.get_scaled_size(60)
                    scaled_height = self.get_scaled_size(90)
                    card_label.setPixmap(pixmap.scaled(scaled_width, scaled_height, Qt.AspectRatioMode.KeepAspectRatio))
                else:
                    card_label.clear()
                    card_label.setText("?")
            else:
                card_label.clear()
                card_label.setText("?")
        
        # Update player displays
        for i, player_frame in enumerate(self.player_displays):
            player = self.game.players[i]
            frame_ref = cast(Any, player_frame)
            
            # Update chips and bet
            frame_ref.chips_label.setText(f"${player.chips}")
            frame_ref.bet_label.setText(f"${player.current_bet}")
            
            # Update card visibility based on if it's human player
            if player.is_human and player.hand:
                # Show human player's cards
                for j, card_label in enumerate(frame_ref.card_labels):
                    if j < len(player.hand) and player.hand[j] is not None:
                        pixmap = self.load_card_image(player.hand[j])
                        if pixmap:
                            scaled_width = self.get_scaled_size(56)
                            scaled_height = self.get_scaled_size(80)
                            card_label.setPixmap(pixmap.scaled(scaled_width, scaled_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                            card_label.setStyleSheet(card_label.front_style)  # type: ignore[attr-defined]
                            card_label.setText("")
                        else:
                            card_label.clear()
                            card_label.setStyleSheet(card_label.front_style)  # type: ignore[attr-defined]
                    else:
                        card_label.clear()
                        card_label.setText("?")
                        card_label.setStyleSheet(card_label.front_style)  # type: ignore[attr-defined]
            else:
                # Hide other players' cards
                for card_label in frame_ref.card_labels:
                    card_label.clear()
                    card_label.setText("?")
                    card_label.setStyleSheet(card_label.back_style)  # type: ignore[attr-defined]
            
            # Highlight current player
            if player.is_folded:
                self.set_player_frame_state(player_frame, "folded")
                frame_ref.position_indicator.setStyleSheet("color: #A0AEC0; background: transparent;")
                muted_chips_style = """
                    QLabel {
                        color: #CBD5F5;
                        background: rgba(80, 80, 80, 0.35);
                        border: 1px solid rgba(200, 200, 200, 0.2);
                        border-radius: 8px;
                        padding: 4px 10px;
                    }
                """
                muted_bet_style = """
                    QLabel {
                        color: #E2E8F0;
                        background: rgba(60, 60, 60, 0.3);
                        border: 1px solid rgba(180, 180, 180, 0.25);
                        border-radius: 6px;
                        padding: 3px 8px;
                    }
                """
                frame_ref.chips_label.setStyleSheet(muted_chips_style)  # type: ignore[attr-defined]
                frame_ref.bet_label.setStyleSheet(muted_bet_style)  # type: ignore[attr-defined]
            elif current_player and i == self.game.current_player:
                self.set_player_frame_state(player_frame, "highlight")
                frame_ref.position_indicator.setStyleSheet("color: #1A1A1A; background: transparent;")
                frame_ref.chips_label.setStyleSheet(getattr(frame_ref.chips_label, "default_style", frame_ref.chips_label.styleSheet()))  # type: ignore[attr-defined]
                frame_ref.bet_label.setStyleSheet(getattr(frame_ref.bet_label, "default_style", frame_ref.bet_label.styleSheet()))  # type: ignore[attr-defined]
            else:
                self.set_player_frame_state(player_frame, "base")
                frame_ref.position_indicator.setStyleSheet("color: #32CD32; background: transparent;")
                frame_ref.chips_label.setStyleSheet(getattr(frame_ref.chips_label, "default_style", frame_ref.chips_label.styleSheet()))  # type: ignore[attr-defined]
                frame_ref.bet_label.setStyleSheet(getattr(frame_ref.bet_label, "default_style", frame_ref.bet_label.styleSheet()))  # type: ignore[attr-defined]
    
    def update_action_buttons(self):
        """Actualiza el estado de los botones de acción"""
        human_player = self.game.get_human_player()
        current_player = self.game.get_current_player()
        
        # Enable buttons only if it's human player's turn
        is_human_turn = bool(current_player and current_player.is_human)
        
        self.fold_button.setEnabled(is_human_turn)
        self.check_call_button.setEnabled(is_human_turn)
        self.raise_button.setEnabled(is_human_turn)
        
        if is_human_turn and human_player:
            # Update check/call button text
            if self.game.current_bet > human_player.current_bet:
                call_amount = min(self.game.current_bet - human_player.current_bet, human_player.chips)
                self.check_call_button.setText(f"Igualar ${call_amount}")
            else:
                self.check_call_button.setText("Pasar")
            
            # Update bet slider limits
            max_bet = human_player.chips
            self.bet_slider.setMaximum(max_bet)
            self.bet_spinbox.setMaximum(max_bet)
            
            # Set minimum raise
            min_raise = max(self.game.big_blind, self.game.current_bet - human_player.current_bet + self.game.min_raise)
            self.bet_slider.setMinimum(min_raise)
            self.bet_spinbox.setMinimum(min_raise)
    
    def fold_action(self):
        """Maneja la acción de retirarse"""
        if self.game.player_action(PlayerAction.FOLD):
            self.status_label.setText("Te has retirado.")
            self.update_display()
            self.update_action_buttons()
            self.check_bot_turn()
    
    def check_call_action(self):
        """Maneja la acción de pasar o igualar"""
        human_player = self.game.get_human_player()
        if not human_player:
            return
            
        if self.game.current_bet > human_player.current_bet:
            # Call
            if self.game.player_action(PlayerAction.CALL):
                call_amount = min(self.game.current_bet - human_player.current_bet, human_player.chips)
                self.status_label.setText(f"Has igualado con ${call_amount}.")
        else:
            # Check
            if self.game.player_action(PlayerAction.CHECK):
                self.status_label.setText("Has pasado.")
        
        self.update_display()
        self.update_action_buttons()
        self.check_bot_turn()
    
    def raise_action(self):
        """Maneja la acción de subir"""
        raise_amount = self.bet_spinbox.value()
        if self.game.player_action(PlayerAction.RAISE, raise_amount):
            self.status_label.setText(f"Has subido a ${raise_amount}.")
            self.update_display()
            self.update_action_buttons()
            self.check_bot_turn()
    
    def check_bot_turn(self):
        """Verifica si es el turno de un bot y programa su acción"""
        current_player = self.game.get_current_player()
        if current_player and not current_player.is_human and self.game.phase not in [GamePhase.FINISHED, GamePhase.SHOWDOWN]:
            self.bot_timer.start(2000)  # 2 second delay for bot action
    
    def handle_bot_action(self):
        """Maneja las acciones de los bots"""
        self.bot_timer.stop()
        
        current_player = self.game.get_current_player()
        if not current_player or current_player.is_human:
            return
        
        # Simple bot AI - random actions for now
        actions = []
        
        # Can always fold
        actions.append(PlayerAction.FOLD)
        
        # Can call if there's a bet to call
        if self.game.current_bet > current_player.current_bet and current_player.chips > 0:
            actions.append(PlayerAction.CALL)
        elif self.game.current_bet == current_player.current_bet:
            actions.append(PlayerAction.CHECK)
        
        # Can raise if has chips
        if current_player.chips > self.game.min_raise:
            actions.append(PlayerAction.RAISE)
        
        # Random decision with some basic logic
        chosen_action = random.choice(actions)
        
        # Simple logic: fold 30% of time, call/check 50%, raise 20%
        rand = random.random()
        if rand < 0.3:
            chosen_action = PlayerAction.FOLD
        elif rand < 0.8 and PlayerAction.CALL in actions:
            chosen_action = PlayerAction.CALL
        elif rand < 0.8 and PlayerAction.CHECK in actions:
            chosen_action = PlayerAction.CHECK
        elif PlayerAction.RAISE in actions:
            chosen_action = PlayerAction.RAISE
        
        # Execute action
        if chosen_action == PlayerAction.RAISE:
            raise_amount = min(current_player.chips, self.game.min_raise + random.randint(0, 50))
            self.game.player_action(chosen_action, raise_amount)
            self.status_label.setText(f"{current_player.name} sube a ${raise_amount}.")
        elif chosen_action == PlayerAction.CALL:
            self.game.player_action(chosen_action)
            self.status_label.setText(f"{current_player.name} iguala.")
        elif chosen_action == PlayerAction.CHECK:
            self.game.player_action(chosen_action)
            self.status_label.setText(f"{current_player.name} pasa.")
        else:  # FOLD
            self.game.player_action(chosen_action)
            self.status_label.setText(f"{current_player.name} se retira.")
        
        self.update_display()
        self.update_action_buttons()
        
        # Check if game phase advanced or another bot needs to act
        if self.game.phase == GamePhase.FINISHED:
            self.status_label.setText("Mano terminada. Haz clic en 'Nueva Mano' para continuar.")
        elif self.game.phase == GamePhase.SHOWDOWN:
            self.status_label.setText("¡Showdown! Mostrando cartas...")
        else:
            self.check_bot_turn()
    
    def load_card_image(self, card):
        """Crea un pixmap con la representación visual elegante de la carta con escalado responsive"""
        # Base card size that scales with window
        base_width = 80
        base_height = 120
        scale = self.get_scale_factor()
        card_width = max(40, int(base_width * scale))  # Minimum 40px width
        card_height = max(60, int(base_height * scale))  # Minimum 60px height
        
        pixmap = QPixmap(card_width, card_height)
        
        # Create gradient background
        gradient = QLinearGradient(0, 0, 0, card_height)
        gradient.setColorAt(0, QColor(248, 248, 248))
        gradient.setColorAt(1, QColor(230, 230, 230))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Fill background with gradient
        painter.fillRect(0, 0, card_width, card_height, QBrush(gradient))
        
        # Define color based on suit
        if card.suit in ['Corazones', 'Diamantes', 'Hearts', 'Diamonds']:
            color = QColor(220, 20, 60)  # Crimson red
        else:
            color = QColor(0, 0, 0)  # Black
        
        # Suit symbols mapping
        suit_symbols = {
            'Corazones': '♥', 'Hearts': '♥',
            'Diamantes': '♦', 'Diamonds': '♦',
            'Tréboles': '♣', 'Clubs': '♣',
            'Picas': '♠', 'Spades': '♠'
        }
        
        symbol = suit_symbols.get(card.suit, card.suit[0] if card.suit else '?')

        # Draw card border with subtle shadow (scaled)
        border_pen = QPen(QColor(180, 180, 180), max(1, int(2 * scale)))
        painter.setPen(border_pen)
        border_radius = max(4, int(8 * scale))
        painter.drawRoundedRect(1, 1, card_width-2, card_height-2, border_radius, border_radius)

        # Set color for card content
        painter.setPen(QPen(color, max(1, int(2 * scale))))

        # Responsive font sizes
        corner_font_size = max(8, int(10 * scale))
        large_font_size = max(12, int(16 * scale))
        symbol_font_size = max(16, int(24 * scale))
        small_symbol_size = max(6, int(8 * scale))

        # Draw value in top-left corner
        font_corner = QFont("Arial", corner_font_size, QFont.Weight.Bold)
        painter.setFont(font_corner)
        margin_x = max(3, int(6 * scale))
        margin_y = max(12, int(18 * scale))
        painter.drawText(margin_x, margin_y, card.value)

        # Draw suit symbol in top-left
        font_suit_small = QFont("Arial", small_symbol_size, QFont.Weight.Bold)
        painter.setFont(font_suit_small)
        painter.drawText(margin_x, margin_y + max(10, int(14 * scale)), symbol)

        # Draw large value in center
        font_large = QFont("Arial", large_font_size, QFont.Weight.Bold)
        painter.setFont(font_large)
        fm = QFontMetrics(font_large)
        value_width = fm.horizontalAdvance(card.value)
        center_y = int(card_height * 0.54)
        painter.drawText(card_width // 2 - value_width // 2, center_y, card.value)

        # Draw large suit symbol in center
        font_symbol_large = QFont("Arial", symbol_font_size, QFont.Weight.Bold)
        painter.setFont(font_symbol_large)
        fm_symbol = QFontMetrics(font_symbol_large)
        symbol_width = fm_symbol.horizontalAdvance(symbol)
        symbol_y = int(card_height * 0.75)
        painter.drawText(card_width // 2 - symbol_width // 2, symbol_y, symbol)

        # Draw value and suit in bottom-right corner (rotated)
        painter.save()
        bottom_x = card_width - margin_x - max(8, int(12 * scale))
        bottom_y = card_height - margin_x - max(8, int(12 * scale))
        painter.translate(bottom_x, bottom_y)
        painter.rotate(180)
        painter.setFont(font_corner)
        painter.drawText(0, max(10, int(14 * scale)), card.value)
        painter.setFont(font_suit_small)
        painter.drawText(0, max(20, int(28 * scale)), symbol)
        painter.restore()
        
        painter.end()
        return pixmap

def main():
    app = QApplication(sys.argv)
    window = PokerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()