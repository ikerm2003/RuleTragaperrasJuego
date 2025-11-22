#!/usr/bin/env python3
"""Pruebas para la clase :mod:`Tragaperras.tragaperras_table`."""

import unittest
from typing import Dict, List

from Tragaperras.tragaperras_logic import SCATTER_SYMBOL, WILD_SYMBOL
from Tragaperras.tragaperras_table import SlotMachineTable


class DeterministicSlotMachineTable(SlotMachineTable):
    """Tabla de tragaperras con una cuadricula fija para pruebas."""

    def __init__(self, grid, **kwargs):
        kwargs.setdefault("rtp_range", (1.0, 1.0))
        kwargs.setdefault("loss_recovery_chance", 0.0)
        kwargs.setdefault("loss_recovery_multiplier_range", (0.0, 0.0))
        kwargs.setdefault("balance", 1000)
        kwargs.setdefault("bet_per_line", 10)
        kwargs.setdefault("active_lines", (0,))
        super().__init__(**kwargs)
        self._grid = tuple(tuple(symbol for symbol in row) for row in grid)

    def _generate_grid(self):  
        return self._grid


class TestSlotMachineTable(unittest.TestCase):
    """Suite de tests para verificar la integración de la mesa con la UI."""

    def setUp(self):
        self.grid = (
            ("7️⃣", "7️⃣", "7️⃣"),
            (WILD_SYMBOL, SCATTER_SYMBOL, "🍋"),
            ("🍒", "⭐", "🍒"),
        )
        self.table = DeterministicSlotMachineTable(self.grid)

    def test_spin_emits_callbacks_in_order(self):
        events: List[str] = []

        def recorder(name: str):
            def _inner(**_kwargs):
                events.append(name)

            return _inner

        self.table.register_ui_callback("spin_started", recorder("start"))
        self.table.register_ui_callback("spin_completed", recorder("completed"))
        self.table.register_ui_callback("balance_changed", recorder("balance"))
        self.table.register_ui_callback("statistics_changed", recorder("stats"))

        result = self.table.spin()

        self.assertEqual(events[:4], ["start", "completed", "balance", "stats"])
        self.assertEqual(result.grid, self.grid)
        self.assertEqual(self.table.get_history()[0], result)

    def test_statistics_are_updated(self):
        result = self.table.spin()
        stats = self.table.get_statistics()

        self.assertEqual(stats.total_spins, 1)
        self.assertEqual(stats.total_bet, result.total_bet)
        self.assertEqual(stats.total_payout, result.total_payout)
        self.assertGreaterEqual(stats.wild_symbols_seen, 1)

    def test_setters_notify_ui(self):
        captured: Dict[str, int] = {}

        def on_bet_changed(bet_per_line: int):
            captured["bet"] = bet_per_line

        def on_lines_changed(lines):
            captured["lines"] = len(tuple(lines))

        self.table.register_ui_callback("bet_changed", on_bet_changed)
        self.table.register_ui_callback("lines_changed", on_lines_changed)

        self.table.set_bet_per_line(25)
        self.table.set_active_lines((0, 1, 2))

        self.assertEqual(captured["bet"], 25)
        self.assertEqual(captured["lines"], 3)

    def test_reset_statistics(self):
        self.table.spin()
        self.table.reset_statistics()
        stats = self.table.get_statistics()

        self.assertEqual(stats.total_spins, 0)
        self.assertEqual(stats.total_bet, 0)
        self.assertEqual(stats.total_payout, 0)
        self.assertEqual(stats.wild_symbols_seen, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
