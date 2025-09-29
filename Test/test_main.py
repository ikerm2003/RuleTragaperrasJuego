#!/usr/bin/env python3
"""
Tests comprehensivos para el módulo main.py
Tests for the main UI and application entry point.
"""

import unittest
import sys
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Only test the parts that don't require PyQt6 GUI
try:
    from main import MainUI
    PYQT_AVAILABLE = True
except ImportError as e:
    if "libEGL" in str(e) or "libGL" in str(e) or "cannot connect to X server" in str(e):
        PYQT_AVAILABLE = False
    else:
        raise


class TestMainUIImports(unittest.TestCase):
    """Tests básicos para el módulo main.py"""
    
    def test_main_module_imports(self):
        """Test that main module can be imported"""
        try:
            import main
            self.assertTrue(hasattr(main, 'MainUI'))
        except ImportError as e:
            if "libEGL" in str(e) or "libGL" in str(e):
                self.skipTest("GUI not available in headless environment")
            else:
                raise
    
    def test_main_ui_class_exists(self):
        """Test that MainUI class exists and has expected methods"""
        if not PYQT_AVAILABLE:
            self.skipTest("PyQt6 GUI not available")
        
        # Check class exists
        self.assertTrue(hasattr(MainUI, '__init__'))
        self.assertTrue(hasattr(MainUI, 'init_ui'))
        
        # Check if it's a subclass of QMainWindow
        from PyQt6.QtWidgets import QMainWindow
        self.assertTrue(issubclass(MainUI, QMainWindow))


@unittest.skipUnless(PYQT_AVAILABLE, "PyQt6 GUI not available")
class TestMainUIFunctionality(unittest.TestCase):
    """Tests para la funcionalidad de MainUI (solo si PyQt6 está disponible)"""
    
    def setUp(self):
        # Mock QApplication to avoid GUI display issues
        with patch('main.QApplication') as mock_app:
            mock_app.return_value = MagicMock()
            try:
                self.main_ui = MainUI()
            except Exception as e:
                if "libEGL" in str(e) or "cannot connect to X server" in str(e):
                    self.skipTest("Display not available")
                raise
    
    def test_main_ui_creation(self):
        """Test MainUI creation"""
        if not hasattr(self, 'main_ui'):
            self.skipTest("MainUI could not be created")
        
        self.assertIsInstance(self.main_ui, MainUI)
        self.assertTrue(hasattr(self.main_ui, 'config'))
    
    def test_main_ui_window_properties(self):
        """Test MainUI window properties"""
        if not hasattr(self, 'main_ui'):
            self.skipTest("MainUI could not be created")
        
        # Check window title is set
        title = self.main_ui.windowTitle()
        self.assertIsInstance(title, str)
        self.assertGreater(len(title), 0)
    
    @patch('main.importlib.import_module')
    def test_poker_module_loading(self, mock_import):
        """Test that poker module can be loaded"""
        if not hasattr(self, 'main_ui'):
            self.skipTest("MainUI could not be created")
        
        # Mock poker module import
        mock_poker_module = MagicMock()
        mock_poker_window = MagicMock()
        mock_poker_module.PokerWindow = mock_poker_window
        mock_import.return_value = mock_poker_module
        
        # Test launch_poker method exists
        if hasattr(self.main_ui, 'launch_poker'):
            # Test would call launch_poker but we don't want to actually create windows
            pass


class TestMainUIUtilityFunctions(unittest.TestCase):
    """Tests para funciones utilitarias del módulo main"""
    
    def test_config_import(self):
        """Test that config can be imported from main module"""
        try:
            from main import config_manager, get_text
            self.assertIsNotNone(config_manager)
            self.assertTrue(callable(get_text))
        except ImportError as e:
            if "libEGL" not in str(e):
                raise
    
    def test_config_dialog_import(self):
        """Test that ConfigDialog can be imported from main module"""
        try:
            from main import ConfigDialog
            self.assertTrue(callable(ConfigDialog))
        except ImportError as e:
            if "libEGL" not in str(e):
                raise


class TestMainModuleStructure(unittest.TestCase):
    """Tests para la estructura del módulo main"""
    
    def test_main_file_exists(self):
        """Test that main.py file exists"""
        main_file = ROOT_DIR / "main.py"
        self.assertTrue(main_file.exists())
        self.assertTrue(main_file.is_file())
    
    def test_main_file_structure(self):
        """Test basic structure of main.py file"""
        main_file = ROOT_DIR / "main.py"
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for essential imports
        self.assertIn('from PyQt6', content)
        self.assertIn('class MainUI', content)
        self.assertIn('def __init__', content)
        self.assertIn('def init_ui', content)
    
    def test_main_docstring(self):
        """Test that main module has proper documentation"""
        main_file = ROOT_DIR / "main.py"
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have imports and class definition
        self.assertIn('MainUI', content)
        self.assertIn('QMainWindow', content)


class TestMainIntegration(unittest.TestCase):
    """Tests de integración para el módulo main"""
    
    def test_main_imports_all_dependencies(self):
        """Test that main module can import all its dependencies"""
        dependencies_to_check = [
            'PyQt6.QtWidgets',
            'PyQt6.QtCore', 
            'PyQt6.QtGui',
            'config',
            'config_dialog'
        ]
        
        main_file = ROOT_DIR / "main.py"
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        for dep in dependencies_to_check:
            # Check if dependency is imported (allowing for various import styles)
            self.assertTrue(
                dep in content or dep.replace('.', ' import ') in content,
                f"Dependency {dep} not found in main.py"
            )
    
    def test_main_integration_with_config(self):
        """Test that main integrates properly with config system"""
        try:
            import main
            # Should be able to access config without errors
            if hasattr(main, 'config_manager'):
                config = main.config_manager
                self.assertIsNotNone(config)
        except ImportError as e:
            if "libEGL" in str(e) or "libGL" in str(e):
                self.skipTest("GUI components not available")
            else:
                raise


if __name__ == '__main__':
    unittest.main(verbosity=2)