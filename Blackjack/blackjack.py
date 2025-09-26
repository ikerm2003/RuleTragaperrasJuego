from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor
from PyQt6.QtCore import Qt

from ..main import MainUI
import sys
import os
import random

from ..cardCommon import BaseCard, BaseDeck
    
class BlackjackGame:
    def __init__(self):
        self.deck = BaseDeck()
        self.deck.shuffle()
        self.players_cards = []
        self.community_cards = []
    
    def start_new_hand(self):
        self.deck = BaseDeck()
        self.deck.shuffle()
        ## Todo: Add player management with deal new hands.    
            
class BlackJackWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game = BlackjackGame()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Blackjack")
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
            card_label = QLabel()
            card_label.setFixedSize(80, 120)
            card_label.setStyleSheet("border: 1px solid black; background-color: white;")
            self.player_card_labels.append(card_label)
            player_layout.addWidget(card_label)
        main_layout.addLayout(player_layout)

        # Botones de acción
        action_layout = QHBoxLayout()
        fold_button = QPushButton("Pasar")
        call_button = QPushButton("Igualar")
        raise_button = QPushButton("Subir")
        new_hand_button = QPushButton("Nueva Mano")

        fold_button.clicked.connect(self.fold)
        call_button.clicked.connect(self.call)
        raise_button.clicked.connect(self.raise_bet)
        new_hand_button.clicked.connect(self.new_hand)

        action_layout.addWidget(fold_button)
        action_layout.addWidget(call_button)
        action_layout.addWidget(raise_button)
        action_layout.addWidget(new_hand_button)
        main_layout.addLayout(action_layout)

        # Estado del juego
        self.status_label = QLabel("¡Bienvenido al juego de póker! Haz clic en 'Nueva Mano' para empezar.")
        main_layout.addWidget(self.status_label)

        # Iniciar primera mano
        self.new_hand()

    def load_card_image(self, card):
        """Crea un pixmap con la representación visual de la carta"""
        pixmap = QPixmap(80, 120)
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
        font = QFont("Arial", 14, QFont.Weight.Bold)
        painter.setFont(font)
        
        # Dibujar el valor en la esquina superior izquierda
        painter.drawText(5, 20, card.value)
        
        # Fuente más pequeña para el símbolo del palo
        font_small = QFont("Arial", 10)
        painter.setFont(font_small)
        
        # Símbolos de los palos
        suit_symbols = {
            'Hearts': '♥',
            'Diamonds': '♦',
            'Clubs': '♣',
            'Spades': '♠'
        }
        
        # Dibujar símbolo del palo
        painter.drawText(5, 35, suit_symbols.get(card.suit, card.suit))
        
        # Dibujar valor y símbolo más grandes en el centro
        font_center = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(font_center)
        painter.drawText(25, 70, f"{card.value}")
        painter.drawText(25, 90, suit_symbols.get(card.suit, card.suit))
        
        # Dibujar borde
        painter.setPen(QColor("black"))
        painter.drawRect(0, 0, 79, 119)
        
        painter.end()
        return pixmap

    def update_cards(self):
        # Actualizar cartas comunitarias
        for i, card in enumerate(self.game.community_cards):
            if i < len(self.community_card_labels):
                pixmap = self.load_card_image(card)
                self.community_card_labels[i].setPixmap(pixmap)
                self.community_card_labels[i].setScaledContents(True)
        
        # Actualizar cartas del jugador
        for i, card in enumerate(self.game.players_cards):
            if i < len(self.player_card_labels):
                pixmap = self.load_card_image(card)
                self.player_card_labels[i].setPixmap(pixmap)
                self.player_card_labels[i].setScaledContents(True)

    def new_hand(self):
        self.game.start_new_hand()
        self.update_cards()
        self.status_label.setText("Nueva mano iniciada. ¡Elige tu acción!")

    def fold(self):
        self.status_label.setText("Has pasado. Inicia una nueva mano.")
        self.clear_cards()

    def call(self):
        self.status_label.setText("Has igualado la apuesta.")

    def raise_bet(self):
        self.status_label.setText("Has subido la apuesta.")

    def clear_cards(self):
        for label in self.community_card_labels + self.player_card_labels:
            label.clear()  # Limpia tanto texto como pixmap

def main():
    app = QApplication(sys.argv)
    window = BlackJackWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()