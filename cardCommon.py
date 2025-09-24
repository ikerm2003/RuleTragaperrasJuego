from abc import ABC, abstractmethod
import random

class BaseCard(ABC):
    """Clase base abstracta para todas las cartas"""
    
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit
    
    def __str__(self):
        return f"{self.value} de {self.suit}"
    
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.value}', '{self.suit}')"
    
    def __eq__(self, other):
        if not isinstance(other, BaseCard):
            return False
        return self.value == other.value and self.suit == other.suit
    
    def __hash__(self):
        return hash((self.value, self.suit))
    
    @abstractmethod
    def get_numeric_value(self) -> int:
        """Método abstracto para obtener el valor numérico de la carta"""
        pass


class BaseDeck(ABC):
    """Clase base abstracta para todas las barajas"""
    
    def __init__(self):
        self.cards = []
        self._create_deck()
    
    @abstractmethod
    def _create_deck(self) -> list[str]:
        """Método abstracto para crear la baraja específica"""
        pass
    
    def shuffle(self):
        """Baraja las cartas"""
        random.shuffle(self.cards)
    
    def deal(self, num_cards=1):
        """Reparte un número específico de cartas"""
        if num_cards > len(self.cards):
            raise ValueError("No hay suficientes cartas en la baraja")
        
        dealt_cards = []
        for _ in range(num_cards):
            if self.cards:
                dealt_cards.append(self.cards.pop())
        return dealt_cards
    
    def reset(self):
        """Resetea la baraja a su estado inicial"""
        self.cards.clear()
        self._create_deck()
    
    def __len__(self):
        return len(self.cards)
    
    def is_empty(self):
        return len(self.cards) == 0


class PokerCard(BaseCard):
    """Carta específica para póker con valores y palos estándar"""
    
    POKER_VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    POKER_SUITS = ['Corazones', 'Diamantes', 'Tréboles', 'Picas']
    
    def __init__(self, value, suit):
        if value not in self.POKER_VALUES:
            raise ValueError(f"Valor inválido: {value}")
        if suit not in self.POKER_SUITS:
            raise ValueError(f"Palo inválido: {suit}")
        super().__init__(value, suit)
    
    def get_numeric_value(self) -> int:
        """Devuelve el valor numérico de la carta para comparaciones"""
        value_map = {
            '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8,
            '9': 9, '10': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
        }
        return value_map[self.value]


class PokerDeck(BaseDeck):
    """Baraja estándar de póker de 52 cartas"""

    def _create_deck(self) -> list[str]:
        """Crea una baraja completa de póker"""
        self.cards = []
        for suit in PokerCard.POKER_SUITS:
            for value in PokerCard.POKER_VALUES:
                self.cards.append(PokerCard(value, suit))
        return self.cards


class SpanishCard(BaseCard):
    """Carta española con valores y palos tradicionales"""
    
    SPANISH_VALUES = ['1', '2', '3', '4', '5', '6', '7', 'Sota', 'Caballo', 'Rey']
    SPANISH_SUITS = ['Oros', 'Copas', 'Espadas', 'Bastos']
    
    def __init__(self, value, suit):
        if value not in self.SPANISH_VALUES:
            raise ValueError(f"Valor inválido: {value}")
        if suit not in self.SPANISH_SUITS:
            raise ValueError(f"Palo inválido: {suit}")
        super().__init__(value, suit)
    
    def get_numeric_value(self) -> int:
        """Devuelve el valor numérico de la carta para comparaciones"""
        if self.value in ['1', '2', '3', '4', '5', '6', '7']:
            return int(self.value)
        elif self.value == 'Sota':
            return 10
        elif self.value == 'Caballo':
            return 11
        elif self.value == 'Rey':
            return 12
        return 0


class SpanishDeck(BaseDeck):
    """Baraja española de 40 cartas"""

    def _create_deck(self) -> list[str]:
        """Crea una baraja española completa"""
        self.cards = []
        for suit in SpanishCard.SPANISH_SUITS:
            for value in SpanishCard.SPANISH_VALUES:
                self.cards.append(SpanishCard(value, suit)) 

                self.cards.append(SpanishCard(value, suit))
        return self.cards