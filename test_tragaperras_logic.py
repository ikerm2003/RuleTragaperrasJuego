import unittest

from Tragaperras.tragaperras_logic import (
    SlotMachine,
    WILD_SYMBOL,
    SCATTER_SYMBOL,
)


class FixedGridSlotMachine(SlotMachine):
    """Versión de la tragaperras que devuelve una cuadricula fija."""

    def __init__(self, fixed_grid, **kwargs):
        kwargs.setdefault("rtp_range", (1.0, 1.0))
        kwargs.setdefault("loss_recovery_chance", 0.0)
        kwargs.setdefault("loss_recovery_multiplier_range", (0.0, 0.0))
        super().__init__(**kwargs)
        self._fixed_grid = tuple(tuple(cell for cell in row) for row in fixed_grid)

    def _generate_grid(self):  # type: ignore[override]
        return self._fixed_grid


class TestSlotMachineLogic(unittest.TestCase):
    def test_three_of_a_kind_payout(self):
        grid = (
            ("7️⃣", "7️⃣", "7️⃣"),
            ("🍒", "🍋", "💎"),
            ("⭐", "🔔", "🍒"),
        )
        machine = FixedGridSlotMachine(
            grid,
            balance=1000,
            bet_per_line=10,
            active_lines=(0,),
        )

        result = machine.spin()

        self.assertEqual(result.total_bet, 10)
        self.assertEqual(len(result.line_wins), 1)
        self.assertEqual(result.line_wins[0].symbol, "7️⃣")
        self.assertEqual(result.line_wins[0].payout_multiplier, 45)
        self.assertEqual(result.total_payout, 45 * 10)
        self.assertEqual(result.rtp_factor_applied, 1.0)
        self.assertEqual(machine.balance, 1000 - 10 + 45 * 10)

    def test_scatter_multiplier(self):
        grid = tuple(tuple(SCATTER_SYMBOL for _ in range(3)) for _ in range(3))
        machine = FixedGridSlotMachine(
            grid,
            balance=500,
            bet_per_line=5,
            active_lines=(0, 1, 2),
        )

        result = machine.spin()

        self.assertEqual(result.scatter_count, 9)
        self.assertEqual(result.scatter_multiplier, 25)
        self.assertEqual(result.total_bet, 15)
        self.assertEqual(result.total_payout, 25 * 15)
        self.assertEqual(result.rtp_factor_applied, 1.0)
        self.assertEqual(machine.balance, 500 - 15 + 25 * 15)

    def test_wild_substitution(self):
        grid = (
            (WILD_SYMBOL, WILD_SYMBOL, "💎"),
            ("🍒", "🍋", "🔔"),
            ("⭐", "🍋", "🍒"),
        )
        machine = FixedGridSlotMachine(
            grid,
            balance=300,
            bet_per_line=5,
            active_lines=(0,),
        )

        result = machine.spin()

        self.assertEqual(result.total_payout, 32 * 5)  # 💎 paga x32
        self.assertEqual(result.rtp_factor_applied, 1.0)
        self.assertEqual(machine.balance, 300 - 5 + 32 * 5)

    def test_insufficient_balance_raises(self):
        machine = SlotMachine(
            balance=20,
            bet_per_line=10,
            rtp_range=(1.0, 1.0),
            loss_recovery_chance=0.0,
        )  # 10 líneas activas -> apuesta 90
        with self.assertRaises(ValueError):
            machine.spin()


if __name__ == "__main__":
    unittest.main()
