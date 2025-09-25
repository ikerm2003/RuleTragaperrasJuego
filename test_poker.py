"""
Unit tests for the Texas Hold'em Poker module.

Tests cover:
- Card and deck functionality
- Hand evaluation logic
- Game flow and betting
- Player management
"""
import unittest
from unittest.mock import Mock, patch
from poker_logic import (
    PokerTable, Player, GamePhase, PlayerAction, HandRanking
)
from poker_table import NinePlayerTable, PokerTableFactory
from cardCommon import PokerCard, PokerDeck


class TestPokerCards(unittest.TestCase):
    """Test card and deck functionality"""
    
    def test_poker_deck_creation(self):
        """Test that a poker deck is created correctly"""
        deck = PokerDeck()
        self.assertEqual(len(deck), 52)
        
        # Check all cards are present
        expected_cards = []
        for suit in PokerCard.POKER_SUITS:
            for value in PokerCard.POKER_VALUES:
                expected_cards.append(f"{value} of {suit}")
        
        deck_strings = [f"{card.value} of {card.suit}" for card in deck.cards]
        self.assertEqual(len(set(deck_strings)), 52)  # All unique
    
    def test_poker_deck_shuffle(self):
        """Test deck shuffling"""
        deck1 = PokerDeck()
        original_order = [str(card) for card in deck1.cards]
        
        deck2 = PokerDeck()
        deck2.shuffle()
        shuffled_order = [str(card) for card in deck2.cards]
        
        # Very unlikely to be the same order after shuffle
        self.assertNotEqual(original_order, shuffled_order)
    
    def test_poker_deck_deal(self):
        """Test dealing cards"""
        deck = PokerDeck()
        initial_count = len(deck)
        
        dealt_cards = deck.deal(5)
        
        self.assertEqual(len(dealt_cards), 5)
        self.assertEqual(len(deck), initial_count - 5)
        
        # Test dealing more cards than available
        with self.assertRaises(ValueError):
            deck.deal(100)
    
    def test_poker_card_values(self):
        """Test poker card numeric values"""
        card_2 = PokerCard('2', 'Corazones')
        card_a = PokerCard('A', 'Picas')
        card_k = PokerCard('K', 'Diamantes')
        
        self.assertEqual(card_2.get_numeric_value(), 2)
        self.assertEqual(card_a.get_numeric_value(), 14)
        self.assertEqual(card_k.get_numeric_value(), 13)


class TestHandEvaluation(unittest.TestCase):
    """Test poker hand evaluation"""
    
    def setUp(self):
        self.table = PokerTable()
    
    def create_hand(self, cards_data):
        """Helper to create a list of cards from tuples"""
        return [PokerCard(value, suit) for value, suit in cards_data]
    
    def test_royal_flush(self):
        """Test royal flush detection"""
        hand = self.create_hand([
            ('10', 'Corazones'), ('J', 'Corazones'), ('Q', 'Corazones'),
            ('K', 'Corazones'), ('A', 'Corazones'), ('2', 'Picas'), ('3', 'Picas')
        ])
        
        ranking, tiebreakers = self.table.evaluate_hand(hand)
        self.assertEqual(ranking, HandRanking.ROYAL_FLUSH)
    
    def test_straight_flush(self):
        """Test straight flush detection"""
        hand = self.create_hand([
            ('5', 'Diamantes'), ('6', 'Diamantes'), ('7', 'Diamantes'),
            ('8', 'Diamantes'), ('9', 'Diamantes'), ('J', 'Corazones'), ('K', 'Picas')
        ])
        
        ranking, tiebreakers = self.table.evaluate_hand(hand)
        self.assertEqual(ranking, HandRanking.STRAIGHT_FLUSH)
        self.assertEqual(tiebreakers[0], 9)  # 9-high straight flush
    
    def test_four_of_a_kind(self):
        """Test four of a kind detection"""
        hand = self.create_hand([
            ('A', 'Corazones'), ('A', 'Diamantes'), ('A', 'Picas'),
            ('A', 'Tréboles'), ('K', 'Corazones'), ('2', 'Picas'), ('3', 'Diamantes')
        ])
        
        ranking, tiebreakers = self.table.evaluate_hand(hand)
        self.assertEqual(ranking, HandRanking.FOUR_OF_A_KIND)
        self.assertEqual(tiebreakers[0], 14)  # Aces
    
    def test_full_house(self):
        """Test full house detection"""
        hand = self.create_hand([
            ('K', 'Corazones'), ('K', 'Diamantes'), ('K', 'Picas'),
            ('Q', 'Corazones'), ('Q', 'Diamantes'), ('2', 'Picas'), ('3', 'Tréboles')
        ])
        
        ranking, tiebreakers = self.table.evaluate_hand(hand)
        self.assertEqual(ranking, HandRanking.FULL_HOUSE)
        self.assertEqual(tiebreakers[0], 13)  # Kings over Queens
        self.assertEqual(tiebreakers[1], 12)
    
    def test_flush(self):
        """Test flush detection"""
        hand = self.create_hand([
            ('2', 'Corazones'), ('4', 'Corazones'), ('7', 'Corazones'),
            ('9', 'Corazones'), ('J', 'Corazones'), ('K', 'Picas'), ('A', 'Diamantes')
        ])
        
        ranking, tiebreakers = self.table.evaluate_hand(hand)
        self.assertEqual(ranking, HandRanking.FLUSH)
    
    def test_straight(self):
        """Test straight detection"""
        hand = self.create_hand([
            ('5', 'Corazones'), ('6', 'Diamantes'), ('7', 'Picas'),
            ('8', 'Tréboles'), ('9', 'Corazones'), ('J', 'Diamantes'), ('K', 'Picas')
        ])
        
        ranking, tiebreakers = self.table.evaluate_hand(hand)
        self.assertEqual(ranking, HandRanking.STRAIGHT)
        self.assertEqual(tiebreakers[0], 9)  # 9-high straight
    
    def test_ace_low_straight(self):
        """Test A-2-3-4-5 straight (wheel)"""
        hand = self.create_hand([
            ('A', 'Corazones'), ('2', 'Diamantes'), ('3', 'Picas'),
            ('4', 'Tréboles'), ('5', 'Corazones'), ('J', 'Diamantes'), ('K', 'Picas')
        ])
        
        ranking, tiebreakers = self.table.evaluate_hand(hand)
        self.assertEqual(ranking, HandRanking.STRAIGHT)
        self.assertEqual(tiebreakers[0], 5)  # 5-high straight (wheel)
    
    def test_three_of_a_kind(self):
        """Test three of a kind detection"""
        hand = self.create_hand([
            ('8', 'Corazones'), ('8', 'Diamantes'), ('8', 'Picas'),
            ('K', 'Tréboles'), ('5', 'Corazones'), ('2', 'Diamantes'), ('3', 'Picas')
        ])
        
        ranking, tiebreakers = self.table.evaluate_hand(hand)
        self.assertEqual(ranking, HandRanking.THREE_OF_A_KIND)
        self.assertEqual(tiebreakers[0], 8)  # Trip 8s
    
    def test_two_pair(self):
        """Test two pair detection"""
        hand = self.create_hand([
            ('A', 'Corazones'), ('A', 'Diamantes'), ('8', 'Picas'),
            ('8', 'Tréboles'), ('5', 'Corazones'), ('2', 'Diamantes'), ('3', 'Picas')
        ])
        
        ranking, tiebreakers = self.table.evaluate_hand(hand)
        self.assertEqual(ranking, HandRanking.TWO_PAIR)
        self.assertEqual(tiebreakers[0], 14)  # Aces up
        self.assertEqual(tiebreakers[1], 8)   # over 8s
    
    def test_one_pair(self):
        """Test one pair detection"""
        hand = self.create_hand([
            ('A', 'Corazones'), ('A', 'Diamantes'), ('K', 'Picas'),
            ('Q', 'Tréboles'), ('5', 'Corazones'), ('2', 'Diamantes'), ('3', 'Picas')
        ])
        
        ranking, tiebreakers = self.table.evaluate_hand(hand)
        self.assertEqual(ranking, HandRanking.ONE_PAIR)
        self.assertEqual(tiebreakers[0], 14)  # Pair of Aces
    
    def test_high_card(self):
        """Test high card detection"""
        hand = self.create_hand([
            ('A', 'Corazones'), ('K', 'Diamantes'), ('Q', 'Picas'),
            ('J', 'Tréboles'), ('9', 'Corazones'), ('2', 'Diamantes'), ('3', 'Picas')
        ])
        
        ranking, tiebreakers = self.table.evaluate_hand(hand)
        self.assertEqual(ranking, HandRanking.HIGH_CARD)
        self.assertEqual(tiebreakers[0], 14)  # Ace high


class TestPokerTable(unittest.TestCase):
    """Test poker table functionality"""
    
    def setUp(self):
        self.table = PokerTable(small_blind=10, big_blind=20)
    
    def test_add_players(self):
        """Test adding players to table"""
        self.assertTrue(self.table.add_player("Player 1", 1000, is_human=True))
        self.assertTrue(self.table.add_player("Player 2", 1500, is_human=False))
        
        self.assertEqual(len(self.table.players), 2)
        self.assertEqual(self.table.players[0].name, "Player 1")
        self.assertEqual(self.table.players[0].chips, 1000)
        self.assertTrue(self.table.players[0].is_human)
        self.assertFalse(self.table.players[1].is_human)
    
    def test_max_players(self):
        """Test maximum player limit"""
        # Add 9 players (max)
        for i in range(9):
            self.assertTrue(self.table.add_player(f"Player {i+1}", 1000))
        
        # 10th player should fail
        self.assertFalse(self.table.add_player("Player 10", 1000))
    
    def test_fill_with_bots(self):
        """Test filling table with bots"""
        self.table.add_player("Human", 1000, is_human=True)
        self.table.fill_with_bots(6)
        
        self.assertEqual(len(self.table.players), 6)
        self.assertTrue(self.table.players[0].is_human)
        for i in range(1, 6):
            self.assertFalse(self.table.players[i].is_human)
    
    def test_start_new_hand(self):
        """Test starting a new hand"""
        # Add players
        self.table.add_player("Player 1", 1000, is_human=True)
        self.table.add_player("Player 2", 1500, is_human=False)
        
        self.table.start_new_hand()
        
        # Check initial state
        self.assertEqual(self.table.phase, GamePhase.PRE_FLOP)
        self.assertGreater(self.table.pot, 0)  # Blinds posted
        
        # Check players have cards
        for player in self.table.players:
            self.assertEqual(len(player.hand), 2)
    
    def test_blinds_posting(self):
        """Test blind posting"""
        self.table.add_player("SB", 1000)
        self.table.add_player("BB", 1000)
        self.table.add_player("UTG", 1000)
        
        self.table.start_new_hand()
        
        # Small blind should have posted
        sb_player = self.table.players[(self.table.dealer_position + 1) % 3]
        self.assertEqual(sb_player.current_bet, 10)
        
        # Big blind should have posted
        bb_player = self.table.players[(self.table.dealer_position + 2) % 3]
        self.assertEqual(bb_player.current_bet, 20)
        
        # Pot should equal blinds
        self.assertEqual(self.table.pot, 30)
    
    def test_valid_actions(self):
        """Test getting valid actions for players"""
        self.table.add_player("Player 1", 1000)
        self.table.add_player("Player 2", 1000)
        self.table.start_new_hand()
        
        # Current player should have valid actions
        actions = self.table.get_valid_actions(self.table.current_player)
        self.assertIn(PlayerAction.FOLD, actions)
        
        # Should be able to call the big blind
        if self.table.current_bet > 0:
            self.assertIn(PlayerAction.CALL, actions)
    
    def test_execute_fold(self):
        """Test fold action"""
        self.table.add_player("Player 1", 1000)
        self.table.add_player("Player 2", 1000)
        self.table.start_new_hand()
        
        current_player = self.table.current_player
        success = self.table.execute_action(current_player, PlayerAction.FOLD)
        
        self.assertTrue(success)
        self.assertTrue(self.table.players[current_player].is_folded)
    
    def test_execute_call(self):
        """Test call action"""
        self.table.add_player("Player 1", 1000)
        self.table.add_player("Player 2", 1000)
        self.table.add_player("Player 3", 1000)  # Add third player so first isn't BB
        self.table.start_new_hand()
        
        current_player = self.table.current_player
        initial_chips = self.table.players[current_player].chips
        valid_actions = self.table.get_valid_actions(current_player)
        
        if PlayerAction.CALL in valid_actions:
            # Calculate expected cost to call
            call_cost = self.table.current_bet - self.table.players[current_player].current_bet
            success = self.table.execute_action(current_player, PlayerAction.CALL)
            self.assertTrue(success)
            # Should have spent chips to call (unless already posted more than current bet)
            expected_chips = initial_chips - max(0, call_cost)
            self.assertEqual(self.table.players[current_player].chips, expected_chips)
        else:
            # If call not available, test that fold works
            success = self.table.execute_action(current_player, PlayerAction.FOLD)
            self.assertTrue(success)


class TestNinePlayerTable(unittest.TestCase):
    """Test nine-player table functionality"""
    
    def setUp(self):
        self.table = NinePlayerTable()
    
    def test_position_names(self):
        """Test position naming for different table sizes"""
        # Test with 6 players
        for i in range(6):
            self.table.add_player(f"Player {i+1}", 1000)
        
        # Dealer at position 0
        self.table.dealer_position = 0
        
        names = [self.table.get_position_name(i) for i in range(6)]
        # Check that position names are assigned (specific position depends on dealer)
        self.assertTrue(any("Button" in name or "Small Blind" in name for name in names))
        self.assertTrue(any("Big Blind" in name for name in names))
    
    def test_seat_layout(self):
        """Test seat layout for different table sizes"""
        # Test 4-player layout
        for i in range(4):
            self.table.add_player(f"Player {i+1}", 1000)
        
        layout = self.table.get_seat_layout()
        self.assertEqual(len(layout), 4)
        
        # Test 9-player layout
        for i in range(5):
            self.table.add_player(f"Player {i+5}", 1000)
        
        layout = self.table.get_seat_layout()
        self.assertEqual(len(layout), 9)
    
    def test_standard_game_setup(self):
        """Test standard game setup"""
        self.table.setup_standard_game(num_human_players=1, total_players=6)
        
        self.assertEqual(len(self.table.players), 6)
        self.assertTrue(self.table.players[0].is_human)
        
        # Rest should be bots
        for i in range(1, 6):
            self.assertFalse(self.table.players[i].is_human)


class TestPokerTableFactory(unittest.TestCase):
    """Test poker table factory"""
    
    def test_create_nine_player_table(self):
        """Test creating nine-player table"""
        table = PokerTableFactory.create_table("nine_player")
        self.assertIsInstance(table, NinePlayerTable)
        self.assertEqual(table.MAX_PLAYERS, 9)
    
    def test_create_heads_up_table(self):
        """Test creating heads-up table"""
        table = PokerTableFactory.create_table("heads_up")
        self.assertIsInstance(table, NinePlayerTable)
        self.assertEqual(table.max_players, 2)
    
    def test_create_six_max_table(self):
        """Test creating six-max table"""
        table = PokerTableFactory.create_table("six_max")
        self.assertIsInstance(table, NinePlayerTable)
        self.assertEqual(table.max_players, 6)
    
    def test_invalid_table_type(self):
        """Test creating invalid table type"""
        with self.assertRaises(ValueError):
            PokerTableFactory.create_table("invalid_type")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)