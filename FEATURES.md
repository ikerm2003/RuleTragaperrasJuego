# New Features Documentation

This document describes the new features implemented to enhance the casino game experience.

## 🎨 Gameplay Animations

### Overview
The game now includes smooth, configurable animations that make gameplay more visually engaging.

### Features
- **Card dealing animations**: Cards smoothly animate from the deck to players
- **Player highlight transitions**: Current player highlighting with subtle animations
- **Bet change animations**: Visual feedback when bet amounts change
- **Pot update animations**: Bouncing effect when pot values change
- **Configurable speeds**: Animations can be disabled, slow, normal, or fast

### Implementation
```python
# Animation methods in poker_ui.py
def animate_bet_change(self, bet_label)
def animate_player_highlight(self, player_position)
def animate_card_deal(self, card_label, delay=0)
def animate_pot_update(self)
```

### Configuration
Animations respect user preferences from the configuration system:
- Speed multipliers: Disabled (0.0x), Slow (1.5x), Normal (1.0x), Fast (0.5x)
- Enable/disable toggle for all animations
- Smooth easing curves for professional feel

## 💰 Enhanced Bet Display

### Overview
Improved bet display system shows accurate betting information with better visual feedback.

### Improvements
- **Accurate bet tracking**: Shows current bet and total bet for the hand
- **Real-time updates**: Immediate visual feedback during betting rounds
- **Enhanced styling**: Better visual design with backgrounds and borders
- **Animation feedback**: Bet labels animate when amounts change
- **Clear information**: Distinguishes between current bet and total bet

### Display Logic
```
No bet: "Bet: $0"
First bet: "Bet: $50"
Raised bet: "Bet: $100 (Total: $150)"
Multiple raises: "Bet: $200 (Total: $350)"
```

### Visual Enhancements
- Golden color scheme for better visibility
- Semi-transparent backgrounds for better readability
- Rounded borders for modern appearance
- Animation on value changes

## ⚙️ Configuration System

### Overview
Comprehensive configuration system allowing users to customize their experience.

### Configuration Categories

#### Display Settings
- **Fullscreen mode**: Toggle fullscreen/windowed mode
- **Resolution**: Auto, HD (1280x720), Full HD (1920x1080), Ultra HD (2560x1440)
- **VSync**: Vertical synchronization toggle

#### Interface Settings
- **Language**: Spanish/English support
- **Animation speed**: Disabled/Slow/Normal/Fast
- **Enable animations**: Master toggle for all animations
- **Show tooltips**: Help text toggle
- **Sound**: Audio enable/disable

#### Gameplay Settings
- **Auto-fold timeout**: Time before automatic fold (10-120 seconds)
- **Confirm actions**: Confirmation dialogs for important actions
- **Probability hints**: Show/hide probability information

### Configuration Dialog
Tabbed interface with three main sections:
1. **Display**: Screen and visual settings
2. **Interface**: Language and interaction preferences  
3. **Gameplay**: Game-specific options

### Persistence
- Settings saved to `casino_config.json`
- Automatic loading on startup
- Reset to defaults option
- Type-safe configuration with enums

## 🌐 Internationalization

### Languages Supported
- **Spanish** (default): Native language support
- **English**: Full translation available

### Key Translated Elements
- Window titles and menu items
- Game names (Poker, Blackjack, Roulette, Slot Machine)
- Action buttons (Fold, Call, Raise, Check)
- Configuration dialog
- Interface labels

### Translation System
```python
from config import get_text

# Usage
title = get_text('casino_title')  # "Casino de tu mama" or "Your Mom's Casino"
poker = get_text('poker')         # "Póker" or "Poker"
```

## 🎮 Enhanced Main Menu

### Features
- **Modern design**: Professional casino-style interface
- **Game launcher**: Easy access to different games
- **Configuration access**: Settings available from main menu
- **Responsive layout**: Adapts to different screen sizes
- **Visual feedback**: Hover effects and animations

### Game Integration
- **Poker**: Fully integrated with new features
- **Other games**: Placeholder for future implementation
- **Consistent styling**: Unified visual theme

## 🛠️ Technical Implementation

### Architecture
- **Modular design**: Separated concerns across multiple files
- **Configuration layer**: Centralized settings management
- **Animation system**: PyQt6 QPropertyAnimation integration
- **Translation system**: Dictionary-based with fallbacks
- **Error handling**: Graceful degradation when features unavailable

### Files Structure
```
config.py           - Configuration management system
config_dialog.py    - Configuration UI dialog
poker_ui.py         - Enhanced poker interface with animations
mainui.py           - Improved main menu with game launcher
demo_features.py    - Feature demonstration script
```

### Compatibility
- **PyQt6 dependent**: Requires PyQt6 for full functionality
- **Graceful fallback**: Works without advanced features if dependencies missing
- **Test compatibility**: All existing tests still pass
- **Minimal changes**: Surgical modifications to existing codebase

## 🚀 Usage Examples

### Running the Demo
```bash
python demo_features.py
```

### Launching Games
```bash
# Main casino interface
python mainui.py

# Direct poker launch
python poker_main.py
```

### Configuration Usage
```python
from config import config_manager, get_text

# Check settings
if config_manager.are_animations_enabled():
    animate_something()

# Change language
config_manager.set('interface', 'language', 'en')
config_manager.save_config()
```

## 📋 Future Enhancements

### Planned Features
- Sound effects system
- More animation types (card flips, chip movements)
- Additional language support
- Tournament mode configuration
- Advanced AI personality settings
- Hand history and statistics
- Online multiplayer options

### Extensibility
The configuration system is designed to easily accommodate new settings:
- Add new enums for option types
- Extend translation dictionaries
- Add new configuration sections
- Implement new animation types

## 🔧 Development Notes

### Adding New Animations
1. Create animation method in poker_ui.py
2. Check `config_manager.are_animations_enabled()`
3. Use `config_manager.get_animation_speed()` for duration
4. Apply easing curves for smooth motion

### Adding New Translations
1. Add key-value pairs to `TRANSLATIONS` in config.py
2. Use `get_text(key)` in UI code
3. Test with both languages
4. Update configuration dialog if needed

### Adding New Settings
1. Add to `DEFAULT_CONFIG` in config.py
2. Create UI controls in config_dialog.py
3. Add getter methods to ConfigManager
4. Update settings persistence logic