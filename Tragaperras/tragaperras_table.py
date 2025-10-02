"""Controladores y gestores de mesa para el módulo de tragaperras.

Este módulo extiende la lógica de :mod:`tragaperras_logic` para ofrecer una
interfaz lista para enlazar con la capa de UI, siguiendo la estructura usada en
el juego de póker. Permite registrar *callbacks* de interfaz, gestionar
estadísticas de la sesión, almacenar el historial reciente de tiradas y
exponer utilidades de configuración que la UI puede consumir.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Deque, Dict, Iterable, List, Optional, Tuple

from .tragaperras_logic import PAYLINES, SlotMachine, SpinResult, WILD_SYMBOL


# ---------------------------------------------------------------------------
# Modelos de apoyo


Callback = Callable[..., None]


@dataclass(slots=True)
class SlotMachineStatistics:
	"""Estadísticas acumuladas de la sesión actual.

	Attributes
	----------
	total_spins:
		Número total de tiradas ejecutadas.
	total_bet:
		Créditos apostados en total.
	total_payout:
		Créditos devueltos como premios.
	biggest_win:
		Premio neto más alto registrado.
	wild_symbols_seen:
		Conteo total de comodines aparecidos en la cuadricula.
	"""

	total_spins: int = 0
	total_bet: int = 0
	total_payout: int = 0
	biggest_win: int = 0
	wild_symbols_seen: int = 0

	@property
	def net_profit(self) -> int:
		"""Retorna la ganancia neta acumulada."""

		return self.total_payout - self.total_bet

	@property
	def rtp(self) -> float:
		"""Devuelve el retorno teórico al jugador (RTP) acumulado."""

		if self.total_bet <= 0:
			return 0.0
		return self.total_payout / self.total_bet


# ---------------------------------------------------------------------------
# Implementación de la mesa controladora


class BaseSlotMachineTable(SlotMachine):
	"""Extiende :class:`SlotMachine` con utilidades para la capa de UI."""

	def __init__(
		self,
		*,
		history_size: int = 30,
		**kwargs,
	) -> None:
		super().__init__(**kwargs)
		self._callbacks: Dict[str, List[Callback]] = {}
		self._history: Deque[SpinResult] = deque(maxlen=history_size)
		self.statistics = SlotMachineStatistics()
		self._is_spinning: bool = False

	# ------------------------------------------------------------------
	# Gestión de callbacks

	def register_ui_callback(self, event: str, callback: Callback) -> None:
		"""Registra una función a invocar cuando ocurra ``event``."""

		self._callbacks.setdefault(event, []).append(callback)

	def unregister_ui_callback(self, event: str, callback: Callback) -> None:
		"""Elimina un callback registrado si está presente."""

		callbacks = self._callbacks.get(event)
		if not callbacks:
			return
		try:
			callbacks.remove(callback)
		except ValueError:
			pass
		if not callbacks:
			self._callbacks.pop(event, None)

	def clear_callbacks(self) -> None:
		"""Elimina todas las subscripciones registradas."""

		self._callbacks.clear()

	def _notify(self, event: str, **payload) -> None:
		for callback in self._callbacks.get(event, []):
			callback(**payload)

	# ------------------------------------------------------------------
	# Overrides con notificaciones

	def set_bet_per_line(self, amount: int) -> None:  # type: ignore[override]
		super().set_bet_per_line(amount)
		self._notify("bet_changed", bet_per_line=self.bet_per_line)

	def set_active_lines(self, lines: Iterable[int]) -> None:  # type: ignore[override]
		super().set_active_lines(lines)
		self._notify("lines_changed", lines=self.active_lines)

	def add_credits(self, amount: int) -> None:  # type: ignore[override]
		super().add_credits(amount)
		self._notify("balance_changed", balance=self.balance)

	def spin(self) -> SpinResult:  # type: ignore[override]
		if self._is_spinning:
			raise RuntimeError("Ya hay una tirada en curso")

		total_bet = self.bet_per_line * len(self.active_lines)
		self._notify(
			"spin_started",
			bet_per_line=self.bet_per_line,
			lines=self.active_lines,
			total_bet=total_bet,
		)

		self._is_spinning = True
		try:
			result = super().spin()
		finally:
			self._is_spinning = False

		self._history.appendleft(result)
		self._update_statistics(result)

		self._notify("spin_completed", result=result)
		self._notify("balance_changed", balance=self.balance)
		self._notify("statistics_changed", statistics=self.statistics)

		return result

	# ------------------------------------------------------------------
	# Utilidades públicas

	def is_spinning(self) -> bool:
		"""Indica si hay una tirada en progreso."""

		return self._is_spinning

	def get_history(self) -> Tuple[SpinResult, ...]:
		"""Devuelve el historial reciente de tiradas."""

		return tuple(self._history)

	def get_statistics(self) -> SlotMachineStatistics:
		"""Devuelve las estadísticas acumuladas (referencia viva)."""

		return self.statistics

	def reset_statistics(self) -> None:
		"""Reinicia las estadísticas acumuladas."""

		self.statistics = SlotMachineStatistics()
		self._notify("statistics_changed", statistics=self.statistics)

	def sample_symbol(self) -> str:
		"""Obtiene un símbolo aleatorio usando la configuración actual.

		Resulta útil para animaciones de UI que desean mostrar símbolos
		transitorios durante las tiradas.
		"""

		return self.rng.choices(self._symbols, weights=self._weights, k=1)[0]

	def get_default_active_lines(self, count: int) -> Tuple[int, ...]:
		"""Devuelve los índices de las ``count`` primeras líneas de pago."""

		count = max(1, min(count, len(PAYLINES)))
		return tuple(range(count))

	# ------------------------------------------------------------------
	# Internos

	def _update_statistics(self, result: SpinResult) -> None:
		self.statistics.total_spins += 1
		self.statistics.total_bet += result.total_bet
		self.statistics.total_payout += result.total_payout
		self.statistics.biggest_win = max(self.statistics.biggest_win, result.net_win)

		wild_count = sum(1 for row in result.grid for cell in row if cell == WILD_SYMBOL)
		self.statistics.wild_symbols_seen += wild_count


class SlotMachineTable(BaseSlotMachineTable):
	"""Mesa estándar de tragaperras lista para integrarse con la UI."""

	def __init__(
		self,
		*,
		history_size: int = 30,
		autoplay_interval_ms: int = 1200,
		**kwargs,
	) -> None:
		super().__init__(history_size=history_size, **kwargs)
		self.autoplay_enabled: bool = False
		self.autoplay_interval_ms = autoplay_interval_ms

	def enable_autoplay(self, enabled: bool) -> None:
		"""Activa o desactiva el modo de juego automático."""

		if self.autoplay_enabled == enabled:
			return
		self.autoplay_enabled = enabled
		self._notify("autoplay_changed", enabled=self.autoplay_enabled)

	def toggle_autoplay(self) -> bool:
		"""Invierte el estado del modo automático y lo devuelve."""

		self.enable_autoplay(not self.autoplay_enabled)
		return self.autoplay_enabled


class SlotMachineTableFactory:
	"""Fábrica sencilla para crear mesas de tragaperras."""

	@staticmethod
	def create_table(**kwargs) -> SlotMachineTable:
		return SlotMachineTable(**kwargs)
