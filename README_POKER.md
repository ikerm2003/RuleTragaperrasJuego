# Texas Hold'em Poker Module Documentation

## Overview

This module implements a complete Texas Hold'em poker game using PyQt6 with support for up to 9 players. The system features a modular architecture with clear separation between game logic and UI components.

## Architecture

### Core Components

1. **poker_logic.py** - Core game engine
   - Game rules and hand evaluation
   - Player management and actions
   - Betting logic and pot management

2. **poker_table.py** - Table management
   - Abstract base classes for poker tables
   - 9-player table implementation
   - Position management and factory patterns

3. **poker_ui.py** - User interface
   - PyQt6 GUI components
   - Responsive scaling system
   - Visual card rendering

4. **poker_main.py** - Application entry point
   - Main application setup
   - Integration between components

## Features

### Game Features
- ✅ Standard Texas Hold'em rules
- ✅ Support for 2-9 players
- ✅ Automatic bot players
- ✅ Complete hand evaluation (all poker hands)
- ✅ Proper betting rounds (pre-flop, flop, turn, river)
- ✅ Side pot handling for all-in situations
- ✅ Position-based naming (UTG, Button, Blinds, etc.)

### UI Features
- ✅ Responsive scaling for different screen sizes
- ✅ Professional poker table design
- ✅ Real-time game state updates
- ✅ Interactive action buttons
- ✅ Visual card representations
- ✅ Player highlighting and state indication

## Quick Start

### Running the Game

```python
# Basic usage
from poker_main import main
main()

# Or directly import and configure
from poker_ui import PokerWindow
from PyQt6.QtWidgets import QApplication
import sys

app = QApplication(sys.argv)
window = PokerWindow(num_players=6)  # 6-player table
window.show()
sys.exit(app.exec())
```

### Creating Different Table Types

```python
from poker_table import PokerTableFactory

# Create different table types
nine_max_table = PokerTableFactory.create_table("nine_player")
heads_up_table = PokerTableFactory.create_table("heads_up")
six_max_table = PokerTableFactory.create_table("six_max")
```

## API Reference

### PokerTable Class

Core game logic management.

```python
class PokerTable:
    def __init__(self, small_blind: int = 10, big_blind: int = 20)
    def add_player(self, name: str, chips: int = 1000, is_human: bool = False) -> bool
    def start_new_hand(self)
    def execute_action(self, player_position: int, action: PlayerAction, amount: int = 0) -> bool
    def get_valid_actions(self, player_position: int) -> List[PlayerAction]
    def evaluate_hand(self, cards: List[PokerCard]) -> Tuple[HandRanking, List[int]]
```

### NinePlayerTable Class

Extended table with position management.

```python
class NinePlayerTable(BasePokerTable):
    def setup_standard_game(self, num_human_players: int = 1, total_players: int = 6)
    def get_position_name(self, position: int) -> str
    def get_seat_layout(self) -> List[Tuple[int, int, str]]
```

### Hand Rankings

The system supports all standard poker hands:

```python
class HandRanking(Enum):
    HIGH_CARD = 1        # A♠ K♦ Q♣ J♥ 9♠
    ONE_PAIR = 2         # A♠ A♦ K♣ Q♥ J♠
    TWO_PAIR = 3         # A♠ A♦ K♣ K♥ Q♠
    THREE_OF_A_KIND = 4  # A♠ A♦ A♣ K♥ Q♠
    STRAIGHT = 5         # A♠ 2♦ 3♣ 4♥ 5♠ (wheel) or 10♠ J♦ Q♣ K♥ A♠
    FLUSH = 6            # A♠ K♠ Q♠ J♠ 9♠
    FULL_HOUSE = 7       # A♠ A♦ A♣ K♥ K♠
    FOUR_OF_A_KIND = 8   # A♠ A♦ A♣ A♥ K♠
    STRAIGHT_FLUSH = 9   # 9♠ 10♠ J♠ Q♠ K♠
    ROYAL_FLUSH = 10     # 10♠ J♠ Q♠ K♠ A♠
```

## Game Flow

### Standard Hand Progression

1. **Setup**: Players are dealt 2 hole cards
2. **Pre-flop**: Betting round after dealing hole cards
3. **Flop**: 3 community cards dealt, betting round
4. **Turn**: 4th community card dealt, betting round
5. **River**: 5th community card dealt, betting round
6. **Showdown**: Best hands compared, pot distributed

### Player Actions

```python
class PlayerAction(Enum):
    FOLD = "fold"      # Give up the hand
    CHECK = "check"    # Pass action (no bet to call)
    CALL = "call"      # Match current bet
    RAISE = "raise"    # Increase the bet
    ALL_IN = "all_in"  # Bet all remaining chips
```

## Configuration

### Table Settings

```python
# Configure blinds
table = PokerTable(small_blind=25, big_blind=50)

# Set up players
table.add_player("Human Player", chips=2000, is_human=True)
table.fill_with_bots(target_players=6)
```

### UI Scaling

The UI automatically scales based on window size, but you can customize:

```python
class PokerWindow(QMainWindow):
    def __init__(self):
        # Base dimensions for scaling calculations
        self.base_width = 1400
        self.base_height = 900
```

## Testing

Run the comprehensive test suite:

```bash
python -m unittest test_poker.py -v
```

### Test Coverage

- ✅ Card and deck functionality
- ✅ Hand evaluation (all poker hands)
- ✅ Game logic and betting
- ✅ Player management
- ✅ Table configuration
- ✅ Factory patterns

## Customization

### Adding New Table Types

```python
class CustomTable(BasePokerTable):
    def __init__(self):
        super().__init__(small_blind=5, big_blind=10)
        self.max_players = 4  # Custom limit
    
    def update_display(self):
        # Custom UI updates
        pass
```

### Custom Bot Strategies

```python
def custom_bot_strategy(self, player_position: int) -> Tuple[PlayerAction, int]:
    """Implement custom bot decision making"""
    valid_actions = self.get_valid_actions(player_position)
    
    # Your custom logic here
    if PlayerAction.RAISE in valid_actions and random.random() < 0.3:
        return PlayerAction.RAISE, self.current_bet * 2
    elif PlayerAction.CALL in valid_actions:
        return PlayerAction.CALL, 0
    else:
        return PlayerAction.FOLD, 0

# Override the method
table.get_bot_action = custom_bot_strategy
```

## Integration with Main Application

The poker module integrates with the existing game suite architecture:

```python
# In main application
def launch_poker():
    from poker_main import create_poker_application
    poker_app = create_poker_application(num_players=6)
    if poker_app:
        window = PokerWindow()
        window.show()
        return poker_app.exec()
```

## Performance Considerations

- Hand evaluation uses efficient algorithms for 7-card analysis
- UI updates are batched to prevent flickering
- Bot actions are delayed for better user experience
- Memory usage is optimized for long gaming sessions

## Troubleshooting

### Common Issues

1. **PyQt6 not found**
   ```bash
   pip install PyQt6
   ```

2. **Cards not displaying**
   - Check that card images are being generated correctly
   - Verify QPixmap rendering in `load_card_image()` method

3. **Game logic errors**
   - Run unit tests to identify specific issues
   - Check hand evaluation with `test_poker.py`

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Game will output detailed state information
```

## Future Enhancements

### Planned Features
- [ ] Tournament mode
- [ ] Hand history
- [ ] Advanced AI personalities
- [ ] Online multiplayer support
- [ ] Statistics tracking
- [ ] Custom themes

### Contributing

When adding new features:

1. Follow the existing ABC patterns
2. Add comprehensive unit tests
3. Update this documentation
4. Maintain separation between UI and logic
5. Ensure responsive UI scaling

## License

This module is part of the RuleTragaperrasJuego project and follows the same licensing terms as the main repository.