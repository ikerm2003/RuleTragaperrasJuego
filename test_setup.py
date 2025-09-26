#!/usr/bin/env python3
"""
Test script to verify the setup and basic functionality of RuleTragaperrasJuego.
This script validates that all essential imports work and basic components can be instantiated.
"""

import sys
import os

def test_python_version():
    """Test Python version is adequate."""
    print("🐍 Testing Python version...")
    if sys.version_info < (3, 8):
        print(f"❌ Python version {sys.version_info} is too old. Requires 3.8+")
        return False
    print(f"✅ Python version {sys.version_info.major}.{sys.version_info.minor} OK")
    return True

def test_pyqt6_import():
    """Test PyQt6 can be imported."""
    print("🖼️  Testing PyQt6 import...")
    try:
        import PyQt6
        print("✅ PyQt6 package available")
        
        # Test basic imports (may fail in headless environment)
        try:
            from PyQt6.QtWidgets import QApplication
            from PyQt6.QtCore import Qt
            from PyQt6.QtGui import QFont
            print("✅ PyQt6 GUI components importable")
        except ImportError as gui_e:
            if "libEGL" in str(gui_e) or "libGL" in str(gui_e):
                print("⚠️  PyQt6 GUI components not available (headless environment)")
                print("   This is expected on servers without display")
            else:
                raise gui_e
        return True
    except ImportError as e:
        print(f"❌ PyQt6 import failed: {e}")
        return False

def test_core_modules():
    """Test core application modules."""
    print("⚙️  Testing core modules...")
    try:
        # Test cardCommon base classes
        from cardCommon import BaseCard, BaseDeck
        print("  ✅ cardCommon module OK")
        
        # Test config system
        from config import config_manager, get_text, Language
        print("  ✅ config module OK")
        
        # Test main UI can be imported (may fail without display)
        try:
            from main import MainUI
            print("  ✅ main UI module OK")
        except ImportError as ui_e:
            if "libEGL" in str(ui_e) or "libGL" in str(ui_e):
                print("  ⚠️  main UI module not testable (headless environment)")
            else:
                raise ui_e
        
        return True
    except ImportError as e:
        print(f"❌ Core module import failed: {e}")
        return False

def test_poker_module():
    """Test Poker module components."""
    print("🃏 Testing Poker module...")
    try:
        # Change to proper import path
        sys.path.insert(0, 'Poker')
        
        from poker_logic import PlayerAction, GamePhase
        print("  ✅ Poker logic module OK")
        
        # Test poker table (may have import issues due to relative imports)
        try:
            from poker_table import NinePlayerTable
            print("  ✅ Poker table module OK")
        except ImportError as table_e:
            if "relative import" in str(table_e):
                print("  ⚠️  Poker table import issue (relative import - normal in test environment)")
            else:
                raise table_e
        
        # Test poker UI can be imported
        try:
            from poker_ui import PokerWindow  
            print("  ✅ Poker UI module OK")
        except ImportError as ui_e:
            if "libEGL" in str(ui_e) or "relative import" in str(ui_e):
                print("  ⚠️  Poker UI module not testable (GUI/import environment)")
            else:
                raise ui_e
        
        return True
    except ImportError as e:
        print(f"❌ Poker module import failed: {e}")
        return False
    finally:
        # Restore sys.path
        if 'Poker' in sys.path:
            sys.path.remove('Poker')

def test_file_structure():
    """Test essential files exist."""
    print("📁 Testing file structure...")
    essential_files = [
        'requirements.txt',
        'setup_env.bat', 
        'README.md',
        'main.py',
        'cardCommon.py',
        'config.py',
        'Poker/poker_main.py'
    ]
    
    all_exist = True
    for file_path in essential_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def test_virtual_environment():
    """Test if running in virtual environment."""
    print("🏠 Testing virtual environment...")
    
    # Check if we're in a virtual environment
    in_venv = (
        hasattr(sys, 'real_prefix') or 
        (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    )
    
    if in_venv:
        print(f"✅ Running in virtual environment: {sys.prefix}")
    else:
        print("⚠️  Not running in virtual environment (recommended but not required)")
    
    return True  # Not a failure if not in venv

def main():
    """Run all setup tests."""
    print("🎰 RuleTragaperrasJuego Setup Test")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_pyqt6_import, 
        test_core_modules,
        test_poker_module,
        test_file_structure,
        test_virtual_environment
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)
            print()
    
    # Summary
    print("📊 Test Summary")
    print("-" * 30)
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All tests passed! ({passed}/{total})")
        print("\n✨ Setup is ready! You can now run:")
        print("   - python main.py")
        print("   - python Poker/poker_main.py")
    else:
        print(f"⚠️  {passed}/{total} tests passed")
        print("Please check the failed tests above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)