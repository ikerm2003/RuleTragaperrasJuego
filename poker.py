from typing import Any
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QSlider, QSpinBox, QGridLayout, QFrame, QMessageBox)
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor, QPalette
from PyQt6.QtCore import Qt, QTimer

import sys
import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional

from cardCommon import PokerDeck
    
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
    hand: List = None #type:ignore
    current_bet: int = 0
    total_bet_in_hand: int = 0
    is_active: bool = True
    is_folded: bool = False
    is_all_in: bool = False
    is_human: bool = False
    
    def __post_init__(self):
        if self.hand is None:
            self.hand = [] #type:ignore
    
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
        self.winner: Optional[Player] = None  # Para almacenar el ganador de la mano
        
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
        
        # Small blind
        sb_player = self.players[sb_pos]
        sb_amount = min(self.small_blind, sb_player.chips)
        sb_player.chips -= sb_amount
        sb_player.current_bet = sb_amount
        sb_player.total_bet_in_hand = sb_amount
        self.pot += sb_amount
        
        # Big blind
        bb_player = self.players[bb_pos]
        bb_amount = min(self.big_blind, bb_player.chips)
        bb_player.chips -= bb_amount
        bb_player.current_bet = bb_amount
        bb_player.total_bet_in_hand = bb_amount
        self.pot += bb_amount
        
        self.current_bet = bb_amount
    
    def deal_flop(self):
        """Reparte el flop (3 cartas comunitarias)"""
        if self.phase == GamePhase.PRE_FLOP:
            self.community_cards.extend(self.deck.deal(3))
            self.phase = GamePhase.FLOP
            self._reset_betting_round()
    
    def deal_turn(self):
        """Reparte el turn (4ta carta comunitaria)"""
        if self.phase == GamePhase.FLOP:
            self.community_cards.extend(self.deck.deal(1))
            self.phase = GamePhase.TURN
            self._reset_betting_round()
    
    def deal_river(self):
        """Reparte el river (5ta carta comunitaria)"""
        if self.phase == GamePhase.TURN:
            self.community_cards.extend(self.deck.deal(1))
            self.phase = GamePhase.RIVER
            self._reset_betting_round()
    
    def _reset_betting_round(self):
        """Reinicia la ronda de apuestas"""
        for player in self.players:
            player.current_bet = 0
        self.current_bet = 0
        self.current_player = (self.dealer_position + 1) % len(self.players)
        while not self.players[self.current_player].can_act():
            self.current_player = (self.current_player + 1) % len(self.players)
    
    def player_action(self, action: PlayerAction, amount: int = 0) -> bool:
        """Procesa la acción de un jugador"""
        if not self.players[self.current_player].can_act():
            return False
        
        player = self.players[self.current_player]
        
        if action == PlayerAction.FOLD:
            player.is_folded = True
            player.is_active = False
        
        elif action == PlayerAction.CALL:
            call_amount = min(self.current_bet - player.current_bet, player.chips)
            player.chips -= call_amount
            player.current_bet += call_amount
            player.total_bet_in_hand += call_amount
            self.pot += call_amount
            
            if player.chips == 0:
                player.is_all_in = True
        
        elif action == PlayerAction.RAISE:
            total_bet = self.current_bet + amount
            if total_bet > player.current_bet + player.chips:
                # All-in
                amount = player.chips
                player.is_all_in = True
            
            bet_increase = total_bet - player.current_bet
            player.chips -= bet_increase
            player.current_bet = total_bet
            player.total_bet_in_hand += bet_increase
            self.pot += bet_increase
            self.current_bet = total_bet
            
            if player.chips == 0:
                player.is_all_in = True
        
        elif action == PlayerAction.CHECK:
            if player.current_bet < self.current_bet:
                return False  # Can't check when there's a bet to call
        
        # Move to next player
        self._next_player()
        return True
    
    def _next_player(self):
        """Avanza al siguiente jugador activo"""
        initial_player = self.current_player
        self.current_player = (self.current_player + 1) % len(self.players)
        
        while not self.players[self.current_player].can_act():
            self.current_player = (self.current_player + 1) % len(self.players)
            if self.current_player == initial_player:
                break  # Everyone has acted
        
        # Check if betting round is over
        if self._is_betting_round_over():
            self._advance_phase()
    
    def _is_betting_round_over(self) -> bool:
        """Verifica si la ronda de apuestas ha terminado"""
        active_players = [p for p in self.players if p.can_act()]
        if len(active_players) <= 1:
            return True
        
        # Check if all active players have matched the current bet
        return all(p.current_bet == self.current_bet or p.is_all_in 
                  for p in self.players if not p.is_folded)
    
    def _advance_phase(self):
        """Avanza a la siguiente fase del juego"""
        if self.phase == GamePhase.PRE_FLOP:
            self.deal_flop()
        elif self.phase == GamePhase.FLOP:
            self.deal_turn()
        elif self.phase == GamePhase.TURN:
            self.deal_river()
        elif self.phase == GamePhase.RIVER:
            self.phase = GamePhase.SHOWDOWN
            self._showdown()
    
    def _showdown(self):
        """Determina el ganador y distribuye el pot"""
        active_players = [p for p in self.players if not p.is_folded]
        if not active_players:
            self.phase = GamePhase.FINISHED
            return
        # Guardar el pot antes de distribuirlo
        pot_amount = self.pot
        if len(active_players) == 1:
            # Solo un jugador activo
            winner = active_players[0]
            winner.chips += self.pot
            self.winner = winner
        else:
            # Evaluar manos para determinar ganador
            # Por simplicidad, elegimos al primer jugador activo
            # En una implementación real evaluarías las manos usando Puntuation
            winner = active_players[0]
            winner.chips += self.pot
            self.winner = winner
        
        # Guardar información del pot ganado
        self._last_pot = pot_amount
        self.pot = 0
        self.phase = GamePhase.FINISHED
        
        # Advance dealer button
        self.dealer_position = (self.dealer_position + 1) % len(self.players)

    def get_current_player(self) -> Optional[Player]:
        """Obtiene el jugador actual"""
        if 0 <= self.current_player < len(self.players):
            return self.players[self.current_player]
        return None
    
    def get_human_player(self) -> Optional[Player]:
        """Obtiene el jugador humano"""
        for player in self.players:
            if player.is_human:
                return player
        return None
    
class Puntuation:
    def __init__(self, player_hand, community_cards):
        self.player_hand = player_hand
        self.community_cards = community_cards
        self.all_cards = player_hand + community_cards
        self.rankings = {
            "High Card": 1,
            "One Pair": 2,
            "Two Pair": 3,
            "Three of a Kind": 4,
            "Straight": 5,
            "Flush": 6,
            "Full House": 7,
            "Four of a Kind": 8,
            "Straight Flush": 9,
            "Royal Flush": 10
        }
        if self.check_hand(self.all_cards):
            self.rank_hand = self.evaluate_hand(self.all_cards)
        else:
            raise ValueError("Invalid hand: duplicate cards detected.")

    def check_hand(self, cards):
        # Se comprueba que la mano del jugador y las cartas comunitarias formen una mano válida de póker
        # No puede haber cartas repetidas, mismas cartas en la mano del jugador y en las comunitarias, etc.
        seen = set()
        for card in cards:
            if card in seen:
                return False
            seen.add(card)
        return True

    def evaluate_hand(self, cards):
        # Ordenar cartas por valor para facilitar detección de escaleras
        numeric_values = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, 
                         '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}
        
        values = [card.value for card in cards]
        suits = [card.suit for card in cards]
        value_counts = {value: values.count(value) for value in set(values)}
        suit_counts = {suit: suits.count(suit) for suit in set(suits)}
        
        # Verificar escalera
        def is_straight(values):
            nums = sorted([numeric_values[v] for v in values])
            for i in range(len(nums) - 4):
                if nums[i+4] - nums[i] == 4 and len(set(nums[i:i+5])) == 5:
                    return True
            return False
        
        # Verificar color
        is_flush = 5 in suit_counts.values()
        is_straight_hand = is_straight(values)
        
        # Evaluar mano en orden de mayor a menor
        if is_straight_hand and is_flush:
            if all(v in values for v in ['10', 'J', 'Q', 'K', 'A']):
                return self.rankings["Royal Flush"]
            return self.rankings["Straight Flush"]
        elif 4 in value_counts.values():
            return self.rankings["Four of a Kind"]
        elif 3 in value_counts.values() and 2 in value_counts.values():
            return self.rankings["Full House"]
        elif is_flush:
            return self.rankings["Flush"]
        elif is_straight_hand:
            return self.rankings["Straight"]
        elif 3 in value_counts.values():
            return self.rankings["Three of a Kind"]
        elif list(value_counts.values()).count(2) == 2:
            return self.rankings["Two Pair"]
        elif 2 in value_counts.values():
            return self.rankings["One Pair"]
        else:
            return self.rankings["High Card"]


class PlayerDisplayFrame(QFrame):
    """Custom QFrame that can store player display elements"""
    def __init__(self):
        super().__init__()
        self.name_label: Optional[QLabel] = None
        self.chips_label: Optional[QLabel] = None
        self.bet_label: Optional[QLabel] = None
        self.total_bet_label: Optional[QLabel] = None
        self.card_labels: List[QLabel] = []
        self.crown_label: Optional[QLabel] = None


class PokerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Texas Hold'em Poker")
        self.setGeometry(50, 50, 1400, 900)  # Ventana más grande para mejor visualización
        
        # Initialize game with 4 players
        self.game = PokerGame(num_players=4, small_blind=10, big_blind=20)
        
        # UI elements
        self.community_card_labels = []
        self.player_displays = []
        self.action_buttons = []
        
        # Timer for bot actions
        self.bot_timer = QTimer()
        self.bot_timer.timeout.connect(self.handle_bot_action)
        
        self.init_ui()
        self.start_new_game()
        
    def init_ui(self):
        # Set main widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Game info section
        info_layout = QHBoxLayout()
        
        self.pot_label = QLabel("Pot: $0")
        self.pot_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.pot_label.setStyleSheet("color: white; background-color: #2d5a27; padding: 10px; border-radius: 5px;")
        
        self.phase_label = QLabel("Fase: Esperando")
        self.phase_label.setFont(QFont("Arial", 12))
        self.phase_label.setStyleSheet("color: white; background-color: #2d5a27; padding: 8px; border-radius: 5px;")
        
        self.current_player_label = QLabel("Turno: -")
        self.current_player_label.setFont(QFont("Arial", 12))
        self.current_player_label.setStyleSheet("color: white; background-color: #8B4513; padding: 8px; border-radius: 5px;")
        
        info_layout.addWidget(self.pot_label)
        info_layout.addWidget(self.phase_label)
        info_layout.addWidget(self.current_player_label)
        info_layout.addStretch()
        
        main_layout.addLayout(info_layout)
        
        # Main game area
        game_widget = QFrame()
        game_widget.setStyleSheet("""
            QFrame {
                background-color: #0e5c2f;
                border: 3px solid #8B4513;
                border-radius: 15px;
                margin: 10px;
            }
        """)
        game_widget.setFixedHeight(600)  # Más alto para acomodar mejor los elementos
        main_layout.addWidget(game_widget)
        
        game_layout = QGridLayout(game_widget)
        game_layout.setSpacing(20)  # Mejor espaciado entre elementos
        
        # Players positions (4 players around the table)
        player_positions = [
            (2, 1),  # Human player (bottom)
            (1, 0),  # Bot 1 (left)
            (0, 1),  # Bot 2 (top)
            (1, 2),  # Bot 3 (right)
        ]
        
        # Create player displays
        for i, pos in enumerate(player_positions):
            player_frame = self.create_player_display(i)
            self.player_displays.append(player_frame)
            game_layout.addWidget(player_frame, pos[0], pos[1], Qt.AlignmentFlag.AlignCenter)
        
        # Community cards in center
        community_frame = QFrame()
        community_frame.setStyleSheet("background-color: rgba(255,255,255,0.1); border-radius: 10px;")
        community_layout = QHBoxLayout(community_frame)
        
        for i in range(5):
            card_label = QLabel()
            card_label.setFixedSize(80, 120)  # Cartas más grandes
            card_label.setStyleSheet("""
                border: 3px solid #FFD700;
                background-color: white;
                border-radius: 10px;
                margin: 5px;
                font-size: 14px;
                font-weight: bold;
            """)
            card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_label.setText("?")
            self.community_card_labels.append(card_label)
            community_layout.addWidget(card_label)
        
        game_layout.addWidget(community_frame, 1, 1, Qt.AlignmentFlag.AlignCenter)
        
        # Status label
        self.status_label = QLabel("¡Bienvenido al Texas Hold'em! Haz clic en 'Nueva Mano' para empezar.")
        self.status_label.setStyleSheet("background-color: #f0f0f0; padding: 8px; border-radius: 5px;")
        main_layout.addWidget(self.status_label)
        
        # Create action panel
        self.create_action_panel(main_layout)
    
    def create_player_display(self, player_index: int) -> PlayerDisplayFrame:
        """Crea la visualización de un jugador"""
        player = self.game.players[player_index]
        
        frame = PlayerDisplayFrame()
        frame.setFixedSize(220, 160)  # Más grande para mejor legibilidad
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(139, 69, 19, 0.9);
                border: 2px solid #8B4513;
                border-radius: 12px;
                color: white;
                padding: 5px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(4)  # Mejor espaciado
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Crown (inicialmente oculto)
        crown_label = QLabel("👑")
        crown_label.setFont(QFont("Arial", 16))
        crown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        crown_label.setStyleSheet("color: gold;")
        crown_label.hide()  # Oculto por defecto
        
        # Player name and chips
        name_label = QLabel(player.name)
        name_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("color: white; font-weight: bold;")
        
        chips_label = QLabel(f"Fichas: ${player.chips}")
        chips_label.setFont(QFont("Arial", 9))
        chips_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chips_label.setStyleSheet("color: lightgreen; font-weight: bold;")
        
        # Cards area
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(5)
        card_labels = []
        for i in range(2):
            card_label = QLabel()
            card_label.setFixedSize(45, 65)  # Cartas más grandes
            card_label.setStyleSheet("""
                border: 2px solid white;
                background-color: navy;
                border-radius: 6px;
                margin: 2px;
                color: white;
                font-size: 10px;
                font-weight: bold;
            """)
            card_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            card_label.setText("?")
            cards_layout.addWidget(card_label)
            card_labels.append(card_label)
        
        # Bet info mejorada
        bet_label = QLabel("Apuesta: $0")
        bet_label.setFont(QFont("Arial", 9))
        bet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bet_label.setStyleSheet("color: yellow; font-weight: bold; background-color: rgba(0,0,0,0.3); padding: 2px; border-radius: 3px;")
        
        # Total apostado en la mano
        total_bet_label = QLabel("Total: $0")
        total_bet_label.setFont(QFont("Arial", 9))
        total_bet_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        total_bet_label.setStyleSheet("color: cyan; font-weight: bold; background-color: rgba(0,0,0,0.3); padding: 2px; border-radius: 3px;")
        
        layout.addWidget(crown_label)
        layout.addWidget(name_label)
        layout.addWidget(chips_label)
        layout.addLayout(cards_layout)
        layout.addWidget(bet_label)
        layout.addWidget(total_bet_label)
        
        # Store references to labels for updating
        frame.name_label = name_label
        frame.chips_label = chips_label
        frame.bet_label = bet_label
        frame.total_bet_label = total_bet_label
        frame.card_labels = card_labels
        frame.crown_label = crown_label
        
        return frame
    
    def create_action_panel(self, main_layout):
        """Crea el panel de acciones para el jugador humano"""
        action_frame = QFrame()
        action_frame.setStyleSheet("""
            QFrame {
                background-color: #2d5a27;
                border: 2px solid #4a7c59;
                border-radius: 10px;
                padding: 10px;
                margin: 5px;
            }
        """)
        action_layout = QVBoxLayout(action_frame)
        
        # Betting controls
        bet_layout = QHBoxLayout()
        
        bet_layout.addWidget(QLabel("Apostar:"))
        
        self.bet_slider = QSlider(Qt.Orientation.Horizontal)
        self.bet_slider.setMinimum(0)
        self.bet_slider.setMaximum(1000)
        self.bet_slider.setValue(20)
        self.bet_slider.valueChanged.connect(self.update_bet_spinbox)
        
        self.bet_spinbox = QSpinBox()
        self.bet_spinbox.setMinimum(0)
        self.bet_spinbox.setMaximum(10000)
        self.bet_spinbox.setValue(20)
        self.bet_spinbox.valueChanged.connect(self.update_bet_slider)
        
        bet_layout.addWidget(self.bet_slider)
        bet_layout.addWidget(self.bet_spinbox)
        
        action_layout.addLayout(bet_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.fold_button = QPushButton("Retirarse")
        self.fold_button.setStyleSheet(self.get_button_style("#d32f2f"))
        self.fold_button.clicked.connect(self.fold_action)
        
        self.check_call_button = QPushButton("Igualar")
        self.check_call_button.setStyleSheet(self.get_button_style("#388e3c"))
        self.check_call_button.clicked.connect(self.check_call_action)
        
        self.raise_button = QPushButton("Subir")
        self.raise_button.setStyleSheet(self.get_button_style("#f57c00"))
        self.raise_button.clicked.connect(self.raise_action)
        
        self.new_hand_button = QPushButton("Nueva Mano")
        self.new_hand_button.setStyleSheet(self.get_button_style("#1976d2"))
        self.new_hand_button.clicked.connect(self.start_new_game)
        
        button_layout.addWidget(self.fold_button)
        button_layout.addWidget(self.check_call_button)
        button_layout.addWidget(self.raise_button)
        button_layout.addWidget(self.new_hand_button)
        
        action_layout.addLayout(button_layout)
        main_layout.addWidget(action_frame)
    
    def get_button_style(self, color: str) -> str:
        """Obtiene el estilo CSS para un botón"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {color}dd;
            }}
            QPushButton:pressed {{
                background-color: {color}bb;
            }}
            QPushButton:disabled {{
                background-color: #666666;
                color: #999999;
            }}
        """
    def update_bet_slider(self, value):
        """Actualiza el slider cuando cambia el spinbox"""
        self.bet_slider.setValue(value)
    
    def update_bet_spinbox(self, value):
        """Actualiza el spinbox cuando cambia el slider"""
        self.bet_spinbox.setValue(value)
    
    def start_new_game(self):
        """Inicia una nueva mano"""
        self.game.winner = None  # Reset winner
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
            if i < len(self.game.community_cards):
                pixmap = self.load_card_image(self.game.community_cards[i])
                card_label.setPixmap(pixmap.scaled(80, 120, Qt.AspectRatioMode.KeepAspectRatio))
                card_label.setText("")  # Limpiar texto cuando hay imagen
                card_label.setStyleSheet("""
                    border: 3px solid #FFD700;
                    background-color: white;
                    border-radius: 10px;
                    margin: 5px;
                """)
            else:
                card_label.clear()
                card_label.setText("?")
                card_label.setStyleSheet("""
                    border: 3px solid #FFD700;
                    background-color: white;
                    border-radius: 10px;
                    margin: 5px;
                    font-size: 14px;
                    font-weight: bold;
                    color: black;
                """)
        
        # Update player displays
        for i, player_frame in enumerate(self.player_displays):
            player = self.game.players[i]
            
            # Update chips and bet info
            player_frame.chips_label.setText(f"Fichas: ${player.chips}")
            player_frame.bet_label.setText(f"Apuesta: ${player.current_bet}")
            player_frame.total_bet_label.setText(f"Total: ${player.total_bet_in_hand}")
            
            # Mostrar corona si es el ganador
            if self.game.winner and player == self.game.winner and self.game.phase == GamePhase.FINISHED:
                player_frame.crown_label.show()
            else:
                player_frame.crown_label.hide()
            
            # Update card visibility
            show_cards = False
            if player.is_human:
                show_cards = True  # Siempre mostrar cartas del jugador humano
            elif player.is_folded or self.game.phase == GamePhase.FINISHED:
                show_cards = True  # Mostrar cartas si se retiró o terminó el juego
            
            if show_cards and player.hand:
                # Show player's cards
                for j, card_label in enumerate(player_frame.card_labels):
                    if j < len(player.hand):
                        pixmap = self.load_card_image(player.hand[j])
                        card_label.setPixmap(pixmap.scaled(45, 65, Qt.AspectRatioMode.KeepAspectRatio))
                        card_label.setText("")  # Limpiar texto cuando hay imagen
                        card_label.setStyleSheet("""
                            border: 2px solid white;
                            background-color: white;
                            border-radius: 6px;
                            margin: 2px;
                        """)
                        card_label.show()  # Asegurar que esté visible
                    else:
                        # Ocultar labels de cartas que no existen
                        card_label.clear()
                        card_label.hide()
            else:
                # Hide cards (show back of cards)
                for j, card_label in enumerate(player_frame.card_labels):
                    card_label.clear()
                    if player.hand and j < len(player.hand):
                        # Mostrar reverso de carta solo si la carta existe
                        card_label.setText("?")
                        card_label.setStyleSheet("""
                            border: 2px solid white;
                            background-color: navy;
                            border-radius: 6px;
                            margin: 2px;
                            color: white;
                            font-size: 12px;
                            font-weight: bold;
                        """)
                        card_label.show()
                    else:
                        # Ocultar completamente labels innecesarios
                        card_label.hide()

        # Highlight current player
        if current_player and i == self.game.current_player and not player.is_folded:
            player_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 215, 0, 0.9);
                    border: 4px solid #FFD700;
                    border-radius: 12px;
                    color: black;
                    padding: 5px;
                    }
                """)
        # Show folded players differently
        elif player.is_folded:
            player_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(100, 100, 100, 0.7);
                    border: 2px solid #666666;
                    border-radius: 12px;
                    color: #cccccc;
                    padding: 5px;
                    }
                """)
        # Show winner with golden border
        elif self.game.winner and player == self.game.winner and self.game.phase == GamePhase.FINISHED:
            player_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 215, 0, 0.95);
                border: 5px solid gold;
                border-radius: 12px;
                color: black;
                padding: 5px;
                font-weight: bold;
                }
            """)
        else:
            player_frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(139, 69, 19, 0.9);
                    border: 2px solid #8B4513;
                    border-radius: 12px;
                    color: white;
                    padding: 5px;
                }
                """)
        # Mostrar mensaje de ganador si la partida terminó
        if self.game.phase == GamePhase.FINISHED and self.game.winner:
            self.show_winner_message()

    def show_winner_message(self):
        """Muestra un mensaje emergente con el ganador"""
        if self.game.winner:
            winner_name = self.game.winner.name
            pot_won = getattr(self.game, '_last_pot', 0)
            
            msg = QMessageBox()
            msg.setWindowTitle("¡Partida Terminada!")
            msg.setText(f"🎉 ¡{winner_name} ha ganado la mano! 🎉")
            msg.setInformativeText(f"Ganó ${pot_won} fichas")
            msg.setIcon(QMessageBox.Icon.Information)
            msg.setStandardButtons(QMessageBox.StandardButton.Ok)
            msg.exec()
    
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
            # No mostrar mensaje aquí porque update_display ya lo hace
        elif self.game.phase == GamePhase.SHOWDOWN:
            self.status_label.setText("¡Showdown! Mostrando cartas...")
        else:
            self.check_bot_turn()
    
    def load_card_image(self, card):
        """Crea un pixmap con la representación visual de la carta"""
        pixmap = QPixmap(120, 180)  # Cartas más grandes
        pixmap.fill(QColor("white"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Definir color según el palo
        if card.suit in ['Corazones', 'Diamantes']:
            color = QColor("red")
        else:
            color = QColor("black")
        
        painter.setPen(color)
        
        # Fuente para el valor - más grande
        font = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Dibujar el valor en la esquina superior izquierda
        painter.drawText(8, 25, card.value)
        
        # Fuente más pequeña para el símbolo del palo
        font_small = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font_small)
        
        # Símbolos de los palos
        suit_symbols = {
            'Corazones': '♥',
            'Diamantes': '♦',
            'Tréboles': '♣',
            'Picas': '♠'
        }
        
        # Dibujar símbolo del palo
        symbol = suit_symbols.get(card.suit, card.suit)
        painter.drawText(8, 45, symbol)
        
        # Dibujar valor y símbolo más grandes en el centro
        font_center = QFont("Arial", 20, QFont.Weight.Bold)
        painter.setFont(font_center)
        painter.drawText(45, 95, f"{card.value}")
        
        font_center_symbol = QFont("Arial", 28, QFont.Weight.Bold)
        painter.setFont(font_center_symbol)
        painter.drawText(45, 125, symbol)
        
        # Valor y símbolo rotados en la esquina inferior derecha
        painter.save()
        painter.translate(112, 155)
        painter.rotate(180)
        font_small_rotated = QFont("Arial", 12, QFont.Weight.Bold)
        painter.setFont(font_small_rotated)
        painter.drawText(0, 0, card.value)
        painter.drawText(0, 15, symbol)
        painter.restore()
        
        # Dibujar borde limpio
        painter.setPen(QColor("black"))
        painter.drawRect(0, 0, 119, 179)
        
        painter.end()
        return pixmap

def main():
    app = QApplication(sys.argv)
    window = PokerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()