"""Tests para el contrato unificado de eventos de juego (Fase A)."""

from __future__ import annotations

import sys
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from achievements import AchievementManager
from config import ConfigManager
from game_events import GameEventService, GameRoundEvent


class _DummyConfig:
    def __init__(self):
        self.updated_stats = []
        self._values = {
            ("interface", "sound_enabled"): False,
            ("interface", "sound_volume"): 0.7,
            ("interface", "sfx_enabled"): True,
            ("interface", "sfx_volume"): 1.0,
            ("interface", "sfx_muted"): False,
            ("interface", "music_enabled"): True,
            ("interface", "music_volume"): 1.0,
            ("interface", "music_muted"): False,
        }

    @contextmanager
    def batch_update(self):
        yield

    def get(self, section, key, default=None):
        return self._values.get((section, key), default)

    def set(self, section, key, value):
        self._values[(section, key)] = value

    def save_config(self):
        return True

    def update_statistic(self, stat_name, value, increment=True):
        self.updated_stats.append((stat_name, value, increment))


class _DummyAchievementManager:
    def __init__(self):
        self.game_stat_calls = []
        self.win_calls = []
        self.loss_calls = 0

    def update_game_stat(self, game_type, increment=1):
        self.game_stat_calls.append((game_type, increment))
        return []

    def update_win(self, amount):
        self.win_calls.append(amount)
        return []

    def update_loss(self):
        self.loss_calls += 1


class _DummyMissionManager:
    def __init__(self):
        self.hand_calls = []
        self.win_calls = []

    def update_on_hand_played(self, game_type):
        self.hand_calls.append(game_type)
        return []

    def update_on_win(self, amount):
        self.win_calls.append(amount)
        return []


class TestGameRoundEvent(unittest.TestCase):
    def test_alias_normalization(self):
        self.assertEqual(GameRoundEvent("ruleta").normalized_game_type(), "roulette")
        self.assertEqual(GameRoundEvent("tragaperras").normalized_game_type(), "slots")
        self.assertEqual(GameRoundEvent("blackjack").normalized_game_type(), "blackjack")

    def test_invalid_game_type_raises(self):
        with self.assertRaises(ValueError):
            GameRoundEvent("baccarat").normalized_game_type()


class TestGameEventService(unittest.TestCase):
    def setUp(self):
        self.cfg = _DummyConfig()
        self.ach = _DummyAchievementManager()
        self.mis = _DummyMissionManager()
        self.service = GameEventService(
            cfg=self.cfg,
            achievement_manager=self.ach,
            mission_manager=self.mis,
        )

    def test_record_round_positive_net_win(self):
        event = GameRoundEvent(game_type="slots", rounds_played=1, wagered=20, net_win=15)
        result = self.service.record_round(event)

        self.assertEqual(self.ach.game_stat_calls, [("slots", 1)])
        self.assertEqual(self.ach.win_calls, [15])
        self.assertEqual(self.ach.loss_calls, 0)
        self.assertEqual(self.mis.hand_calls, ["slots"])
        self.assertEqual(self.mis.win_calls, [15])
        self.assertIn(("total_wagered", 20, True), self.cfg.updated_stats)
        self.assertEqual(result["game_type"], "slots")

    def test_record_round_negative_net_win(self):
        event = GameRoundEvent(game_type="roulette", rounds_played=1, wagered=40, net_win=-40)
        self.service.record_round(event)

        self.assertEqual(self.ach.game_stat_calls, [("roulette", 1)])
        self.assertEqual(self.ach.win_calls, [])
        self.assertEqual(self.ach.loss_calls, 1)
        self.assertEqual(self.mis.hand_calls, ["roulette"])
        self.assertEqual(self.mis.win_calls, [])


class TestAchievementGameStatMapping(unittest.TestCase):
    def test_roulette_and_slots_use_spin_stats(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            config_path = Path(tmp_dir) / "test_config.json"
            cfg = ConfigManager(config_file=str(config_path))
            manager = AchievementManager(cfg)

            manager.update_game_stat("roulette", increment=1)
            manager.update_game_stat("slots", increment=2)

            self.assertEqual(cfg.get_statistic("roulette_spins"), 1)
            self.assertEqual(cfg.get_statistic("slots_spins"), 2)
            self.assertEqual(cfg.get_statistic("roulette_hands", 0), 0)
            self.assertEqual(cfg.get_statistic("slots_hands", 0), 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
