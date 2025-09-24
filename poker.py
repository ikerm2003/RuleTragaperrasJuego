### Juego del poker (Texas Hold'em)
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor
# from PyQt6.QtCore import Qt

# from mainui import MainUI
import sys
# import os
# import random

from cardCommon import PokerDeck
    
    
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

class PokerGame:
    def __init__(self):
        self.deck = PokerDeck()
        self.deck.shuffle()
        self.players_hands = []  # List of lists to hold each player's hand
        self.community_cards = []
        self.possible_combinations = [
    "High Card", "One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"
]
    
    def start_new_hand(self):
        self.deck = PokerDeck()
        self.deck.shuffle()
        self.player_cards = self.deck.deal(2)
        self.community_cards = self.deck.deal(3)

    def deal_turn(self):
        self.community_cards.append(self.deck.deal(1)[0])

    def deal_river(self):
        self.community_cards.append(self.deck.deal(1)[0])


class PokerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Poker Game")
        self.setGeometry(150, 150, 800, 600)
        self.game = PokerGame()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Texas Hold'em Poker")
        self.setGeometry(100, 100, 800, 600)

        # Widget principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Mesa de juego (fondo verde)
        table_label = QLabel()
        table_label.setStyleSheet("background-color: green; border: 2px solid black;")
        table_label.setFixedHeight(300)
        main_layout.addWidget(table_label)

        # Cartas comunitarias
        self.community_card_labels = []
        community_layout = QHBoxLayout()
        for _ in range(5):
            card_label = QLabel()
            card_label.setFixedSize(80, 120)
            card_label.setStyleSheet("border: 1px solid black; background-color: white;")
            self.community_card_labels.append(card_label)
            community_layout.addWidget(card_label)
        main_layout.addLayout(community_layout)

        # Cartas del jugador
        self.player_card_labels = []
        player_layout = QHBoxLayout()
        for _ in range(2):
            for player_hand in self.players_hands:
                if self.deck.cards:  # Verificar que hay cartas disponibles
                    player_hand.append(self.deck.cards.pop())
                else:
                    raise ValueError("No hay suficientes cartas en el mazo")
        # Deal five community cards
        for _ in range(5):
            self.community_cards.append(self.deck.cards.pop())

    def evaluate_hand(self, player_hand):
        # Placeholder for hand evaluation logic
        # This should return the rank of the hand (e.g., pair, flush, etc.)
        for combination in self.possible_combinations:
            player_hand.sort(key=lambda card: card.rank, reverse=True)
            self.check_combination(player_hand, combination)
            
    def check_combination(self, player_hand, combination):
        if combination == "High Card":
            if self.is_high_card(player_hand):
                return combination
        if combination == "One Pair":
            pass
        if combination == "Two Pair":
            pass
        if combination == "Three of a Kind":
            pass
        if combination == "Straight":
            pass
        if combination == "Flush":
            pass
        if combination == "Full House":
            pass
        if combination == "Four of a Kind":
            pass
        if combination == "Straight Flush":
            pass
        if combination == "Royal Flush":
            pass