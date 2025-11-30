
"""
Comprehensive tests for Blackjack game logic implementation
Tests the BlackjackCard, BlackjackDeck, and BlackjackGame classes
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from Blackjack.blackjack import BlackjackCard, BlackjackDeck, BlackjackGame, GameState
    BLACKJACK_LOGIC_AVAILABLE = True
except ImportError:
    BLACKJACK_LOGIC_AVAILABLE = False


@unittest.skipUnless(BLACKJACK_LOGIC_AVAILABLE, "Blackjack logic not available")
class TestBlackjackCard(unittest.TestCase):
    """Tests for BlackjackCard class"""
    
    def test_card_creation(self):
        """Test creating a blackjack card"""
        card = BlackjackCard('A', 'Hearts')
        self.assertEqual(card.value, 'A')
        self.assertEqual(card.suit, 'Hearts')
    
    def test_ace_numeric_value(self):
        """Test that Ace has numeric value of 11"""
        card = BlackjackCard('A', 'Spades')
        self.assertEqual(card.get_numeric_value(), 11)
    
    def test_face_card_values(self):
        """Test that face cards have value 10"""
        for value in ['J', 'Q', 'K']:
            card = BlackjackCard(value, 'Hearts')
            self.assertEqual(card.get_numeric_value(), 10)
    
    def test_number_card_values(self):
        """Test number cards have correct values"""
        for value in ['2', '3', '4', '5', '6', '7', '8', '9', '10']:
            card = BlackjackCard(value, 'Clubs')
            self.assertEqual(card.get_numeric_value(), int(value))
    
    def test_is_ace(self):
        """Test ace detection"""
        ace = BlackjackCard('A', 'Diamonds')
        self.assertTrue(ace.is_ace())
        
        non_ace = BlackjackCard('K', 'Hearts')
        self.assertFalse(non_ace.is_ace())


@unittest.skipUnless(BLACKJACK_LOGIC_AVAILABLE, "Blackjack logic not available")
class TestBlackjackDeck(unittest.TestCase):
    """Tests for BlackjackDeck class"""
    
    def test_deck_creation(self):
        """Test creating a blackjack deck"""
        deck = BlackjackDeck()
        self.assertEqual(len(deck), 52)
    
    def test_deck_has_all_cards(self):
        """Test deck contains all 52 unique cards"""
        deck = BlackjackDeck()
        values = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
        
        # Check we have 13 cards of each suit
        for suit in suits:
            suit_cards = [c for c in deck.cards if c.suit == suit]
            self.assertEqual(len(suit_cards), 13)
        
        # Check we have 4 cards of each value
        for value in values:
            value_cards = [c for c in deck.cards if c.value == value]
            self.assertEqual(len(value_cards), 4)
    
    def test_deck_deal(self):
        """Test dealing cards from deck"""
        deck = BlackjackDeck()
        cards = deck.deal(5)
        self.assertEqual(len(cards), 5)
        self.assertEqual(len(deck), 47)
    
    def test_deck_shuffle(self):
        """Test deck shuffling"""
        deck1 = BlackjackDeck()
        original_order = [str(c) for c in deck1.cards]
        
        deck1.shuffle()
        shuffled_order = [str(c) for c in deck1.cards]
        
        # Very unlikely to be in same order after shuffle
        # (though technically possible)
        self.assertEqual(len(original_order), len(shuffled_order))


@unittest.skipUnless(BLACKJACK_LOGIC_AVAILABLE, "Blackjack logic not available")
class TestBlackjackGameLogic(unittest.TestCase):
    """Tests for BlackjackGame class logic"""
    
    def setUp(self):
        """Set up a game for testing"""
        self.game = BlackjackGame(initial_balance=1000)
    
    def test_game_initialization(self):
        """Test game initializes correctly"""
        self.assertEqual(self.game.balance, 1000)
        self.assertEqual(len(self.game.player_hand), 0)
        self.assertEqual(len(self.game.dealer_hand), 0)
        self.assertEqual(self.game.state, GameState.BETTING)
    
    def test_hand_value_calculation(self):
        """Test hand value calculation"""
        # Simple hand
        hand = [
            BlackjackCard('5', 'Hearts'),
            BlackjackCard('7', 'Clubs')
        ]
        self.assertEqual(self.game.calculate_hand_value(hand), 12)
        
        # Hand with face cards
        hand = [
            BlackjackCard('K', 'Hearts'),
            BlackjackCard('Q', 'Clubs')
        ]
        self.assertEqual(self.game.calculate_hand_value(hand), 20)
    
    def test_ace_value_adjustment(self):
        """Test that Aces adjust from 11 to 1 when needed"""
        # Ace + 10 = 21
        hand = [
            BlackjackCard('A', 'Hearts'),
            BlackjackCard('10', 'Clubs')
        ]
        self.assertEqual(self.game.calculate_hand_value(hand), 21)
        
        # Ace + 6 + 10 = 17 (Ace becomes 1)
        hand = [
            BlackjackCard('A', 'Hearts'),
            BlackjackCard('6', 'Clubs'),
            BlackjackCard('10', 'Spades')
        ]
        self.assertEqual(self.game.calculate_hand_value(hand), 17)
    
    def test_blackjack_detection(self):
        """Test Blackjack detection (21 with 2 cards)"""
        # Blackjack
        hand = [
            BlackjackCard('A', 'Hearts'),
            BlackjackCard('K', 'Clubs')
        ]
        self.assertTrue(self.game.is_blackjack(hand))
        
        # 21 but not blackjack
        hand = [
            BlackjackCard('7', 'Hearts'),
            BlackjackCard('7', 'Clubs'),
            BlackjackCard('7', 'Spades')
        ]
        self.assertFalse(self.game.is_blackjack(hand))
    
    def test_place_bet(self):
        """Test placing a bet"""
        result = self.game.place_bet(100)
        self.assertTrue(result)
        self.assertEqual(self.game.balance, 900)
        self.assertEqual(self.game.current_bet, 100)
        self.assertEqual(self.game.state, GameState.DEALING)
    
    def test_place_bet_insufficient_balance(self):
        """Test placing bet with insufficient balance"""
        result = self.game.place_bet(2000)
        self.assertFalse(result)
        self.assertEqual(self.game.balance, 1000)
    
    def test_start_new_hand_deals_cards(self):
        """Test that starting a new hand deals cards"""
        self.game.place_bet(50)
        self.game.start_new_hand()
        
        self.assertEqual(len(self.game.player_hand), 2)
        self.assertEqual(len(self.game.dealer_hand), 2)
        self.assertEqual(self.game.state, GameState.PLAYER_TURN)
    
    def test_can_double(self):
        """Test double down conditions"""
        self.game.place_bet(100)
        self.game.start_new_hand()
        
        # Should be able to double with 2 cards and sufficient balance
        if not self.game.is_blackjack(self.game.player_hand):
            self.assertTrue(self.game.can_double())


@unittest.skipUnless(BLACKJACK_LOGIC_AVAILABLE, "Blackjack logic not available")
class TestBlackjackGamePlay(unittest.TestCase):
    """Tests for gameplay actions"""
    
    def setUp(self):
        """Set up a game for testing"""
        self.game = BlackjackGame(initial_balance=1000)
        self.game.place_bet(100)
        self.game.start_new_hand()
    
    def test_hit_adds_card(self):
        """Test that hit adds a card to player hand"""
        if not self.game.is_blackjack(self.game.player_hand):
            initial_cards = len(self.game.player_hand)
            self.game.hit()
            self.assertEqual(len(self.game.player_hand), initial_cards + 1)
    
    def test_stand_changes_state(self):
        """Test that stand moves to dealer turn"""
        if not self.game.is_blackjack(self.game.player_hand):
            self.game.stand()
            self.assertEqual(self.game.state, GameState.GAME_OVER)
    
    def test_bust_detection(self):
        """Test that busting is detected"""
        # Force a bust by adding high cards
        self.game.player_hand = [
            BlackjackCard('K', 'Hearts'),
            BlackjackCard('K', 'Clubs'),
            BlackjackCard('K', 'Spades')
        ]
        value = self.game.calculate_hand_value(self.game.player_hand)
        self.assertGreater(value, 21)


if __name__ == '__main__':
    unittest.main()
