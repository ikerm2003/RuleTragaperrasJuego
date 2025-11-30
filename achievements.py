
"""
Achievement System for Casino Game
Manages achievements, tracking progress, and unlocking rewards
"""

from enum import Enum
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass


class AchievementCategory(Enum):
    """Categories for achievements"""
    GENERAL = "general"
    POKER = "poker"
    BLACKJACK = "blackjack"
    ROULETTE = "roulette"
    SLOTS = "slots"
    WEALTH = "wealth"
    SOCIAL = "social"


@dataclass
class Achievement:
    """Represents an achievement"""
    id: str
    name_en: str
    name_es: str
    description_en: str
    description_es: str
    category: AchievementCategory
    target: int  # Target value to complete
    reward: int  # Credits reward
    hidden: bool = False  # Hidden until unlocked
    
    def get_name(self, language: str = 'es') -> str:
        """Get achievement name in specified language"""
        return self.name_es if language == 'es' else self.name_en
    
    def get_description(self, language: str = 'es') -> str:
        """Get achievement description in specified language"""
        return self.description_es if language == 'es' else self.description_en


class AchievementManager:
    """Manages all achievements in the game"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.achievements = self._initialize_achievements()
        self.listeners: List[Callable] = []
    
    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """Initialize all achievements"""
        achievements = {}
        
        # General achievements
        achievements['first_game'] = Achievement(
            id='first_game',
            name_en='First Steps',
            name_es='Primeros Pasos',
            description_en='Play your first game',
            description_es='Juega tu primer juego',
            category=AchievementCategory.GENERAL,
            target=1,
            reward=100
        )
        
        achievements['played_100'] = Achievement(
            id='played_100',
            name_en='Century Player',
            name_es='Jugador Centenario',
            description_en='Play 100 hands total',
            description_es='Juega 100 manos en total',
            category=AchievementCategory.GENERAL,
            target=100,
            reward=500
        )
        
        achievements['played_1000'] = Achievement(
            id='played_1000',
            name_en='Veteran',
            name_es='Veterano',
            description_en='Play 1000 hands total',
            description_es='Juega 1000 manos en total',
            category=AchievementCategory.GENERAL,
            target=1000,
            reward=2000
        )
        
        # Wealth achievements
        achievements['first_win'] = Achievement(
            id='first_win',
            name_en='Lucky Start',
            name_es='Comienzo Afortunado',
            description_en='Win your first hand',
            description_es='Gana tu primera mano',
            category=AchievementCategory.WEALTH,
            target=1,
            reward=50
        )
        
        achievements['win_10'] = Achievement(
            id='win_10',
            name_en='On a Roll',
            name_es='En Racha',
            description_en='Win 10 hands',
            description_es='Gana 10 manos',
            category=AchievementCategory.WEALTH,
            target=10,
            reward=200
        )
        
        achievements['win_100'] = Achievement(
            id='win_100',
            name_en='Winner',
            name_es='Ganador',
            description_en='Win 100 hands',
            description_es='Gana 100 manos',
            category=AchievementCategory.WEALTH,
            target=100,
            reward=1000
        )
        
        achievements['big_win_1000'] = Achievement(
            id='big_win_1000',
            name_en='Big Winner',
            name_es='Gran Ganador',
            description_en='Win 1000 credits in a single hand',
            description_es='Gana 1000 créditos en una sola mano',
            category=AchievementCategory.WEALTH,
            target=1000,
            reward=500
        )
        
        achievements['big_win_5000'] = Achievement(
            id='big_win_5000',
            name_en='Jackpot!',
            name_es='¡Jackpot!',
            description_en='Win 5000 credits in a single hand',
            description_es='Gana 5000 créditos en una sola mano',
            category=AchievementCategory.WEALTH,
            target=5000,
            reward=2000
        )
        
        achievements['millionaire'] = Achievement(
            id='millionaire',
            name_en='Millionaire',
            name_es='Millonario',
            description_en='Accumulate 10000 credits',
            description_es='Acumula 10000 créditos',
            category=AchievementCategory.WEALTH,
            target=10000,
            reward=5000
        )
        
        # Poker achievements
        achievements['poker_10'] = Achievement(
            id='poker_10',
            name_en='Poker Novice',
            name_es='Novato del Póker',
            description_en='Play 10 poker hands',
            description_es='Juega 10 manos de póker',
            category=AchievementCategory.POKER,
            target=10,
            reward=100
        )
        
        achievements['poker_100'] = Achievement(
            id='poker_100',
            name_en='Poker Pro',
            name_es='Profesional del Póker',
            description_en='Play 100 poker hands',
            description_es='Juega 100 manos de póker',
            category=AchievementCategory.POKER,
            target=100,
            reward=500
        )
        
        # Blackjack achievements
        achievements['blackjack_10'] = Achievement(
            id='blackjack_10',
            name_en='21 Enthusiast',
            name_es='Entusiasta del 21',
            description_en='Play 10 blackjack hands',
            description_es='Juega 10 manos de blackjack',
            category=AchievementCategory.BLACKJACK,
            target=10,
            reward=100
        )
        
        achievements['blackjack_100'] = Achievement(
            id='blackjack_100',
            name_en='Card Counter',
            name_es='Contador de Cartas',
            description_en='Play 100 blackjack hands',
            description_es='Juega 100 manos de blackjack',
            category=AchievementCategory.BLACKJACK,
            target=100,
            reward=500
        )
        
        # Roulette achievements
        achievements['roulette_10'] = Achievement(
            id='roulette_10',
            name_en='Wheel Spinner',
            name_es='Girador de Ruleta',
            description_en='Spin the roulette 10 times',
            description_es='Gira la ruleta 10 veces',
            category=AchievementCategory.ROULETTE,
            target=10,
            reward=100
        )
        
        achievements['roulette_100'] = Achievement(
            id='roulette_100',
            name_en='Roulette Master',
            name_es='Maestro de la Ruleta',
            description_en='Spin the roulette 100 times',
            description_es='Gira la ruleta 100 veces',
            category=AchievementCategory.ROULETTE,
            target=100,
            reward=500
        )
        
        # Slots achievements
        achievements['slots_10'] = Achievement(
            id='slots_10',
            name_en='Slot Beginner',
            name_es='Principiante de Tragaperras',
            description_en='Spin slots 10 times',
            description_es='Gira las tragaperras 10 veces',
            category=AchievementCategory.SLOTS,
            target=10,
            reward=100
        )
        
        achievements['slots_100'] = Achievement(
            id='slots_100',
            name_en='Slot Expert',
            name_es='Experto en Tragaperras',
            description_en='Spin slots 100 times',
            description_es='Gira las tragaperras 100 veces',
            category=AchievementCategory.SLOTS,
            target=100,
            reward=500
        )
        
        # Hidden achievements
        achievements['all_games'] = Achievement(
            id='all_games',
            name_en='Jack of All Trades',
            name_es='Maestro de Todos',
            description_en='Play at least 10 hands of each game',
            description_es='Juega al menos 10 manos de cada juego',
            category=AchievementCategory.GENERAL,
            target=1,
            reward=1000,
            hidden=True
        )
        
        return achievements
    
    def add_listener(self, callback: Callable) -> None:
        """Add a listener for achievement unlocks"""
        self.listeners.append(callback)
    
    def _notify_unlock(self, achievement: Achievement) -> None:
        """Notify listeners of achievement unlock"""
        for listener in self.listeners:
            listener(achievement)
    
    def check_and_unlock(self, achievement_id: str, current_value: int) -> bool:
        """Check if achievement should be unlocked and unlock it"""
        if achievement_id not in self.achievements:
            return False
        
        achievement = self.achievements[achievement_id]
        
        # Check if already unlocked
        if self.config.is_achievement_unlocked(achievement_id):
            return False
        
        # Update progress
        self.config.set_achievement_progress(achievement_id, current_value)
        
        # Check if target reached
        if current_value >= achievement.target:
            success = self.config.unlock_achievement(achievement_id)
            if success:
                # Award credits
                current_balance = self.config.get_effective_balance()
                self.config.set_effective_balance(current_balance + achievement.reward)
                self._notify_unlock(achievement)
                return True
        
        return False
    
    def update_game_stat(self, game_type: str, increment: int = 1) -> List[Achievement]:
        """Update game-specific statistics and check achievements"""
        unlocked = []
        
        # Update total hands
        self.config.update_statistic('total_hands_played', increment)
        total_hands = self.config.get_statistic('total_hands_played')
        
        # Check general achievements
        if self.check_and_unlock('first_game', total_hands):
            unlocked.append(self.achievements['first_game'])
        if self.check_and_unlock('played_100', total_hands):
            unlocked.append(self.achievements['played_100'])
        if self.check_and_unlock('played_1000', total_hands):
            unlocked.append(self.achievements['played_1000'])
        
        # Update game-specific stats
        stat_name = f'{game_type}_hands'
        self.config.update_statistic(stat_name, increment)
        game_hands = self.config.get_statistic(stat_name)
        
        # Check game-specific achievements
        if game_type == 'poker':
            if self.check_and_unlock('poker_10', game_hands):
                unlocked.append(self.achievements['poker_10'])
            if self.check_and_unlock('poker_100', game_hands):
                unlocked.append(self.achievements['poker_100'])
        elif game_type == 'blackjack':
            if self.check_and_unlock('blackjack_10', game_hands):
                unlocked.append(self.achievements['blackjack_10'])
            if self.check_and_unlock('blackjack_100', game_hands):
                unlocked.append(self.achievements['blackjack_100'])
        elif game_type == 'roulette':
            if self.check_and_unlock('roulette_10', game_hands):
                unlocked.append(self.achievements['roulette_10'])
            if self.check_and_unlock('roulette_100', game_hands):
                unlocked.append(self.achievements['roulette_100'])
        elif game_type == 'slots':
            if self.check_and_unlock('slots_10', game_hands):
                unlocked.append(self.achievements['slots_10'])
            if self.check_and_unlock('slots_100', game_hands):
                unlocked.append(self.achievements['slots_100'])
        
        # Check "all games" achievement
        if (self.config.get_statistic('poker_hands') >= 10 and
            self.config.get_statistic('blackjack_hands') >= 10 and
            self.config.get_statistic('roulette_spins') >= 10 and
            self.config.get_statistic('slots_spins') >= 10):
            if self.check_and_unlock('all_games', 1):
                unlocked.append(self.achievements['all_games'])
        
        return unlocked
    
    def update_win(self, amount: int) -> List[Achievement]:
        """Update win statistics and check achievements"""
        unlocked = []
        
        # Update wins
        self.config.update_statistic('total_wins', 1)
        total_wins = self.config.get_statistic('total_wins')
        
        # Update amount won
        self.config.update_statistic('total_won', amount)
        
        # Check win achievements
        if self.check_and_unlock('first_win', total_wins):
            unlocked.append(self.achievements['first_win'])
        if self.check_and_unlock('win_10', total_wins):
            unlocked.append(self.achievements['win_10'])
        if self.check_and_unlock('win_100', total_wins):
            unlocked.append(self.achievements['win_100'])
        
        # Check big win achievements
        if self.check_and_unlock('big_win_1000', amount):
            unlocked.append(self.achievements['big_win_1000'])
        if self.check_and_unlock('big_win_5000', amount):
            unlocked.append(self.achievements['big_win_5000'])
        
        # Update biggest win
        current_biggest = self.config.get_statistic('biggest_win')
        if amount > current_biggest:
            self.config.update_statistic('biggest_win', amount, increment=False)
        
        # Check millionaire achievement
        current_balance = self.config.get_effective_balance()
        if self.check_and_unlock('millionaire', current_balance):
            unlocked.append(self.achievements['millionaire'])
        
        return unlocked
    
    def update_loss(self) -> None:
        """Update loss statistics"""
        self.config.update_statistic('total_losses', 1)
    
    def get_all_achievements(self) -> List[Achievement]:
        """Get all achievements"""
        return list(self.achievements.values())
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """Get all unlocked achievements"""
        return [ach for ach in self.achievements.values() 
                if self.config.is_achievement_unlocked(ach.id)]
    
    def get_locked_achievements(self, include_hidden: bool = False) -> List[Achievement]:
        """Get all locked achievements"""
        locked = [ach for ach in self.achievements.values() 
                  if not self.config.is_achievement_unlocked(ach.id)]
        if not include_hidden:
            locked = [ach for ach in locked if not ach.hidden]
        return locked
    
    def get_achievement_progress_percent(self, achievement_id: str) -> float:
        """Get achievement progress as percentage"""
        if achievement_id not in self.achievements:
            return 0.0
        
        achievement = self.achievements[achievement_id]
        current = self.config.get_achievement_progress(achievement_id)
        
        if achievement.target == 0:
            return 100.0
        
        progress = min(100.0, (current / achievement.target) * 100.0)
        return progress
