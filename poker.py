### Juego del poker (Texas Hold'em)
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor
from PyQt6.QtCore import Qt
import sys
import os
import random
from mainui import MainUI

from cardGamesCommon import BaseCard, BaseDeck


class PokerGame(QWidget):
    def __init__(self):
        super().__init__()
        self.deck = BaseDeck()
        self.deck.shuffle()
        self.players_hands = []  # List of lists to hold each player's hand
        self.community_cards = []
        self.possible_combinations = [
    "High Card", "One Pair", "Two Pair", "Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush", "Royal Flush"
]
    
    def start_new_hand(self, num_players=1):
        self.deck = BaseDeck()
        self.deck.shuffle()
        self.players_hands = [[] for _ in range(num_players)]
        self.community_cards = []
        # Deal two cards to each player
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