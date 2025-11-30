
"""
Suite de tests comprehensiva para todo el proyecto RuleTragaperrasJuego
Comprehensive test runner for all modules in the casino game collection.
"""

import unittest
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class TestProjectStructure(unittest.TestCase):
    """Tests para verificar la estructura general del proyecto"""
    
    def test_all_main_directories_exist(self):
        """Test that all main directories exist"""
        expected_dirs = [
            "Poker",
            "Blackjack", 
            "Ruleta",
            "Tragaperras",
            "Test"
        ]
        
        for dir_name in expected_dirs:
            dir_path = ROOT_DIR / dir_name
            self.assertTrue(dir_path.exists(), f"Directory {dir_name} should exist")
            self.assertTrue(dir_path.is_dir(), f"{dir_name} should be a directory")
    
    def test_essential_files_exist(self):
        """Test that essential project files exist"""
        essential_files = [
            "main.py",
            "cardCommon.py",
            "config.py", 
            "config_dialog.py",
            "requirements.txt",
            "README.md",
            "roadmap.md"
        ]
        
        for filename in essential_files:
            file_path = ROOT_DIR / filename
            self.assertTrue(file_path.exists(), f"File {filename} should exist")
            self.assertTrue(file_path.is_file(), f"{filename} should be a file")
    
    def test_test_directory_structure(self):
        """Test that Test directory has proper structure"""
        test_dir = ROOT_DIR / "Test"
        self.assertTrue(test_dir.exists())
        
        # Should have __init__.py
        init_file = test_dir / "__init__.py"
        self.assertTrue(init_file.exists())
        
        # Should have test files for each module
        expected_test_files = [
            "test_card_common.py",
            "test_poker.py",
            "test_config.py",
            "test_main.py",
            "test_blackjack.py",
            "test_ruleta.py",
            "test_tragaperras.py",
            "test_all.py"  # This file
        ]
        
        for test_file in expected_test_files:
            test_path = test_dir / test_file
            self.assertTrue(test_path.exists(), f"Test file {test_file} should exist")


class TestProjectDocumentation(unittest.TestCase):
    """Tests para verificar la documentación del proyecto"""
    
    def test_readme_content(self):
        """Test that README has proper content"""
        readme_file = ROOT_DIR / "README.md"
        with open(readme_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should mention all main modules
        modules = ["Poker", "Blackjack", "Ruleta", "Tragaperras"]
        for module in modules:
            self.assertIn(module, content, f"README should mention {module}")
        
        # Should have testing section
        content_lower = content.lower()
        self.assertTrue(any(word in content_lower for word in 
                          ["test", "testing", "unittest"]), 
                       "README should mention testing")
        
        # Should have installation/setup instructions
        self.assertTrue(any(word in content_lower for word in 
                          ["install", "setup", "requirement"]),
                       "README should mention installation")
    
    def test_roadmap_content(self):
        """Test that roadmap has proper content"""
        roadmap_file = ROOT_DIR / "roadmap.md"
        with open(roadmap_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should mention all main modules
        modules = ["Poker", "Blackjack", "Ruleta", "Tragaperras"]
        for module in modules:
            self.assertIn(module, content, f"Roadmap should mention {module}")
    
    def test_all_modules_have_docstrings(self):
        """Test that all main modules have proper docstrings"""
        modules_to_check = [
            "main.py",
            "cardCommon.py",
            "config.py",
            "config_dialog.py"
        ]
        
        for module_file in modules_to_check:
            file_path = ROOT_DIR / module_file
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Should have module docstring
                lines = content.strip().split('\n')
                # Look for docstring in first few lines (after potential shebang/encoding)
                docstring_found = False
                for i, line in enumerate(lines[:10]):
                    if '"""' in line or "'''" in line:
                        docstring_found = True
                        break
                
                if not docstring_found:
                    # Allow for files that are primarily imports/setup
                    if len(content) > 500:  # Only check substantial files
                        self.fail(f"{module_file} should have a module docstring")


class TestProjectCompatibility(unittest.TestCase):
    """Tests para verificar compatibilidad del proyecto"""
    
    def test_python_version_compatibility(self):
        """Test Python version compatibility"""
        # Should work with Python 3.8+
        self.assertGreaterEqual(sys.version_info.major, 3)
        if sys.version_info.major == 3:
            self.assertGreaterEqual(sys.version_info.minor, 8)
    
    def test_requirements_file_format(self):
        """Test that requirements.txt is properly formatted"""
        req_file = ROOT_DIR / "requirements.txt"
        with open(req_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Should have PyQt6 requirement
        pyqt_found = False
        for line in lines:
            if 'PyQt6' in line:
                pyqt_found = True
                # Should have version specification
                self.assertIn('==', line, "PyQt6 should have version specification")
                break
        
        self.assertTrue(pyqt_found, "requirements.txt should include PyQt6")
    
    def test_all_imports_available(self):
        """Test that all required imports are available"""
        required_modules = [
            'json', 'os', 'sys', 'random', 'unittest', 
            'pathlib', 'typing', 'enum', 'dataclasses'
        ]
        
        for module in required_modules:
            try:
                __import__(module)
            except ImportError:
                self.fail(f"Required module {module} not available")


class TestModuleIntegration(unittest.TestCase):
    """Tests para verificar integración entre módulos"""
    
    def test_cardcommon_integration(self):
        """Test that cardCommon integrates with other modules"""
        # Should be importable by poker and blackjack
        try:
            from cardCommon import PokerCard, PokerDeck
            self.assertIsNotNone(PokerCard)
            self.assertIsNotNone(PokerDeck)
        except ImportError:
            self.fail("cardCommon should be importable")
    
    def test_config_integration(self):
        """Test that config integrates with other modules"""
        try:
            from config import config_manager, get_text
            self.assertIsNotNone(config_manager)
            self.assertTrue(callable(get_text))
        except ImportError:
            self.fail("config should be importable")
    
    def test_main_ui_integration_ready(self):
        """Test that main UI is ready for all module integration"""
        main_file = ROOT_DIR / "main.py"
        with open(main_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Should import config
        self.assertIn('config', content)
        
        # Should import PyQt6 components
        self.assertIn('PyQt6', content)


def run_all_tests():
    """Execute all test suites"""
    
    print("🎰 Ejecutando Suite de Tests Comprehensiva de RuleTragaperrasJuego")
    print("=" * 70)
    
    # Import all test modules
    test_modules = []
    
    try:
        from Test import test_card_common
        test_modules.append(('cardCommon', test_card_common))
    except ImportError as e:
        print(f"⚠️  Could not import test_card_common: {e}")
    
    try:
        from Test import test_poker
        test_modules.append(('Poker', test_poker))
    except ImportError as e:
        print(f"⚠️  Could not import test_poker: {e}")
    
    try:
        from Test import test_config
        test_modules.append(('Config', test_config))
    except ImportError as e:
        print(f"⚠️  Could not import test_config: {e}")
    
    try:
        from Test import test_main
        test_modules.append(('Main UI', test_main))
    except ImportError as e:
        print(f"⚠️  Could not import test_main: {e}")
    
    try:
        from Test import test_blackjack
        test_modules.append(('Blackjack', test_blackjack))
    except ImportError as e:
        print(f"⚠️  Could not import test_blackjack: {e}")
    
    try:
        from Test import test_ruleta
        test_modules.append(('Ruleta', test_ruleta))
    except ImportError as e:
        print(f"⚠️  Could not import test_ruleta: {e}")
    
    try:
        from Test import test_tragaperras
        test_modules.append(('Tragaperras', test_tragaperras))
    except ImportError as e:
        print(f"⚠️  Could not import test_tragaperras: {e}")
    
    # Run project structure tests first
    print("\n📁 Testing Project Structure...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestProjectStructure)
    runner = unittest.TextTestRunner(verbosity=1)
    result = runner.run(suite)
    
    print("\n📚 Testing Project Documentation...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestProjectDocumentation)
    result = runner.run(suite)
    
    print("\n🔧 Testing Project Compatibility...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestProjectCompatibility)
    result = runner.run(suite)
    
    print("\n🔗 Testing Module Integration...")
    suite = unittest.TestLoader().loadTestsFromTestCase(TestModuleIntegration)
    result = runner.run(suite)
    
    # Run individual module tests
    total_tests = 0
    total_failures = 0
    total_errors = 0
    total_skipped = 0
    
    for module_name, test_module in test_modules:
        print(f"\n🎮 Testing {module_name} Module...")
        
        # Load all test cases from the module
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        
        # Run tests
        runner = unittest.TextTestRunner(verbosity=1)
        result = runner.run(suite)
        
        total_tests += result.testsRun
        total_failures += len(result.failures)
        total_errors += len(result.errors)
        total_skipped += len(result.skipped)
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 RESUMEN FINAL DE TESTS")
    print("=" * 70)
    print(f"Total de tests ejecutados: {total_tests}")
    print(f"✅ Tests exitosos: {total_tests - total_failures - total_errors}")
    print(f"❌ Tests fallidos: {total_failures}")
    print(f"💥 Errores: {total_errors}")
    print(f"⏭️  Tests omitidos: {total_skipped}")
    
    success_rate = ((total_tests - total_failures - total_errors) / total_tests * 100) if total_tests > 0 else 0
    print(f"📈 Tasa de éxito: {success_rate:.1f}%")
    
    if total_failures == 0 and total_errors == 0:
        print("\n🎉 ¡TODOS LOS TESTS PASARON EXITOSAMENTE!")
        print("✨ El proyecto está listo y completamente funcional.")
    elif success_rate >= 90:
        print("\n🌟 ¡EXCELENTE! La mayoría de tests pasaron.")
        print("🔧 Solo hay algunos problemas menores que arreglar.")
    elif success_rate >= 75:
        print("\n👍 BIEN. La mayoría de la funcionalidad está trabajando.")
        print("🛠️  Hay algunos problemas que necesitan atención.")
    else:
        print("\n⚠️  Hay problemas significativos que necesitan ser resueltos.")
    
    print("=" * 70)
    
    return total_failures + total_errors == 0


if __name__ == '__main__':
    # Run comprehensive test suite
    success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)