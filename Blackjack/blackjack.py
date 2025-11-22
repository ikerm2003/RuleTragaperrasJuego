from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox, QMessageBox
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor
from PyQt6.QtCore import Qt

import sys
import os
import random
from typing import List, Tuple, Optional
from enum import Enum

import sys
from pathlib import Path

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from ..cardCommon import BaseCard, BaseDeck


class BlackjackCard(BaseCard):
    """Carta específica para Blackjack con valores estándar"""
    
    BLACKJACK_VALUES = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    BLACKJACK_SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    
    def __init__(self, value, suit):
        if value not in self.BLACKJACK_VALUES:
            raise ValueError(f"Valor inválido: {value}")
        if suit not in self.BLACKJACK_SUITS:
            raise ValueError(f"Palo inválido: {suit}")
        super().__init__(value, suit)
    
    def get_numeric_value(self) -> int:
        """Devuelve el valor numérico básico de la carta para Blackjack"""
        if self.value in ['J', 'Q', 'K']:
            return 10
        elif self.value == 'A':
            return 11  # Aces default to 11, adjusted later if needed
        else:
            return int(self.value)
    
    def is_ace(self) -> bool:
        """Verifica si la carta es un As"""
        return self.value == 'A'


class BlackjackDeck(BaseDeck):
    """Baraja estándar de 52 cartas para Blackjack"""

    def _create_deck(self) -> list:
        """Crea una baraja completa de Blackjack"""
        self.cards = []
        for suit in BlackjackCard.BLACKJACK_SUITS:
            for value in BlackjackCard.BLACKJACK_VALUES:
                self.cards.append(BlackjackCard(value, suit))
        return self.cards


class GameState(Enum):
    """Estados del juego de Blackjack"""
    BETTING = "betting"
    DEALING = "dealing"
    PLAYER_TURN = "player_turn"
    DEALER_TURN = "dealer_turn"
    GAME_OVER = "game_over"


class BlackjackGame:
    """Lógica completa del juego de Blackjack"""
    
    def __init__(self, initial_balance: int = 1000):
        self.deck = BlackjackDeck()
        self.deck.shuffle()
        
        self.player_hand: List[BlackjackCard] = []
        self.dealer_hand: List[BlackjackCard] = []
        
        self.balance = initial_balance
        self.current_bet = 0
        self.state = GameState.BETTING
        
        self.player_stood = False
        self.insurance_bet = 0
    
    def calculate_hand_value(self, hand: List[BlackjackCard]) -> int:
        """Calcula el valor de una mano, ajustando Ases si es necesario"""
        value = sum(card.get_numeric_value() for card in hand)
        aces = sum(1 for card in hand if card.is_ace())
        
        # Ajustar Ases de 11 a 1 si la mano se pasa de 21
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    def is_blackjack(self, hand: List[BlackjackCard]) -> bool:
        """Verifica si una mano es Blackjack (21 con 2 cartas)"""
        return len(hand) == 2 and self.calculate_hand_value(hand) == 21
    
    def can_double(self) -> bool:
        """Verifica si el jugador puede doblar"""
        return len(self.player_hand) == 2 and self.balance >= self.current_bet
    
    def can_split(self) -> bool:
        """Verifica si el jugador puede dividir (no implementado aún en UI)"""
        return (len(self.player_hand) == 2 and 
                self.player_hand[0].value == self.player_hand[1].value and
                self.balance >= self.current_bet)
    
    def can_take_insurance(self) -> bool:
        """Verifica si el jugador puede tomar seguro"""
        return (len(self.dealer_hand) == 2 and 
                self.dealer_hand[0].is_ace() and 
                self.balance >= self.current_bet // 2)
    
    def place_bet(self, amount: int) -> bool:
        """Coloca una apuesta"""
        if amount <= 0 or amount > self.balance:
            return False
        self.current_bet = amount
        self.balance -= amount
        self.state = GameState.DEALING
        return True
    
    def start_new_hand(self):
        """Inicia una nueva mano"""
        if len(self.deck) < 20:  # Rebarajar si quedan pocas cartas
            self.deck = BlackjackDeck()
            self.deck.shuffle()
        
        self.player_hand = []
        self.dealer_hand = []
        self.player_stood = False
        self.insurance_bet = 0
        
        # Repartir cartas iniciales
        self.player_hand.append(self.deck.deal(1)[0])
        self.dealer_hand.append(self.deck.deal(1)[0])
        self.player_hand.append(self.deck.deal(1)[0])
        self.dealer_hand.append(self.deck.deal(1)[0])
        
        self.state = GameState.PLAYER_TURN
        
        # Verificar Blackjack
        if self.is_blackjack(self.player_hand):
            self.state = GameState.DEALER_TURN
            self.resolve_hand()
    
    def hit(self) -> bool:
        """El jugador pide una carta"""
        if self.state != GameState.PLAYER_TURN:
            return False
        
        self.player_hand.append(self.deck.deal(1)[0])
        
        if self.calculate_hand_value(self.player_hand) > 21:
            self.state = GameState.GAME_OVER
            self.resolve_hand()
        
        return True
    
    def stand(self) -> bool:
        """El jugador se planta"""
        if self.state != GameState.PLAYER_TURN:
            return False
        
        self.player_stood = True
        self.state = GameState.DEALER_TURN
        self.dealer_play()
        return True
    
    def double_down(self) -> bool:
        """El jugador dobla su apuesta"""
        if not self.can_double():
            return False
        
        self.balance -= self.current_bet
        self.current_bet *= 2
        self.player_hand.append(self.deck.deal(1)[0])
        
        if self.calculate_hand_value(self.player_hand) > 21:
            self.state = GameState.GAME_OVER
            self.resolve_hand()
        else:
            self.player_stood = True
            self.state = GameState.DEALER_TURN
            self.dealer_play()
        
        return True
    
    def dealer_play(self):
        """El dealer juega su mano"""
        self.state = GameState.DEALER_TURN
        
        # El dealer debe pedir hasta llegar a 17 o más
        while self.calculate_hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.deal(1)[0])
        
        self.state = GameState.GAME_OVER
        self.resolve_hand()
    
    def resolve_hand(self) -> Tuple[str, int]:
        """Resuelve la mano y determina el ganador"""
        player_value = self.calculate_hand_value(self.player_hand)
        dealer_value = self.calculate_hand_value(self.dealer_hand)
        
        player_blackjack = self.is_blackjack(self.player_hand)
        dealer_blackjack = self.is_blackjack(self.dealer_hand)
        
        # Determinar resultado
        if player_value > 21:
            result = "¡Te pasaste! Dealer gana."
            winnings = 0
        elif dealer_value > 21:
            result = "¡Dealer se pasó! Ganaste."
            winnings = self.current_bet * 2
        elif player_blackjack and not dealer_blackjack:
            result = "¡BLACKJACK! Ganaste."
            winnings = int(self.current_bet * 2.5)
        elif dealer_blackjack and not player_blackjack:
            result = "Dealer tiene Blackjack. Perdiste."
            winnings = 0
        elif player_blackjack and dealer_blackjack:
            result = "Empate - Ambos tienen Blackjack."
            winnings = self.current_bet
        elif player_value > dealer_value:
            result = f"Ganaste con {player_value} vs {dealer_value}."
            winnings = self.current_bet * 2
        elif dealer_value > player_value:
            result = f"Dealer gana con {dealer_value} vs {player_value}."
            winnings = 0
        else:
            result = f"Empate con {player_value}."
            winnings = self.current_bet
        
        self.balance += winnings
        self.state = GameState.BETTING
        
        return result, winnings    


class BlackJackWindow(QMainWindow):
    """Ventana principal del juego de Blackjack"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.game = BlackjackGame(initial_balance=1000)
        self.parent_window = parent
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Blackjack - Casino")
        self.setGeometry(100, 100, 900, 700)

        # Widget principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        
        # Balance display
        balance_layout = QHBoxLayout()
        self.balance_label = QLabel(f"Balance: ${self.game.balance}")
        self.balance_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.balance_label.setStyleSheet("color: gold;")
        balance_layout.addWidget(self.balance_label)
        balance_layout.addStretch()
        main_layout.addLayout(balance_layout)

        # Dealer section
        dealer_label = QLabel("DEALER")
        dealer_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        dealer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(dealer_label)
        
        # Cartas del dealer
        self.dealer_card_labels = []
        dealer_cards_layout = QHBoxLayout()
        dealer_cards_layout.addStretch()
        for _ in range(7):  # Max 7 cards in most scenarios
            card_label = QLabel()
            card_label.setFixedSize(80, 120)
            card_label.setStyleSheet("border: 2px solid #333; background-color: white; border-radius: 5px;")
            card_label.hide()
            self.dealer_card_labels.append(card_label)
            dealer_cards_layout.addWidget(card_label)
        dealer_cards_layout.addStretch()
        main_layout.addLayout(dealer_cards_layout)
        
        self.dealer_value_label = QLabel("")
        self.dealer_value_label.setFont(QFont("Arial", 12))
        self.dealer_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.dealer_value_label)

        # Spacer
        main_layout.addSpacing(30)
        
        # Player section
        player_label = QLabel("PLAYER")
        player_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(player_label)
        
        # Cartas del jugador
        self.player_card_labels = []
        player_cards_layout = QHBoxLayout()
        player_cards_layout.addStretch()
        for _ in range(7):
            card_label = QLabel()
            card_label.setFixedSize(80, 120)
            card_label.setStyleSheet("border: 2px solid #333; background-color: white; border-radius: 5px;")
            card_label.hide()
            self.player_card_labels.append(card_label)
            player_cards_layout.addWidget(card_label)
        player_cards_layout.addStretch()
        main_layout.addLayout(player_cards_layout)
        
        self.player_value_label = QLabel("")
        self.player_value_label.setFont(QFont("Arial", 12))
        self.player_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.player_value_label)

        # Betting section
        bet_layout = QHBoxLayout()
        bet_label = QLabel("Apuesta:")
        bet_label.setFont(QFont("Arial", 12))
        self.bet_spinbox = QSpinBox()
        self.bet_spinbox.setMinimum(10)
        self.bet_spinbox.setMaximum(1000)
        self.bet_spinbox.setValue(50)
        self.bet_spinbox.setSingleStep(10)
        self.bet_spinbox.setPrefix("$")
        
        self.deal_button = QPushButton("Repartir")
        self.deal_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.deal_button.clicked.connect(self.deal_cards)
        
        bet_layout.addStretch()
        bet_layout.addWidget(bet_label)
        bet_layout.addWidget(self.bet_spinbox)
        bet_layout.addWidget(self.deal_button)
        bet_layout.addStretch()
        main_layout.addLayout(bet_layout)

        # Action buttons
        self.action_layout = QHBoxLayout()
        self.hit_button = QPushButton("Pedir")
        self.stand_button = QPushButton("Plantarse")
        self.double_button = QPushButton("Doblar")
        
        self.hit_button.setFont(QFont("Arial", 12))
        self.stand_button.setFont(QFont("Arial", 12))
        self.double_button.setFont(QFont("Arial", 12))
        
        self.hit_button.clicked.connect(self.hit)
        self.stand_button.clicked.connect(self.stand)
        self.double_button.clicked.connect(self.double_down)
        
        self.action_layout.addStretch()
        self.action_layout.addWidget(self.hit_button)
        self.action_layout.addWidget(self.stand_button)
        self.action_layout.addWidget(self.double_button)
        self.action_layout.addStretch()
        main_layout.addLayout(self.action_layout)
        
        # Disable action buttons initially
        self.set_action_buttons_enabled(False)

        # Status label
        self.status_label = QLabel("¡Bienvenido a Blackjack! Coloca tu apuesta para empezar.")
        self.status_label.setFont(QFont("Arial", 13))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            padding: 10px;
            background-color: rgba(0, 0, 0, 0.5);
            color: white;
            border-radius: 5px;
        """)
        main_layout.addWidget(self.status_label)
        
        # Back button
        back_button = QPushButton("Volver al Menú")
        back_button.clicked.connect(self.close)
        main_layout.addWidget(back_button)

        # Set background
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(21, 101, 52, 1),
                           stop:1 rgba(22, 163, 74, 1));
            }
        """)
    
    def set_action_buttons_enabled(self, enabled: bool):
        """Habilita o deshabilita los botones de acción"""
        self.hit_button.setEnabled(enabled)
        self.stand_button.setEnabled(enabled)
        self.double_button.setEnabled(enabled and self.game.can_double())


    def load_card_image(self, card: BlackjackCard, hidden: bool = False):
        """Crea un pixmap con la representación visual de la carta"""
        pixmap = QPixmap(80, 120)
        
        if hidden:
            # Carta boca abajo
            pixmap.fill(QColor("#1e40af"))
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QColor("white"))
            painter.drawRect(5, 5, 69, 109)
            painter.drawText(20, 65, "🂠")
            painter.end()
            return pixmap
        
        # Carta boca arriba
        pixmap.fill(QColor("white"))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Definir color según el palo
        if card.suit in ['Hearts', 'Diamonds']:
            color = QColor("red")
        else:
            color = QColor("black")
        
        painter.setPen(color)
        
        # Fuente para el valor
        font = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Dibujar el valor en la esquina superior izquierda
        painter.drawText(8, 22, card.value)
        
        # Fuente más pequeña para el símbolo del palo
        font_small = QFont("Arial", 12)
        painter.setFont(font_small)
        
        # Símbolos de los palos
        suit_symbols = {
            'Hearts': '♥',
            'Diamonds': '♦',
            'Clubs': '♣',
            'Spades': '♠'
        }
        
        # Dibujar símbolo del palo
        painter.drawText(8, 40, suit_symbols.get(card.suit, card.suit))
        
        # Dibujar valor y símbolo más grandes en el centro
        font_center = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(font_center)
        painter.drawText(20, 70, f"{card.value}")
        painter.drawText(25, 95, suit_symbols.get(card.suit, card.suit))
        
        # Dibujar borde
        painter.setPen(QColor("#333"))
        painter.drawRect(0, 0, 79, 119)
        
        painter.end()
        return pixmap

    def update_display(self):
        """Actualiza la visualización de las cartas y valores"""
        # Limpiar todas las cartas primero
        for label in self.dealer_card_labels + self.player_card_labels:
            label.clear()
            label.hide()
        
        # Mostrar cartas del dealer
        for i, card in enumerate(self.game.dealer_hand):
            if i < len(self.dealer_card_labels):
                # Ocultar segunda carta del dealer si el jugador aún está jugando
                hide_card = (i == 1 and self.game.state == GameState.PLAYER_TURN)
                pixmap = self.load_card_image(card, hidden=hide_card)
                self.dealer_card_labels[i].setPixmap(pixmap)
                self.dealer_card_labels[i].setScaledContents(True)
                self.dealer_card_labels[i].show()
        
        # Mostrar valor del dealer
        if self.game.state == GameState.PLAYER_TURN:
            # Solo mostrar valor de la primera carta
            if self.game.dealer_hand:
                dealer_value = self.game.dealer_hand[0].get_numeric_value()
                self.dealer_value_label.setText(f"Mostrando: {dealer_value}")
        else:
            dealer_value = self.game.calculate_hand_value(self.game.dealer_hand)
            self.dealer_value_label.setText(f"Total: {dealer_value}")
        
        # Mostrar cartas del jugador
        for i, card in enumerate(self.game.player_hand):
            if i < len(self.player_card_labels):
                pixmap = self.load_card_image(card)
                self.player_card_labels[i].setPixmap(pixmap)
                self.player_card_labels[i].setScaledContents(True)
                self.player_card_labels[i].show()
        
        # Mostrar valor del jugador
        if self.game.player_hand:
            player_value = self.game.calculate_hand_value(self.game.player_hand)
            self.player_value_label.setText(f"Total: {player_value}")
        else:
            self.player_value_label.setText("")
        
        # Actualizar balance
        self.balance_label.setText(f"Balance: ${self.game.balance}")
    
    def deal_cards(self):
        """Reparte las cartas iniciales"""
        bet_amount = self.bet_spinbox.value()
        
        if bet_amount > self.game.balance:
            QMessageBox.warning(self, "Error", "No tienes suficiente balance para esa apuesta.")
            return
        
        if not self.game.place_bet(bet_amount):
            QMessageBox.warning(self, "Error", "No se pudo colocar la apuesta.")
            return
        
        self.game.start_new_hand()
        self.update_display()
        
        # Verificar si el jugador tiene Blackjack
        if self.game.is_blackjack(self.game.player_hand):
            result, winnings = self.game.resolve_hand()
            self.status_label.setText(result)
            self.update_display()
            self.set_action_buttons_enabled(False)
            self.bet_spinbox.setEnabled(True)
            self.deal_button.setEnabled(True)
        else:
            self.status_label.setText(f"Apuesta: ${bet_amount}. ¿Qué quieres hacer?")
            self.set_action_buttons_enabled(True)
            self.bet_spinbox.setEnabled(False)
            self.deal_button.setEnabled(False)
    
    def hit(self):
        """El jugador pide una carta"""
        self.game.hit()
        self.update_display()
        
        if self.game.state == GameState.GAME_OVER:
            result, winnings = self.game.resolve_hand()
            self.status_label.setText(result)
            self.set_action_buttons_enabled(False)
            self.bet_spinbox.setEnabled(True)
            self.deal_button.setEnabled(True)
    
    def stand(self):
        """El jugador se planta"""
        self.game.stand()
        self.update_display()
        
        result, winnings = self.game.resolve_hand()
        self.status_label.setText(result)
        self.set_action_buttons_enabled(False)
        self.bet_spinbox.setEnabled(True)
        self.deal_button.setEnabled(True)
    
    def double_down(self):
        """El jugador dobla su apuesta"""
        if not self.game.can_double():
            QMessageBox.warning(self, "Error", "No puedes doblar en este momento.")
            return
        
        self.game.double_down()
        self.update_display()
        
        result, winnings = self.game.resolve_hand()
        self.status_label.setText(result)
        self.set_action_buttons_enabled(False)
        self.bet_spinbox.setEnabled(True)
        self.deal_button.setEnabled(True)
    
    def closeEvent(self, a0):
        """Handle window close event"""
        if self.parent_window:
            self.parent_window.show()
        a0.accept()


def main():
    """Entry point for standalone blackjack game"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        owns_app = True
    else:
        owns_app = False
    
    window = BlackJackWindow()
    window.show()
    
    if owns_app:
        sys.exit(app.exec())
    
    return window, owns_app, app


def open_blackjack_window(parent=None):
    """Open blackjack window from main UI"""
    return main() if parent is None else (BlackJackWindow(parent), False, None)


if __name__ == "__main__":
    main()