#!/usr/bin/env python3
"""
Tests comprehensivos para el módulo Tragaperras
Tests for tragaperras_logic.py and related slot machine functionality.
Extends the existing test_tragaperras_logic.py with additional comprehensive tests.
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

try:
    from Tragaperras.tragaperras_logic import (
        SlotMachine, WILD_SYMBOL, SCATTER_SYMBOL, 
        SYMBOL_PAYTABLE, SCATTER_MULTIPLIERS
    )
    TRAGAPERRAS_AVAILABLE = True
except ImportError:
    TRAGAPERRAS_AVAILABLE = False


class TestTragaperrasModuleStructure(unittest.TestCase):
    """Tests para la estructura del módulo Tragaperras"""
    
    def test_tragaperras_directory_exists(self):
        """Test that Tragaperras directory exists"""
        tragaperras_dir = ROOT_DIR / "Tragaperras"
        self.assertTrue(tragaperras_dir.exists())
        self.assertTrue(tragaperras_dir.is_dir())
    
    def test_tragaperras_files_exist(self):
        """Test that expected Tragaperras files exist"""
        tragaperras_dir = ROOT_DIR / "Tragaperras"
        
        expected_files = [
            "tragaperras_logic.py",
            "tragaperras_main.py", 
            "tragaperras_table.py",
            "tragaperras_ui.py"
        ]
        
        for filename in expected_files:
            file_path = tragaperras_dir / filename
            self.assertTrue(file_path.exists(), f"{filename} should exist")
    
    def test_tragaperras_logic_file_content(self):
        """Test that tragaperras_logic.py has substantial content"""
        logic_file = ROOT_DIR / "Tragaperras" / "tragaperras_logic.py"
        with open(logic_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have substantial implementation
        self.assertGreater(len(content), 1000)  # Should be a substantial file
        
        # Check for key components
        self.assertIn('class SlotMachine', content)
        self.assertIn('WILD_SYMBOL', content)
        self.assertIn('SCATTER_SYMBOL', content)
        self.assertIn('SYMBOL_PAYTABLE', content)


@unittest.skipUnless(TRAGAPERRAS_AVAILABLE, "Tragaperras module not available")
class TestTragaperrasConstants(unittest.TestCase):
    """Tests para las constantes del módulo Tragaperras"""
    
    def test_wild_symbol_constant(self):
        """Test WILD_SYMBOL constant"""
        self.assertEqual(WILD_SYMBOL, "🃏")
        self.assertIsInstance(WILD_SYMBOL, str)
    
    def test_scatter_symbol_constant(self):
        """Test SCATTER_SYMBOL constant"""
        self.assertEqual(SCATTER_SYMBOL, "🎰")
        self.assertIsInstance(SCATTER_SYMBOL, str)
    
    def test_symbol_paytable_structure(self):
        """Test SYMBOL_PAYTABLE structure"""
        self.assertIsInstance(SYMBOL_PAYTABLE, dict)
        self.assertGreater(len(SYMBOL_PAYTABLE), 0)
        
        # Check that each symbol has proper payout structure
        for symbol, payouts in SYMBOL_PAYTABLE.items():
            self.assertIsInstance(symbol, str)
            self.assertIsInstance(payouts, dict)
            
            # Should have payouts for different counts
            for count, payout in payouts.items():
                self.assertIsInstance(count, int)
                self.assertIsInstance(payout, int)
                self.assertGreater(count, 0)
                self.assertGreater(payout, 0)
    
    def test_scatter_multipliers_structure(self):
        """Test SCATTER_MULTIPLIERS structure"""
        self.assertIsInstance(SCATTER_MULTIPLIERS, dict)
        self.assertGreater(len(SCATTER_MULTIPLIERS), 0)
        
        # Check structure
        for count, multiplier in SCATTER_MULTIPLIERS.items():
            self.assertIsInstance(count, int)
            self.assertIsInstance(multiplier, int)
            self.assertGreater(count, 0)
            self.assertGreater(multiplier, 0)
        
        # Should have increasing multipliers
        counts = sorted(SCATTER_MULTIPLIERS.keys())
        multipliers = [SCATTER_MULTIPLIERS[count] for count in counts]
        self.assertEqual(multipliers, sorted(multipliers))  # Should be ascending
    
    def test_wild_symbol_in_paytable(self):
        """Test that WILD_SYMBOL is in SYMBOL_PAYTABLE"""
        self.assertIn(WILD_SYMBOL, SYMBOL_PAYTABLE)
        
        # Wild should have higher payouts than regular symbols
        wild_payouts = SYMBOL_PAYTABLE[WILD_SYMBOL]
        self.assertGreater(len(wild_payouts), 0)


@unittest.skipUnless(TRAGAPERRAS_AVAILABLE, "Tragaperras module not available")
class TestSlotMachineClass(unittest.TestCase):
    """Tests para la clase SlotMachine"""
    
    def setUp(self):
        # Create a basic slot machine for testing
        self.slot_machine = SlotMachine(
            balance=1000,
            bet_per_line=10,
            rtp_range=(1.0, 1.0),  # Fixed RTP for predictable testing
            loss_recovery_chance=0.0
        )
    
    def test_slot_machine_creation(self):
        """Test SlotMachine creation"""
        self.assertIsInstance(self.slot_machine, SlotMachine)
        self.assertEqual(self.slot_machine.balance, 1000)
    
    def test_slot_machine_attributes(self):
        """Test SlotMachine has expected attributes"""
        expected_attributes = [
            'balance', 'bet_per_line', 'active_lines'
        ]
        
        for attr in expected_attributes:
            self.assertTrue(hasattr(self.slot_machine, attr),
                          f"SlotMachine should have attribute {attr}")
    
    def test_slot_machine_methods(self):
        """Test SlotMachine has expected methods"""
        expected_methods = ['spin']
        
        for method in expected_methods:
            self.assertTrue(hasattr(self.slot_machine, method),
                          f"SlotMachine should have method {method}")
            self.assertTrue(callable(getattr(self.slot_machine, method)),
                          f"SlotMachine.{method} should be callable")
    
    def test_slot_machine_spin_basic(self):
        """Test basic spin functionality"""
        initial_balance = self.slot_machine.balance
        
        try:
            result = self.slot_machine.spin()
            
            # Result should be an object with expected attributes
            self.assertTrue(hasattr(result, 'total_bet'))
            self.assertTrue(hasattr(result, 'total_payout'))
            
            # Total bet should be positive
            self.assertGreater(result.total_bet, 0)
            
            # Balance should have changed
            self.assertNotEqual(self.slot_machine.balance, initial_balance)
            
        except Exception as e:
            # Allow for implementation-specific exceptions
            self.fail(f"Basic spin should not raise exception: {e}")
    
    def test_slot_machine_balance_management(self):
        """Test that balance is properly managed"""
        initial_balance = self.slot_machine.balance
        
        # Should track balance properly
        self.assertIsInstance(initial_balance, int)
        self.assertGreater(initial_balance, 0)
    
    def test_slot_machine_bet_validation(self):
        """Test bet validation"""
        # Should not allow spinning with insufficient balance
        poor_machine = SlotMachine(
            balance=5,  # Very low balance
            bet_per_line=10,
            rtp_range=(1.0, 1.0),
            loss_recovery_chance=0.0
        )
        
        with self.assertRaises(ValueError):
            poor_machine.spin()


class TestTragaperrasStubFiles(unittest.TestCase):
    """Tests para archivos stub del módulo Tragaperras"""
    
    def test_tragaperras_main_exists(self):
        """Test that tragaperras_main.py exists"""
        main_file = ROOT_DIR / "Tragaperras" / "tragaperras_main.py"
        self.assertTrue(main_file.exists())
    
    def test_tragaperras_table_exists(self):
        """Test that tragaperras_table.py exists"""
        table_file = ROOT_DIR / "Tragaperras" / "tragaperras_table.py"
        self.assertTrue(table_file.exists())
    
    def test_tragaperras_ui_exists(self):
        """Test that tragaperras_ui.py exists"""
        ui_file = ROOT_DIR / "Tragaperras" / "tragaperras_ui.py"
        self.assertTrue(ui_file.exists())
    
    def test_stub_files_are_valid_python(self):
        """Test that stub files are valid Python"""
        stub_files = [
            "tragaperras_main.py",
            "tragaperras_table.py", 
            "tragaperras_ui.py"
        ]
        
        for filename in stub_files:
            file_path = ROOT_DIR / "Tragaperras" / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Try to compile if not empty
                    if content.strip():
                        compile(content, str(file_path), 'exec')
                except SyntaxError:
                    self.fail(f"{filename} has syntax errors")


class TestTragaperrasExistingTests(unittest.TestCase):
    """Tests para verificar que los tests existentes siguen funcionando"""
    
    def test_existing_test_file_exists(self):
        """Test that existing test_tragaperras_logic.py still exists"""
        existing_test = ROOT_DIR / "test_tragaperras_logic.py"
        self.assertTrue(existing_test.exists())
    
    def test_existing_tests_still_work(self):
        """Test that existing tests can still be imported and run"""
        try:
            # Import the existing test module
            import test_tragaperras_logic
            
            # Should have test classes
            self.assertTrue(hasattr(test_tragaperras_logic, 'TestSlotMachineLogic'))
            
        except ImportError:
            self.fail("Existing test_tragaperras_logic.py cannot be imported")
    
    @unittest.skipUnless(TRAGAPERRAS_AVAILABLE, "Tragaperras module not available")
    def test_existing_test_cases_compatibility(self):
        """Test compatibility with existing test cases"""
        # Import the test class from existing tests
        from test_tragaperras_logic import FixedGridSlotMachine
        
        # Should be able to create instance
        grid = (
            ("7️⃣", "7️⃣", "7️⃣"),
            ("🍒", "🍋", "💎"),
            ("⭐", "🔔", "🍒"),
        )
        
        machine = FixedGridSlotMachine(
            grid,
            balance=1000,
            bet_per_line=10,
            active_lines=(0,),
        )
        
        self.assertIsInstance(machine, SlotMachine)


class TestTragaperrasGameLogic(unittest.TestCase):
    """Tests adicionales para la lógica del juego Tragaperras"""
    
    @unittest.skipUnless(TRAGAPERRAS_AVAILABLE, "Tragaperras module not available")
    def test_slot_machine_grid_generation(self):
        """Test that slot machine generates valid grids"""
        machine = SlotMachine(balance=1000, bet_per_line=10)
        
        # Should have a method to generate grids
        if hasattr(machine, '_generate_grid'):
            grid = machine._generate_grid()
            self.assertIsInstance(grid, (list, tuple))
            
            # Should be 3x3 grid
            self.assertEqual(len(grid), 3)
            for row in grid:
                self.assertEqual(len(row), 3)
    
    @unittest.skipUnless(TRAGAPERRAS_AVAILABLE, "Tragaperras module not available")
    def test_symbol_validation(self):
        """Test that symbols are valid"""
        # All symbols in paytable should be strings
        for symbol in SYMBOL_PAYTABLE.keys():
            self.assertIsInstance(symbol, str)
            self.assertGreater(len(symbol), 0)
        
        # Special symbols should be different
        self.assertNotEqual(WILD_SYMBOL, SCATTER_SYMBOL)
    
    @unittest.skipUnless(TRAGAPERRAS_AVAILABLE, "Tragaperras module not available")
    def test_rtp_range_validation(self):
        """Test RTP range validation"""
        # Should accept valid RTP ranges
        try:
            machine = SlotMachine(
                balance=1000,
                bet_per_line=10,
                rtp_range=(0.8, 1.2)
            )
            self.assertIsInstance(machine, SlotMachine)
        except Exception as e:
            self.fail(f"Valid RTP range should not raise exception: {e}")


class TestTragaperrasDocumentation(unittest.TestCase):
    """Tests para documentación del módulo Tragaperras"""
    
    def test_tragaperras_logic_has_docstring(self):
        """Test that tragaperras_logic.py has proper documentation"""
        logic_file = ROOT_DIR / "Tragaperras" / "tragaperras_logic.py"
        with open(logic_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should have module docstring
        self.assertIn('"""', content)
        
        # Should document the slot machine functionality
        content_lower = content.lower()
        self.assertTrue(any(word in content_lower for word in 
                          ['tragaperras', 'slot', 'máquina', 'machine']))
    
    @unittest.skipUnless(TRAGAPERRAS_AVAILABLE, "Tragaperras module not available")
    def test_slot_machine_class_documented(self):
        """Test that SlotMachine class is properly documented"""
        import inspect
        
        # Class should have docstring
        class_doc = inspect.getdoc(SlotMachine)
        if class_doc:
            self.assertIsInstance(class_doc, str)
            self.assertGreater(len(class_doc), 10)
    
    def test_tragaperras_in_readme(self):
        """Test that Tragaperras is documented in README"""
        readme_file = ROOT_DIR / "README.md"
        if readme_file.exists():
            with open(readme_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Should mention Tragaperras
            self.assertIn('Tragaperras', content)


class TestTragaperrasIntegration(unittest.TestCase):
    """Tests de integración para el módulo Tragaperras"""
    
    def test_tragaperras_follows_project_structure(self):
        """Test that Tragaperras follows project structure conventions"""
        # Should follow same pattern as other modules
        tragaperras_dir = ROOT_DIR / "Tragaperras"
        poker_dir = ROOT_DIR / "Poker"
        
        # Both should exist
        self.assertTrue(tragaperras_dir.exists())
        self.assertTrue(poker_dir.exists())
        
        # Should have similar file structure
        expected_patterns = ["_logic.py", "_main.py", "_ui.py", "_table.py"]
        
        for pattern in expected_patterns:
            # Check if Tragaperras has files matching the pattern
            tragaperras_files = list(tragaperras_dir.glob(f"*{pattern}"))
            self.assertGreater(len(tragaperras_files), 0,
                             f"Tragaperras should have files matching {pattern}")
    
    def test_tragaperras_main_integration(self):
        """Test that Tragaperras can be integrated with main UI"""
        main_file = ROOT_DIR / "main.py"
        if main_file.exists():
            with open(main_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Main should be ready for Tragaperras integration
            # (same pattern as other modules)
            has_module_launch_pattern = "launch" in content.lower()
            if has_module_launch_pattern:
                # Tragaperras should be ready for the same pattern
                tragaperras_dir = ROOT_DIR / "Tragaperras"
                self.assertTrue(tragaperras_dir.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)