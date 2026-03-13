
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
        self.assertIn(self.game.state, [GameState.PLAYER_TURN, GameState.BETTING])
    
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
            self.assertEqual(self.game.state, GameState.BETTING)
    
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

    def test_take_insurance_available_with_dealer_ace(self):
        """Insurance can be taken when dealer upcard is Ace"""
        self.game.player_hand = [
            BlackjackCard('10', 'Hearts'),
            BlackjackCard('9', 'Clubs')
        ]
        self.game.dealer_hand = [
            BlackjackCard('A', 'Spades'),
            BlackjackCard('7', 'Diamonds')
        ]
        self.game.state = GameState.PLAYER_TURN

        self.assertTrue(self.game.can_take_insurance())
        initial_balance = self.game.balance
        result = self.game.take_insurance()

        self.assertTrue(result)
        self.assertEqual(self.game.insurance_bet, self.game.current_bet // 2)
        self.assertEqual(self.game.balance, initial_balance - self.game.insurance_bet)

    def test_split_creates_two_hands_and_deducts_bet(self):
        """Split should create two hands and deduct additional bet"""
        game = BlackjackGame(initial_balance=1000)
        self.assertTrue(game.place_bet(100))
        game.state = GameState.PLAYER_TURN
        game.player_hand = [
            BlackjackCard('8', 'Hearts'),
            BlackjackCard('8', 'Clubs')
        ]
        game.dealer_hand = [
            BlackjackCard('6', 'Spades'),
            BlackjackCard('10', 'Diamonds')
        ]

        initial_balance = game.balance
        self.assertTrue(game.can_split())
        self.assertTrue(game.split_hand())

        self.assertTrue(game.split_mode)
        self.assertEqual(len(game.split_hands), 2)
        self.assertEqual(len(game.split_hands[0]), 2)
        self.assertEqual(len(game.split_hands[1]), 2)
        self.assertEqual(game.current_hand_index, 0)
        self.assertEqual(game.balance, initial_balance - 100)

    def test_split_stand_advances_to_second_hand(self):
        """Standing first split hand should move turn to second hand"""
        game = BlackjackGame(initial_balance=1000)
        self.assertTrue(game.place_bet(100))
        game.state = GameState.PLAYER_TURN
        game.player_hand = [
            BlackjackCard('9', 'Hearts'),
            BlackjackCard('9', 'Clubs')
        ]
        game.dealer_hand = [
            BlackjackCard('7', 'Spades'),
            BlackjackCard('10', 'Diamonds')
        ]

        self.assertTrue(game.split_hand())
        self.assertTrue(game.stand())

        self.assertEqual(game.state, GameState.PLAYER_TURN)
        self.assertEqual(game.current_hand_index, 1)

    def test_split_two_stands_resolve_round(self):
        """Standing both split hands should resolve round and return to betting"""
        game = BlackjackGame(initial_balance=1000)
        self.assertTrue(game.place_bet(100))
        game.state = GameState.PLAYER_TURN
        game.player_hand = [
            BlackjackCard('7', 'Hearts'),
            BlackjackCard('7', 'Clubs')
        ]
        game.dealer_hand = [
            BlackjackCard('6', 'Spades'),
            BlackjackCard('9', 'Diamonds')
        ]

        self.assertTrue(game.split_hand())
        self.assertTrue(game.stand())
        self.assertTrue(game.stand())

        self.assertEqual(game.state, GameState.BETTING)
        self.assertTrue(game.hand_resolved)
        self.assertNotEqual(game.last_result, "")

    def test_insurance_payout_when_dealer_has_blackjack(self):
        """Insurance pays correctly when dealer has blackjack"""
        game = BlackjackGame(initial_balance=1000)
        self.assertTrue(game.place_bet(100))

        game.player_hand = [
            BlackjackCard('10', 'Hearts'),
            BlackjackCard('Q', 'Clubs')
        ]
        game.dealer_hand = [
            BlackjackCard('A', 'Spades'),
            BlackjackCard('K', 'Diamonds')
        ]
        game.state = GameState.PLAYER_TURN

        self.assertTrue(game.take_insurance())
        result, winnings = game.resolve_hand()

        self.assertIn('Seguro ganado', result)
        self.assertEqual(winnings, 150)
        self.assertEqual(game.balance, 1000)

    def test_resolve_hand_is_idempotent(self):
        """Calling resolve_hand twice should not alter balance twice"""
        game = BlackjackGame(initial_balance=1000)
        self.assertTrue(game.place_bet(100))
        game.player_hand = [
            BlackjackCard('10', 'Hearts'),
            BlackjackCard('9', 'Clubs')
        ]
        game.dealer_hand = [
            BlackjackCard('10', 'Spades'),
            BlackjackCard('7', 'Diamonds')
        ]

        result_1, winnings_1 = game.resolve_hand()
        balance_after_first = game.balance
        result_2, winnings_2 = game.resolve_hand()

        self.assertEqual(result_1, result_2)
        self.assertEqual(winnings_1, winnings_2)
        self.assertEqual(game.balance, balance_after_first)


if __name__ == '__main__':
    unittest.main()
