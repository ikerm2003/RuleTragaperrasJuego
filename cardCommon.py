"""
Modulo básico para la gestión de distintas barajas de cartas. 
Incluye las clases que definen las cartas y las barajas.
"""
import random

__all__ = ['BaseCard', 'BaseDeck', 'PokerCard', 'PokerDeck', 'SpanishCard', 'SpanishDeck']

class BaseCard:
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
        

    def __repr__(self):
        return f"{self.value} of {self.suit}"

class BaseDeck:
    def __init__(self):
        self.cards = []

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self, num=1):
        return [self.cards.pop() for _ in range(num)]

class PokerCard(BaseCard):
    pass

class PokerDeck(BaseDeck):
    def __init__(self):
        super().__init__()
        self.cards = [PokerCard(value, suit) for suit in PokerDeck.SUITS for value in PokerDeck.VALUES]

    SUITS = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    pass

class SpanishCard(BaseCard):
    pass

class SpanishDeck(BaseDeck):
    def __init__(self):
        super().__init__()
        self.cards = [SpanishCard(value, suit) for suit in SpanishDeck.SUITS for value in SpanishDeck.VALUES]

    SUITS = ['Oros', 'Copas', 'Espadas', 'Bastos']
    VALUES = ['1', '2', '3', '4', '5', '6', '7', '10', '11', '12']