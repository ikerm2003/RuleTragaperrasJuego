#!/usr/bin/env python3
"""
Demo script to showcase the new features implemented for the poker game.
This script demonstrates the configuration system and translation features
without requiring PyQt6.
"""

import json
import os
from config import config_manager, get_text, Language, AnimationSpeed, Resolution

def demo_configuration_system():
    """Demonstrate the configuration system"""
    print("=== Configuration System Demo ===")
    print()
    
    # Show current configuration
    print("Current Configuration:")
    print(f"  Language: {config_manager.get_language()}")
    print(f"  Fullscreen: {config_manager.is_fullscreen()}")
    print(f"  Resolution: {config_manager.get_resolution()}")
    print(f"  Animation Speed: {config_manager.get_animation_speed()}")
    print(f"  Animations Enabled: {config_manager.are_animations_enabled()}")
    print()
    
    # Test configuration changes
    print("Testing Configuration Changes:")
    
    # Change language to English
    config_manager.set('interface', 'language', Language.ENGLISH.value)
    print(f"  Changed language to English: {config_manager.get_language()}")
    
    # Change animation speed
    config_manager.set('interface', 'animation_speed', AnimationSpeed.FAST.value)
    print(f"  Changed animation speed to FAST: {config_manager.get_animation_speed()}")
    
    # Enable fullscreen
    config_manager.set('display', 'fullscreen', True)
    print(f"  Enabled fullscreen: {config_manager.is_fullscreen()}")
    
    # Change resolution
    config_manager.set('display', 'resolution', Resolution.FULL_HD.value)
    print(f"  Set resolution to Full HD: {config_manager.get_resolution()}")
    print()
    
    # Save configuration
    if config_manager.save_config():
        print("✅ Configuration saved successfully!")
    else:
        print("❌ Failed to save configuration")
    print()

def demo_translation_system():
    """Demonstrate the translation system"""
    print("=== Translation System Demo ===")
    print()
    
    # Test Spanish translations
    print("Spanish Translations:")
    config_manager.set('interface', 'language', Language.SPANISH.value)
    spanish_texts = [
        'casino_title', 'poker', 'blackjack', 'roulette', 'slot_machine',
        'settings', 'bet', 'fold', 'call', 'raise', 'check', 'new_hand'
    ]
    
    for key in spanish_texts:
        print(f"  {key}: {get_text(key)}")
    print()
    
    # Test English translations
    print("English Translations:")
    config_manager.set('interface', 'language', Language.ENGLISH.value)
    for key in spanish_texts:
        print(f"  {key}: {get_text(key)}")
    print()

def demo_animation_settings():
    """Demonstrate animation settings"""
    print("=== Animation Settings Demo ===")
    print()
    
    print("Animation Speed Options:")
    for speed in AnimationSpeed:
        print(f"  {speed.name}: {speed.value}x multiplier")
    print()
    
    print("Animation Settings Logic:")
    
    # Test different animation speeds
    for speed in [AnimationSpeed.DISABLED, AnimationSpeed.SLOW, AnimationSpeed.NORMAL, AnimationSpeed.FAST]:
        config_manager.set('interface', 'animation_speed', speed.value)
        duration = 300  # Base duration in ms
        
        if config_manager.get_animation_speed() > 0:
            actual_duration = int(duration / config_manager.get_animation_speed())
            print(f"  {speed.name}: Base 300ms -> {actual_duration}ms")
        else:
            print(f"  {speed.name}: Animations disabled")
    print()

def demo_bet_display_improvements():
    """Demonstrate bet display logic"""
    print("=== Bet Display Improvements Demo ===")
    print()
    
    print("Enhanced Bet Display Logic:")
    
    # Simulate different bet scenarios
    scenarios = [
        {'current_bet': 0, 'total_bet': 0, 'description': 'No bet'},
        {'current_bet': 50, 'total_bet': 50, 'description': 'First bet'},
        {'current_bet': 100, 'total_bet': 150, 'description': 'Raised bet'},
        {'current_bet': 200, 'total_bet': 350, 'description': 'Multiple raises'},
    ]
    
    for scenario in scenarios:
        current_bet = scenario['current_bet']
        total_bet = scenario['total_bet']
        description = scenario['description']
        
        if current_bet > 0:
            if total_bet > current_bet:
                bet_text = f"Bet: ${current_bet} (Total: ${total_bet})"
            else:
                bet_text = f"Bet: ${current_bet}"
        else:
            bet_text = "Bet: $0"
        
        print(f"  {description}: {bet_text}")
    print()

def show_config_file():
    """Show the configuration file content"""
    print("=== Configuration File Content ===")
    print()
    
    config_file = 'casino_config.json'
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config_content = json.load(f)
        
        print(f"Configuration file ({config_file}):")
        print(json.dumps(config_content, indent=2, ensure_ascii=False))
    else:
        print("No configuration file found (using defaults)")
    print()

def main():
    """Main demo function"""
    print("🎮 Casino Game Enhancement Features Demo")
    print("=" * 50)
    print()
    
    # Run demos
    demo_configuration_system()
    demo_translation_system()
    demo_animation_settings()
    demo_bet_display_improvements()
    show_config_file()
    
    # Reset to original state
    print("=== Cleanup ===")
    config_manager.reset_to_defaults()
    config_manager.save_config()
    print("✅ Configuration reset to defaults")
    print()
    print("Demo completed! 🎉")
    print()
    print("Key Features Implemented:")
    print("  ✅ Smooth gameplay animations with configurable speeds")
    print("  ✅ Enhanced bet display with real-time updates")
    print("  ✅ Comprehensive configuration system")
    print("  ✅ Bilingual support (Spanish/English)")
    print("  ✅ Fullscreen and resolution options")
    print("  ✅ Settings persistence")

if __name__ == "__main__":
    main()