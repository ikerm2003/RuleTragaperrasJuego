# GitHub Copilot Instructions for RuleTragaperrasJuego

## Project Overview

RuleTragaperrasJuego is a Python-based casino game collection featuring multiple card and casino games. The main implemented component is a comprehensive Texas Hold'em Poker module with a modern PyQt6 GUI, supporting up to 9 players with bot AI.

## Architecture & File Organization

### Core Components
- **Poker Module** (Primary): Full-featured Texas Hold'em implementation
  - `poker_logic.py`: Core game rules, hand evaluation, betting logic
  - `poker_table.py`: Table management, player positioning, 9-player support
  - `poker_ui.py`: PyQt6 responsive UI with professional poker table design
  - `poker_main.py`: Application entry point
  - `test_poker.py`: Comprehensive unit tests (30 tests)

- **Base Classes**: Abstract base class pattern for extensibility
  - `cardCommon.py`: Abstract base classes for cards and decks
  - ABC pattern enforced for all card games

- **Other Games** (Stubs): Ready for implementation
  - `blackjack.py`: Blackjack implementation
  - `ruleta.py`: Roulette (empty stub)
  - `tragaperras.py`: Slot machine (empty stub)
  - `mainui.py`: Main menu interface

### Key Design Patterns
- **Abstract Base Classes**: All card games inherit from `cardCommon.py` ABC structure
- **Factory Pattern**: `PokerTableFactory` for different table configurations
- **Separation of Concerns**: Clear separation between UI (`poker_ui.py`) and logic (`poker_logic.py`)
- **Responsive Design**: UI scales dynamically with window size

## Development Guidelines

### Code Style & Standards
- **Language**: Python 3.x with type hints where applicable
- **GUI Framework**: PyQt6 for all UI components
- **Testing**: unittest framework (not pytest)
- **Documentation**: Comprehensive docstrings with examples
- **Error Handling**: Robust error handling throughout game logic

### Testing Patterns
```python
# Use unittest.TestCase for all tests
class TestPokerLogic(unittest.TestCase):
    def setUp(self):
        self.table = PokerTable(small_blind=10, big_blind=20)
    
    def test_feature_name(self):
        """Test description with expected behavior"""
        # Test implementation
```

- **Test Structure**: Organized by component (`TestPokerCards`, `TestPokerTable`, etc.)
- **Coverage**: 30 comprehensive tests covering all poker functionality
- **Run Tests**: `python -m unittest test_poker.py -v`

### UI Development
- **Framework**: PyQt6 with responsive scaling utilities
- **Layout**: Grid-based positioning for poker table (supports 2-9 players)
- **Styling**: Professional casino appearance with gradients and shadows
- **Scalability**: All UI elements scale with window size using `get_scaled_size()`

### Game Logic Patterns
```python
# Player actions using Enums
class PlayerAction(Enum):
    FOLD = "fold"
    CHECK = "check"
    CALL = "call"
    RAISE = "raise"
    ALL_IN = "all_in"

# Hand evaluation with proper tie-breaking
def evaluate_hand(self, cards: List[PokerCard]) -> Tuple[HandRanking, List[int]]:
    """Returns (hand_type, tie_breaker_values)"""
```

## Component Relationships

### Poker Module Flow
1. **Entry Point**: `poker_main.py` creates window and table
2. **Table Management**: `poker_table.py` handles game state and players
3. **Game Logic**: `poker_logic.py` processes actions and evaluates hands
4. **UI Updates**: `poker_ui.py` reflects game state changes
5. **Testing**: `test_poker.py` validates all components

### Inheritance Hierarchy
```
BaseCard (ABC) <- PokerCard
BaseDeck (ABC) <- PokerDeck
PokerTable <- BasePokerTable (ABC) <- NinePlayerTable
```

## Implementation Guidelines

### Adding New Games
1. Inherit from appropriate ABC in `cardCommon.py`
2. Follow the poker module structure (logic/ui/table separation)
3. Add comprehensive unit tests
4. Update main UI integration in `mainui.py`

### Poker Enhancements
- **AI Strategy**: Extend bot logic in `poker_table.py`
- **UI Features**: Add animations/effects in `poker_ui.py`
- **Game Variants**: Create new table types via factory pattern
- **Tournament**: Extend table management for multi-table support

### Current Capabilities
- ✅ Full Texas Hold'em rules implementation
- ✅ 9-player table support with proper positioning
- ✅ Bot players with basic AI strategy
- ✅ Responsive PyQt6 UI with professional styling
- ✅ Comprehensive hand evaluation (including edge cases)
- ✅ Complete betting system with all actions
- ✅ Robust error handling and validation
- ✅ 100% test coverage for poker functionality

### Future Roadmap (from roadmap.md)
- [ ] MainUI integration
- [ ] Blackjack completion
- [ ] Ruleta implementation
- [ ] Tragaperras implementation
- [ ] Multiplayer support
- [ ] Daily missions system
- [ ] Auto-refill functionality
- [ ] Keyboard shortcuts

## Debug & Troubleshooting

### Common Issues
1. **PyQt6 Dependencies**: `pip install PyQt6`
2. **Card Display Issues**: Check `load_card_image()` in UI module
3. **Game Logic Errors**: Run specific test classes to isolate issues

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Enables detailed game state logging
```

### Performance
- UI animations and effects are optimized for smooth gameplay
- Card shuffling uses Python's `random.shuffle()` for proper randomization
- Memory management: Cards and players are properly cleaned up between hands

## Context for AI Assistance

When working on this project:
- **Preserve ABC Structure**: Always maintain abstract base class patterns
- **Test First**: Add/update unit tests for any logic changes
- **UI Separation**: Keep UI code separate from game logic
- **Scalable Design**: Ensure any UI changes work across different window sizes
- **Spanish Context**: Some UI text and comments may be in Spanish (this is intentional)
- **Backward Compatibility**: Preserve existing API when adding features

The project is well-structured with clear separation of concerns, comprehensive testing, and professional UI design. Focus on maintaining these standards when making modifications or additions.