
"""
Comprehensive tests for Ruleta game logic implementation
Tests the RouletteGame, Bet, and BetType classes
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from Ruleta.ruleta_logic import RouletteGame, Bet, BetType, RED_NUMBERS, BLACK_NUMBERS
    RULETA_LOGIC_AVAILABLE = True
except ImportError:
    RULETA_LOGIC_AVAILABLE = False


@unittest.skipUnless(RULETA_LOGIC_AVAILABLE, "Ruleta logic not available")
class TestRouletteConstants(unittest.TestCase):
    """Tests for roulette constants"""
    
    def test_red_numbers_count(self):
        """Test that there are 18 red numbers"""
        self.assertEqual(len(RED_NUMBERS), 18)
    
    def test_black_numbers_count(self):
        """Test that there are 18 black numbers"""
        self.assertEqual(len(BLACK_NUMBERS), 18)
    
    def test_no_overlap(self):
        """Test that red and black don't overlap"""
        overlap = RED_NUMBERS.intersection(BLACK_NUMBERS)
        self.assertEqual(len(overlap), 0)
    
    def test_all_numbers_covered(self):
        """Test that all numbers 1-36 are either red or black"""
        all_colored = RED_NUMBERS.union(BLACK_NUMBERS)
        self.assertEqual(len(all_colored), 36)
        for i in range(1, 37):
            self.assertIn(i, all_colored)


@unittest.skipUnless(RULETA_LOGIC_AVAILABLE, "Ruleta logic not available")
class TestBet(unittest.TestCase):
    """Tests for Bet class"""
    
    def test_bet_creation(self):
        """Test creating a bet"""
        bet = Bet(BetType.STRAIGHT_UP, [17], 10)
        self.assertEqual(bet.bet_type, BetType.STRAIGHT_UP)
        self.assertEqual(bet.numbers, [17])
        self.assertEqual(bet.amount, 10)
    
    def test_straight_up_payout(self):
        """Test straight up bet payout (35:1)"""
        bet = Bet(BetType.STRAIGHT_UP, [17], 10)
        self.assertEqual(bet.get_payout_multiplier(), 35)
        # Winning payout includes original bet
        self.assertEqual(bet.calculate_payout(17), 360)  # 10 * 35 + 10
    
    def test_split_payout(self):
        """Test split bet payout (17:1)"""
        bet = Bet(BetType.SPLIT, [17, 18], 10)
        self.assertEqual(bet.get_payout_multiplier(), 17)
    
    def test_dozen_payout(self):
        """Test dozen bet payout (2:1)"""
        bet = Bet(BetType.DOZEN, list(range(1, 13)), 10)
        self.assertEqual(bet.get_payout_multiplier(), 2)
    
    def test_even_money_payout(self):
        """Test even money bets (1:1)"""
        for bet_type in [BetType.RED, BetType.BLACK, BetType.EVEN, 
                         BetType.ODD, BetType.LOW, BetType.HIGH]:
            bet = Bet(bet_type, [1, 2, 3], 10)
            self.assertEqual(bet.get_payout_multiplier(), 1)
    
    def test_bet_check_win(self):
        """Test checking if a bet wins"""
        bet = Bet(BetType.STRAIGHT_UP, [17], 10)
        self.assertTrue(bet.check_win(17))
        self.assertFalse(bet.check_win(18))
    
    def test_losing_bet_payout(self):
        """Test that losing bet returns 0"""
        bet = Bet(BetType.STRAIGHT_UP, [17], 10)
        self.assertEqual(bet.calculate_payout(18), 0)


@unittest.skipUnless(RULETA_LOGIC_AVAILABLE, "Ruleta logic not available")
class TestRouletteGame(unittest.TestCase):
    """Tests for RouletteGame class"""
    
    def setUp(self):
        """Set up a game for testing"""
        self.game = RouletteGame(initial_balance=1000)
    
    def test_game_initialization(self):
        """Test game initializes correctly"""
        self.assertEqual(self.game.balance, 1000)
        self.assertEqual(len(self.game.bets), 0)
        self.assertIsNone(self.game.last_winning_number)
        self.assertEqual(len(self.game.history), 0)
    
    def test_get_number_color(self):
        """Test getting color of numbers"""
        self.assertEqual(self.game.get_number_color(0), "green")
        self.assertEqual(self.game.get_number_color(1), "red")
        self.assertEqual(self.game.get_number_color(2), "black")
        self.assertEqual(self.game.get_number_color(18), "red")
    
    def test_place_bet(self):
        """Test placing a bet"""
        bet = self.game.create_straight_up_bet(17, 10)
        result = self.game.place_bet(bet)
        self.assertTrue(result)
        self.assertEqual(self.game.balance, 990)
        self.assertEqual(len(self.game.bets), 1)
    
    def test_place_bet_insufficient_balance(self):
        """Test placing bet with insufficient balance"""
        bet = self.game.create_straight_up_bet(17, 2000)
        result = self.game.place_bet(bet)
        self.assertFalse(result)
        self.assertEqual(self.game.balance, 1000)
    
    def test_clear_bets(self):
        """Test clearing all bets returns money"""
        bet = self.game.create_straight_up_bet(17, 100)
        self.game.place_bet(bet)
        self.assertEqual(self.game.balance, 900)
        
        self.game.clear_bets()
        self.assertEqual(self.game.balance, 1000)
        self.assertEqual(len(self.game.bets), 0)
    
    def test_spin_updates_history(self):
        """Test that spinning updates history"""
        bet = self.game.create_straight_up_bet(17, 10)
        self.game.place_bet(bet)
        
        winning_number, winnings = self.game.spin()
        
        self.assertIsNotNone(winning_number)
        self.assertGreaterEqual(winning_number, 0)
        self.assertLessEqual(winning_number, 36)
        self.assertEqual(len(self.game.history), 1)
        self.assertEqual(self.game.last_winning_number, winning_number)


@unittest.skipUnless(RULETA_LOGIC_AVAILABLE, "Ruleta logic not available")
class TestRouletteBetCreation(unittest.TestCase):
    """Tests for bet creation methods"""
    
    def setUp(self):
        """Set up a game for testing"""
        self.game = RouletteGame(initial_balance=1000)
    
    def test_create_straight_up_bet(self):
        """Test creating straight up bet"""
        bet = self.game.create_straight_up_bet(17, 10)
        self.assertIsNotNone(bet)
        self.assertEqual(bet.bet_type, BetType.STRAIGHT_UP)
        self.assertEqual(bet.numbers, [17])
        self.assertEqual(bet.amount, 10)
    
    def test_create_invalid_straight_up(self):
        """Test creating invalid straight up bet"""
        bet = self.game.create_straight_up_bet(37, 10)  # Invalid number
        self.assertIsNone(bet)
    
    def test_create_split_bet(self):
        """Test creating split bet"""
        bet = self.game.create_split_bet([17, 18], 10)
        self.assertIsNotNone(bet)
        self.assertEqual(bet.bet_type, BetType.SPLIT)
        self.assertEqual(len(bet.numbers), 2)
    
    def test_create_street_bet(self):
        """Test creating street bet"""
        bet = self.game.create_street_bet(1, 10)
        self.assertIsNotNone(bet)
        self.assertEqual(bet.bet_type, BetType.STREET)
        self.assertEqual(bet.numbers, [1, 2, 3])
    
    def test_create_dozen_bet(self):
        """Test creating dozen bet"""
        bet = self.game.create_dozen_bet(1, 10)
        self.assertIsNotNone(bet)
        self.assertEqual(bet.bet_type, BetType.DOZEN)
        self.assertEqual(len(bet.numbers), 12)
        self.assertEqual(bet.numbers[0], 1)
        self.assertEqual(bet.numbers[-1], 12)
    
    def test_create_column_bet(self):
        """Test creating column bet"""
        bet = self.game.create_column_bet(1, 10)
        self.assertIsNotNone(bet)
        self.assertEqual(bet.bet_type, BetType.COLUMN)
        self.assertEqual(len(bet.numbers), 12)
        # Column 1: 1, 4, 7, 10, ..., 34
        self.assertEqual(bet.numbers[0], 1)
    
    def test_create_color_bet(self):
        """Test creating color bet"""
        red_bet = self.game.create_color_bet("red", 10)
        self.assertIsNotNone(red_bet)
        self.assertEqual(red_bet.bet_type, BetType.RED)
        self.assertEqual(len(red_bet.numbers), 18)
        
        black_bet = self.game.create_color_bet("black", 10)
        self.assertIsNotNone(black_bet)
        self.assertEqual(black_bet.bet_type, BetType.BLACK)
    
    def test_create_even_odd_bet(self):
        """Test creating even/odd bet"""
        even_bet = self.game.create_even_odd_bet(True, 10)
        self.assertEqual(even_bet.bet_type, BetType.EVEN)
        self.assertEqual(len(even_bet.numbers), 18)
        
        odd_bet = self.game.create_even_odd_bet(False, 10)
        self.assertEqual(odd_bet.bet_type, BetType.ODD)
        self.assertEqual(len(odd_bet.numbers), 18)
    
    def test_create_high_low_bet(self):
        """Test creating high/low bet"""
        high_bet = self.game.create_high_low_bet(True, 10)
        self.assertEqual(high_bet.bet_type, BetType.HIGH)
        self.assertEqual(high_bet.numbers, list(range(19, 37)))
        
        low_bet = self.game.create_high_low_bet(False, 10)
        self.assertEqual(low_bet.bet_type, BetType.LOW)
        self.assertEqual(low_bet.numbers, list(range(1, 19)))


@unittest.skipUnless(RULETA_LOGIC_AVAILABLE, "Ruleta logic not available")
class TestRouletteStatistics(unittest.TestCase):
    """Tests for roulette statistics"""
    
    def setUp(self):
        """Set up a game for testing"""
        self.game = RouletteGame(initial_balance=1000)
    
    def test_statistics_empty_history(self):
        """Test statistics with empty history"""
        stats = self.game.get_statistics()
        self.assertEqual(stats['total_spins'], 0)
    
    def test_statistics_with_history(self):
        """Test statistics after some spins"""
        # Manually add to history for testing
        self.game.history = [0, 1, 2, 3, 4, 5]  # 0=green, 1,3,5=red, 2,4=black
        
        stats = self.game.get_statistics()
        self.assertEqual(stats['total_spins'], 6)
        self.assertEqual(stats['zero_count'], 1)
        self.assertEqual(stats['red_count'], 3)
        self.assertEqual(stats['black_count'], 2)


if __name__ == '__main__':
    unittest.main()
