
"""
Tests for keyboard shortcuts functionality
Tests the keyboard shortcut system in the main UI
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestKeyboardShortcutsConfiguration(unittest.TestCase):
    """Tests for keyboard shortcuts configuration"""
    
    def test_main_module_has_shortcut_imports(self):
        """Test that main module imports necessary classes for shortcuts"""
        try:
            import main
            # Check that main.py file contains QShortcut import
            main_file = ROOT_DIR / "main.py"
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.assertIn('QShortcut', content)
            self.assertIn('QKeySequence', content)
        except ImportError as e:
            if "libEGL" in str(e) or "libGL" in str(e) or "cannot connect to X server" in str(e):
                self.skipTest("GUI not available in headless environment")
            else:
                raise
    
    def test_main_has_setup_shortcuts_method(self):
        """Test that MainUI has setup_shortcuts method"""
        try:
            import main
            self.assertTrue(hasattr(main.MainUI, 'setup_shortcuts'))
        except ImportError as e:
            if "libEGL" in str(e) or "libGL" in str(e):
                self.skipTest("GUI not available")
            else:
                raise
    
    def test_main_has_toggle_fullscreen_method(self):
        """Test that MainUI has toggle_fullscreen method"""
        try:
            import main
            self.assertTrue(hasattr(main.MainUI, 'toggle_fullscreen'))
        except ImportError as e:
            if "libEGL" in str(e) or "libGL" in str(e):
                self.skipTest("GUI not available")
            else:
                raise


class TestKeyboardShortcutsTranslations(unittest.TestCase):
    """Tests for keyboard shortcuts translations"""
    
    def test_shortcuts_translation_keys_exist(self):
        """Test that translation keys for shortcuts exist"""
        from config import TRANSLATIONS, Language
        
        required_keys = [
            'keyboard_shortcuts',
            'shortcuts_help',
        ]
        
        for lang in [Language.ENGLISH, Language.SPANISH]:
            for key in required_keys:
                self.assertIn(key, TRANSLATIONS[lang], 
                            f"Missing translation key '{key}' for {lang.value}")
    
    def test_shortcuts_help_text_content(self):
        """Test that shortcuts help text has expected content"""
        from config import get_text, Language
        
        # Check English
        help_text_en = get_text('shortcuts_help', Language.ENGLISH)
        self.assertIn('1-4', help_text_en)
        self.assertIn('F11', help_text_en)
        
        # Check Spanish
        help_text_es = get_text('shortcuts_help', Language.SPANISH)
        self.assertIn('1-4', help_text_es)
        self.assertIn('F11', help_text_es)


class TestKeyboardShortcutsDocumentation(unittest.TestCase):
    """Tests for keyboard shortcuts documentation"""
    
    def test_readme_mentions_shortcuts(self):
        """Test that README mentions keyboard shortcuts"""
        readme_file = ROOT_DIR / "README.md"
        if readme_file.exists():
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()
            
            # Should mention shortcuts or keyboard
            has_mention = any(word in content for word in [
                'shortcut', 'atajo', 'keyboard', 'teclado', 'tecla'
            ])
            self.assertTrue(has_mention, "README should mention keyboard shortcuts")


class TestKeyboardShortcutsIntegration(unittest.TestCase):
    """Integration tests for keyboard shortcuts"""
    
    def test_button_labels_include_shortcut_hints(self):
        """Test that game buttons show shortcut hints"""
        main_file = ROOT_DIR / "main.py"
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that buttons include numbers in their labels
        self.assertIn('(1)', content)
        self.assertIn('(2)', content)
        self.assertIn('(3)', content)
        self.assertIn('(4)', content)


if __name__ == '__main__':
    unittest.main(verbosity=2)
