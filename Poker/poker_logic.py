"""
Texas Hold'em Poker Game Logic Module

This module contains the core game logic for Texas Hold'em poker,
separate from the UI implementation.
"""

import random
import sys
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import cardCommon

PokerCard = cardCommon.PokerCard
PokerDeck = cardCommon.PokerDeck


class GamePhase(Enum):
    """GamePhase enumerates the sequential phases of a standard Texas Hold'em hand.

    Phases:

        WAITING   : Waiting for enough players to start (value: "Esperando jugadores").
        PRE_FLOP  : Hole cards dealt; first betting round (value: "Pre-flop").
        FLOP      : Three community cards revealed; second betting round (value: "Flop").
        TURN      : Fourth community card revealed; third betting round (value: "Turn").
        RIVER     : Fifth community card revealed; final betting round (value: "River").
        SHOWDOWN  : Remaining players reveal hands to determine the winner (value: "Showdown").
        FINISHED  : Hand resolution complete; pot awarded; ready for next hand (value: "Mano terminada").

    Typical lifecycle:
        WAITING -> PRE_FLOP -> FLOP -> TURN -> RIVER -> SHOWDOWN -> FINISHED

    Notes:
        - Transition logic should ensure phases advance in the defined order.
        - FINISHED indicates cleanup/reset is required before starting a new hand.
    """

    WAITING = "Esperando jugadores"
    PRE_FLOP = "Pre-flop"
    FLOP = "Flop"
    TURN = "Turn"
    RIVER = "River"
    SHOWDOWN = "Showdown"
    FINISHED = "Mano terminada"


class PlayerAction(Enum):
    """Represents the various actions a player can take during their turn.

    Actions:

        FOLD    : Player folds their hand, forfeiting any claim to the pot (value: "fold").
        CALL    : Player matches the current highest bet (value: "call").
        RAISE   : Player increases the current bet by at least the minimum raise amount (value: "raise").
        CHECK   : Player passes action without betting when no bet is required (value: "check").
        ALL_IN  : Player bets all their remaining chips (value: "all_in").
    """

    FOLD = "fold"
    CALL = "call"
    RAISE = "raise"
    CHECK = "check"
    ALL_IN = "all_in"


@dataclass
class Player:
    """Represents a player at the poker table.

    Attributes:

        name: Player's display name.
        chips: Current chip count.
        position: Seat position at the table (0-indexed).
        hand: List of two hole cards.
        current_bet: Amount currently bet in the ongoing betting round.
        total_bet_in_hand: Total amount bet in the current hand.
        is_active: Whether the player is still active in the hand (not folded).
        is_folded: Whether the player has folded this hand.
        is_all_in: Whether the player is all-in.
        is_human: Whether the player is a human or a bot.
    """

    name: str
    chips: int
    position: int
    hand: List[PokerCard] = None  # type: ignore
    current_bet: int = 0
    total_bet_in_hand: int = 0
    is_active: bool = True
    is_folded: bool = False
    is_all_in: bool = False
    is_human: bool = False

    def __post_init__(self):
        """Initialize the player's hand."""
        if self.hand is None:
            self.hand = []

    def can_act(self) -> bool:
        """Check if the player can take an action (not folded or all-in and has chips)"""
        return (
            self.is_active
            and not self.is_folded
            and not self.is_all_in
            and self.chips > 0
        )

    def reset_for_new_hand(self):
        """Reset player state for a new hand"""
        self.hand = []
        self.current_bet = 0
        self.total_bet_in_hand = 0
        self.is_folded = False
        self.is_all_in = False
        self.is_active = self.chips > 0  # Only active if has chips


class HandRanking(Enum):
    """Enumeration of poker hand rankings from lowest to highest.

    Rankings:

        HIGH_CARD       : No combination, highest card wins (value: 1).
        ONE_PAIR       : Two cards of the same rank (value: 2).
        TWO_PAIR       : Two different pairs (value: 3).
        THREE_OF_A_KIND: Three cards of the same rank (value: 4).
        STRAIGHT       : Five consecutive cards of mixed suits (value: 5).
        FLUSH          : Five cards of the same suit (value: 6).
        FULL_HOUSE     : Three of a kind plus a pair (value: 7).
        FOUR_OF_A_KIND : Four cards of the same rank (value: 8).
        STRAIGHT_FLUSH : Five consecutive cards of the same suit (value: 9).
        ROYAL_FLUSH    : A, K, Q, J, 10 all of the same suit (value: 10).
    """

    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class PokerTable:
    """
    Base class for a Texas Hold'em poker table supporting up to 9 players.
    Manages game state, players, and core game logic.
    """

    MAX_PLAYERS = 9

    def __init__(self, small_blind: int = 10, big_blind: int = 20):
        self.deck = PokerDeck()
        self.players: List[Player] = []
        self.community_cards: List[PokerCard] = []
        self.pot = 0
        self.side_pots = []  # For all-in situations
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.dealer_position = 0
        self.current_player = 0
        self.current_bet = 0
        self.phase = GamePhase.WAITING
        self.min_raise = big_blind
        self.betting_round_complete = False
        self.last_hand_results: List[Dict[str, Any]] = []

    def add_player(self, name: str, chips: int = 1000, is_human: bool = False) -> bool:
        """Add a player to the table.

        Args:
            name: Player's display name. \n
            chips: Starting chip count (default 1000).
            is_human: Whether the player is human or bot (default False).

        Returns:
            bool: True if player added successfully, False if table is full.
        """
        if len(self.players) >= self.MAX_PLAYERS:
            return False

        position = len(self.players)
        player = Player(name=name, chips=chips, position=position, is_human=is_human)
        self.players.append(player)
        return True

    def fill_with_bots(self, target_players: Optional[int] = None):
        """Fill empty seats with bot players.

        Args:
            target_players (Optional[int]): Desired total number of players (2-9). If None, fills to max or current+1.
        """
        if target_players is None:
            target_players = min(self.MAX_PLAYERS, max(2, len(self.players) + 1))

        target_players = min(target_players, self.MAX_PLAYERS)

        while len(self.players) < target_players:
            bot_name = f"Bot {len(self.players)}"
            self.add_player(bot_name, chips=1000, is_human=False)

    def start_new_hand(self):
        """Inicia una nueva mano de poker"""
        self.last_hand_results = []
        if len([p for p in self.players if p.chips > 0]) < 2:
            self.phase = GamePhase.FINISHED
            return

        # Reset game state
        self.deck = PokerDeck()
        self.deck.shuffle()
        self.community_cards = []
        self.pot = 0
        self.side_pots = []
        self.current_bet = 0
        self.min_raise = self.big_blind
        self.phase = GamePhase.PRE_FLOP
        self.betting_round_complete = False

        # Reset players for new hand
        for player in self.players:
            player.reset_for_new_hand()

        # Remove broke players
        self.players = [p for p in self.players if p.chips > 0]

        if len(self.players) < 2:
            self.phase = GamePhase.FINISHED
            return

        # Update positions after removing players
        for i, player in enumerate(self.players):
            player.position = i

        # Move dealer button
        self.dealer_position = (self.dealer_position + 1) % len(self.players)

        # Deal hole cards
        for _ in range(2):
            for player in self.players:
                player.hand.extend(self.deck.deal(1))

        # Post blinds
        self._post_blinds()

        # Set current player (left of big blind)
        self._set_first_to_act()

    def _post_blinds(self):
        """Posts small blind and big blind"""
        if len(self.players) < 2:
            return

        if len(self.players) == 2:
            # Heads up: dealer posts small blind
            sb_pos = self.dealer_position
            bb_pos = (self.dealer_position + 1) % len(self.players)
        else:
            sb_pos = (self.dealer_position + 1) % len(self.players)
            bb_pos = (self.dealer_position + 2) % len(self.players)

        # Small blind
        sb_player = self.players[sb_pos]
        sb_amount = min(self.small_blind, sb_player.chips)
        sb_player.current_bet = sb_amount
        sb_player.total_bet_in_hand = sb_amount
        sb_player.chips -= sb_amount
        self.pot += sb_amount
        if sb_player.chips == 0:
            sb_player.is_all_in = True

        # Big blind
        bb_player = self.players[bb_pos]
        bb_amount = min(self.big_blind, bb_player.chips)
        bb_player.current_bet = bb_amount
        bb_player.total_bet_in_hand = bb_amount
        bb_player.chips -= bb_amount
        self.pot += bb_amount
        self.current_bet = bb_amount
        if bb_player.chips == 0:
            bb_player.is_all_in = True

    def _set_first_to_act(self):
        """Set the first player to act in the current betting round"""
        if self.phase == GamePhase.PRE_FLOP:
            if len(self.players) == 2:
                # Heads up: big blind acts first preflop
                self.current_player = (self.dealer_position + 1) % len(self.players)
            else:
                # Multi-way: first player after big blind
                self.current_player = (self.dealer_position + 3) % len(self.players)
        else:
            # Post-flop: first active player after dealer
            self.current_player = (self.dealer_position + 1) % len(self.players)

        # Find first player who can act
        players_checked = 0
        while players_checked < len(self.players):
            if self.players[self.current_player].can_act():
                break
            self.current_player = (self.current_player + 1) % len(self.players)
            players_checked += 1

    def advance_phase(self):
        """Advance to the next phase of the hand"""
        if self.phase == GamePhase.PRE_FLOP:
            self._deal_flop()
            self.phase = GamePhase.FLOP
        elif self.phase == GamePhase.FLOP:
            self._deal_turn()
            self.phase = GamePhase.TURN
        elif self.phase == GamePhase.TURN:
            self._deal_river()
            self.phase = GamePhase.RIVER
        elif self.phase == GamePhase.RIVER:
            self.phase = GamePhase.SHOWDOWN
            self._showdown()

        # Reset for new betting round
        if self.phase in [GamePhase.FLOP, GamePhase.TURN, GamePhase.RIVER]:
            self.current_bet = 0
            self.min_raise = self.big_blind
            for player in self.players:
                player.current_bet = 0
            self._set_first_to_act()
            self.betting_round_complete = False

    def _deal_flop(self):
        """Deal the flop (3 community cards)"""
        self.deck.deal(1)  # Burn card
        self.community_cards.extend(self.deck.deal(3))

    def _deal_turn(self):
        """Deal the turn (4th community card)"""
        self.deck.deal(1)  # Burn card
        self.community_cards.extend(self.deck.deal(1))

    def _deal_river(self):
        """Deal the river (5th community card)"""
        self.deck.deal(1)  # Burn card
        self.community_cards.extend(self.deck.deal(1))

    def _showdown(self):
        """Handle showdown - determine winner(s)"""
        active_players = [p for p in self.players if not p.is_folded]
        if len(active_players) == 1:
            # Only one player left - they win
            winner = active_players[0]
            winnings = self.pot
            winner.chips += winnings
            self.last_hand_results = [
                {"player": winner, "name": winner.name, "amount": winnings}
            ]
            self.pot = 0
            self.phase = GamePhase.FINISHED
            return self.last_hand_results

        # Evaluate hands and determine winners
        player_hands = []
        showdown_map: Dict[int, Tuple[HandRanking, Tuple[int, ...]]] = {}
        for player in active_players:
            ranking, tiebreakers = self.evaluate_hand(
                player.hand + self.community_cards
            )
            key = tuple(tiebreakers)
            showdown_map[player.position] = (ranking, key)
            player_hands.append((player, ranking, key))

        # Sort by hand strength (higher is better)
        player_hands.sort(key=lambda x: (x[1].value, x[2]), reverse=True)

        # Find all players with the best hand (for ties)
        best_ranking = player_hands[0][1]
        best_tiebreakers = player_hands[0][2]
        winners = [
            p
            for p, ranking, tiebreakers in player_hands
            if ranking == best_ranking and tiebreakers == best_tiebreakers
        ]

        # Distribute pot
        pot_share = self.pot // len(winners)
        remainder = self.pot % len(winners)

        results: List[Dict[str, Any]] = []
        for i, winner in enumerate(winners):
            winnings = pot_share
            if i < remainder:  # Distribute remainder to first winners
                winnings += 1
            winner.chips += winnings
            ranking_enum = showdown_map[winner.position][0]
            results.append(
                {
                    "player": winner,
                    "name": winner.name,
                    "amount": winnings,
                    "ranking": ranking_enum,
                    "ranking_name": self._hand_ranking_to_string(ranking_enum),
                }
            )

        self.pot = 0
        self.phase = GamePhase.FINISHED
        self.last_hand_results = results
        self._log_hand_scores(showdown_map=showdown_map, winners=winners)
        return results

    def evaluate_hand(self, cards: List[PokerCard]) -> Tuple[HandRanking, List[int]]:
        """
        Evaluate a 7-card hand (2 hole cards + 5 community cards)
        Returns (HandRanking, tiebreaker_values)
        """
        if len(cards) != 7:
            raise ValueError("Must evaluate exactly 7 cards")

        # Get all possible 5-card combinations
        from itertools import combinations

        best_hand = None
        best_ranking = HandRanking.HIGH_CARD
        best_tiebreakers = []

        for combo in combinations(cards, 5):
            ranking, tiebreakers = self._evaluate_5_card_hand(list(combo))
            if ranking.value > best_ranking.value or (
                ranking.value == best_ranking.value and tiebreakers > best_tiebreakers
            ):
                best_hand = combo
                best_ranking = ranking
                best_tiebreakers = tiebreakers

        return best_ranking, best_tiebreakers

    def _evaluate_5_card_hand(
        self, cards: List[PokerCard]
    ) -> Tuple[HandRanking, List[int]]:
        """Evaluate exactly 5 cards and return ranking with tiebreakers"""
        values = [card.get_numeric_value() for card in cards]
        suits = [card.suit for card in cards]

        value_counts = Counter(values)
        is_flush = len(set(suits)) == 1

        # Check for straight
        sorted_values = sorted(set(values))
        is_straight = False
        straight_high = 0

        if len(sorted_values) == 5 and sorted_values[-1] - sorted_values[0] == 4:
            is_straight = True
            straight_high = sorted_values[-1]
        elif sorted_values == [2, 3, 4, 5, 14]:  # A-2-3-4-5 straight
            is_straight = True
            straight_high = 5  # In low straight, 5 is the high card

        # Sort value counts for tiebreakers
        counts = sorted(value_counts.items(), key=lambda x: (x[1], x[0]), reverse=True)

        # Determine hand ranking
        if is_straight and is_flush:
            if straight_high == 14 and min(values) == 10:
                return HandRanking.ROYAL_FLUSH, [14]
            else:
                return HandRanking.STRAIGHT_FLUSH, [straight_high]
        elif 4 in value_counts.values():
            four_kind = [v for v, c in counts if c == 4][0]
            kicker = [v for v, c in counts if c == 1][0]
            return HandRanking.FOUR_OF_A_KIND, [four_kind, kicker]
        elif 3 in value_counts.values() and 2 in value_counts.values():
            three_kind = [v for v, c in counts if c == 3][0]
            pair = [v for v, c in counts if c == 2][0]
            return HandRanking.FULL_HOUSE, [three_kind, pair]
        elif is_flush:
            return HandRanking.FLUSH, sorted(values, reverse=True)
        elif is_straight:
            return HandRanking.STRAIGHT, [straight_high]
        elif 3 in value_counts.values():
            three_kind = [v for v, c in counts if c == 3][0]
            kickers = sorted([v for v, c in counts if c == 1], reverse=True)
            return HandRanking.THREE_OF_A_KIND, [three_kind] + kickers
        elif list(value_counts.values()).count(2) == 2:
            pairs = sorted([v for v, c in counts if c == 2], reverse=True)
            kicker = [v for v, c in counts if c == 1][0]
            return HandRanking.TWO_PAIR, pairs + [kicker]
        elif 2 in value_counts.values():
            pair = [v for v, c in counts if c == 2][0]
            kickers = sorted([v for v, c in counts if c == 1], reverse=True)
            return HandRanking.ONE_PAIR, [pair] + kickers
        else:
            return HandRanking.HIGH_CARD, sorted(values, reverse=True)

    def get_valid_actions(self, player_position: int) -> List[PlayerAction]:
        """Get valid actions for a player"""
        player = self.players[player_position]
        if not player.can_act():
            return []

        actions = []

        # Can always fold
        actions.append(PlayerAction.FOLD)

        # Check/call logic
        if self.current_bet == 0:
            actions.append(PlayerAction.CHECK)
        else:
            call_amount = self.current_bet - player.current_bet
            if call_amount <= player.chips:
                actions.append(PlayerAction.CALL)
            if call_amount >= player.chips and player.chips > 0:
                actions.append(PlayerAction.ALL_IN)

        # Raise logic
        if player.chips > self.current_bet - player.current_bet:
            min_raise_total = self.current_bet + self.min_raise
            if player.chips + player.current_bet >= min_raise_total:
                actions.append(PlayerAction.RAISE)
            elif player.chips > 0:
                actions.append(PlayerAction.ALL_IN)

        return actions

    def execute_action(
        self, player_position: int, action: PlayerAction, amount: int = 0
    ) -> bool:
        """Execute a player action. Returns True if successful."""
        if player_position != self.current_player:
            return False

        player = self.players[player_position]
        if not player.can_act():
            return False

        valid_actions = self.get_valid_actions(player_position)
        if action not in valid_actions:
            return False

        if action == PlayerAction.FOLD:
            player.is_folded = True
        elif action == PlayerAction.CHECK:
            pass  # No action needed
        elif action == PlayerAction.CALL:
            call_amount = min(self.current_bet - player.current_bet, player.chips)
            player.chips -= call_amount
            player.current_bet += call_amount
            player.total_bet_in_hand += call_amount
            self.pot += call_amount
            if player.chips == 0:
                player.is_all_in = True
        elif action == PlayerAction.RAISE:
            # Validate raise amount
            total_bet = max(amount, self.current_bet + self.min_raise)
            raise_amount = min(total_bet - player.current_bet, player.chips)

            player.chips -= raise_amount
            player.current_bet += raise_amount
            player.total_bet_in_hand += raise_amount
            self.pot += raise_amount

            self.current_bet = player.current_bet
            self.min_raise = raise_amount - (self.current_bet - player.current_bet)

            if player.chips == 0:
                player.is_all_in = True
        elif action == PlayerAction.ALL_IN:
            all_in_amount = player.chips
            player.chips = 0
            player.current_bet += all_in_amount
            player.total_bet_in_hand += all_in_amount
            self.pot += all_in_amount
            player.is_all_in = True

            if player.current_bet > self.current_bet:
                self.min_raise = max(
                    self.min_raise, player.current_bet - self.current_bet
                )
                self.current_bet = player.current_bet

        # Move to next player
        self._next_player()

        # Check if betting round is complete
        self._check_betting_round_complete()

        if self.is_hand_over() and not self.last_hand_results:
            self._finalize_uncontested_pot()

        return True

    def _finalize_uncontested_pot(self):
        """Award the pot to the remaining active player when everyone else folds."""
        active_players = [p for p in self.players if not p.is_folded]
        if len(active_players) != 1:
            return

        winner = active_players[0]
        winnings = self.pot
        winner.chips += winnings
        self.pot = 0
        self.phase = GamePhase.FINISHED
        self.last_hand_results = [
            {
                "player": winner,
                "name": winner.name,
                "amount": winnings,
                "ranking": None,
                "ranking_name": "Ganó sin mostrar mano",
            }
        ]
        self.betting_round_complete = True
        self._log_hand_scores(
            showdown_map=None, winners=[winner], note="Ganador por abandono"
        )

    def _next_player(self):
        """Move to the next player who can act"""
        players_checked = 0
        while players_checked < len(self.players):
            self.current_player = (self.current_player + 1) % len(self.players)
            if self.players[self.current_player].can_act():
                break
            players_checked += 1

    def _check_betting_round_complete(self):
        """Check if the current betting round is complete"""
        active_players = [p for p in self.players if not p.is_folded]

        if len(active_players) <= 1:
            self.betting_round_complete = True
            return

        acting_players = [p for p in active_players if not p.is_all_in]

        if len(acting_players) == 0:
            # All remaining players are all-in
            self.betting_round_complete = True
            return

        if len(acting_players) == 1:
            # Only one player can act, others are all-in
            self.betting_round_complete = True
            return

        # Check if all acting players have matched the current bet
        all_matched = True
        for player in acting_players:
            if player.current_bet != self.current_bet:
                all_matched = False
                break

        self.betting_round_complete = all_matched

    def is_hand_over(self) -> bool:
        """Check if the current hand is over"""
        active_players = [p for p in self.players if not p.is_folded]
        return (
            len(active_players) <= 1
            or self.phase == GamePhase.FINISHED
            or self.phase == GamePhase.SHOWDOWN
        )

    def _hand_ranking_to_string(self, ranking: Optional[HandRanking]) -> str:
        mapping = {
            HandRanking.HIGH_CARD: "Carta alta",
            HandRanking.ONE_PAIR: "Pareja",
            HandRanking.TWO_PAIR: "Doble pareja",
            HandRanking.THREE_OF_A_KIND: "Trío",
            HandRanking.STRAIGHT: "Escalera",
            HandRanking.FLUSH: "Color",
            HandRanking.FULL_HOUSE: "Full House",
            HandRanking.FOUR_OF_A_KIND: "Póker",
            HandRanking.STRAIGHT_FLUSH: "Escalera de color",
            HandRanking.ROYAL_FLUSH: "Escalera real",
        }
        if ranking is None:
            return "Sin puntuación"
        return mapping.get(ranking, ranking.name.replace("_", " ").title())

    def _cards_to_text(self, cards: List[PokerCard]) -> str:
        if not cards:
            return "-"
        suit_symbols = {
            "Corazones": "♥",
            "Diamantes": "♦",
            "Picas": "♠",
            "Tréboles": "♣",
            "Treboles": "♣",
        }
        parts: List[str] = []
        for card in cards:
            symbol = suit_symbols.get(card.suit, card.suit[:1])
            parts.append(f"{card.value}{symbol}")
        return " ".join(parts)

    def _format_player_cards(self, player: Player) -> str:
        return self._cards_to_text(player.hand)

    def _log_hand_scores(
        self,
        showdown_map: Optional[Dict[int, Tuple[HandRanking, Tuple[int, ...]]]] = None,
        winners: Optional[List[Player]] = None,
        note: str = "",
    ) -> None:
        print("\n=== Resumen de la mano ===")
        if note:
            print(note)
        community_text = self._cards_to_text(self.community_cards)
        if community_text != "-":
            print(f"Cartas comunitarias: {community_text}")

        winners_positions = {p.position for p in winners} if winners else set()

        for player in self.players:
            status_parts = []
            if player.position in winners_positions:
                status_parts.append("Ganador")
            if player.is_folded:
                status_parts.append("Retirado")
            elif player.is_all_in and not player.is_folded:
                status_parts.append("All-in")
            status = ", ".join(status_parts) if status_parts else "Activo"

            ranking = None
            if showdown_map and player.position in showdown_map:
                ranking = showdown_map[player.position][0]
            elif (
                showdown_map is None
                and len(self.community_cards) == 5
                and len(player.hand) >= 2
            ):
                try:
                    ranking, _ = self.evaluate_hand(player.hand + self.community_cards)
                except ValueError:
                    ranking = None

            ranking_text = self._hand_ranking_to_string(ranking)
            print(
                f"{player.name}: {status} | Cartas: {self._format_player_cards(player)} "
                f"| Puntuación: {ranking_text} | Apuesta total: ${player.total_bet_in_hand}"
            )

        print("==========================\n")

    def get_bot_action(self, player_position: int) -> Tuple[PlayerAction, int]:
        """Get a bot action (simple random strategy for now)"""
        valid_actions = self.get_valid_actions(player_position)
        if not valid_actions:
            return PlayerAction.FOLD, 0

        # Simple bot strategy
        player = self.players[player_position]

        # Random decision making (can be improved)
        if PlayerAction.CHECK in valid_actions and random.random() < 0.4:
            return PlayerAction.CHECK, 0
        elif PlayerAction.CALL in valid_actions and random.random() < 0.6:
            return PlayerAction.CALL, 0
        elif PlayerAction.RAISE in valid_actions and random.random() < 0.2:
            # Simple raise: minimum raise or small random amount
            min_raise_total = self.current_bet + self.min_raise
            max_raise = min(player.chips + player.current_bet, min_raise_total * 3)
            raise_amount = random.randint(min_raise_total, max_raise)
            return PlayerAction.RAISE, raise_amount
        elif PlayerAction.FOLD in valid_actions:
            return PlayerAction.FOLD, 0
        else:
            # Fallback
            return valid_actions[0], 0
