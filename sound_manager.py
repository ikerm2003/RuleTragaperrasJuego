
"""Gestión centralizada de audio para la app de casino."""

from __future__ import annotations

import os
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional


class SoundEffect(Enum):
    """Available sound effects"""
    BUTTON_CLICK = "button_click"
    CARD_DEAL = "card_deal"
    CARD_FLIP = "card_flip"
    CHIP_PLACE = "chip_place"
    CHIP_COLLECT = "chip_collect"
    WIN = "win"
    LOSE = "lose"
    BIG_WIN = "big_win"
    JACKPOT = "jackpot"
    ROULETTE_SPIN = "roulette_spin"
    SLOT_SPIN = "slot_spin"
    ACHIEVEMENT_UNLOCK = "achievement"
    MISSION_COMPLETE = "mission"
    NOTIFICATION = "notification"


class AudioCategory(Enum):
    """Categorías de audio con volumen/mute independiente."""

    SFX = "sfx"
    MUSIC = "music"


class MusicContext(Enum):
    """Contextos musicales de alto nivel para mapear pistas por escena."""

    MENU = "menu"
    POKER = "poker"
    BLACKJACK = "blackjack"
    ROULETTE = "roulette"
    SLOTS = "slots"


class SoundManager:
    """Manages game audio"""
    
    EFFECT_FILE_MAP = {
        SoundEffect.BUTTON_CLICK: "button_click.wav",
        SoundEffect.CARD_DEAL: "card_deal.wav",
        SoundEffect.CARD_FLIP: "card_flip.wav",
        SoundEffect.CHIP_PLACE: "chip_place.wav",
        SoundEffect.CHIP_COLLECT: "chip_collect.wav",
        SoundEffect.WIN: "win.wav",
        SoundEffect.LOSE: "lose.wav",
        SoundEffect.BIG_WIN: "big_win.wav",
        SoundEffect.JACKPOT: "jackpot.wav",
        SoundEffect.ROULETTE_SPIN: "roulette_spin.wav",
        SoundEffect.SLOT_SPIN: "slot_spin.wav",
        SoundEffect.ACHIEVEMENT_UNLOCK: "achievement.wav",
        SoundEffect.MISSION_COMPLETE: "mission.wav",
        SoundEffect.NOTIFICATION: "notification.wav",
    }

    MUSIC_TRACK_CANDIDATES = {
        MusicContext.MENU: ["main_theme", "menu_theme", "lobby_theme"],
        MusicContext.POKER: ["poker_theme", "card_table", "game_theme"],
        MusicContext.BLACKJACK: ["blackjack_theme", "vip_table", "game_theme"],
        MusicContext.ROULETTE: ["roulette_theme", "wheel_spin_theme", "game_theme"],
        MusicContext.SLOTS: ["slots_theme", "arcade_reels", "game_theme"],
    }

    def __init__(self, config_manager):
        self.config = config_manager
        self.sounds: Dict[SoundEffect, Optional[Any]] = {}
        self.music_player: Optional[Any] = None
        self.music_output: Optional[Any] = None
        self.initialized = False
        self._missing_assets_warned: set[str] = set()
        self._current_music_track: Optional[str] = None
        
        # Try to initialize PyQt6 audio
        self._initialize_audio()
    
    def _initialize_audio(self):
        """Initialize audio system"""
        try:
            from PyQt6.QtMultimedia import QSoundEffect, QMediaPlayer, QAudioOutput
            from PyQt6.QtCore import QUrl
            
            self.QSoundEffect = QSoundEffect
            self.QMediaPlayer = QMediaPlayer
            self.QAudioOutput = QAudioOutput
            self.QUrl = QUrl
            
            # Create sound directory tree if it doesn't exist
            self.sounds_dir = Path(__file__).resolve().parent / "sounds"
            self.sfx_dir = self.sounds_dir / "sfx"
            self.music_dir = self.sounds_dir / "music"
            self.sfx_dir.mkdir(parents=True, exist_ok=True)
            self.music_dir.mkdir(parents=True, exist_ok=True)

            self.music_output = self.QAudioOutput()
            self.music_player = self.QMediaPlayer()
            self.music_player.setAudioOutput(self.music_output)
            self.music_output.setVolume(self._effective_volume(AudioCategory.MUSIC))
            
            self.initialized = True
        except ImportError:
            print("PyQt6.QtMultimedia not available. Sound disabled.")
            self.initialized = False
    
    def is_enabled(self) -> bool:
        """Check if sound is enabled"""
        return self.initialized and self.config.get('interface', 'sound_enabled', True)

    def is_category_enabled(self, category: AudioCategory) -> bool:
        """Check if a category is enabled and not muted."""
        if not self.is_enabled():
            return False
        enabled_key = f"{category.value}_enabled"
        mute_key = f"{category.value}_muted"
        return bool(self.config.get('interface', enabled_key, True)) and not bool(
            self.config.get('interface', mute_key, False)
        )

    def _effective_volume(self, category: AudioCategory) -> float:
        master = float(self.config.get('interface', 'sound_volume', 0.7))
        category_volume = float(self.config.get('interface', f'{category.value}_volume', 1.0))
        if not self.is_category_enabled(category):
            return 0.0
        return max(0.0, min(1.0, master * category_volume))

    def _resolve_effect_path(self, effect: SoundEffect) -> Optional[Path]:
        file_name = self.EFFECT_FILE_MAP.get(effect)
        if not file_name:
            return None
        candidate = self.sfx_dir / file_name
        return candidate if candidate.exists() else None

    def _resolve_music_path(self, track: str) -> Optional[Path]:
        track_base = self.music_dir / track
        candidates = [
            track_base.with_suffix('.mp3'),
            track_base.with_suffix('.ogg'),
            track_base.with_suffix('.wav'),
        ]
        return next((path for path in candidates if path.exists()), None)

    def _get_context_track_candidates(self, context: MusicContext) -> list[str]:
        config_key = f"music_track_{context.value}"
        configured = self.config.get('interface', config_key, None)
        if isinstance(configured, str):
            # Permite override simple: "mi_track" o lista CSV: "track_a, track_b"
            custom = [item.strip() for item in configured.split(',') if item.strip()]
            if custom:
                return custom
        return list(self.MUSIC_TRACK_CANDIDATES.get(context, []))

    def _warn_missing_asset_once(self, asset_key: str) -> None:
        if asset_key in self._missing_assets_warned:
            return
        self._missing_assets_warned.add(asset_key)
        print(f"[Sound] Asset not found: {asset_key}")

    @staticmethod
    def _fallback_beep() -> None:
        try:
            from PyQt6.QtWidgets import QApplication
            QApplication.beep()
        except Exception:
            pass

    def _get_or_create_effect(self, effect: SoundEffect):
        sound = self.sounds.get(effect)
        if sound is not None:
            return sound

        sound = self.QSoundEffect()
        sound.setLoopCount(1)
        self.sounds[effect] = sound
        return sound
    
    def play_effect(self, effect: SoundEffect) -> None:
        """Play a sound effect"""
        if not self.is_category_enabled(AudioCategory.SFX):
            return

        if not self.initialized:
            self._fallback_beep()
            return

        asset_path = self._resolve_effect_path(effect)
        if asset_path is None:
            self._warn_missing_asset_once(f"sfx/{effect.value}")
            self._fallback_beep()
            return

        sound = self._get_or_create_effect(effect)
        sound.setSource(self.QUrl.fromLocalFile(str(asset_path)))
        sound.setVolume(self._effective_volume(AudioCategory.SFX))
        sound.play()
    
    def play_button_click(self) -> None:
        """Play button click sound"""
        self.play_effect(SoundEffect.BUTTON_CLICK)
    
    def play_card_deal(self) -> None:
        """Play card dealing sound"""
        self.play_effect(SoundEffect.CARD_DEAL)
    
    def play_card_flip(self) -> None:
        """Play card flip sound"""
        self.play_effect(SoundEffect.CARD_FLIP)
    
    def play_chip_place(self) -> None:
        """Play chip placement sound"""
        self.play_effect(SoundEffect.CHIP_PLACE)
    
    def play_chip_collect(self) -> None:
        """Play chip collection sound"""
        self.play_effect(SoundEffect.CHIP_COLLECT)
    
    def play_win(self, big_win: bool = False) -> None:
        """Play win sound"""
        if big_win:
            self.play_effect(SoundEffect.BIG_WIN)
        else:
            self.play_effect(SoundEffect.WIN)
    
    def play_lose(self) -> None:
        """Play lose sound"""
        self.play_effect(SoundEffect.LOSE)
    
    def play_jackpot(self) -> None:
        """Play jackpot sound"""
        self.play_effect(SoundEffect.JACKPOT)
    
    def play_roulette_spin(self) -> None:
        """Play roulette spin sound"""
        self.play_effect(SoundEffect.ROULETTE_SPIN)
    
    def play_slot_spin(self) -> None:
        """Play slot machine spin sound"""
        self.play_effect(SoundEffect.SLOT_SPIN)
    
    def play_achievement_unlock(self) -> None:
        """Play achievement unlock sound"""
        self.play_effect(SoundEffect.ACHIEVEMENT_UNLOCK)
    
    def play_mission_complete(self) -> None:
        """Play mission complete sound"""
        self.play_effect(SoundEffect.MISSION_COMPLETE)
    
    def play_notification(self) -> None:
        """Play notification sound"""
        self.play_effect(SoundEffect.NOTIFICATION)
    
    def start_background_music(self, track: str = "main_theme") -> None:
        """Start background music"""
        if not self.is_category_enabled(AudioCategory.MUSIC):
            return

        if not self.initialized or self.music_player is None or self.music_output is None:
            return

        selected = self._resolve_music_path(track)
        if selected is None:
            self._warn_missing_asset_once(f"music/{track}")
            return

        if self._current_music_track == track:
            return

        self.music_output.setVolume(self._effective_volume(AudioCategory.MUSIC))
        self.music_player.setSource(self.QUrl.fromLocalFile(str(selected)))
        self.music_player.play()
        self._current_music_track = track

    def play_music_for_context(self, context: MusicContext) -> None:
        """Reproduce la primera pista disponible para un contexto de UI/juego."""
        if not self.is_category_enabled(AudioCategory.MUSIC):
            return

        for track in self._get_context_track_candidates(context):
            if self._resolve_music_path(track) is None:
                continue
            self.start_background_music(track)
            return

        self._warn_missing_asset_once(f"music/context:{context.value}")
    
    def stop_background_music(self) -> None:
        """Stop background music"""
        if not self.initialized or self.music_player is None:
            return
        self.music_player.stop()
        self._current_music_track = None
    
    def set_volume(self, volume: float) -> None:
        """Set master volume (0.0 to 1.0)"""
        volume = max(0.0, min(1.0, float(volume)))
        # Store in config
        self.config.set('interface', 'sound_volume', volume)
        self.config.save_config()

        if self.music_output is not None:
            self.music_output.setVolume(self._effective_volume(AudioCategory.MUSIC))
    
    def get_volume(self) -> float:
        """Get master volume"""
        return self.config.get('interface', 'sound_volume', 0.7)

    def set_category_volume(self, category: AudioCategory, volume: float) -> None:
        """Set category volume (0.0 to 1.0)."""
        volume = max(0.0, min(1.0, float(volume)))
        self.config.set('interface', f'{category.value}_volume', volume)
        self.config.save_config()
        if category == AudioCategory.MUSIC and self.music_output is not None:
            self.music_output.setVolume(self._effective_volume(AudioCategory.MUSIC))

    def get_category_volume(self, category: AudioCategory) -> float:
        """Get category volume."""
        return float(self.config.get('interface', f'{category.value}_volume', 1.0))

    def set_category_muted(self, category: AudioCategory, muted: bool) -> None:
        """Mute or unmute a category."""
        self.config.set('interface', f'{category.value}_muted', bool(muted))
        self.config.save_config()
        if category == AudioCategory.MUSIC and self.music_output is not None:
            self.music_output.setVolume(self._effective_volume(AudioCategory.MUSIC))

    def is_category_muted(self, category: AudioCategory) -> bool:
        """Return mute state for category."""
        return bool(self.config.get('interface', f'{category.value}_muted', False))


# Create global sound manager instance
_sound_manager: Optional[SoundManager] = None


def get_sound_manager(config_manager=None):
    """Get the global sound manager instance"""
    global _sound_manager
    if _sound_manager is None and config_manager is not None:
        _sound_manager = SoundManager(config_manager)
    return _sound_manager
