#!/usr/bin/env python3
"""
Tests comprehensivos para el módulo cardCommon.py
Tests the abstract base classes and concrete implementations for cards and decks.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from cardCommon import BaseCard, BaseDeck, PokerCard, PokerDeck


class ConcreteCard(BaseCard):
    """Implementación concreta de BaseCard para testing"""
    
    def get_numeric_value(self) -> int:
        value_map = {'A': 1, '2': 2, '3': 3, '4': 4, '5': 5}
        return value_map.get(self.value, 1)


class ConcreteDeck(BaseDeck):
    """Implementación concreta de BaseDeck para testing"""
    
    def _create_deck(self):
        self.cards = [
            ConcreteCard('A', 'Hearts'),
            ConcreteCard('2', 'Hearts'),
            ConcreteCard('3', 'Hearts')
        ]


class TestBaseCard(unittest.TestCase):
    """Tests para la clase base abstracta BaseCard"""
    
    def setUp(self):
        self.card1 = ConcreteCard('A', 'Hearts')
        self.card2 = ConcreteCard('A', 'Hearts')
        self.card3 = ConcreteCard('K', 'Spades')
    
    def test_card_creation(self):
        """Test basic card creation"""
        card = ConcreteCard('A', 'Hearts')
        self.assertEqual(card.value, 'A')
        self.assertEqual(card.suit, 'Hearts')
    
    def test_card_string_representation(self):
        """Test string representation of cards"""
        self.assertEqual(str(self.card1), "A de Hearts")
        self.assertEqual(repr(self.card1), "ConcreteCard('A', 'Hearts')")
    
    def test_card_equality(self):
        """Test card equality comparison"""
        self.assertEqual(self.card1, self.card2)
        self.assertNotEqual(self.card1, self.card3)
        self.assertNotEqual(self.card1, "not a card")
    
    def test_card_hash(self):
        """Test card hashing for use in sets/dicts"""
        card_set = {self.card1, self.card2, self.card3}
        self.assertEqual(len(card_set), 2)  # card1 and card2 are equal
    
    def test_get_numeric_value(self):
        """Test abstract method implementation"""
        self.assertEqual(self.card1.get_numeric_value(), 1)
        card_5 = ConcreteCard('5', 'Diamonds')
        self.assertEqual(card_5.get_numeric_value(), 5)


class TestBaseDeck(unittest.TestCase):
    """Tests para la clase base abstracta BaseDeck"""
    
    def setUp(self):
        self.deck = ConcreteDeck()
    
    def test_deck_creation(self):
        """Test basic deck creation"""
        self.assertIsInstance(self.deck.cards, list)
        self.assertEqual(len(self.deck), 3)
        self.assertFalse(self.deck.is_empty())
    
    def test_deck_shuffle(self):
        """Test deck shuffling"""
        original_cards = self.deck.cards.copy()
        self.deck.shuffle()
        # Cards should still be the same, just potentially different order
        self.assertEqual(len(self.deck.cards), len(original_cards))
        self.assertEqual(set(str(c) for c in self.deck.cards), 
                        set(str(c) for c in original_cards))
    
    def test_deal_single_card(self):
        """Test dealing a single card"""
        initial_count = len(self.deck)
        dealt_card = self.deck.deal(1)
        
        self.assertEqual(len(dealt_card), 1)
        self.assertIsInstance(dealt_card[0], ConcreteCard)
        self.assertEqual(len(self.deck), initial_count - 1)
    
    def test_deal_multiple_cards(self):
        """Test dealing multiple cards"""
        dealt_cards = self.deck.deal(2)
        self.assertEqual(len(dealt_cards), 2)
        self.assertEqual(len(self.deck), 1)
    
    def test_deal_too_many_cards(self):
        """Test dealing more cards than available"""
        with self.assertRaises(ValueError):
            self.deck.deal(5)  # Only 3 cards in deck
    
    def test_deck_reset(self):
        """Test deck reset functionality"""
        self.deck.deal(2)
        self.assertEqual(len(self.deck), 1)
        
        self.deck.reset()
        self.assertEqual(len(self.deck), 3)
        self.assertFalse(self.deck.is_empty())
    
    def test_empty_deck(self):
        """Test empty deck detection"""
        self.deck.deal(3)
        self.assertTrue(self.deck.is_empty())
        self.assertEqual(len(self.deck), 0)


class TestPokerCard(unittest.TestCase):
    """Tests para la implementación específica PokerCard"""
    
    def test_valid_poker_card_creation(self):
        """Test creating valid poker cards"""
        card = PokerCard('A', 'Corazones')
        self.assertEqual(card.value, 'A')
        self.assertEqual(card.suit, 'Corazones')
    
    def test_invalid_value_creation(self):
        """Test creating poker cards with invalid values"""
        with self.assertRaises(ValueError):
            PokerCard('X', 'Corazones')
    
    def test_invalid_suit_creation(self):
        """Test creating poker cards with invalid suits"""
        with self.assertRaises(ValueError):
            PokerCard('A', 'InvalidSuit')
    
    def test_poker_card_numeric_values(self):
        """Test numeric values of poker cards"""
        test_cases = [
            ('2', 2), ('3', 3), ('4', 4), ('5', 5), ('6', 6),
            ('7', 7), ('8', 8), ('9', 9), ('10', 10),
            ('J', 11), ('Q', 12), ('K', 13), ('A', 14)
        ]
        
        for value, expected in test_cases:
            card = PokerCard(value, 'Corazones')
            self.assertEqual(card.get_numeric_value(), expected)
    
    def test_poker_card_constants(self):
        """Test poker card constants"""
        self.assertIn('A', PokerCard.POKER_VALUES)
        self.assertIn('K', PokerCard.POKER_VALUES)
        self.assertIn('Corazones', PokerCard.POKER_SUITS)
        self.assertIn('Picas', PokerCard.POKER_SUITS)
        
        self.assertEqual(len(PokerCard.POKER_VALUES), 13)
        self.assertEqual(len(PokerCard.POKER_SUITS), 4)


class TestPokerDeck(unittest.TestCase):
    """Tests para la implementación específica PokerDeck"""
    
    def setUp(self):
        self.deck = PokerDeck()
    
    def test_poker_deck_creation(self):
        """Test poker deck creation"""
        self.assertEqual(len(self.deck), 52)
        self.assertFalse(self.deck.is_empty())
    
    def test_poker_deck_contains_all_cards(self):
        """Test that poker deck contains all 52 unique cards"""
        cards_set = set()
        for card in self.deck.cards:
            cards_set.add((card.value, card.suit))
        
        self.assertEqual(len(cards_set), 52)
        
        # Verify all values and suits are present
        for suit in PokerCard.POKER_SUITS:
            for value in PokerCard.POKER_VALUES:
                self.assertIn((value, suit), cards_set)
    
    def test_poker_deck_card_types(self):
        """Test that all cards in deck are PokerCard instances"""
        for card in self.deck.cards:
            self.assertIsInstance(card, PokerCard)
    
    def test_poker_deck_shuffling(self):
        """Test poker deck shuffling preserves all cards"""
        original_cards = [(c.value, c.suit) for c in self.deck.cards]
        self.deck.shuffle()
        shuffled_cards = [(c.value, c.suit) for c in self.deck.cards]
        
        self.assertEqual(len(original_cards), len(shuffled_cards))
        self.assertEqual(set(original_cards), set(shuffled_cards))
    
    def test_poker_deck_dealing(self):
        """Test dealing from poker deck"""
        dealt_cards = self.deck.deal(5)
        self.assertEqual(len(dealt_cards), 5)
        self.assertEqual(len(self.deck), 47)
        
        for card in dealt_cards:
            self.assertIsInstance(card, PokerCard)
    
    def test_poker_deck_reset(self):
        """Test poker deck reset"""
        self.deck.deal(10)
        self.assertEqual(len(self.deck), 42)
        
        self.deck.reset()
        self.assertEqual(len(self.deck), 52)


class TestCardDeckIntegration(unittest.TestCase):
    """Tests de integración entre cartas y barajas"""
    
    def test_poker_deck_card_consistency(self):
        """Test consistency between PokerDeck and PokerCard"""
        deck = PokerDeck()
        
        # Deal all cards and verify they are valid
        all_cards = deck.deal(52)
        self.assertEqual(len(all_cards), 52)
        
        for card in all_cards:
            self.assertIsInstance(card, PokerCard)
            self.assertIn(card.value, PokerCard.POKER_VALUES)
            self.assertIn(card.suit, PokerCard.POKER_SUITS)
            self.assertIsInstance(card.get_numeric_value(), int)
            self.assertGreaterEqual(card.get_numeric_value(), 2)
            self.assertLessEqual(card.get_numeric_value(), 14)
    
    def test_card_uniqueness_in_deck(self):
        """Test that no duplicate cards exist in a fresh deck"""
        deck = PokerDeck()
        card_strings = [str(card) for card in deck.cards]
        self.assertEqual(len(card_strings), len(set(card_strings)))


if __name__ == '__main__':
    unittest.main(verbosity=2)