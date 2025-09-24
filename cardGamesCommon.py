import random
from PyQt6.QtWidgets import QGraphicsPixmapItem
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

class BaseCard:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def get_image(self, image_path) -> QGraphicsPixmapItem:
        self.image_path = image_path
        self.image = QPixmap(image_path)
        self.image = self.image.scaled(80, 120, Qt.AspectRatioMode.KeepAspectRatio)
        self.image_item = QGraphicsPixmapItem(self.image)
        self.image_item.setPos(0, 0)
        return self.image_item

    def __repr__(self):
        return f"{self.value} of {self.suit}"
    
class BaseDeck:
    def __init__(self):
        self.suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        self.values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.number_values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        self.figure_values = ['J', 'Q', 'K', 'A']
        self.cards = [BaseCard(value, suit) for suit in self.suits for value in self.values]
        
    def shuffle(self):
        random.shuffle(self.cards)
        

