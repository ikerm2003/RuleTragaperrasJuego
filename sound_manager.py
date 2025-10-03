#!/usr/bin/env python3
"""
Sound Manager for Casino Game
Manages sound effects and background music
"""

from enum import Enum
from typing import Dict, Optional
import os


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


class SoundManager:
    """Manages game audio"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.sounds: Dict[SoundEffect, Optional[any]] = {}
        self.music_player: Optional[any] = None
        self.initialized = False
        
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
            
            # Create sound directory if it doesn't exist
            self.sounds_dir = os.path.join(os.path.dirname(__file__), 'sounds')
            if not os.path.exists(self.sounds_dir):
                os.makedirs(self.sounds_dir)
            
            self.initialized = True
        except ImportError:
            print("PyQt6.QtMultimedia not available. Sound disabled.")
            self.initialized = False
    
    def is_enabled(self) -> bool:
        """Check if sound is enabled"""
        return self.initialized and self.config.get('interface', 'sound_enabled', True)
    
    def play_effect(self, effect: SoundEffect) -> None:
        """Play a sound effect"""
        if not self.is_enabled():
            return
        
        # For now, just log that sound would be played
        # In a real implementation, we would load and play actual sound files
        print(f"[Sound] Would play: {effect.value}")
    
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
        if not self.is_enabled():
            return
        
        print(f"[Music] Would start: {track}")
    
    def stop_background_music(self) -> None:
        """Stop background music"""
        if not self.is_enabled():
            return
        
        print("[Music] Would stop")
    
    def set_volume(self, volume: float) -> None:
        """Set master volume (0.0 to 1.0)"""
        # Store in config
        self.config.set('interface', 'sound_volume', volume)
        self.config.save_config()
        
        print(f"[Sound] Volume set to: {volume}")
    
    def get_volume(self) -> float:
        """Get master volume"""
        return self.config.get('interface', 'sound_volume', 0.7)


# Create global sound manager instance
_sound_manager: Optional[SoundManager] = None


def get_sound_manager(config_manager=None):
    """Get the global sound manager instance"""
    global _sound_manager
    if _sound_manager is None and config_manager is not None:
        _sound_manager = SoundManager(config_manager)
    return _sound_manager
