
"""
Tests comprehensivos para el módulo Poker
Tests for poker_logic.py, poker_table.py, and related poker functionality.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import poker modules
from Poker.poker_logic import (
    GamePhase, PlayerAction, Player, HandRanking, PokerTable
)
from cardCommon import PokerCard, PokerDeck


class TestGamePhase(unittest.TestCase):
    """Tests para la enum GamePhase"""
    
    def test_game_phase_values(self):
        """Test GamePhase enum values"""
        expected_phases = {
            GamePhase.WAITING: "Esperando jugadores",
            GamePhase.PRE_FLOP: "Pre-flop", 
            GamePhase.FLOP: "Flop",
            GamePhase.TURN: "Turn",
            GamePhase.RIVER: "River",
            GamePhase.SHOWDOWN: "Showdown",
            GamePhase.FINISHED: "Mano terminada"
        }
        
        for phase, expected_value in expected_phases.items():
            self.assertEqual(phase.value, expected_value)
    
    def test_game_phase_count(self):
        """Test that all expected phases are present"""
        phases = list(GamePhase)
        self.assertEqual(len(phases), 7)


class TestPlayerAction(unittest.TestCase):
    """Tests para la enum PlayerAction"""
    
    def test_player_action_values(self):
        """Test PlayerAction enum values"""
        expected_actions = {
            PlayerAction.FOLD: "fold",
            PlayerAction.CALL: "call",
            PlayerAction.RAISE: "raise",
            PlayerAction.CHECK: "check",
            PlayerAction.ALL_IN: "all_in"
        }
        
        for action, expected_value in expected_actions.items():
            self.assertEqual(action.value, expected_value)
    
    def test_player_action_count(self):
        """Test that all expected actions are present"""
        actions = list(PlayerAction)
        self.assertEqual(len(actions), 5)


class TestPlayer(unittest.TestCase):
    """Tests para la clase Player"""
    
    def setUp(self):
        self.player = Player(name="TestPlayer", chips=1000, position=0)
    
    def test_player_creation(self):
        """Test player creation with default values"""
        self.assertEqual(self.player.name, "TestPlayer")
        self.assertEqual(self.player.chips, 1000)
        self.assertEqual(self.player.position, 0)
        self.assertEqual(self.player.current_bet, 0)
        self.assertEqual(self.player.total_bet_in_hand, 0)
        self.assertTrue(self.player.is_active)
        self.assertFalse(self.player.is_folded)
        self.assertFalse(self.player.is_all_in)
        self.assertFalse(self.player.is_human)
        self.assertEqual(self.player.hand, [])
    
    def test_player_can_act(self):
        """Test player can_act method"""
        # Active player with chips can act
        self.assertTrue(self.player.can_act())
        
        # Folded player cannot act
        self.player.is_folded = True
        self.assertFalse(self.player.can_act())
        
        # All-in player cannot act
        self.player.is_folded = False
        self.player.is_all_in = True
        self.assertFalse(self.player.can_act())
        
        # Player with no chips cannot act
        self.player.is_all_in = False
        self.player.chips = 0
        self.assertFalse(self.player.can_act())
        
        # Inactive player cannot act
        self.player.chips = 100
        self.player.is_active = False
        self.assertFalse(self.player.can_act())
    
    def test_player_reset_for_new_hand(self):
        """Test player reset functionality"""
        # Set up player state
        self.player.hand = [PokerCard('A', 'Corazones'), PokerCard('K', 'Picas')]
        self.player.current_bet = 50
        self.player.total_bet_in_hand = 150
        self.player.is_folded = True
        self.player.is_all_in = True
        
        # Reset for new hand
        self.player.reset_for_new_hand()
        
        # Verify reset state
        self.assertEqual(self.player.hand, [])
        self.assertEqual(self.player.current_bet, 0)
        self.assertEqual(self.player.total_bet_in_hand, 0)
        self.assertFalse(self.player.is_folded)
        self.assertFalse(self.player.is_all_in)
        self.assertTrue(self.player.is_active)  # Has chips
        
    def test_player_reset_with_no_chips(self):
        """Test player reset when they have no chips"""
        self.player.chips = 0
        self.player.reset_for_new_hand()
        self.assertFalse(self.player.is_active)  # No chips = not active


class TestHandRanking(unittest.TestCase):
    """Tests para la enum HandRanking"""
    
    def test_hand_ranking_values(self):
        """Test HandRanking enum values and ordering"""
        expected_rankings = [
            (HandRanking.HIGH_CARD, 1),
            (HandRanking.ONE_PAIR, 2),
            (HandRanking.TWO_PAIR, 3),
            (HandRanking.THREE_OF_A_KIND, 4),
            (HandRanking.STRAIGHT, 5),
            (HandRanking.FLUSH, 6),
            (HandRanking.FULL_HOUSE, 7),
            (HandRanking.FOUR_OF_A_KIND, 8),
            (HandRanking.STRAIGHT_FLUSH, 9),
            (HandRanking.ROYAL_FLUSH, 10)
        ]
        
        for ranking, expected_value in expected_rankings:
            self.assertEqual(ranking.value, expected_value)
    
    def test_hand_ranking_ordering(self):
        """Test that hand rankings are properly ordered"""
        self.assertLess(HandRanking.HIGH_CARD.value, HandRanking.ONE_PAIR.value)
        self.assertLess(HandRanking.ONE_PAIR.value, HandRanking.TWO_PAIR.value)
        self.assertLess(HandRanking.FLUSH.value, HandRanking.FULL_HOUSE.value)
        self.assertLess(HandRanking.STRAIGHT_FLUSH.value, HandRanking.ROYAL_FLUSH.value)


class TestPokerTable(unittest.TestCase):
    """Tests para la clase PokerTable"""
    
    def setUp(self):
        self.table = PokerTable(small_blind=10, big_blind=20)
    
    def test_table_creation(self):
        """Test poker table creation"""
        self.assertEqual(self.table.small_blind, 10)
        self.assertEqual(self.table.big_blind, 20)
        self.assertEqual(self.table.min_raise, 20)  # Usually equals big blind
        self.assertEqual(self.table.phase, GamePhase.WAITING)
        self.assertEqual(len(self.table.players), 0)
        self.assertEqual(len(self.table.community_cards), 0)
        self.assertEqual(self.table.pot, 0)
        self.assertEqual(self.table.current_bet, 0)
    
    def test_add_player(self):
        """Test adding players to the table"""
        result1 = self.table.add_player("Alice", 1000, True)
        self.assertTrue(result1)
        self.assertEqual(len(self.table.players), 1)
        self.assertEqual(self.table.players[0].name, "Alice")
        
        result2 = self.table.add_player("Bob", 1500, False)
        self.assertTrue(result2)
        self.assertEqual(len(self.table.players), 2)
        self.assertEqual(self.table.players[1].name, "Bob")
    
    def test_add_too_many_players(self):
        """Test adding more than maximum players"""
        # Add 9 players (maximum)
        for i in range(9):
            result = self.table.add_player(f"Player{i}", 1000, False)
            self.assertTrue(result)
        
        self.assertEqual(len(self.table.players), 9)
        
        # Try to add 10th player
        result = self.table.add_player("Extra", 1000, False)
        self.assertFalse(result)  # Should return False, not raise exception
    
    def test_can_start_hand(self):
        """Test hand start conditions"""
        # Need at least 2 players to start
        self.assertEqual(len(self.table.players), 0)
        
        # Add one player
        self.table.add_player("Alice", 1000, True)
        self.assertEqual(len(self.table.players), 1)
        
        # Add second player
        self.table.add_player("Bob", 1000, False)
        self.assertEqual(len(self.table.players), 2)
        
        # Now should be able to start a hand
        self.table.start_new_hand()
        self.assertEqual(self.table.phase, GamePhase.PRE_FLOP)
    
    def test_get_valid_actions_waiting_phase(self):
        """Test valid actions during waiting phase"""
        self.table.add_player("Alice", 1000, True)
        
        # In waiting phase, should return actions based on current game state
        actions = self.table.get_valid_actions(0)
        self.assertIsInstance(actions, list)
        # During waiting phase, actions may still be available depending on implementation
    
    def test_hand_evaluation_high_card(self):
        """Test hand evaluation for high card"""
        cards = [
            PokerCard('A', 'Corazones'),
            PokerCard('J', 'Picas'),
            PokerCard('9', 'Diamantes'),
            PokerCard('7', 'Tréboles'),
            PokerCard('5', 'Corazones'),
            PokerCard('3', 'Picas'),
            PokerCard('2', 'Diamantes')
        ]
        
        ranking, tie_breakers = self.table.evaluate_hand(cards)
        self.assertEqual(ranking, HandRanking.HIGH_CARD)
        self.assertEqual(tie_breakers[0], 14)  # Ace high
    
    def test_hand_evaluation_one_pair(self):
        """Test hand evaluation for one pair"""
        cards = [
            PokerCard('A', 'Corazones'),
            PokerCard('A', 'Picas'),
            PokerCard('9', 'Diamantes'),
            PokerCard('7', 'Tréboles'),
            PokerCard('5', 'Corazones'),
            PokerCard('3', 'Picas'),
            PokerCard('2', 'Diamantes')
        ]
        
        ranking, tie_breakers = self.table.evaluate_hand(cards)
        self.assertEqual(ranking, HandRanking.ONE_PAIR)
        self.assertEqual(tie_breakers[0], 14)  # Pair of Aces
    
    def test_hand_evaluation_two_pair(self):
        """Test hand evaluation for two pair"""
        cards = [
            PokerCard('A', 'Corazones'),
            PokerCard('A', 'Picas'),
            PokerCard('9', 'Diamantes'),
            PokerCard('9', 'Tréboles'),
            PokerCard('5', 'Corazones'),
            PokerCard('3', 'Picas'),
            PokerCard('2', 'Diamantes')
        ]
        
        ranking, tie_breakers = self.table.evaluate_hand(cards)
        self.assertEqual(ranking, HandRanking.TWO_PAIR)
        self.assertEqual(tie_breakers[0], 14)  # Higher pair (Aces)
        self.assertEqual(tie_breakers[1], 9)   # Lower pair (9s)
    
    def test_hand_evaluation_three_of_a_kind(self):
        """Test hand evaluation for three of a kind"""
        cards = [
            PokerCard('A', 'Corazones'),
            PokerCard('A', 'Picas'),
            PokerCard('A', 'Diamantes'),
            PokerCard('9', 'Tréboles'),
            PokerCard('5', 'Corazones'),
            PokerCard('3', 'Picas'),
            PokerCard('2', 'Diamantes')
        ]
        
        ranking, tie_breakers = self.table.evaluate_hand(cards)
        self.assertEqual(ranking, HandRanking.THREE_OF_A_KIND)
        self.assertEqual(tie_breakers[0], 14)  # Three Aces
    
    def test_hand_evaluation_straight(self):
        """Test hand evaluation for straight"""
        cards = [
            PokerCard('10', 'Corazones'),
            PokerCard('J', 'Picas'),
            PokerCard('Q', 'Diamantes'),
            PokerCard('K', 'Tréboles'),
            PokerCard('A', 'Corazones'),
            PokerCard('3', 'Picas'),
            PokerCard('2', 'Diamantes')
        ]
        
        ranking, tie_breakers = self.table.evaluate_hand(cards)
        self.assertEqual(ranking, HandRanking.STRAIGHT)
        self.assertEqual(tie_breakers[0], 14)  # Ace high straight
    
    def test_hand_evaluation_flush(self):
        """Test hand evaluation for flush"""
        cards = [
            PokerCard('A', 'Corazones'),
            PokerCard('J', 'Corazones'),
            PokerCard('9', 'Corazones'),
            PokerCard('7', 'Corazones'),
            PokerCard('5', 'Corazones'),
            PokerCard('3', 'Picas'),
            PokerCard('2', 'Diamantes')
        ]
        
        ranking, tie_breakers = self.table.evaluate_hand(cards)
        self.assertEqual(ranking, HandRanking.FLUSH)
        self.assertEqual(tie_breakers[0], 14)  # Ace high flush
    
    def test_hand_evaluation_full_house(self):
        """Test hand evaluation for full house"""
        cards = [
            PokerCard('A', 'Corazones'),
            PokerCard('A', 'Picas'),
            PokerCard('A', 'Diamantes'),
            PokerCard('9', 'Tréboles'),
            PokerCard('9', 'Corazones'),
            PokerCard('3', 'Picas'),
            PokerCard('2', 'Diamantes')
        ]
        
        ranking, tie_breakers = self.table.evaluate_hand(cards)
        self.assertEqual(ranking, HandRanking.FULL_HOUSE)
        self.assertEqual(tie_breakers[0], 14)  # Three Aces
        self.assertEqual(tie_breakers[1], 9)   # Pair of 9s
    
    def test_hand_evaluation_four_of_a_kind(self):
        """Test hand evaluation for four of a kind"""
        cards = [
            PokerCard('A', 'Corazones'),
            PokerCard('A', 'Picas'),
            PokerCard('A', 'Diamantes'),
            PokerCard('A', 'Tréboles'),
            PokerCard('9', 'Corazones'),
            PokerCard('3', 'Picas'),
            PokerCard('2', 'Diamantes')
        ]
        
        ranking, tie_breakers = self.table.evaluate_hand(cards)
        self.assertEqual(ranking, HandRanking.FOUR_OF_A_KIND)
        self.assertEqual(tie_breakers[0], 14)  # Four Aces
    
    def test_hand_evaluation_straight_flush(self):
        """Test hand evaluation for straight flush"""
        cards = [
            PokerCard('9', 'Corazones'),
            PokerCard('10', 'Corazones'),
            PokerCard('J', 'Corazones'),
            PokerCard('Q', 'Corazones'),
            PokerCard('K', 'Corazones'),
            PokerCard('3', 'Picas'),
            PokerCard('2', 'Diamantes')
        ]
        
        ranking, tie_breakers = self.table.evaluate_hand(cards)
        self.assertEqual(ranking, HandRanking.STRAIGHT_FLUSH)
        self.assertEqual(tie_breakers[0], 13)  # King high straight flush
    
    def test_hand_evaluation_royal_flush(self):
        """Test hand evaluation for royal flush"""
        cards = [
            PokerCard('10', 'Corazones'),
            PokerCard('J', 'Corazones'),
            PokerCard('Q', 'Corazones'),
            PokerCard('K', 'Corazones'),
            PokerCard('A', 'Corazones'),
            PokerCard('3', 'Picas'),
            PokerCard('2', 'Diamantes')
        ]
        
        ranking, tie_breakers = self.table.evaluate_hand(cards)
        self.assertEqual(ranking, HandRanking.ROYAL_FLUSH)
        self.assertEqual(tie_breakers[0], 14)  # Ace high (royal flush)
    
    def test_hand_evaluation_ace_low_straight(self):
        """Test hand evaluation for ace-low straight (A-2-3-4-5)"""
        cards = [
            PokerCard('A', 'Corazones'),
            PokerCard('2', 'Picas'),
            PokerCard('3', 'Diamantes'),
            PokerCard('4', 'Tréboles'),
            PokerCard('5', 'Corazones'),
            PokerCard('K', 'Picas'),
            PokerCard('Q', 'Diamantes')
        ]
        
        ranking, tie_breakers = self.table.evaluate_hand(cards)
        self.assertEqual(ranking, HandRanking.STRAIGHT)
        self.assertEqual(tie_breakers[0], 5)  # 5-high straight (ace low)
    
    def test_bot_action_generation(self):
        """Test bot action generation"""
        # Set up a table with 2 players
        self.table.add_player("Human", 1000, True)
        self.table.add_player("Bot", 1000, False)
        
        # Start a hand to test bot actions
        self.table.start_new_hand()
        
        # Get bot action
        action, amount = self.table.get_bot_action(1)
        self.assertIsInstance(action, PlayerAction)
        self.assertIsInstance(amount, int)
        self.assertGreaterEqual(amount, 0)
    
    def test_side_pot_calculation_basic(self):
        """Test basic side pot tracking"""
        # Set up players with different chip amounts
        self.table.add_player("Player1", 100, False)
        self.table.add_player("Player2", 200, False)
        self.table.add_player("Player3", 300, False)
        
        self.assertEqual(len(self.table.players), 3)
        
        # Test that side_pots is initialized
        self.assertIsInstance(self.table.side_pots, list)
        self.assertEqual(len(self.table.side_pots), 0)  # Initially empty


class TestPokerGameFlow(unittest.TestCase):
    """Tests de flujo completo del juego de poker"""
    
    def setUp(self):
        self.table = PokerTable(small_blind=10, big_blind=20)
        
        # Add 3 players for testing
        self.table.add_player("Alice", 1000, True)
        self.table.add_player("Bob", 1000, False)
        self.table.add_player("Charlie", 1000, False)
    
    def test_full_hand_flow(self):
        """Test a complete hand from start to finish"""
        # Initial state
        self.assertEqual(self.table.phase, GamePhase.WAITING)
        
        # Start hand
        self.table.start_new_hand()
        self.assertEqual(self.table.phase, GamePhase.PRE_FLOP)
        
        # Check that players have cards
        for player in self.table.players:
            if player.is_active:
                self.assertEqual(len(player.hand), 2)
        
        # Check blinds are posted
        self.assertGreater(self.table.pot, 0)
    
    def test_player_actions_preflop(self):
        """Test player actions in pre-flop phase"""
        self.table.start_new_hand()
        self.assertEqual(self.table.phase, GamePhase.PRE_FLOP)
        
        current_player = self.table.current_player
        valid_actions = self.table.get_valid_actions(current_player)
        
        # Should have some valid actions
        self.assertGreater(len(valid_actions), 0)
        
        # Fold action should always be available (except maybe for all-in scenarios)
        if self.table.players[current_player].chips > 0:
            self.assertIn(PlayerAction.FOLD, valid_actions)
    
    def test_betting_round_completion(self):
        """Test completion of a betting round"""
        self.table.start_new_hand()
        
        # Simulate all players calling or folding to complete betting round
        while not self.table.betting_round_complete:
            current_player = self.table.current_player
            valid_actions = self.table.get_valid_actions(current_player)
            
            if valid_actions:
                # Simple strategy: call if possible, otherwise fold
                if PlayerAction.CALL in valid_actions:
                    result = self.table.execute_action(current_player, PlayerAction.CALL, 0)
                elif PlayerAction.CHECK in valid_actions:
                    result = self.table.execute_action(current_player, PlayerAction.CHECK, 0)
                else:
                    result = self.table.execute_action(current_player, PlayerAction.FOLD, 0)
                
                self.assertTrue(result)  # Action should be successful
            else:
                break


if __name__ == '__main__':
    unittest.main(verbosity=2)