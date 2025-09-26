"""
Poker Table Base Module

Defines the base table structure for Texas Hold'em supporting up to 9 players.
Follows ABC pattern similar to the existing card system.
"""
from abc import ABC
from typing import List, Optional, Tuple
from poker_logic import PokerTable, Player, GamePhase, PlayerAction


class BasePokerTable(PokerTable, ABC):
    """
    Abstract base class for poker tables.
    Extends the core PokerTable with UI integration hooks.
    """
    
    def __init__(self, small_blind: int = 10, big_blind: int = 20):
        super().__init__(small_blind, big_blind)
        self._ui_callbacks = {}
    
    def register_ui_callback(self, event: str, callback):
        """Register UI callbacks for game events"""
        self._ui_callbacks[event] = callback
    
    def _notify_ui(self, event: str, **kwargs):
        """Notify UI of game events"""
        if event in self._ui_callbacks:
            self._ui_callbacks[event](**kwargs)
    
    def update_display(self):
        """Update the table display (implemented via UI callbacks)."""
        self._notify_ui('update_display')
    
    def highlight_current_player(self, player_position: int):
        """Highlight the current player (implemented via UI callbacks)."""
        self._notify_ui('highlight_player', player_position=player_position)
    
    def show_action_buttons(self, player_position: int, actions: List[PlayerAction]):
        """Show available action buttons (implemented via UI callbacks)."""
        self._notify_ui('show_actions', player_position=player_position, actions=actions)
    
    def start_new_hand(self):
        """Override to add UI notifications"""
        super().start_new_hand()
        self._notify_ui('hand_started')
        self.update_display()
        if not self.is_hand_over():
            self.highlight_current_player(self.current_player)
            if self.players[self.current_player].is_human:
                actions = self.get_valid_actions(self.current_player)
                self.show_action_buttons(self.current_player, actions)
    
    def execute_action(self, player_position: int, action: PlayerAction, amount: int = 0) -> bool:
        """Override to add UI notifications"""
        success = super().execute_action(player_position, action, amount)
        if success:
            self._notify_ui('action_executed', 
                          player=player_position, 
                          action=action, 
                          amount=amount)
            self.update_display()
            
            # Check if we need to advance phase
            if self.betting_round_complete and not self.is_hand_over():
                self.advance_phase()
                self.update_display()
            
            # Handle next player or end hand
            if not self.is_hand_over():
                self.highlight_current_player(self.current_player)
                if self.players[self.current_player].is_human:
                    actions = self.get_valid_actions(self.current_player)
                    self.show_action_buttons(self.current_player, actions)
            else:
                self._notify_ui('hand_ended', results=self.last_hand_results)
        
        return success


class NinePlayerTable(BasePokerTable):
    """
    Standard 9-player Texas Hold'em table.
    Implements the full table with position management.
    """
    
    # Standard 9-player positions
    POSITION_NAMES = [
        "Under the Gun (UTG)",
        "UTG+1", 
        "UTG+2",
        "Middle Position 1",
        "Middle Position 2", 
        "Cutoff (CO)",
        "Button (BTN)",
        "Small Blind (SB)",
        "Big Blind (BB)"
    ]
    
    def __init__(self, small_blind: int = 10, big_blind: int = 20):
        super().__init__(small_blind, big_blind)
        self.max_players = 9
    
    def get_position_name(self, position: int) -> str:
        """Get the name of a position relative to the dealer"""
        if not self.players or position >= len(self.players):
            return f"Seat {position + 1}"
        
        # Calculate position relative to dealer
        num_players = len(self.players)
        if num_players < 3:
            if position == self.dealer_position:
                return "Button/Small Blind"
            else:
                return "Big Blind"
        
        # For 3+ players, calculate relative position
        relative_pos = (position - self.dealer_position - 1) % num_players
        
        if num_players <= len(self.POSITION_NAMES):
            # Use standard position names, but adjust for fewer players
            if num_players == 3:
                names = ["Button", "Small Blind", "Big Blind"]
                return names[relative_pos]
            elif num_players == 4:
                names = ["Button", "Small Blind", "Big Blind", "UTG"]
                return names[relative_pos]
            elif num_players == 5:
                names = ["Button", "Small Blind", "Big Blind", "UTG", "Cutoff"]
                return names[relative_pos]
            elif num_players == 6:
                names = ["Button", "Small Blind", "Big Blind", "UTG", "MP", "Cutoff"]
                return names[relative_pos]
            else:
                # 7-9 players: use more complete naming
                if relative_pos == 0:
                    return "Small Blind (SB)"
                elif relative_pos == 1:
                    return "Big Blind (BB)"
                elif relative_pos == 2:
                    return "Under the Gun (UTG)"
                elif relative_pos == num_players - 1:
                    return "Button (BTN)"
                elif relative_pos == num_players - 2:
                    return "Cutoff (CO)"
                else:
                    return f"Middle Position {relative_pos - 2}"
        
        return f"Position {relative_pos + 1}"
    
    def get_seat_layout(self) -> List[Tuple[int, int, str]]:
        """
        Get the physical layout of seats for UI positioning.
        Returns list of (row, col, description) for each player position.
        """
        num_players = len(self.players)
        
        if num_players <= 4:
            # Use existing 4-player layout from base_table
            return [
                (3, 1, "bottom"),    # Position 0 (human player)
                (2, 0, "left"),      # Position 1
                (1, 1, "top"),       # Position 2
                (2, 2, "right")      # Position 3
            ][:num_players]
        
        # 5-9 player oval table layout
        layouts = {
            5: [
                (3, 1, "bottom"),    # 0
                (3, 0, "bottom-left"), # 1
                (1, 0, "top-left"),  # 2
                (1, 2, "top-right"), # 3
                (3, 2, "bottom-right") # 4
            ],
            6: [
                (3, 1, "bottom"),    # 0
                (3, 0, "bottom-left"), # 1
                (2, 0, "left"),      # 2
                (1, 1, "top"),       # 3
                (2, 2, "right"),     # 4
                (3, 2, "bottom-right") # 5
            ],
            7: [
                (3, 1, "bottom"),    # 0
                (3, 0, "bottom-left"), # 1
                (2, 0, "left"),      # 2
                (1, 0, "top-left"),  # 3
                (1, 2, "top-right"), # 4
                (2, 2, "right"),     # 5
                (3, 2, "bottom-right") # 6
            ],
            8: [
                (3, 1, "bottom"),    # 0
                (3, 0, "bottom-left"), # 1
                (2, 0, "left"),      # 2
                (1, 0, "top-left"),  # 3
                (1, 1, "top"),       # 4
                (1, 2, "top-right"), # 5
                (2, 2, "right"),     # 6
                (3, 2, "bottom-right") # 7
            ],
            9: [
                (4, 1, "bottom"),    # 0
                (3, 0, "bottom-left"), # 1
                (2, 0, "left"),      # 2
                (1, 0, "top-left"),  # 3
                (1, 1, "top"),       # 4
                (1, 2, "top-right"), # 5
                (2, 2, "right"),     # 6
                (3, 2, "bottom-right"), # 7
                (4, 2, "bottom-right-2") # 8
            ]
        }
        
        return layouts.get(num_players, layouts[9][:num_players])
    
    def setup_standard_game(self, num_human_players: int = 1, total_players: int = 6):
        """
        Set up a standard game with human players and bots.
        
        Args:
            num_human_players: Number of human players (1-2 recommended)
            total_players: Total players at table (2-9)
        """
        total_players = max(2, min(total_players, self.MAX_PLAYERS))
        num_human_players = max(1, min(num_human_players, total_players))
        
        # Clear existing players
        self.players.clear()
        
        # Add human players first
        for i in range(num_human_players):
            human_name = "You" if i == 0 else f"Player {i + 1}"
            self.add_player(human_name, chips=1000, is_human=True)
        
        # Fill remaining seats with bots
        while len(self.players) < total_players:
            bot_num = len(self.players) - num_human_players + 1
            self.add_player(f"Bot {bot_num}", chips=1000, is_human=False)
        
        # Set initial dealer position randomly
        import random
        self.dealer_position = random.randint(0, len(self.players) - 1)
    

class PokerTableFactory:
    """Factory class for creating different types of poker tables"""
    
    @staticmethod
    def create_table(table_type: str = "nine_player", **kwargs) -> BasePokerTable:
        """
        Create a poker table of the specified type.
        
        Args:
            table_type: Type of table ("nine_player", "heads_up", etc.)
            **kwargs: Additional arguments for table creation
        
        Returns:
            BasePokerTable instance
        """
        if table_type == "nine_player":
            return NinePlayerTable(**kwargs)
        elif table_type == "heads_up":
            table = NinePlayerTable(**kwargs)
            table.max_players = 2
            return table
        elif table_type == "six_max":
            table = NinePlayerTable(**kwargs)
            table.max_players = 6
            return table
        else:
            raise ValueError(f"Unknown table type: {table_type}")