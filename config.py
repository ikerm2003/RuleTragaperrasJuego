"""
Configuration module for the Casino game.
Handles settings for UI, animations, language, and display options.
"""
import json
import os
from typing import Dict, Any, Optional
from enum import Enum

class Language(Enum):
    ENGLISH = "en"
    SPANISH = "es"

class Resolution(Enum):
    HD = (1280, 720)
    FULL_HD = (1920, 1080)
    ULTRA_HD = (2560, 1440)
    AUTO = (-1, -1)  # Use system default

class AnimationSpeed(Enum):
    SLOW = 1.5
    NORMAL = 1.0
    FAST = 0.5
    DISABLED = 0.0

class ConfigManager:
    """Manages application configuration settings"""
    
    DEFAULT_CONFIG = {
        'display': {
            'fullscreen': False,
            'resolution': Resolution.AUTO.value,
            'vsync': True,
        },
        'interface': {
            'language': Language.SPANISH.value,
            'animation_speed': AnimationSpeed.NORMAL.value,
            'show_tooltips': True,
            'card_animation_enabled': True,
            'sound_enabled': True,
        },
        'gameplay': {
            'auto_fold_timeout': 30,
            'confirm_actions': True,
            'show_probability_hints': False,
        }
    }
    
    def __init__(self, config_file: str = 'casino_config.json'):
        self.config_file = config_file
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved_config = json.load(f)
                    self._merge_config(saved_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}. Using defaults.")
    
    def save_config(self) -> bool:
        """Save current configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False
    
    def _merge_config(self, saved_config: Dict[str, Any]) -> None:
        """Merge saved config with defaults"""
        for section, values in saved_config.items():
            if section in self.config:
                if isinstance(values, dict) and isinstance(self.config[section], dict):
                    self.config[section].update(values)
                else:
                    self.config[section] = values
    
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(section, {}).get(key, default)
    
    def set(self, section: str, key: str, value: Any) -> None:
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
    
    def is_fullscreen(self) -> bool:
        """Check if fullscreen mode is enabled"""
        return self.get('display', 'fullscreen', False)
    
    def get_resolution(self) -> tuple:
        """Get current resolution setting"""
        return tuple(self.get('display', 'resolution', Resolution.AUTO.value))
    
    def get_language(self) -> Language:
        """Get current language setting"""
        lang_code = self.get('interface', 'language', Language.SPANISH.value)
        try:
            return Language(lang_code)
        except ValueError:
            return Language.SPANISH
    
    def get_animation_speed(self) -> float:
        """Get animation speed multiplier"""
        return self.get('interface', 'animation_speed', AnimationSpeed.NORMAL.value)
    
    def are_animations_enabled(self) -> bool:
        """Check if animations are enabled"""
        return self.get('interface', 'card_animation_enabled', True)
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()


# Global config instance
config_manager = ConfigManager()

# Translations dictionary
TRANSLATIONS = {
    Language.ENGLISH: {
        'casino_title': 'Your Mom\'s Casino',
        'poker': 'Poker',
        'blackjack': 'Blackjack',
        'roulette': 'Roulette',
        'slot_machine': 'Slot Machine',
    'game_menu': 'Game',
        'settings': 'Settings',
    'exit': 'Exit',
        'fullscreen': 'Fullscreen',
        'resolution': 'Resolution',
        'language': 'Language',
        'animation_speed': 'Animation Speed',
        'enable_animations': 'Enable Animations',
        'sound': 'Sound',
        'apply': 'Apply',
        'cancel': 'Cancel',
        'reset_defaults': 'Reset to Defaults',
        'bet': 'Bet',
    'balance': 'Balance',
    'total_bet': 'Total Bet',
    'last_win': 'Last Win',
    'statistics': 'Statistics',
    'ready_to_spin': 'Ready to spin!',
    'bet_per_line': 'Bet per line',
    'lines': 'Lines',
    'add_credits': 'Add credits (+200)',
    'reset_statistics': 'Reset statistics',
    'history': 'History',
    'not_enough_balance_title': 'Insufficient balance',
    'action_not_available': 'Action not available',
    'win_message': 'You won {total} credits!',
    'loss_message': 'No prize this time. Try again!',
    'spinning_message': 'Spinning...',
    'invalid_bet_title': 'Invalid bet',
    'invalid_lines_title': 'Invalid lines',
    'credits_added': '200 credits added to your balance.',
    'statistics_reset': 'Statistics reset.',
    'auto_play': 'Auto play',
    'spin': 'Spin',
        'fold': 'Fold',
        'call': 'Call',
        'raise': 'Raise',
        'check': 'Check',
        'new_hand': 'New Hand',
        'pot': 'POT',
        'phase': 'PHASE',
        'community_cards': 'Community Cards',
        'slow': 'Slow',
        'normal': 'Normal',
        'fast': 'Fast',
        'disabled': 'Disabled',
    },
    Language.SPANISH: {
        'casino_title': 'Casino de tu mama',
        'poker': 'Póker',
        'blackjack': 'Blackjack',
        'roulette': 'Ruleta',
        'slot_machine': 'Tragaperras',
    'game_menu': 'Juego',
        'settings': 'Configuración',
    'exit': 'Salir',
        'fullscreen': 'Pantalla completa',
        'resolution': 'Resolución',
        'language': 'Idioma',
        'animation_speed': 'Velocidad de animación',
        'enable_animations': 'Activar animaciones',
        'sound': 'Sonido',
        'apply': 'Aplicar',
        'cancel': 'Cancelar',
        'reset_defaults': 'Restaurar valores predeterminados',
        'bet': 'Apuesta',
    'balance': 'Saldo',
    'total_bet': 'Apuesta total',
    'last_win': 'Último premio',
    'statistics': 'Estadísticas',
    'ready_to_spin': '¡Listo para girar!',
    'bet_per_line': 'Apuesta por línea',
    'lines': 'Líneas',
    'add_credits': 'Añadir créditos (+200)',
    'reset_statistics': 'Reiniciar estadísticas',
    'history': 'Historial',
    'not_enough_balance_title': 'Saldo insuficiente',
    'action_not_available': 'Acción no disponible',
    'win_message': '¡Has ganado {total} créditos!',
    'loss_message': 'Sin premio esta vez, ¡sigue intentando!',
    'spinning_message': 'Girando...',
    'invalid_bet_title': 'Apuesta no válida',
    'invalid_lines_title': 'Líneas inválidas',
    'credits_added': 'Se añadieron 200 créditos al saldo.',
    'statistics_reset': 'Se reiniciaron las estadísticas.',
    'auto_play': 'Auto juego',
    'spin': 'Girar',
        'fold': 'Retirarse',
        'call': 'Igualar',
        'raise': 'Subir',
        'check': 'Pasar',
        'new_hand': 'Nueva mano',
        'pot': 'BOTE',
        'phase': 'FASE',
        'community_cards': 'Cartas comunitarias',
        'slow': 'Lenta',
        'normal': 'Normal',
        'fast': 'Rápida',
        'disabled': 'Desactivada',
    }
}

def get_text(key: str, language: Optional[Language] = None) -> str:
    """Get translated text for the current language"""
    if language is None:
        language = config_manager.get_language()
    
    return TRANSLATIONS.get(language, TRANSLATIONS[Language.SPANISH]).get(key, key)