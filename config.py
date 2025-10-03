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
    FRENCH = "fr"
    GERMAN = "de"

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
    },
    Language.FRENCH: {
        'casino_title': 'Casino de ta mère',
        'poker': 'Poker',
        'blackjack': 'Blackjack',
        'roulette': 'Roulette',
        'slot_machine': 'Machine à sous',
        'game_menu': 'Jeu',
        'settings': 'Paramètres',
        'exit': 'Quitter',
        'fullscreen': 'Plein écran',
        'resolution': 'Résolution',
        'language': 'Langue',
        'animation_speed': 'Vitesse d\'animation',
        'enable_animations': 'Activer les animations',
        'sound': 'Son',
        'apply': 'Appliquer',
        'cancel': 'Annuler',
        'reset_defaults': 'Réinitialiser',
        'bet': 'Mise',
        'balance': 'Solde',
        'total_bet': 'Mise totale',
        'last_win': 'Dernier gain',
        'statistics': 'Statistiques',
        'ready_to_spin': 'Prêt à tourner!',
        'bet_per_line': 'Mise par ligne',
        'lines': 'Lignes',
        'add_credits': 'Ajouter des crédits (+200)',
        'reset_statistics': 'Réinitialiser les statistiques',
        'history': 'Historique',
        'not_enough_balance_title': 'Solde insuffisant',
        'action_not_available': 'Action non disponible',
        'win_message': 'Vous avez gagné {total} crédits!',
        'loss_message': 'Pas de prix cette fois, réessayez!',
        'spinning_message': 'En rotation...',
        'invalid_bet_title': 'Mise invalide',
        'invalid_lines_title': 'Lignes invalides',
        'credits_added': '200 crédits ajoutés à votre solde.',
        'statistics_reset': 'Statistiques réinitialisées.',
        'auto_play': 'Jeu automatique',
        'spin': 'Tourner',
        'fold': 'Se coucher',
        'call': 'Suivre',
        'raise': 'Relancer',
        'check': 'Passer',
        'new_hand': 'Nouvelle main',
        'pot': 'POT',
        'phase': 'PHASE',
        'community_cards': 'Cartes communes',
        'slow': 'Lent',
        'normal': 'Normal',
        'fast': 'Rapide',
        'disabled': 'Désactivé',
        'daily_refill_title': 'Recharge Quotidienne',
        'daily_refill_message': 'Votre solde a été rechargé à {balance} crédits! Bon retour!',
        'keyboard_shortcuts': 'Raccourcis Clavier',
        'shortcuts_help': 'Appuyez sur 1-4 pour les jeux, F11 pour plein écran, ESC pour quitter',
        'practice_mode': 'Mode Pratique',
        'practice_mode_on': 'Mode Pratique: ACTIVÉ',
        'practice_mode_off': 'Mode Pratique: DÉSACTIVÉ',
        'practice_balance': 'Solde de Pratique',
        'real_balance': 'Solde Réel',
        'achievements': 'Succès',
        'achievement_unlocked': 'Succès Débloqué!',
        'missions': 'Missions Quotidiennes',
        'mission_completed': 'Mission Terminée!',
        'mission_reward': 'Récompense: {reward} crédits',
        'total_hands': 'Mains Totales',
        'total_wins': 'Victoires Totales',
        'total_losses': 'Défaites Totales',
        'biggest_win': 'Plus Grande Victoire',
        'win_rate': 'Taux de Victoire',
        'view_statistics': 'Voir Statistiques',
        'view_achievements': 'Voir Succès',
        'view_missions': 'Voir Missions',
        'reset_stats': 'Réinitialiser Statistiques',
        'reset_stats_confirm': 'Êtes-vous sûr de vouloir réinitialiser toutes les statistiques?',
        'progress': 'Progrès',
        'completed': 'Terminé',
        'incomplete': 'Incomplet',
        'locked': 'Verrouillé',
        'unlocked': 'Débloqué',
    },
    Language.GERMAN: {
        'casino_title': 'Mamas Casino',
        'poker': 'Poker',
        'blackjack': 'Blackjack',
        'roulette': 'Roulette',
        'slot_machine': 'Spielautomat',
        'game_menu': 'Spiel',
        'settings': 'Einstellungen',
        'exit': 'Beenden',
        'fullscreen': 'Vollbild',
        'resolution': 'Auflösung',
        'language': 'Sprache',
        'animation_speed': 'Animationsgeschwindigkeit',
        'enable_animations': 'Animationen aktivieren',
        'sound': 'Ton',
        'apply': 'Anwenden',
        'cancel': 'Abbrechen',
        'reset_defaults': 'Zurücksetzen',
        'bet': 'Einsatz',
        'balance': 'Guthaben',
        'total_bet': 'Gesamteinsatz',
        'last_win': 'Letzter Gewinn',
        'statistics': 'Statistiken',
        'ready_to_spin': 'Bereit zum Drehen!',
        'bet_per_line': 'Einsatz pro Linie',
        'lines': 'Linien',
        'add_credits': 'Kredite hinzufügen (+200)',
        'reset_statistics': 'Statistiken zurücksetzen',
        'history': 'Verlauf',
        'not_enough_balance_title': 'Unzureichendes Guthaben',
        'action_not_available': 'Aktion nicht verfügbar',
        'win_message': 'Sie haben {total} Kredite gewonnen!',
        'loss_message': 'Dieses Mal kein Preis, versuchen Sie es erneut!',
        'spinning_message': 'Dreht sich...',
        'invalid_bet_title': 'Ungültiger Einsatz',
        'invalid_lines_title': 'Ungültige Linien',
        'credits_added': '200 Kredite zu Ihrem Guthaben hinzugefügt.',
        'statistics_reset': 'Statistiken zurückgesetzt.',
        'auto_play': 'Automatisches Spiel',
        'spin': 'Drehen',
        'fold': 'Aussteigen',
        'call': 'Mitgehen',
        'raise': 'Erhöhen',
        'check': 'Schieben',
        'new_hand': 'Neue Hand',
        'pot': 'POTT',
        'phase': 'PHASE',
        'community_cards': 'Gemeinschaftskarten',
        'slow': 'Langsam',
        'normal': 'Normal',
        'fast': 'Schnell',
        'disabled': 'Deaktiviert',
        'daily_refill_title': 'Tägliche Aufladung',
        'daily_refill_message': 'Ihr Guthaben wurde auf {balance} Kredite aufgefüllt! Willkommen zurück!',
        'keyboard_shortcuts': 'Tastaturkürzel',
        'shortcuts_help': 'Drücken Sie 1-4 für Spiele, F11 für Vollbild, ESC zum Beenden',
        'practice_mode': 'Übungsmodus',
        'practice_mode_on': 'Übungsmodus: EIN',
        'practice_mode_off': 'Übungsmodus: AUS',
        'practice_balance': 'Übungsguthaben',
        'real_balance': 'Echtes Guthaben',
        'achievements': 'Erfolge',
        'achievement_unlocked': 'Erfolg Freigeschaltet!',
        'missions': 'Tägliche Missionen',
        'mission_completed': 'Mission Abgeschlossen!',
        'mission_reward': 'Belohnung: {reward} Kredite',
        'total_hands': 'Gesamte Hände',
        'total_wins': 'Gesamtsiege',
        'total_losses': 'Gesamtverluste',
        'biggest_win': 'Größter Gewinn',
        'win_rate': 'Gewinnrate',
        'view_statistics': 'Statistiken Anzeigen',
        'view_achievements': 'Erfolge Anzeigen',
        'view_missions': 'Missionen Anzeigen',
        'reset_stats': 'Statistiken Zurücksetzen',
        'reset_stats_confirm': 'Sind Sie sicher, dass Sie alle Statistiken zurücksetzen möchten?',
        'progress': 'Fortschritt',
        'completed': 'Abgeschlossen',
        'incomplete': 'Unvollständig',
        'locked': 'Gesperrt',
        'unlocked': 'Freigeschaltet',
    }
}

def get_text(key: str, language: Optional[Language] = None) -> str:
    """Get translated text for the current language"""
    if language is None:
        language = config_manager.get_language()
    
    return TRANSLATIONS.get(language, TRANSLATIONS[Language.SPANISH]).get(key, key)