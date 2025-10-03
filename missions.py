#!/usr/bin/env python3
"""
Daily Missions System for Casino Game
Manages daily missions, rotation, and rewards
"""

import random
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict
from datetime import datetime


class MissionType(Enum):
    """Types of missions"""
    PLAY_HANDS = "play_hands"
    WIN_HANDS = "win_hands"
    WIN_AMOUNT = "win_amount"
    PLAY_GAME = "play_game"
    BIG_WIN = "big_win"


@dataclass
class Mission:
    """Represents a daily mission"""
    id: str
    name_en: str
    name_es: str
    description_en: str
    description_es: str
    mission_type: MissionType
    target: int
    reward: int
    game_type: str = None  # Specific game type or None for any game
    
    def get_name(self, language: str = 'es') -> str:
        """Get mission name in specified language"""
        return self.name_es if language == 'es' else self.name_en
    
    def get_description(self, language: str = 'es') -> str:
        """Get mission description in specified language"""
        return self.description_es if language == 'es' else self.description_en


class MissionManager:
    """Manages daily missions"""
    
    def __init__(self, config_manager):
        self.config = config_manager
        self.mission_templates = self._initialize_mission_templates()
        self.current_missions = []
        self._load_missions()
    
    def _initialize_mission_templates(self) -> List[Mission]:
        """Initialize all possible mission templates"""
        templates = []
        
        # General play missions
        templates.append(Mission(
            id='play_5',
            name_en='Daily Player',
            name_es='Jugador Diario',
            description_en='Play 5 hands in any game',
            description_es='Juega 5 manos en cualquier juego',
            mission_type=MissionType.PLAY_HANDS,
            target=5,
            reward=100
        ))
        
        templates.append(Mission(
            id='play_10',
            name_en='Active Player',
            name_es='Jugador Activo',
            description_en='Play 10 hands in any game',
            description_es='Juega 10 manos en cualquier juego',
            mission_type=MissionType.PLAY_HANDS,
            target=10,
            reward=200
        ))
        
        templates.append(Mission(
            id='play_20',
            name_en='Dedicated Player',
            name_es='Jugador Dedicado',
            description_en='Play 20 hands in any game',
            description_es='Juega 20 manos en cualquier juego',
            mission_type=MissionType.PLAY_HANDS,
            target=20,
            reward=400
        ))
        
        # Win missions
        templates.append(Mission(
            id='win_3',
            name_en='Lucky Day',
            name_es='Día de Suerte',
            description_en='Win 3 hands',
            description_es='Gana 3 manos',
            mission_type=MissionType.WIN_HANDS,
            target=3,
            reward=150
        ))
        
        templates.append(Mission(
            id='win_5',
            name_en='On Fire',
            name_es='En Racha',
            description_en='Win 5 hands',
            description_es='Gana 5 manos',
            mission_type=MissionType.WIN_HANDS,
            target=5,
            reward=300
        ))
        
        templates.append(Mission(
            id='win_10',
            name_en='Unstoppable',
            name_es='Imparable',
            description_en='Win 10 hands',
            description_es='Gana 10 manos',
            mission_type=MissionType.WIN_HANDS,
            target=10,
            reward=600
        ))
        
        # Win amount missions
        templates.append(Mission(
            id='win_500',
            name_en='Small Fortune',
            name_es='Pequeña Fortuna',
            description_en='Win 500 credits total',
            description_es='Gana 500 créditos en total',
            mission_type=MissionType.WIN_AMOUNT,
            target=500,
            reward=250
        ))
        
        templates.append(Mission(
            id='win_1000',
            name_en='Big Earner',
            name_es='Gran Ganador',
            description_en='Win 1000 credits total',
            description_es='Gana 1000 créditos en total',
            mission_type=MissionType.WIN_AMOUNT,
            target=1000,
            reward=500
        ))
        
        # Big win missions
        templates.append(Mission(
            id='big_win_500',
            name_en='Big Score',
            name_es='Gran Golpe',
            description_en='Win 500 credits in a single hand',
            description_es='Gana 500 créditos en una sola mano',
            mission_type=MissionType.BIG_WIN,
            target=500,
            reward=300
        ))
        
        templates.append(Mission(
            id='big_win_1000',
            name_en='Jackpot Hunter',
            name_es='Cazador de Jackpot',
            description_en='Win 1000 credits in a single hand',
            description_es='Gana 1000 créditos en una sola mano',
            mission_type=MissionType.BIG_WIN,
            target=1000,
            reward=600
        ))
        
        # Game-specific missions
        for game_name, game_id in [('Poker', 'poker'), ('Blackjack', 'blackjack'), 
                                     ('Roulette', 'roulette'), ('Slots', 'slots')]:
            templates.append(Mission(
                id=f'{game_id}_5',
                name_en=f'{game_name} Enthusiast',
                name_es=f'Entusiasta de {game_name}',
                description_en=f'Play 5 hands of {game_name}',
                description_es=f'Juega 5 manos de {game_name}',
                mission_type=MissionType.PLAY_GAME,
                target=5,
                reward=150,
                game_type=game_id
            ))
            
            templates.append(Mission(
                id=f'{game_id}_10',
                name_en=f'{game_name} Master',
                name_es=f'Maestro de {game_name}',
                description_en=f'Play 10 hands of {game_name}',
                description_es=f'Juega 10 manos de {game_name}',
                mission_type=MissionType.PLAY_GAME,
                target=10,
                reward=300,
                game_type=game_id
            ))
        
        return templates
    
    def _load_missions(self) -> None:
        """Load today's missions from config"""
        last_mission_date = self.config.get('missions', 'last_mission_date')
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Check if we need to generate new missions
        if last_mission_date != today:
            self._generate_daily_missions()
            self.config.reset_daily_missions()
        else:
            # Load existing missions
            mission_data = self.config.get_daily_missions()
            self.current_missions = []
            for mid in mission_data:
                mission = self._find_mission_template(mid)
                if mission:
                    self.current_missions.append(mission)
    
    def _find_mission_template(self, mission_id: str) -> Mission:
        """Find a mission template by ID"""
        for mission in self.mission_templates:
            if mission.id == mission_id:
                return mission
        return None
    
    def _generate_daily_missions(self) -> None:
        """Generate 3 random daily missions"""
        # Select 3 random missions
        self.current_missions = random.sample(self.mission_templates, 3)
        
        # Save to config
        mission_ids = [m.id for m in self.current_missions]
        self.config.set_daily_missions(mission_ids)
    
    def get_current_missions(self) -> List[Mission]:
        """Get today's active missions"""
        return self.current_missions
    
    def get_mission_progress(self, mission: Mission) -> int:
        """Get current progress for a mission"""
        if self.config.is_mission_completed(mission.id):
            return mission.target
        
        # Get progress based on mission type
        if mission.mission_type == MissionType.PLAY_HANDS:
            # Count total hands played today (would need session tracking)
            return self.config.get('missions', f'progress_{mission.id}', 0)
        elif mission.mission_type == MissionType.WIN_HANDS:
            return self.config.get('missions', f'progress_{mission.id}', 0)
        elif mission.mission_type == MissionType.WIN_AMOUNT:
            return self.config.get('missions', f'progress_{mission.id}', 0)
        elif mission.mission_type == MissionType.PLAY_GAME:
            return self.config.get('missions', f'progress_{mission.id}', 0)
        elif mission.mission_type == MissionType.BIG_WIN:
            return self.config.get('missions', f'progress_{mission.id}', 0)
        
        return 0
    
    def update_mission_progress(self, mission: Mission, increment: int) -> bool:
        """Update mission progress. Returns True if mission completed."""
        if self.config.is_mission_completed(mission.id):
            return False
        
        current = self.get_mission_progress(mission)
        new_progress = current + increment
        
        # Save progress
        self.config.set('missions', f'progress_{mission.id}', new_progress)
        self.config.save_config()
        
        # Check if completed
        if new_progress >= mission.target:
            self.config.mark_mission_completed(mission.id)
            # Award reward
            current_balance = self.config.get_effective_balance()
            self.config.set_effective_balance(current_balance + mission.reward)
            return True
        
        return False
    
    def update_on_hand_played(self, game_type: str) -> List[Mission]:
        """Update missions when a hand is played"""
        completed = []
        
        for mission in self.current_missions:
            if self.config.is_mission_completed(mission.id):
                continue
            
            # Update general play missions
            if mission.mission_type == MissionType.PLAY_HANDS:
                if self.update_mission_progress(mission, 1):
                    completed.append(mission)
            
            # Update game-specific missions
            elif mission.mission_type == MissionType.PLAY_GAME:
                if mission.game_type == game_type:
                    if self.update_mission_progress(mission, 1):
                        completed.append(mission)
        
        return completed
    
    def update_on_win(self, amount: int) -> List[Mission]:
        """Update missions when a hand is won"""
        completed = []
        
        for mission in self.current_missions:
            if self.config.is_mission_completed(mission.id):
                continue
            
            # Update win count missions
            if mission.mission_type == MissionType.WIN_HANDS:
                if self.update_mission_progress(mission, 1):
                    completed.append(mission)
            
            # Update win amount missions
            elif mission.mission_type == MissionType.WIN_AMOUNT:
                if self.update_mission_progress(mission, amount):
                    completed.append(mission)
            
            # Update big win missions
            elif mission.mission_type == MissionType.BIG_WIN:
                if amount >= mission.target:
                    if self.update_mission_progress(mission, amount):
                        completed.append(mission)
        
        return completed
    
    def get_completion_status(self) -> Dict[str, bool]:
        """Get completion status for all missions"""
        status = {}
        for mission in self.current_missions:
            status[mission.id] = self.config.is_mission_completed(mission.id)
        return status
    
    def get_mission_progress_percent(self, mission: Mission) -> float:
        """Get mission progress as percentage"""
        current = self.get_mission_progress(mission)
        if mission.target == 0:
            return 100.0
        return min(100.0, (current / mission.target) * 100.0)
