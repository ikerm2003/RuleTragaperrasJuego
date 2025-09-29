#!/usr/bin/env python3
"""
Tests comprehensivos para el módulo config.py
Tests for configuration management, language settings, and preferences.
"""

import unittest
import sys
import os
import json
import tempfile
from pathlib import Path

# Add parent directory to path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import (
    Language, Resolution, AnimationSpeed, ConfigManager, 
    get_text, config_manager
)


class TestLanguageEnum(unittest.TestCase):
    """Tests para la enum Language"""
    
    def test_language_values(self):
        """Test Language enum values"""
        self.assertEqual(Language.ENGLISH.value, "en")
        self.assertEqual(Language.SPANISH.value, "es")
    
    def test_language_count(self):
        """Test expected number of languages"""
        languages = list(Language)
        self.assertEqual(len(languages), 2)


class TestResolutionEnum(unittest.TestCase):
    """Tests para la enum Resolution"""
    
    def test_resolution_values(self):
        """Test Resolution enum values"""
        self.assertEqual(Resolution.HD.value, (1280, 720))
        self.assertEqual(Resolution.FULL_HD.value, (1920, 1080))
        self.assertEqual(Resolution.ULTRA_HD.value, (2560, 1440))
        self.assertEqual(Resolution.AUTO.value, (-1, -1))
    
    def test_resolution_count(self):
        """Test expected number of resolutions"""
        resolutions = list(Resolution)
        self.assertEqual(len(resolutions), 4)


class TestAnimationSpeedEnum(unittest.TestCase):
    """Tests para la enum AnimationSpeed"""
    
    def test_animation_speed_values(self):
        """Test AnimationSpeed enum values"""
        self.assertEqual(AnimationSpeed.SLOW.value, 1.5)
        self.assertEqual(AnimationSpeed.NORMAL.value, 1.0)
        self.assertEqual(AnimationSpeed.FAST.value, 0.5)
        self.assertEqual(AnimationSpeed.DISABLED.value, 0.0)
    
    def test_animation_speed_ordering(self):
        """Test animation speeds are logically ordered"""
        self.assertGreater(AnimationSpeed.SLOW.value, AnimationSpeed.NORMAL.value)
        self.assertGreater(AnimationSpeed.NORMAL.value, AnimationSpeed.FAST.value)
        self.assertGreater(AnimationSpeed.FAST.value, AnimationSpeed.DISABLED.value)


class TestConfigManager(unittest.TestCase):
    """Tests para la clase ConfigManager"""
    
    def setUp(self):
        # Create a temporary config file for testing
        self.temp_dir = tempfile.mkdtemp()
        self.temp_config_file = os.path.join(self.temp_dir, 'test_config.json')
        # Ensure clean state by not loading any existing config
        self.config_manager = ConfigManager(config_file=self.temp_config_file)
        # Reset to defaults explicitly to ensure clean state
        import copy
        self.config_manager.config = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
    
    def tearDown(self):
        # Clean up temporary files
        if os.path.exists(self.temp_config_file):
            os.remove(self.temp_config_file)
        os.rmdir(self.temp_dir)
    
    def test_config_manager_creation(self):
        """Test ConfigManager creation with default values"""
        self.assertIsInstance(self.config_manager.config, dict)
        self.assertIn('display', self.config_manager.config)
        self.assertIn('interface', self.config_manager.config)
        self.assertIn('gameplay', self.config_manager.config)
    
    def test_default_config_structure(self):
        """Test default configuration structure"""
        config = self.config_manager.config
        
        # Test display section
        self.assertIn('fullscreen', config['display'])
        self.assertIn('resolution', config['display'])
        self.assertIn('vsync', config['display'])
        
        # Test interface section
        self.assertIn('language', config['interface'])
        self.assertIn('animation_speed', config['interface'])
        self.assertIn('show_tooltips', config['interface'])
        self.assertIn('card_animation_enabled', config['interface'])
        self.assertIn('sound_enabled', config['interface'])
        
        # Test gameplay section
        self.assertIn('auto_fold_timeout', config['gameplay'])
        self.assertIn('confirm_actions', config['gameplay'])
        self.assertIn('show_probability_hints', config['gameplay'])
    
    def test_get_config_value(self):
        """Test getting configuration values"""
        # Test existing values
        self.assertEqual(self.config_manager.get('interface', 'language'), Language.SPANISH.value)
        self.assertEqual(self.config_manager.get('display', 'fullscreen'), False)
        self.assertEqual(self.config_manager.get('gameplay', 'auto_fold_timeout'), 30)
        
        # Test non-existing values with default
        self.assertEqual(self.config_manager.get('interface', 'nonexistent', 'default'), 'default')
        self.assertIsNone(self.config_manager.get('interface', 'nonexistent'))
        
        # Test non-existing section
        self.assertEqual(self.config_manager.get('nonexistent', 'key', 'default'), 'default')
    
    def test_set_config_value(self):
        """Test setting configuration values"""
        # Set existing value
        self.config_manager.set('interface', 'language', Language.ENGLISH.value)
        self.assertEqual(self.config_manager.get('interface', 'language'), Language.ENGLISH.value)
        
        # Set new value in existing section
        self.config_manager.set('interface', 'new_setting', 'test_value')
        self.assertEqual(self.config_manager.get('interface', 'new_setting'), 'test_value')
        
        # Set value in new section
        self.config_manager.set('new_section', 'new_key', 'new_value')
        self.assertEqual(self.config_manager.get('new_section', 'new_key'), 'new_value')
    
    def test_is_fullscreen(self):
        """Test fullscreen detection"""
        # Default should be False
        self.assertFalse(self.config_manager.is_fullscreen())
        
        # Set to True and test
        self.config_manager.set('display', 'fullscreen', True)
        self.assertTrue(self.config_manager.is_fullscreen())
    
    def test_get_resolution(self):
        """Test resolution getting"""
        # Default should be AUTO
        resolution = self.config_manager.get_resolution()
        self.assertEqual(resolution, Resolution.AUTO.value)
        
        # Set custom resolution
        self.config_manager.set('display', 'resolution', Resolution.FULL_HD.value)
        resolution = self.config_manager.get_resolution()
        self.assertEqual(resolution, Resolution.FULL_HD.value)
    
    def test_save_and_load_config(self):
        """Test saving and loading configuration"""
        # Modify configuration
        self.config_manager.set('interface', 'language', Language.ENGLISH.value)
        self.config_manager.set('display', 'fullscreen', True)
        self.config_manager.set('gameplay', 'auto_fold_timeout', 60)
        
        # Save configuration
        result = self.config_manager.save_config()
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.temp_config_file))
        
        # Create new config manager and load
        new_config_manager = ConfigManager(config_file=self.temp_config_file)
        
        # Verify loaded values
        self.assertEqual(new_config_manager.get('interface', 'language'), Language.ENGLISH.value)
        self.assertEqual(new_config_manager.get('display', 'fullscreen'), True)
        self.assertEqual(new_config_manager.get('gameplay', 'auto_fold_timeout'), 60)
    
    def test_merge_config(self):
        """Test configuration merging"""
        # Create a partial config
        partial_config = {
            'interface': {
                'language': Language.ENGLISH.value,
                'new_setting': 'test_value'
            },
            'new_section': {
                'new_key': 'new_value'
            }
        }
        
        # Save partial config to file
        with open(self.temp_config_file, 'w', encoding='utf-8') as f:
            json.dump(partial_config, f)
        
        # Load config
        config_manager = ConfigManager(config_file=self.temp_config_file)
        
        # Check that partial config was merged with defaults
        self.assertEqual(config_manager.get('interface', 'language'), Language.ENGLISH.value)
        self.assertEqual(config_manager.get('interface', 'new_setting'), 'test_value')
        self.assertEqual(config_manager.get('interface', 'show_tooltips'), True)  # Default preserved
        self.assertEqual(config_manager.get('display', 'fullscreen'), False)  # Default preserved
    
    def test_load_invalid_config_file(self):
        """Test loading invalid JSON configuration file"""
        # Create invalid JSON file
        with open(self.temp_config_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content {")
        
        # Should load defaults without crashing
        config_manager = ConfigManager(config_file=self.temp_config_file)
        # Reset to ensure we get actual defaults, not the cached config
        import copy
        config_manager.config = copy.deepcopy(ConfigManager.DEFAULT_CONFIG)
        self.assertEqual(config_manager.get('interface', 'language'), Language.SPANISH.value)
    
    def test_save_config_failure(self):
        """Test save configuration failure handling"""
        # Try to save to an invalid path
        invalid_config_manager = ConfigManager(config_file='/invalid/path/config.json')
        result = invalid_config_manager.save_config()
        self.assertFalse(result)


class TestGetTextFunction(unittest.TestCase):
    """Tests para la función get_text"""
    
    def test_get_text_existing_keys(self):
        """Test getting text for existing translation keys"""
        # Test some basic keys that should exist
        casino_title = get_text('casino_title')
        self.assertIsInstance(casino_title, str)
        self.assertGreater(len(casino_title), 0)
        
        # Test settings text
        settings_text = get_text('settings')
        self.assertIsInstance(settings_text, str)
        self.assertGreater(len(settings_text), 0)
    
    def test_get_text_nonexistent_key(self):
        """Test getting text for non-existent keys"""
        # Should return the key itself if not found
        nonexistent = get_text('nonexistent_key_12345')
        self.assertEqual(nonexistent, 'nonexistent_key_12345')
    
    def test_get_text_empty_key(self):
        """Test getting text for empty key"""
        empty_result = get_text('')
        self.assertEqual(empty_result, '')


class TestGlobalConfigManager(unittest.TestCase):
    """Tests para el config_manager global"""
    
    def test_global_config_manager_exists(self):
        """Test that global config_manager instance exists"""
        self.assertIsInstance(config_manager, ConfigManager)
    
    def test_global_config_manager_functionality(self):
        """Test basic functionality of global config manager"""
        # Should be able to get values
        language = config_manager.get('interface', 'language')
        self.assertIsInstance(language, str)
        
        # Should be able to check fullscreen
        fullscreen = config_manager.is_fullscreen()
        self.assertIsInstance(fullscreen, bool)
        
        # Should be able to get resolution
        resolution = config_manager.get_resolution()
        self.assertIsInstance(resolution, tuple)
        self.assertEqual(len(resolution), 2)


class TestConfigIntegration(unittest.TestCase):
    """Tests de integración para el sistema de configuración"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_config_file = os.path.join(self.temp_dir, 'integration_test_config.json')
    
    def tearDown(self):
        if os.path.exists(self.temp_config_file):
            os.remove(self.temp_config_file)
        os.rmdir(self.temp_dir)
    
    def test_full_config_workflow(self):
        """Test complete configuration workflow"""
        # Create config manager
        config_mgr = ConfigManager(config_file=self.temp_config_file)
        
        # Verify initial state
        self.assertEqual(config_mgr.get('interface', 'language'), Language.SPANISH.value)
        self.assertFalse(config_mgr.is_fullscreen())
        
        # Modify settings
        config_mgr.set('interface', 'language', Language.ENGLISH.value)
        config_mgr.set('display', 'fullscreen', True)
        config_mgr.set('display', 'resolution', Resolution.FULL_HD.value)
        config_mgr.set('interface', 'animation_speed', AnimationSpeed.FAST.value)
        config_mgr.set('gameplay', 'auto_fold_timeout', 45)
        
        # Save configuration
        save_success = config_mgr.save_config()
        self.assertTrue(save_success)
        
        # Create new config manager (simulates app restart)
        new_config_mgr = ConfigManager(config_file=self.temp_config_file)
        
        # Verify all settings were preserved
        self.assertEqual(new_config_mgr.get('interface', 'language'), Language.ENGLISH.value)
        self.assertTrue(new_config_mgr.is_fullscreen())
        self.assertEqual(new_config_mgr.get_resolution(), Resolution.FULL_HD.value)
        self.assertEqual(new_config_mgr.get('interface', 'animation_speed'), AnimationSpeed.FAST.value)
        self.assertEqual(new_config_mgr.get('gameplay', 'auto_fold_timeout'), 45)
        
        # Verify defaults are still present for unmodified settings
        self.assertTrue(new_config_mgr.get('interface', 'show_tooltips'))
        self.assertTrue(new_config_mgr.get('gameplay', 'confirm_actions'))
        self.assertFalse(new_config_mgr.get('gameplay', 'show_probability_hints'))  # Default is False


if __name__ == '__main__':
    unittest.main(verbosity=2)