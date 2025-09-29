"""Módulo principal con la lógica de la tragaperras 3x3.

Incluye una implementación avanzada de una máquina tragaperras capaz de:
* Gestionar una cuadricula de 3 filas x 3 rodillos.
* Controlar probabilidades mediante pesos por símbolo.
* Evaluar todas las líneas de pago tradicionales y combinaciones diagonales.
* Incluir comodines, símbolos scatter y pagos progresivos.
* Gestionar apuestas por línea, saldo disponible y retornos detallados.

La clase principal está pensada para reutilizarse desde la capa de UI sin lógica
duplicada.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Configuración de símbolos y pagos

WILD_SYMBOL = "🃏"
SCATTER_SYMBOL = "🎰"

SYMBOL_PAYTABLE: Dict[str, Dict[int, int]] = {
    "7️⃣": {3: 45, 2: 8},
    "💎": {3: 32, 2: 6},
    "⭐": {3: 24, 2: 5},
    "🔔": {3: 18, 2: 4},
    "🍋": {3: 12, 2: 3},
    "🍒": {3: 10, 2: 2},
    WILD_SYMBOL: {3: 55, 2: 10},  # Tres comodines pagan aparte.
}

# Pagos scatter: multiplicadores aplicables al total apostado.
SCATTER_MULTIPLIERS: Dict[int, int] = {
    3: 1,
    4: 2,
    5: 4,
    6: 6,
    7: 10,
    8: 15,
    9: 25,
}
# El retorno real depende del rango ``rtp_range``. Con la configuración por
# defecto (0.8-1.2) las simulaciones arrojan un RTP cercano al 100 %, aunque la
# varianza permite sesiones con grandes pérdidas o ganancias. Ajusta el rango o
# la tabla de pagos para adaptar la dificultad.

# Pesos relativos de aparición para cada símbolo dentro de un rodillo.
SYMBOL_WEIGHTS: Dict[str, int] = {
    "7️⃣": 1,
    "💎": 2,
    "⭐": 3,
    "🔔": 6,
    "🍋": 14,
    "🍒": 16,
    SCATTER_SYMBOL: 2,
    WILD_SYMBOL: 1,
}

# Definición de líneas de pago (de izquierda a derecha). Cada línea se define
# como una secuencia de coordenadas (fila, columna) dentro de la cuadricula.
PAYLINES: Tuple[Tuple[Tuple[int, int], ...], ...] = (
    # Filas directas
    ((0, 0), (0, 1), (0, 2)),
    ((1, 0), (1, 1), (1, 2)),
    ((2, 0), (2, 1), (2, 2)),
    # Diagonales principales
    ((0, 0), (1, 1), (2, 2)),
    ((2, 0), (1, 1), (0, 2)),
    # Formas en V y montañas
    ((0, 0), (1, 1), (0, 2)),
    ((2, 0), (1, 1), (2, 2)),
    ((1, 0), (0, 1), (1, 2)),
    ((1, 0), (2, 1), (1, 2)),
)


# ---------------------------------------------------------------------------
# Modelos auxiliares


@dataclass(frozen=True)
class LineWin:
    """Representa un premio obtenido en una línea de pago."""

    line_index: int
    symbol: str
    length: int
    payout_multiplier: int
    positions: Tuple[Tuple[int, int], ...]

    def payout(self, bet_per_line: int) -> int:
        """Devuelve el premio en créditos considerando la apuesta."""

        return self.payout_multiplier * bet_per_line


@dataclass
class SpinResult:
    """Resultado detallado de un giro de tragaperras."""

    grid: Tuple[Tuple[str, ...], ...]
    total_bet: int
    bet_per_line: int
    lines_played: Tuple[int, ...]
    line_wins: List[LineWin] = field(default_factory=list)
    scatter_count: int = 0
    scatter_multiplier: int = 0
    total_payout: int = 0
    net_win: int = 0
    balance_after_spin: int = 0
    rtp_factor_applied: float = 1.0

    def as_dict(self) -> Dict[str, object]:
        """Convierte el resultado en un diccionario serializable."""

        return {
            "grid": [list(row) for row in self.grid],
            "total_bet": self.total_bet,
            "bet_per_line": self.bet_per_line,
            "lines_played": list(self.lines_played),
            "line_wins": [
                {
                    "line_index": win.line_index,
                    "symbol": win.symbol,
                    "length": win.length,
                    "payout_multiplier": win.payout_multiplier,
                    "positions": [list(pos) for pos in win.positions],
                    "credits": win.payout(self.bet_per_line),
                }
                for win in self.line_wins
            ],
            "scatter_count": self.scatter_count,
            "scatter_multiplier": self.scatter_multiplier,
            "total_payout": self.total_payout,
            "net_win": self.net_win,
            "balance_after_spin": self.balance_after_spin,
            "rtp_factor_applied": self.rtp_factor_applied,
        }


# ---------------------------------------------------------------------------
# Implementación principal


class SlotMachine:
    """Modelo de tragaperras de 3x3 rodillos con múltiples líneas de pago.

    Parameters
    ----------
    balance : int, optional
        Créditos iniciales disponibles, por defecto ``1000``.
    bet_per_line : int, optional
        Apuesta base por línea, por defecto ``5``.
    active_lines : Sequence[int] | None, optional
        Líneas activas (índices basados en ``PAYLINES``). Si se omite se usan
        todas las líneas definidas.
    symbol_paytable : Dict[str, Dict[int, int]], optional
        Tabla de pagos por símbolo. Los valores representan multiplicadores
        sobre la apuesta por línea.
    scatter_multipliers : Dict[int, int], optional
        Multiplicadores aplicables al total apostado cuando aparecen símbolos
        scatter.
    symbol_weights : Dict[str, int], optional
        Pesos relativos de aparición de cada símbolo.
    rng : random.Random | None, optional
        Generador aleatorio para permitir reproducibilidad en tests.
    rtp_range : Tuple[float, float], optional
        Rango de variación aleatoria aplicado al pago total de cada giro. El
        valor mínimo y máximo se interpretan como multiplicadores sobre el
        pago base calculado. Por defecto ``(0.8, 1.2)`` para permitir giros
        con pérdidas y otros con ganancias elevadas.
    loss_recovery_chance : float, optional
        Probabilidad (0-1) de activar un premio consolación cuando la tirada no
        generó ningún pago. Valores mayores hacen la experiencia más amable.
    loss_recovery_multiplier_range : Tuple[float, float], optional
        Rango de multiplicadores sobre la apuesta total usados al otorgar el
        premio consolación.
    """

    rows: int = 3
    reels: int = 3

    def __init__(
        self,
        *,
        balance: int = 1000,
        bet_per_line: int = 5,
        active_lines: Optional[Sequence[int]] = None,
        symbol_paytable: Optional[Dict[str, Dict[int, int]]] = None,
        scatter_multipliers: Optional[Dict[int, int]] = None,
        symbol_weights: Optional[Dict[str, int]] = None,
        rng: Optional[random.Random] = None,
        rtp_range: Tuple[float, float] = (0.8, 1.2),
        loss_recovery_chance: float = 0.08,
        loss_recovery_multiplier_range: Tuple[float, float] = (0.1, 0.4),
    ) -> None:
        self.balance = balance
        self.bet_per_line = bet_per_line
        self.symbol_paytable = symbol_paytable or SYMBOL_PAYTABLE
        self.scatter_multipliers = scatter_multipliers or SCATTER_MULTIPLIERS
        self.symbol_weights = symbol_weights or SYMBOL_WEIGHTS
        self.rng = rng or random.Random()
        self.set_rtp_range(rtp_range)
        self.set_loss_recovery(loss_recovery_chance, loss_recovery_multiplier_range)

        # Determinar líneas activas.
        if active_lines is None:
            self.active_lines: Tuple[int, ...] = tuple(range(len(PAYLINES)))
        else:
            if not active_lines:
                raise ValueError("Debe activarse al menos una línea de pago")
            for line in active_lines:
                if line < 0 or line >= len(PAYLINES):
                    raise ValueError(f"Línea de pago inválida: {line}")
            self.active_lines = tuple(dict.fromkeys(active_lines))  # Sin duplicados.

        # Estadísticas de la última tirada.
        self.last_result: Optional[SpinResult] = None

        # Precalcular lista de símbolos y pesos para generación eficiente.
        self._symbols, self._weights = self._build_symbol_lists()
        self._top_symbol = max(
            (s for s in self.symbol_paytable if s != WILD_SYMBOL),
            key=lambda s: self.symbol_paytable[s].get(3, 0),
        )

    # ------------------------------------------------------------------
    # Configuración y utilidades

    def _build_symbol_lists(self) -> Tuple[List[str], List[int]]:
        symbols: List[str] = []
        weights: List[int] = []
        for symbol, weight in self.symbol_weights.items():
            if weight <= 0:
                continue
            symbols.append(symbol)
            weights.append(weight)
        if not symbols:
            raise ValueError("Debe haber al menos un símbolo con peso positivo")
        return symbols, weights

    def set_bet_per_line(self, amount: int) -> None:
        """Actualiza la apuesta por línea validando el valor recibido."""

        if amount <= 0:
            raise ValueError("La apuesta por línea debe ser mayor que cero")
        self.bet_per_line = amount

    def set_active_lines(self, lines: Iterable[int]) -> None:
        """Define las líneas de pago activas."""

        new_lines = list(lines)
        if not new_lines:
            raise ValueError("Debe activarse al menos una línea de pago")
        for line in new_lines:
            if line < 0 or line >= len(PAYLINES):
                raise ValueError(f"Línea de pago inválida: {line}")
        self.active_lines = tuple(dict.fromkeys(new_lines))

    def set_rtp_range(self, rtp_range: Tuple[float, float]) -> None:
        """Configura el rango de multiplicadores RTP aleatorios."""

        low, high = rtp_range
        if low <= 0 or high <= 0:
            raise ValueError("Los multiplicadores RTP deben ser positivos")
        if low > high:
            raise ValueError("El límite inferior del RTP no puede ser mayor que el superior")
        self.rtp_range = (low, high)

    def set_loss_recovery(
        self,
        chance: float,
        multiplier_range: Tuple[float, float],
    ) -> None:
        """Permite ajustar el premio consolación cuando no hay ganancias."""

        if not 0 <= chance <= 1:
            raise ValueError("La probabilidad de recuperación debe estar entre 0 y 1")
        low, high = multiplier_range
        if low < 0 or high < 0:
            raise ValueError("Los multiplicadores de recuperación deben ser no negativos")
        if low > high:
            raise ValueError("El multiplicador inferior no puede superar al superior")
        self.loss_recovery_chance = chance
        self.loss_recovery_multiplier_range = (low, high)

    def add_credits(self, amount: int) -> None:
        """Agrega créditos al balance."""

        if amount < 0:
            raise ValueError("No se pueden agregar créditos negativos")
        self.balance += amount

    # ------------------------------------------------------------------
    # Generación de tiradas

    def _generate_grid(self) -> Tuple[Tuple[str, ...], ...]:
        """Genera una cuadricula 3x3 de símbolos según los pesos configurados."""

        grid: List[List[str]] = []
        for _ in range(self.rows):
            row = self.rng.choices(self._symbols, weights=self._weights, k=self.reels)
            grid.append(row)
        return tuple(tuple(cell for cell in row) for row in grid)

    # ------------------------------------------------------------------
    # Evaluación de tiradas

    def _evaluate_line(
        self,
        grid: Sequence[Sequence[str]],
        line_index: int,
    ) -> Optional[LineWin]:
        """Evalúa una única línea de pago y devuelve el premio si existe."""

        line_coords = PAYLINES[line_index]
        symbols = [grid[r][c] for r, c in line_coords]

        # Buscar símbolo base (primer símbolo no comodín ni scatter).
        base_symbol = next(
            (s for s in symbols if s not in {WILD_SYMBOL, SCATTER_SYMBOL}),
            None,
        )
        if base_symbol is None:
            # Todos son comodines o scatter -> usar símbolo máximo para pago.
            base_symbol = self._top_symbol

        payouts = self.symbol_paytable.get(base_symbol)
        if not payouts:
            return None

        length = 0
        positions: List[Tuple[int, int]] = []
        for (row, col), symbol in zip(line_coords, symbols):
            if symbol in {base_symbol, WILD_SYMBOL}:
                length += 1
                positions.append((row, col))
            else:
                break

        if length < 2:
            return None

        multiplier = payouts.get(length)
        if multiplier is None:
            return None

        # Caso especial: todo comodines y el símbolo base no es comodín.
        if base_symbol != WILD_SYMBOL and all(
            symbol == WILD_SYMBOL for symbol in symbols[:length]
        ):
            # Permitir pago como si fuese el símbolo más alto.
            payouts_wild = self.symbol_paytable.get(WILD_SYMBOL, {})
            multiplier = max(multiplier, payouts_wild.get(length, 0))

        return LineWin(
            line_index=line_index,
            symbol=base_symbol,
            length=length,
            payout_multiplier=multiplier,
            positions=tuple(positions),
        )

    def _evaluate_grid(self, grid: Sequence[Sequence[str]]) -> Tuple[List[LineWin], int, int]:
        """Evalúa todas las líneas activas y símbolos scatter."""

        line_wins: List[LineWin] = []
        for line_index in self.active_lines:
            win = self._evaluate_line(grid, line_index)
            if win:
                line_wins.append(win)

        scatter_count = sum(symbol == SCATTER_SYMBOL for row in grid for symbol in row)
        scatter_multiplier = 0
        for required, multiplier in sorted(self.scatter_multipliers.items()):
            if scatter_count >= required:
                scatter_multiplier = multiplier

        return line_wins, scatter_count, scatter_multiplier

    # ------------------------------------------------------------------
    # API pública

    def spin(self) -> SpinResult:
        """Realiza un giro, evalúa premios y actualiza el balance."""

        total_bet = self.bet_per_line * len(self.active_lines)
        if total_bet > self.balance:
            raise ValueError("Saldo insuficiente para realizar la apuesta actual")

        self.balance -= total_bet
        grid = self._generate_grid()
        line_wins, scatter_count, scatter_multiplier = self._evaluate_grid(grid)

        line_payout = sum(win.payout(self.bet_per_line) for win in line_wins)
        scatter_payout = scatter_multiplier * total_bet if scatter_multiplier else 0
        base_total_payout = line_payout + scatter_payout

        if self.rtp_range[0] == self.rtp_range[1]:
            rtp_factor = self.rtp_range[0]
        else:
            rtp_factor = self.rng.uniform(self.rtp_range[0], self.rtp_range[1])

        adjusted_total_payout = 0
        if base_total_payout > 0:
            adjusted_total_payout = max(1, int(round(base_total_payout * rtp_factor)))
        elif self.loss_recovery_chance > 0 and self.rng.random() < self.loss_recovery_chance:
            low, high = self.loss_recovery_multiplier_range
            adjusted_total_payout = int(round(total_bet * self.rng.uniform(low, high)))
        self.balance += adjusted_total_payout

        result = SpinResult(
            grid=grid,
            total_bet=total_bet,
            bet_per_line=self.bet_per_line,
            lines_played=self.active_lines,
            line_wins=line_wins,
            scatter_count=scatter_count,
            scatter_multiplier=scatter_multiplier,
            total_payout=adjusted_total_payout,
            net_win=adjusted_total_payout - total_bet,
            balance_after_spin=self.balance,
            rtp_factor_applied=rtp_factor,
        )
        self.last_result = result
        return result

    # ------------------------------------------------------------------
    # Métodos de apoyo

    def get_paytable(self) -> Dict[str, Dict[int, int]]:
        """Devuelve una copia de la tabla de pagos."""

        return {symbol: payouts.copy() for symbol, payouts in self.symbol_paytable.items()}

    def get_active_lines(self) -> Tuple[int, ...]:
        """Devuelve las líneas de pago actualmente activas."""

        return self.active_lines

    def simulate(self, spins: int) -> SpinResult:
        """Realiza múltiples giros consecutivos y devuelve el último resultado."""

        last_result: Optional[SpinResult] = None
        for _ in range(spins):
            last_result = self.spin()
        if last_result is None:
            raise RuntimeError("La simulación no produjo resultados")
        return last_result


# ---------------------------------------------------------------------------
# Pruebas simples (pueden ejecutarse con ``python -m unittest``)


if __name__ == "__main__":
    machine = SlotMachine(balance=200, bet_per_line=5)
    print("Saldo inicial:", machine.balance)
    for i in range(10):
        result = machine.spin()
        # print(f"Spin {i + 1}: {result.as_dict()}")
    print("Saldo final:", machine.balance)