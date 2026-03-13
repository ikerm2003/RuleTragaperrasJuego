import os
import random
import sys
import time
import json
from enum import Enum
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

import RuleTragaperrasJuego.cardCommon as cardCommon

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent.parent
package_parent_dir = parent_dir.parent
for path_entry in (package_parent_dir, parent_dir):
    str_path = str(path_entry)
    if str_path not in sys.path:
        sys.path.insert(0, str_path)

from RuleTragaperrasJuego.game_events import GameRoundEvent, get_game_event_service
from RuleTragaperrasJuego.config import config_manager
from RuleTragaperrasJuego.sound_manager import get_sound_manager

BaseCard = cardCommon.BaseCard
BaseDeck = cardCommon.BaseDeck


class BlackjackCard(BaseCard):
    """Carta específica para Blackjack con valores estándar"""

    BLACKJACK_VALUES = [
        "A",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
        "J",
        "Q",
        "K",
    ]
    BLACKJACK_SUITS = ["Hearts", "Diamonds", "Clubs", "Spades"]

    def __init__(self, value, suit):
        if value not in self.BLACKJACK_VALUES:
            raise ValueError(f"Valor inválido: {value}")
        if suit not in self.BLACKJACK_SUITS:
            raise ValueError(f"Palo inválido: {suit}")
        super().__init__(value, suit)

    def get_numeric_value(self) -> int:
        """Devuelve el valor numérico básico de la carta para Blackjack"""
        if self.value in ["J", "Q", "K"]:
            return 10
        elif self.value == "A":
            return 11  # Aces default to 11, adjusted later if needed
        else:
            return int(self.value)

    def is_ace(self) -> bool:
        """Verifica si la carta es un As"""
        return self.value == "A"


class BlackjackDeck(BaseDeck):
    """Baraja estándar de 52 cartas para Blackjack"""

    def _create_deck(self) -> list:
        """Crea una baraja completa de Blackjack"""
        self.cards = []
        for suit in BlackjackCard.BLACKJACK_SUITS:
            for value in BlackjackCard.BLACKJACK_VALUES:
                self.cards.append(BlackjackCard(value, suit))
        return self.cards


class GameState(Enum):
    """Estados del juego de Blackjack"""

    BETTING = "betting"
    DEALING = "dealing"
    PLAYER_TURN = "player_turn"
    DEALER_TURN = "dealer_turn"
    GAME_OVER = "game_over"


class BlackjackGame:
    """Lógica completa del juego de Blackjack"""

    def __init__(self, initial_balance: int = 1000):
        self.deck = BlackjackDeck()
        self.deck.shuffle()

        self.player_hand: List[BlackjackCard] = []
        self.dealer_hand: List[BlackjackCard] = []

        self.balance = initial_balance
        self.current_bet = 0
        self.state = GameState.BETTING

        self.player_stood = False
        self.insurance_bet = 0
        self.hand_resolved = False
        self.last_result = ""
        self.last_winnings = 0
        self.split_mode = False
        self.split_hands: List[List[BlackjackCard]] = []
        self.split_bets: List[int] = []
        self.current_hand_index = 0

    def calculate_hand_value(self, hand: List[BlackjackCard]) -> int:
        """Calcula el valor de una mano, ajustando Ases si es necesario"""
        value = sum(card.get_numeric_value() for card in hand)
        aces = sum(1 for card in hand if card.is_ace())

        # Ajustar Ases de 11 a 1 si la mano se pasa de 21
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1

        return value

    def is_blackjack(self, hand: List[BlackjackCard]) -> bool:
        """Verifica si una mano es Blackjack (21 con 2 cartas)"""
        return len(hand) == 2 and self.calculate_hand_value(hand) == 21

    def can_double(self) -> bool:
        """Verifica si el jugador puede doblar"""
        active_bet = self.current_bet
        if self.split_mode and self.split_bets:
            active_bet = self.split_bets[self.current_hand_index]

        return (
            self.state == GameState.PLAYER_TURN
            and len(self.player_hand) == 2
            and self.balance >= active_bet
        )

    def can_split(self) -> bool:
        """Verifica si el jugador puede dividir su mano inicial"""
        return (
            self.state == GameState.PLAYER_TURN
            and not self.split_mode
            and
            len(self.player_hand) == 2
            and self.player_hand[0].value == self.player_hand[1].value
            and self.balance >= self.current_bet
        )

    def can_take_insurance(self) -> bool:
        """Verifica si el jugador puede tomar seguro"""
        return (
            self.state == GameState.PLAYER_TURN
            and not self.split_mode
            and
            len(self.dealer_hand) == 2
            and self.dealer_hand[0].is_ace()
            and self.insurance_bet == 0
            and self.balance >= self.current_bet // 2
        )

    def take_insurance(self) -> bool:
        """El jugador toma seguro (mitad de la apuesta principal)."""
        if not self.can_take_insurance():
            return False

        self.insurance_bet = self.current_bet // 2
        self.balance -= self.insurance_bet
        return True

    def split_hand(self) -> bool:
        """Divide la mano del jugador en dos manos independientes."""
        if not self.can_split():
            return False

        first_card, second_card = self.player_hand

        self.balance -= self.current_bet
        self.split_mode = True
        self.split_hands = [
            [first_card, self.deck.deal(1)[0]],
            [second_card, self.deck.deal(1)[0]],
        ]
        self.split_bets = [self.current_bet, self.current_bet]
        self.current_hand_index = 0
        self.player_hand = self.split_hands[self.current_hand_index]

        return True

    def place_bet(self, amount: int) -> bool:
        """Coloca una apuesta"""
        if amount <= 0 or amount > self.balance:
            return False
        self.current_bet = amount
        self.balance -= amount
        self.state = GameState.DEALING
        self.hand_resolved = False
        self.last_result = ""
        self.last_winnings = 0
        self.split_mode = False
        self.split_hands = []
        self.split_bets = []
        self.current_hand_index = 0
        return True

    def start_new_hand(self):
        """Inicia una nueva mano"""
        if len(self.deck) < 20:  # Rebarajar si quedan pocas cartas
            self.deck = BlackjackDeck()
            self.deck.shuffle()

        self.player_hand = []
        self.dealer_hand = []
        self.player_stood = False
        self.insurance_bet = 0
        self.hand_resolved = False
        self.last_result = ""
        self.last_winnings = 0
        self.split_mode = False
        self.split_hands = []
        self.split_bets = []
        self.current_hand_index = 0

        # Repartir cartas iniciales
        self.player_hand.append(self.deck.deal(1)[0])
        self.dealer_hand.append(self.deck.deal(1)[0])
        self.player_hand.append(self.deck.deal(1)[0])
        self.dealer_hand.append(self.deck.deal(1)[0])

        self.state = GameState.PLAYER_TURN

        # Verificar Blackjack
        if self.is_blackjack(self.player_hand):
            self.state = GameState.DEALER_TURN
            self.resolve_hand()

    def _advance_split_hand_or_resolve(self) -> None:
        """Avanza a la siguiente mano dividida o resuelve ronda si no quedan."""
        if not self.split_mode:
            return

        if self.current_hand_index < len(self.split_hands) - 1:
            self.current_hand_index += 1
            self.player_hand = self.split_hands[self.current_hand_index]
            self.current_bet = self.split_bets[self.current_hand_index]
            self.state = GameState.PLAYER_TURN
            return

        self.state = GameState.DEALER_TURN
        self.dealer_play()

    def hit(self) -> bool:
        """El jugador pide una carta"""
        if self.state != GameState.PLAYER_TURN:
            return False

        self.player_hand.append(self.deck.deal(1)[0])

        if self.calculate_hand_value(self.player_hand) > 21:
            if self.split_mode:
                self._advance_split_hand_or_resolve()
            else:
                self.state = GameState.GAME_OVER
                self.resolve_hand()

        return True

    def stand(self) -> bool:
        """El jugador se planta"""
        if self.state != GameState.PLAYER_TURN:
            return False

        self.player_stood = True
        if self.split_mode:
            self._advance_split_hand_or_resolve()
        else:
            self.state = GameState.DEALER_TURN
            self.dealer_play()
        return True

    def double_down(self) -> bool:
        """El jugador dobla su apuesta"""
        if not self.can_double():
            return False

        active_bet = self.current_bet
        if self.split_mode and self.split_bets:
            active_bet = self.split_bets[self.current_hand_index]

        self.balance -= active_bet

        if self.split_mode and self.split_bets:
            self.split_bets[self.current_hand_index] += active_bet
            self.current_bet = self.split_bets[self.current_hand_index]
        else:
            self.current_bet *= 2

        self.player_hand.append(self.deck.deal(1)[0])

        if self.calculate_hand_value(self.player_hand) > 21:
            if self.split_mode:
                self._advance_split_hand_or_resolve()
            else:
                self.state = GameState.GAME_OVER
                self.resolve_hand()
        else:
            self.player_stood = True
            if self.split_mode:
                self._advance_split_hand_or_resolve()
            else:
                self.state = GameState.DEALER_TURN
                self.dealer_play()

        return True

    def dealer_play(self):
        """El dealer juega su mano"""
        self.state = GameState.DEALER_TURN

        # El dealer debe pedir hasta llegar a 17 o más
        while self.calculate_hand_value(self.dealer_hand) < 17:
            self.dealer_hand.append(self.deck.deal(1)[0])

        self.state = GameState.GAME_OVER
        if self.split_mode:
            self.resolve_split_hands()
        else:
            self.resolve_hand()

    def resolve_hand(self) -> Tuple[str, int]:
        """Resuelve la mano y determina el ganador"""
        if self.split_mode:
            return self.resolve_split_hands()

        if self.hand_resolved:
            return self.last_result, self.last_winnings

        player_value = self.calculate_hand_value(self.player_hand)
        dealer_value = self.calculate_hand_value(self.dealer_hand)

        player_blackjack = self.is_blackjack(self.player_hand)
        dealer_blackjack = self.is_blackjack(self.dealer_hand)

        # Determinar resultado
        if player_value > 21:
            result = "¡Te pasaste! Dealer gana."
            winnings = 0
        elif dealer_value > 21:
            result = "¡Dealer se pasó! Ganaste."
            winnings = self.current_bet * 2
        elif player_blackjack and not dealer_blackjack:
            result = "¡BLACKJACK! Ganaste."
            winnings = int(self.current_bet * 2.5)
        elif dealer_blackjack and not player_blackjack:
            result = "Dealer tiene Blackjack. Perdiste."
            winnings = 0
        elif player_blackjack and dealer_blackjack:
            result = "Empate - Ambos tienen Blackjack."
            winnings = self.current_bet
        elif player_value > dealer_value:
            result = f"Ganaste con {player_value} vs {dealer_value}."
            winnings = self.current_bet * 2
        elif dealer_value > player_value:
            result = f"Dealer gana con {dealer_value} vs {player_value}."
            winnings = 0
        else:
            result = f"Empate con {player_value}."
            winnings = self.current_bet

        insurance_winnings = 0
        if self.insurance_bet > 0 and dealer_blackjack:
            insurance_winnings = self.insurance_bet * 3
            result += " Seguro ganado."

        winnings += insurance_winnings

        self.balance += winnings
        self.state = GameState.BETTING

        self.last_result = result
        self.last_winnings = winnings
        self.hand_resolved = True

        return result, winnings

    def resolve_split_hands(self) -> Tuple[str, int]:
        """Resuelve las manos divididas contra la mano del dealer."""
        if self.hand_resolved:
            return self.last_result, self.last_winnings

        dealer_value = self.calculate_hand_value(self.dealer_hand)
        dealer_blackjack = self.is_blackjack(self.dealer_hand)

        total_winnings = 0
        hand_results = []

        for index, hand in enumerate(self.split_hands):
            bet = self.split_bets[index]
            player_value = self.calculate_hand_value(hand)

            if player_value > 21:
                hand_result = f"Mano {index + 1}: te pasaste ({player_value})."
                winnings = 0
            elif dealer_value > 21:
                hand_result = f"Mano {index + 1}: dealer se pasó, ganaste."
                winnings = bet * 2
            elif dealer_blackjack:
                hand_result = f"Mano {index + 1}: dealer blackjack, perdiste."
                winnings = 0
            elif player_value > dealer_value:
                hand_result = (
                    f"Mano {index + 1}: ganaste con {player_value} vs {dealer_value}."
                )
                winnings = bet * 2
            elif dealer_value > player_value:
                hand_result = (
                    f"Mano {index + 1}: dealer gana con {dealer_value} vs {player_value}."
                )
                winnings = 0
            else:
                hand_result = f"Mano {index + 1}: empate con {player_value}."
                winnings = bet

            total_winnings += winnings
            hand_results.append(hand_result)

        if self.insurance_bet > 0 and dealer_blackjack:
            total_winnings += self.insurance_bet * 3
            hand_results.append("Seguro ganado.")

        self.balance += total_winnings
        self.state = GameState.BETTING
        self.player_hand = self.split_hands[0] if self.split_hands else self.player_hand

        self.last_result = " ".join(hand_results)
        self.last_winnings = total_winnings
        self.hand_resolved = True

        return self.last_result, self.last_winnings


class BlackJackWindow(QMainWindow):
    """Ventana principal del juego de Blackjack"""

    UI_LATENCY_THRESHOLDS_MS: dict[str, float] = {
        "ui.blackjack.deal_ms": 40.0,
        "ui.blackjack.hit_ms": 30.0,
        "ui.blackjack.stand_ms": 35.0,
        "ui.blackjack.double_ms": 40.0,
        "ui.blackjack.split_ms": 45.0,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self.game = BlackjackGame(initial_balance=1000)
        self.parent_window = parent
        self._card_pixmap_cache: dict[tuple[str, str, bool], QPixmap] = {}
        self._ui_perf_metrics: dict[str, list[float]] = {}
        self._round_event_reported = False
        self.sound_manager = get_sound_manager(config_manager)
        self.init_ui()

    def _play_sound(self, method_name: str, *args, **kwargs) -> None:
        manager = self.sound_manager
        if manager is None:
            return
        callback = getattr(manager, method_name, None)
        if callable(callback):
            callback(*args, **kwargs)

    def _record_ui_action_latency(self, action_name: str, start_time: float) -> None:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        metric_name = f"ui.blackjack.{action_name}_ms"
        if metric_name not in self._ui_perf_metrics:
            self._ui_perf_metrics[metric_name] = []
        self._ui_perf_metrics[metric_name].append(elapsed_ms)
        if len(self._ui_perf_metrics[metric_name]) > 100:
            self._ui_perf_metrics[metric_name] = self._ui_perf_metrics[metric_name][-100:]

    def _build_metric_summary(self, metric_name: str, samples: list[float]) -> dict:
        ordered = sorted(samples)
        count = len(ordered)
        p95_index = max(0, min(count - 1, int(count * 0.95) - 1))
        avg_ms = sum(ordered) / count
        threshold_ms = self.UI_LATENCY_THRESHOLDS_MS.get(metric_name)

        return {
            "count": count,
            "avg_ms": round(avg_ms, 3),
            "min_ms": round(ordered[0], 3),
            "max_ms": round(ordered[-1], 3),
            "p95_ms": round(ordered[p95_index], 3),
            "threshold_ms": threshold_ms,
            "within_threshold": (
                None
                if threshold_ms is None
                else round(avg_ms, 3) <= threshold_ms
            ),
        }

    def _export_ui_metrics_baseline(self) -> None:
        if not self._ui_perf_metrics:
            return

        report_path = parent_dir / "performance_baseline.json"
        summary = {
            metric: self._build_metric_summary(metric, samples)
            for metric, samples in self._ui_perf_metrics.items()
            if samples
        }

        if not summary:
            return

        snapshot = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "source": "blackjack",
            "metrics": summary,
        }

        data = {"snapshots": []}
        if report_path.exists():
            try:
                with open(report_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict) and isinstance(loaded.get("snapshots"), list):
                    data = loaded
            except (OSError, json.JSONDecodeError):
                data = {"snapshots": []}

        data["snapshots"].append(snapshot)
        data["snapshots"] = data["snapshots"][-200:]

        try:
            with open(report_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except OSError:
            pass

    def init_ui(self):
        self.setWindowTitle("Blackjack - Casino")
        self.setGeometry(100, 100, 900, 700)

        # Widget principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)

        # Balance display
        balance_layout = QHBoxLayout()
        self.balance_label = QLabel(f"Balance: ${self.game.balance}")
        self.balance_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.balance_label.setStyleSheet("color: gold;")
        balance_layout.addWidget(self.balance_label)
        balance_layout.addStretch()
        main_layout.addLayout(balance_layout)

        # Dealer section
        dealer_label = QLabel("DEALER")
        dealer_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        dealer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(dealer_label)

        # Cartas del dealer
        self.dealer_card_labels = []
        dealer_cards_layout = QHBoxLayout()
        dealer_cards_layout.addStretch()
        for _ in range(7):  # Max 7 cards in most scenarios
            card_label = QLabel()
            card_label.setFixedSize(80, 120)
            card_label.setStyleSheet(
                "border: 2px solid #333; background-color: white; border-radius: 5px;"
            )
            card_label.hide()
            self.dealer_card_labels.append(card_label)
            dealer_cards_layout.addWidget(card_label)
        dealer_cards_layout.addStretch()
        main_layout.addLayout(dealer_cards_layout)

        self.dealer_value_label = QLabel("")
        self.dealer_value_label.setFont(QFont("Arial", 12))
        self.dealer_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.dealer_value_label)

        # Spacer
        main_layout.addSpacing(30)

        # Player section
        player_label = QLabel("PLAYER")
        player_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        player_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(player_label)

        # Cartas del jugador
        self.player_card_labels = []
        player_cards_layout = QHBoxLayout()
        player_cards_layout.addStretch()
        for _ in range(7):
            card_label = QLabel()
            card_label.setFixedSize(80, 120)
            card_label.setStyleSheet(
                "border: 2px solid #333; background-color: white; border-radius: 5px;"
            )
            card_label.hide()
            self.player_card_labels.append(card_label)
            player_cards_layout.addWidget(card_label)
        player_cards_layout.addStretch()
        main_layout.addLayout(player_cards_layout)

        self.player_value_label = QLabel("")
        self.player_value_label.setFont(QFont("Arial", 12))
        self.player_value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.player_value_label)

        # Betting section
        bet_layout = QHBoxLayout()
        bet_label = QLabel("Apuesta:")
        bet_label.setFont(QFont("Arial", 12))
        self.bet_spinbox = QSpinBox()
        self.bet_spinbox.setMinimum(10)
        self.bet_spinbox.setMaximum(1000)
        self.bet_spinbox.setValue(50)
        self.bet_spinbox.setSingleStep(10)
        self.bet_spinbox.setPrefix("$")

        self.deal_button = QPushButton("Repartir")
        self.deal_button.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        self.deal_button.clicked.connect(self.deal_cards)

        bet_layout.addStretch()
        bet_layout.addWidget(bet_label)
        bet_layout.addWidget(self.bet_spinbox)
        bet_layout.addWidget(self.deal_button)
        bet_layout.addStretch()
        main_layout.addLayout(bet_layout)

        # Action buttons
        self.action_layout = QHBoxLayout()
        self.hit_button = QPushButton("Pedir")
        self.stand_button = QPushButton("Plantarse")
        self.double_button = QPushButton("Doblar")
        self.split_button = QPushButton("Split")
        self.insurance_button = QPushButton("Seguro")

        self.hit_button.setFont(QFont("Arial", 12))
        self.stand_button.setFont(QFont("Arial", 12))
        self.double_button.setFont(QFont("Arial", 12))
        self.split_button.setFont(QFont("Arial", 12))
        self.insurance_button.setFont(QFont("Arial", 12))

        self.hit_button.clicked.connect(self.hit)
        self.stand_button.clicked.connect(self.stand)
        self.double_button.clicked.connect(self.double_down)
        self.split_button.clicked.connect(self.split_hand)
        self.insurance_button.clicked.connect(self.take_insurance)

        self.action_layout.addStretch()
        self.action_layout.addWidget(self.hit_button)
        self.action_layout.addWidget(self.stand_button)
        self.action_layout.addWidget(self.double_button)
        self.action_layout.addWidget(self.split_button)
        self.action_layout.addWidget(self.insurance_button)
        self.action_layout.addStretch()
        main_layout.addLayout(self.action_layout)

        # Disable action buttons initially
        self.set_action_buttons_enabled(False)

        # Status label
        self.status_label = QLabel(
            "¡Bienvenido a Blackjack! Coloca tu apuesta para empezar."
        )
        self.status_label.setFont(QFont("Arial", 13))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(
            """
            padding: 10px;
            background-color: rgba(0, 0, 0, 0.5);
            color: white;
            border-radius: 5px;
        """
        )
        main_layout.addWidget(self.status_label)

        # Back button
        back_button = QPushButton("Volver al Menú")
        back_button.clicked.connect(self.close)
        main_layout.addWidget(back_button)

        # Set background
        self.setStyleSheet(
            """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(21, 101, 52, 1),
                           stop:1 rgba(22, 163, 74, 1));
            }
        """
        )

    def set_action_buttons_enabled(self, enabled: bool):
        """Habilita o deshabilita los botones de acción"""
        self.hit_button.setEnabled(enabled)
        self.stand_button.setEnabled(enabled)
        self.double_button.setEnabled(enabled and self.game.can_double())
        self.split_button.setEnabled(enabled and self.game.can_split())
        self.insurance_button.setEnabled(enabled and self.game.can_take_insurance())

    def update_turn_status(self):
        """Actualiza texto de estado durante turno del jugador."""
        if self.game.state != GameState.PLAYER_TURN:
            return

        if self.game.split_mode and self.game.split_hands:
            hand_no = self.game.current_hand_index + 1
            hand_total = len(self.game.split_hands)
            active_bet = self.game.split_bets[self.game.current_hand_index]
            self.status_label.setText(
                f"Split activo. Jugando mano {hand_no}/{hand_total}. "
                f"Apuesta mano: ${active_bet}."
            )

    def finalize_round_if_finished(self):
        """Sincroniza la UI cuando la ronda ya se ha resuelto en la lógica."""
        if self.game.state != GameState.BETTING:
            return

        self.status_label.setText(self.game.last_result)
        self.set_action_buttons_enabled(False)
        self.bet_spinbox.setEnabled(True)
        self.deal_button.setEnabled(True)

        if self._round_event_reported:
            return

        wagered = 0
        if self.game.split_mode and self.game.split_bets:
            wagered = sum(self.game.split_bets)
        elif self.game.current_bet > 0:
            wagered = self.game.current_bet
        wagered += max(0, int(self.game.insurance_bet))

        net_win = int(self.game.last_winnings) - int(wagered)
        try:
            get_game_event_service().record_round(
                GameRoundEvent(
                    game_type="blackjack",
                    rounds_played=1,
                    wagered=wagered,
                    net_win=net_win,
                )
            )
            self._round_event_reported = True
        except Exception:
            pass

        try:
            if net_win > 0:
                self._play_sound("play_win", big_win=net_win >= max(500, wagered * 3))
            elif net_win < 0:
                self._play_sound("play_lose")
            else:
                self._play_sound("play_notification")
        except Exception:
            pass

    def load_card_image(self, card: BlackjackCard, hidden: bool = False):
        """Crea un pixmap con la representación visual de la carta"""
        cache_key = (
            "__hidden__" if hidden else str(card.value),
            "__hidden__" if hidden else str(card.suit),
            hidden,
        )
        cached = self._card_pixmap_cache.get(cache_key)
        if cached is not None:
            return cached

        pixmap = QPixmap(80, 120)

        if hidden:
            # Carta boca abajo
            pixmap.fill(QColor("#1e40af"))
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setPen(QColor("white"))
            painter.drawRect(5, 5, 69, 109)
            painter.drawText(20, 65, "🂠")
            painter.end()
            self._card_pixmap_cache[cache_key] = pixmap
            return pixmap

        # Carta boca arriba
        pixmap.fill(QColor("white"))

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Definir color según el palo
        if card.suit in ["Hearts", "Diamonds"]:
            color = QColor("red")
        else:
            color = QColor("black")

        painter.setPen(color)

        # Fuente para el valor
        font = QFont("Arial", 16, QFont.Weight.Bold)
        painter.setFont(font)

        # Dibujar el valor en la esquina superior izquierda
        painter.drawText(8, 22, card.value)

        # Fuente más pequeña para el símbolo del palo
        font_small = QFont("Arial", 12)
        painter.setFont(font_small)

        # Símbolos de los palos
        suit_symbols = {"Hearts": "♥", "Diamonds": "♦", "Clubs": "♣", "Spades": "♠"}

        # Dibujar símbolo del palo
        painter.drawText(8, 40, suit_symbols.get(card.suit, card.suit))

        # Dibujar valor y símbolo más grandes en el centro
        font_center = QFont("Arial", 24, QFont.Weight.Bold)
        painter.setFont(font_center)
        painter.drawText(20, 70, f"{card.value}")
        painter.drawText(25, 95, suit_symbols.get(card.suit, card.suit))

        # Dibujar borde
        painter.setPen(QColor("#333"))
        painter.drawRect(0, 0, 79, 119)

        painter.end()
        self._card_pixmap_cache[cache_key] = pixmap
        return pixmap

    def update_display(self):
        """Actualiza la visualización de las cartas y valores"""
        # Mostrar cartas del dealer
        for i, label in enumerate(self.dealer_card_labels):
            if i < len(self.game.dealer_hand):
                card = self.game.dealer_hand[i]
                # Ocultar segunda carta del dealer si el jugador aún está jugando
                hide_card = i == 1 and self.game.state == GameState.PLAYER_TURN
                pixmap = self.load_card_image(card, hidden=hide_card)
                card_key = (
                    "dealer",
                    i,
                    "__hidden__" if hide_card else str(card.value),
                    "__hidden__" if hide_card else str(card.suit),
                    hide_card,
                )
                self._update_card_label(label, pixmap, card_key)
            else:
                self._hide_card_label(label)

        # Mostrar valor del dealer
        if self.game.state == GameState.PLAYER_TURN:
            # Solo mostrar valor de la primera carta
            if self.game.dealer_hand:
                dealer_value = self.game.dealer_hand[0].get_numeric_value()
                self._set_label_text_if_changed(
                    self.dealer_value_label, f"Mostrando: {dealer_value}"
                )
            else:
                self._set_label_text_if_changed(self.dealer_value_label, "")
        else:
            dealer_value = self.game.calculate_hand_value(self.game.dealer_hand)
            self._set_label_text_if_changed(self.dealer_value_label, f"Total: {dealer_value}")

        # Mostrar cartas del jugador
        for i, label in enumerate(self.player_card_labels):
            if i < len(self.game.player_hand):
                card = self.game.player_hand[i]
                pixmap = self.load_card_image(card)
                card_key = ("player", i, str(card.value), str(card.suit), False)
                self._update_card_label(label, pixmap, card_key)
            else:
                self._hide_card_label(label)

        # Mostrar valor del jugador
        if self.game.player_hand:
            player_value = self.game.calculate_hand_value(self.game.player_hand)
            if self.game.split_mode and self.game.split_hands:
                hand_no = self.game.current_hand_index + 1
                hand_total = len(self.game.split_hands)
                self._set_label_text_if_changed(
                    self.player_value_label,
                    f"Mano {hand_no}/{hand_total} - Total: {player_value}",
                )
            else:
                self._set_label_text_if_changed(self.player_value_label, f"Total: {player_value}")
        else:
            self._set_label_text_if_changed(self.player_value_label, "")

        # Actualizar balance
        self._set_label_text_if_changed(self.balance_label, f"Balance: ${self.game.balance}")

    def _set_label_text_if_changed(self, label: QLabel, text: str):
        if label.text() != text:
            label.setText(text)

    def _update_card_label(
        self,
        label: QLabel,
        pixmap: QPixmap,
        card_key: tuple[str, int, str, str, bool],
    ):
        if label.property("_last_card_key") != card_key:
            label.setPixmap(pixmap)
            label.setProperty("_last_card_key", card_key)

        if not label.property("_scaled_contents"):
            label.setScaledContents(True)
            label.setProperty("_scaled_contents", True)

        if not label.isVisible():
            label.show()

    def _hide_card_label(self, label: QLabel):
        if label.property("_last_card_key") is not None:
            label.clear()
            label.setProperty("_last_card_key", None)

        if label.isVisible():
            label.hide()

    def deal_cards(self):
        """Reparte las cartas iniciales"""
        bet_amount = self.bet_spinbox.value()

        if bet_amount > self.game.balance:
            QMessageBox.warning(
                self, "Error", "No tienes suficiente balance para esa apuesta."
            )
            return

        if not self.game.place_bet(bet_amount):
            QMessageBox.warning(self, "Error", "No se pudo colocar la apuesta.")
            return

        self._round_event_reported = False

        started_at = time.perf_counter()
        self.game.start_new_hand()
        self.update_display()

        # Verificar si la lógica ya resolvió automáticamente (ej: Blackjack natural)
        if self.game.state == GameState.BETTING:
            self.finalize_round_if_finished()
            self.update_display()
        else:
            self.status_label.setText(f"Apuesta: ${bet_amount}. ¿Qué quieres hacer?")
            self.set_action_buttons_enabled(True)
            self.bet_spinbox.setEnabled(False)
            self.deal_button.setEnabled(False)
            self.update_turn_status()

        try:
            self._play_sound("play_card_deal")
        except Exception:
            pass

        self._record_ui_action_latency("deal", started_at)

    def hit(self):
        """El jugador pide una carta"""
        started_at = time.perf_counter()
        self.game.hit()
        try:
            self._play_sound("play_card_deal")
        except Exception:
            pass
        self.update_display()
        self.finalize_round_if_finished()
        self.update_turn_status()
        self._record_ui_action_latency("hit", started_at)

    def stand(self):
        """El jugador se planta"""
        started_at = time.perf_counter()
        self.game.stand()
        self.update_display()
        self.finalize_round_if_finished()
        self.update_turn_status()
        self._record_ui_action_latency("stand", started_at)

    def double_down(self):
        """El jugador dobla su apuesta"""
        if not self.game.can_double():
            QMessageBox.warning(self, "Error", "No puedes doblar en este momento.")
            return

        started_at = time.perf_counter()
        self.game.double_down()
        try:
            self._play_sound("play_chip_place")
        except Exception:
            pass
        self.update_display()
        self.finalize_round_if_finished()
        self.update_turn_status()
        self._record_ui_action_latency("double", started_at)

    def split_hand(self):
        """Divide la mano actual en dos manos."""
        if not self.game.split_hand():
            QMessageBox.warning(self, "Error", "No puedes hacer split en este momento.")
            return

        started_at = time.perf_counter()
        try:
            self._play_sound("play_chip_place")
        except Exception:
            pass
        self.update_display()
        self.set_action_buttons_enabled(True)
        self.bet_spinbox.setEnabled(False)
        self.deal_button.setEnabled(False)
        self.update_turn_status()
        self._record_ui_action_latency("split", started_at)

    def take_insurance(self):
        """El jugador toma seguro cuando el dealer muestra As."""
        if not self.game.take_insurance():
            QMessageBox.warning(
                self,
                "Error",
                "No puedes tomar seguro en este momento.",
            )
            return

        try:
            self._play_sound("play_chip_place")
        except Exception:
            pass

        self.update_display()
        self.status_label.setText(
            f"Seguro tomado por ${self.game.insurance_bet}. El dealer continúa."
        )
        self.set_action_buttons_enabled(True)

    def closeEvent(self, a0):
        """Handle window close event"""
        self._export_ui_metrics_baseline()
        if self.parent_window:
            self.parent_window.show()
        a0.accept()


def main():
    """Entry point for standalone blackjack game"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        owns_app = True
    else:
        owns_app = False

    window = BlackJackWindow()
    window.show()

    if owns_app:
        sys.exit(app.exec())

    return window, owns_app, app


def open_blackjack_window(parent=None):
    """Open blackjack window from main UI"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        owns_app = True
    else:
        owns_app = False

    window = BlackJackWindow(parent)
    window.show()

    return window, owns_app, app


if __name__ == "__main__":
    main()
