"""Tests para SoundManager (Fase B audio)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
PACKAGE_PARENT = ROOT_DIR.parent
if str(PACKAGE_PARENT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_PARENT))

from RuleTragaperrasJuego.sound_manager import AudioCategory, MusicContext, SoundManager


class DummyConfig:
    def __init__(self):
        self.values = {
            ("interface", "sound_enabled"): True,
            ("interface", "sound_volume"): 0.7,
            ("interface", "sfx_enabled"): True,
            ("interface", "sfx_volume"): 1.0,
            ("interface", "sfx_muted"): False,
            ("interface", "music_enabled"): True,
            ("interface", "music_volume"): 0.8,
            ("interface", "music_muted"): False,
        }
        self.saved = 0

    def get(self, section, key, default=None):
        return self.values.get((section, key), default)

    def set(self, section, key, value):
        self.values[(section, key)] = value

    def save_config(self):
        self.saved += 1
        return True


class TestSoundManager(unittest.TestCase):
    def setUp(self):
        self.cfg = DummyConfig()
        self.manager = SoundManager(self.cfg)

    def test_set_master_volume_is_clamped(self):
        self.manager.set_volume(2.0)
        self.assertEqual(self.cfg.get("interface", "sound_volume"), 1.0)

        self.manager.set_volume(-1.0)
        self.assertEqual(self.cfg.get("interface", "sound_volume"), 0.0)

    def test_set_category_volume(self):
        self.manager.set_category_volume(AudioCategory.SFX, 0.35)
        self.assertEqual(self.cfg.values[("interface", "sfx_volume")], 0.35)

    def test_set_and_get_category_muted(self):
        self.manager.set_category_muted(AudioCategory.MUSIC, True)
        self.assertTrue(self.manager.is_category_muted(AudioCategory.MUSIC))
        self.assertFalse(self.manager.is_category_enabled(AudioCategory.MUSIC))

    def test_effective_volume_uses_master_and_category(self):
        self.cfg.set("interface", "sound_volume", 0.5)
        self.cfg.set("interface", "music_volume", 0.4)
        effective = self.manager._effective_volume(AudioCategory.MUSIC)
        self.assertAlmostEqual(effective, 0.2)

    def test_music_context_default_candidates_include_legacy_track(self):
        candidates = self.manager._get_context_track_candidates(MusicContext.MENU)
        self.assertIn("main_theme", candidates)

    def test_music_context_candidates_can_be_overridden_by_config(self):
        self.cfg.set("interface", "music_track_slots", "custom_slots_a, custom_slots_b")
        candidates = self.manager._get_context_track_candidates(MusicContext.SLOTS)
        self.assertEqual(candidates, ["custom_slots_a", "custom_slots_b"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
