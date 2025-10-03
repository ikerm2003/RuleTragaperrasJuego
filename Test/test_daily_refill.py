#!/usr/bin/env python3
"""
Tests for daily refill functionality
Tests the auto-refill system for player balance
"""

import unittest
import sys
import os
import json
from pathlib import Path
from datetime import datetime
import tempfile

# Add parent directory to path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import ConfigManager


class TestDailyRefillConfiguration(unittest.TestCase):
    """Tests for daily refill configuration"""
    
    def test_default_config_has_daily_refill_settings(self):
        """Test that default config includes daily refill settings"""
        from config import ConfigManager
        
        config = ConfigManager()
        
        # Check gameplay settings
        self.assertIsNotNone(config.get('gameplay', 'starting_balance'))
        self.assertIsNotNone(config.get('gameplay', 'daily_refill_enabled'))
        
        # Check player settings
        self.assertIsNotNone(config.get('player', 'current_balance'))
    
    def test_default_starting_balance(self):
        """Test that default starting balance is set"""
        config = ConfigManager()
        
        starting_balance = config.get('gameplay', 'starting_balance', 0)
        self.assertGreater(starting_balance, 0)
        self.assertEqual(starting_balance, 1000)
    
    def test_daily_refill_enabled_by_default(self):
        """Test that daily refill is enabled by default"""
        config = ConfigManager()
        
        daily_refill = config.get('gameplay', 'daily_refill_enabled', False)
        self.assertTrue(daily_refill)


class TestDailyRefillLogic(unittest.TestCase):
    """Tests for daily refill logic"""
    
    def setUp(self):
        """Set up temporary config for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.config = ConfigManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up temporary config file"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_check_daily_refill_method_exists(self):
        """Test that check_daily_refill method exists"""
        self.assertTrue(hasattr(self.config, 'check_daily_refill'))
    
    def test_first_login_no_refill(self):
        """Test that first login doesn't trigger refill"""
        # First login
        result = self.config.check_daily_refill()
        
        # Should not refill on first login (no previous date to compare)
        self.assertFalse(result)
    
    def test_same_day_no_refill(self):
        """Test that logging in same day doesn't trigger refill"""
        # First login
        self.config.check_daily_refill()
        
        # Reduce balance
        self.config.set_player_balance(500)
        
        # Same day login
        result = self.config.check_daily_refill()
        
        # Should not refill on same day
        self.assertFalse(result)
        self.assertEqual(self.config.get_player_balance(), 500)
    
    def test_new_day_with_low_balance_triggers_refill(self):
        """Test that new day with low balance triggers refill"""
        # Set yesterday's login
        yesterday = '2024-01-01'
        self.config.set('player', 'last_login', yesterday)
        self.config.set_player_balance(500)
        self.config.save_config()
        
        # New day login (today will be different from yesterday)
        result = self.config.check_daily_refill()
        
        # Should trigger refill
        self.assertTrue(result)
        self.assertEqual(self.config.get_player_balance(), 1000)
    
    def test_new_day_with_high_balance_no_refill(self):
        """Test that new day with balance above starting doesn't trigger refill"""
        # Set yesterday's login
        yesterday = '2024-01-01'
        self.config.set('player', 'last_login', yesterday)
        self.config.set_player_balance(2000)  # Above starting balance
        self.config.save_config()
        
        # New day login
        result = self.config.check_daily_refill()
        
        # Should not refill (balance is above starting balance)
        self.assertFalse(result)
        self.assertEqual(self.config.get_player_balance(), 2000)
    
    def test_disabled_daily_refill(self):
        """Test that disabled daily refill doesn't trigger"""
        # Disable daily refill
        self.config.set('gameplay', 'daily_refill_enabled', False)
        self.config.set('player', 'last_login', '2024-01-01')
        self.config.set_player_balance(500)
        self.config.save_config()
        
        # Try to trigger refill
        result = self.config.check_daily_refill()
        
        # Should not refill when disabled
        self.assertFalse(result)
        self.assertEqual(self.config.get_player_balance(), 500)


class TestPlayerBalanceMethods(unittest.TestCase):
    """Tests for player balance getter/setter methods"""
    
    def setUp(self):
        """Set up temporary config for testing"""
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.config = ConfigManager(self.temp_file.name)
    
    def tearDown(self):
        """Clean up temporary config file"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_get_player_balance_method_exists(self):
        """Test that get_player_balance method exists"""
        self.assertTrue(hasattr(self.config, 'get_player_balance'))
    
    def test_set_player_balance_method_exists(self):
        """Test that set_player_balance method exists"""
        self.assertTrue(hasattr(self.config, 'set_player_balance'))
    
    def test_default_player_balance(self):
        """Test default player balance"""
        balance = self.config.get_player_balance()
        self.assertEqual(balance, 1000)
    
    def test_set_and_get_player_balance(self):
        """Test setting and getting player balance"""
        self.config.set_player_balance(5000)
        balance = self.config.get_player_balance()
        self.assertEqual(balance, 5000)
    
    def test_player_balance_persists(self):
        """Test that player balance persists after save"""
        self.config.set_player_balance(7500)
        
        # Create new config instance with same file
        new_config = ConfigManager(self.temp_file.name)
        balance = new_config.get_player_balance()
        
        self.assertEqual(balance, 7500)


class TestDailyRefillTranslations(unittest.TestCase):
    """Tests for daily refill translations"""
    
    def test_refill_translation_keys_exist(self):
        """Test that translation keys for daily refill exist"""
        from config import TRANSLATIONS, Language
        
        required_keys = [
            'daily_refill_title',
            'daily_refill_message',
        ]
        
        for lang in [Language.ENGLISH, Language.SPANISH]:
            for key in required_keys:
                self.assertIn(key, TRANSLATIONS[lang], 
                            f"Missing translation key '{key}' for {lang.value}")
    
    def test_refill_message_has_placeholder(self):
        """Test that refill message has balance placeholder"""
        from config import get_text, Language
        
        # Check English
        message_en = get_text('daily_refill_message', Language.ENGLISH)
        self.assertIn('{balance}', message_en)
        
        # Check Spanish
        message_es = get_text('daily_refill_message', Language.SPANISH)
        self.assertIn('{balance}', message_es)


class TestDailyRefillIntegration(unittest.TestCase):
    """Integration tests for daily refill in main UI"""
    
    def test_main_ui_has_check_daily_refill_method(self):
        """Test that MainUI has check_daily_refill method"""
        try:
            import main
            self.assertTrue(hasattr(main.MainUI, 'check_daily_refill'))
        except ImportError as e:
            if "libEGL" in str(e) or "libGL" in str(e):
                self.skipTest("GUI not available")
            else:
                raise
    
    def test_main_ui_calls_check_daily_refill(self):
        """Test that MainUI __init__ includes daily refill check"""
        main_file = ROOT_DIR / "main.py"
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that check_daily_refill is called in __init__ or init_ui
        self.assertIn('check_daily_refill', content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
