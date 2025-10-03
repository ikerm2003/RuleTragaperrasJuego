"""
Configuration module for the Casino game.
Handles settings for UI, animations, language, and display options.
"""
import json
import os
import copy
from typing import Dict, Any, Optional
from enum import Enum
from datetime import datetime

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
            'starting_balance': 1000,
            'daily_refill_enabled': True,
            'practice_mode': False,
        },
        'player': {
            'last_login': None,
            'current_balance': 1000,
            'practice_balance': 10000,
        },
        'statistics': {
            'total_hands_played': 0,
            'total_wins': 0,
            'total_losses': 0,
            'biggest_win': 0,
            'total_wagered': 0,
            'total_won': 0,
            'poker_hands': 0,
            'blackjack_hands': 0,
            'roulette_spins': 0,
            'slots_spins': 0,
        },
        'achievements': {
            'unlocked': [],
            'progress': {},
        },
        'missions': {
            'daily_missions': [],
            'last_mission_date': None,
            'completed_today': [],
        }
    }
    
    def __init__(self, config_file: str = 'casino_config.json'):
        self.config_file = config_file
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
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
        self.config = copy.deepcopy(self.DEFAULT_CONFIG)
    
    def check_daily_refill(self) -> bool:
        """Check if daily refill should be applied and apply it if needed.
        
        Returns:
            True if refill was applied, False otherwise
        """
        if not self.get('gameplay', 'daily_refill_enabled', True):
            return False
        
        last_login = self.get('player', 'last_login')
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if it's a new day (or first login)
        refill_applied = False
        if last_login != today:
            starting_balance = self.get('gameplay', 'starting_balance', 1000)
            current_balance = self.get('player', 'current_balance', 1000)
            
            # Only refill if balance is below starting balance
            if current_balance < starting_balance:
                self.set('player', 'current_balance', starting_balance)
                refill_applied = True
        
        # Update last login
        self.set('player', 'last_login', today)
        self.save_config()
        
        return refill_applied
    
    def get_player_balance(self) -> int:
        """Get current player balance"""
        return self.get('player', 'current_balance', 1000)
    
    def set_player_balance(self, balance: int) -> None:
        """Set player balance"""
        self.set('player', 'current_balance', balance)
        self.save_config()
    
    def is_practice_mode(self) -> bool:
        """Check if practice mode is enabled"""
        return self.get('gameplay', 'practice_mode', False)
    
    def set_practice_mode(self, enabled: bool) -> None:
        """Set practice mode"""
        self.set('gameplay', 'practice_mode', enabled)
        self.save_config()
    
    def get_practice_balance(self) -> int:
        """Get practice mode balance"""
        return self.get('player', 'practice_balance', 10000)
    
    def set_practice_balance(self, balance: int) -> None:
        """Set practice mode balance"""
        self.set('player', 'practice_balance', balance)
        self.save_config()
    
    def get_effective_balance(self) -> int:
        """Get the effective balance based on practice mode"""
        if self.is_practice_mode():
            return self.get_practice_balance()
        return self.get_player_balance()
    
    def set_effective_balance(self, balance: int) -> None:
        """Set the effective balance based on practice mode"""
        if self.is_practice_mode():
            self.set_practice_balance(balance)
        else:
            self.set_player_balance(balance)
    
    # Statistics methods
    def update_statistic(self, stat_name: str, value: int, increment: bool = True) -> None:
        """Update a statistic value"""
        current = self.get('statistics', stat_name, 0)
        if increment:
            self.set('statistics', stat_name, current + value)
        else:
            self.set('statistics', stat_name, value)
        self.save_config()
    
    def get_statistic(self, stat_name: str, default: int = 0) -> int:
        """Get a statistic value"""
        return self.get('statistics', stat_name, default)
    
    def reset_statistics(self) -> None:
        """Reset all statistics"""
        stats = copy.deepcopy(self.DEFAULT_CONFIG['statistics'])
        self.config['statistics'] = stats
        self.save_config()
    
    # Achievement methods
    def unlock_achievement(self, achievement_id: str) -> bool:
        """Unlock an achievement. Returns True if newly unlocked."""
        unlocked = self.get('achievements', 'unlocked', [])
        if achievement_id not in unlocked:
            unlocked.append(achievement_id)
            self.set('achievements', 'unlocked', unlocked)
            self.save_config()
            return True
        return False
    
    def is_achievement_unlocked(self, achievement_id: str) -> bool:
        """Check if an achievement is unlocked"""
        unlocked = self.get('achievements', 'unlocked', [])
        return achievement_id in unlocked
    
    def get_achievement_progress(self, achievement_id: str) -> int:
        """Get progress for an achievement"""
        progress = self.get('achievements', 'progress', {})
        return progress.get(achievement_id, 0)
    
    def set_achievement_progress(self, achievement_id: str, progress: int) -> None:
        """Set progress for an achievement"""
        progress_dict = self.get('achievements', 'progress', {})
        progress_dict[achievement_id] = progress
        self.set('achievements', 'progress', progress_dict)
        self.save_config()
    
    # Mission methods
    def get_daily_missions(self) -> list:
        """Get today's daily missions"""
        return self.get('missions', 'daily_missions', [])
    
    def set_daily_missions(self, missions: list) -> None:
        """Set daily missions"""
        self.set('missions', 'daily_missions', missions)
        self.set('missions', 'last_mission_date', datetime.now().strftime('%Y-%m-%d'))
        self.save_config()
    
    def mark_mission_completed(self, mission_id: str) -> None:
        """Mark a mission as completed"""
        completed = self.get('missions', 'completed_today', [])
        if mission_id not in completed:
            completed.append(mission_id)
            self.set('missions', 'completed_today', completed)
            self.save_config()
    
    def is_mission_completed(self, mission_id: str) -> bool:
        """Check if a mission is completed today"""
        completed = self.get('missions', 'completed_today', [])
        return mission_id in completed
    
    def reset_daily_missions(self) -> None:
        """Reset daily missions (called on new day)"""
        self.set('missions', 'completed_today', [])
        self.save_config()


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
        'daily_refill_title': 'Daily Refill',
        'daily_refill_message': 'Your balance has been refilled to {balance} credits! Welcome back!',
        'keyboard_shortcuts': 'Keyboard Shortcuts',
        'shortcuts_help': 'Press 1-4 for games, F11 for fullscreen, ESC to quit',
        'practice_mode': 'Practice Mode',
        'practice_mode_on': 'Practice Mode: ON',
        'practice_mode_off': 'Practice Mode: OFF',
        'practice_balance': 'Practice Balance',
        'real_balance': 'Real Balance',
        'achievements': 'Achievements',
        'achievement_unlocked': 'Achievement Unlocked!',
        'statistics': 'Statistics',
        'missions': 'Daily Missions',
        'mission_completed': 'Mission Completed!',
        'mission_reward': 'Reward: {reward} credits',
        'total_hands': 'Total Hands',
        'total_wins': 'Total Wins',
        'total_losses': 'Total Losses',
        'biggest_win': 'Biggest Win',
        'win_rate': 'Win Rate',
        'view_statistics': 'View Statistics',
        'view_achievements': 'View Achievements',
        'view_missions': 'View Missions',
        'reset_stats': 'Reset Statistics',
        'reset_stats_confirm': 'Are you sure you want to reset all statistics?',
        'progress': 'Progress',
        'completed': 'Completed',
        'incomplete': 'Incomplete',
        'locked': 'Locked',
        'unlocked': 'Unlocked',
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
        'daily_refill_title': 'Recarga Diaria',
        'daily_refill_message': '¡Tu saldo ha sido recargado a {balance} créditos! ¡Bienvenido de vuelta!',
        'keyboard_shortcuts': 'Atajos de Teclado',
        'shortcuts_help': 'Presiona 1-4 para juegos, F11 para pantalla completa, ESC para salir',
        'practice_mode': 'Modo Práctica',
        'practice_mode_on': 'Modo Práctica: ACTIVADO',
        'practice_mode_off': 'Modo Práctica: DESACTIVADO',
        'practice_balance': 'Saldo de Práctica',
        'real_balance': 'Saldo Real',
        'achievements': 'Logros',
        'achievement_unlocked': '¡Logro Desbloqueado!',
        'statistics': 'Estadísticas',
        'missions': 'Misiones Diarias',
        'mission_completed': '¡Misión Completada!',
        'mission_reward': 'Recompensa: {reward} créditos',
        'total_hands': 'Manos Totales',
        'total_wins': 'Victorias Totales',
        'total_losses': 'Derrotas Totales',
        'biggest_win': 'Mayor Victoria',
        'win_rate': 'Tasa de Victoria',
        'view_statistics': 'Ver Estadísticas',
        'view_achievements': 'Ver Logros',
        'view_missions': 'Ver Misiones',
        'reset_stats': 'Reiniciar Estadísticas',
        'reset_stats_confirm': '¿Estás seguro de que quieres reiniciar todas las estadísticas?',
        'progress': 'Progreso',
        'completed': 'Completado',
        'incomplete': 'Incompleto',
        'locked': 'Bloqueado',
        'unlocked': 'Desbloqueado',
    }
}

def get_text(key: str, language: Optional[Language] = None) -> str:
    """Get translated text for the current language"""
    if language is None:
        language = config_manager.get_language()
    
    return TRANSLATIONS.get(language, TRANSLATIONS[Language.SPANISH]).get(key, key)