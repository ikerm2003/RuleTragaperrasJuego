"""Contrato unificado de eventos de juego para estadísticas, misiones y logros."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from achievements import AchievementManager
from config import config_manager
from missions import MissionManager
from sound_manager import get_sound_manager


_GAME_TYPE_ALIASES = {
    "poker": "poker",
    "blackjack": "blackjack",
    "roulette": "roulette",
    "ruleta": "roulette",
    "slots": "slots",
    "tragaperras": "slots",
}


@dataclass(frozen=True)
class GameRoundEvent:
    """Evento estándar de fin de ronda para todos los juegos."""

    game_type: str
    rounds_played: int = 1
    wagered: int = 0
    net_win: int = 0

    def normalized_game_type(self) -> str:
        normalized = _GAME_TYPE_ALIASES.get(str(self.game_type).strip().lower())
        if normalized is None:
            raise ValueError(f"Tipo de juego no soportado: {self.game_type}")
        return normalized


class GameEventService:
    """Aplica eventos de ronda al estado global de progresión del jugador."""

    def __init__(self, cfg=None, achievement_manager=None, mission_manager=None):
        self.config: Any = cfg if cfg is not None else config_manager
        self.achievement_manager = (
            achievement_manager
            if achievement_manager is not None
            else AchievementManager(self.config)
        )
        self.mission_manager = (
            mission_manager if mission_manager is not None else MissionManager(self.config)
        )
        self.sound_manager = get_sound_manager(self.config)

    def record_round(self, event: GameRoundEvent) -> dict[str, Any]:
        game_type = event.normalized_game_type()
        rounds_played = max(1, int(event.rounds_played))
        wagered = max(0, int(event.wagered))
        net_win = int(event.net_win)

        unlocked_ids: list[str] = []
        completed_mission_ids: list[str] = []

        begin_batch = getattr(self.config, "begin_batch", None)
        end_batch = getattr(self.config, "end_batch", None)
        if callable(begin_batch) and callable(end_batch):
            begin_batch()
            try:
                self._apply_round_updates(
                    game_type,
                    rounds_played,
                    wagered,
                    net_win,
                    unlocked_ids,
                    completed_mission_ids,
                )
            finally:
                end_batch()
        else:
            self._apply_round_updates(
                game_type,
                rounds_played,
                wagered,
                net_win,
                unlocked_ids,
                completed_mission_ids,
            )

        try:
            if unlocked_ids and self.sound_manager is not None:
                self.sound_manager.play_achievement_unlock()
            if completed_mission_ids and self.sound_manager is not None:
                self.sound_manager.play_mission_complete()
        except Exception:
            pass

        return {
            "game_type": game_type,
            "rounds_played": rounds_played,
            "wagered": wagered,
            "net_win": net_win,
            "unlocked_achievements": [item for item in unlocked_ids if item],
            "completed_missions": [item for item in completed_mission_ids if item],
        }

    def _apply_round_updates(
        self,
        game_type: str,
        rounds_played: int,
        wagered: int,
        net_win: int,
        unlocked_ids: list[str],
        completed_mission_ids: list[str],
    ) -> None:
        """Aplica las actualizaciones de progresión de una ronda."""
        if wagered > 0:
            self.config.update_statistic("total_wagered", wagered)

        unlocked = self.achievement_manager.update_game_stat(
            game_type, increment=rounds_played
        )
        unlocked_ids.extend(getattr(item, "id", "") for item in unlocked)

        for _ in range(rounds_played):
            completed = self.mission_manager.update_on_hand_played(game_type)
            completed_mission_ids.extend(getattr(item, "id", "") for item in completed)

        if net_win > 0:
            unlocked_win = self.achievement_manager.update_win(net_win)
            unlocked_ids.extend(getattr(item, "id", "") for item in unlocked_win)
            completed_win = self.mission_manager.update_on_win(net_win)
            completed_mission_ids.extend(
                getattr(item, "id", "") for item in completed_win
            )
        elif net_win < 0:
            self.achievement_manager.update_loss()


_default_service: GameEventService | None = None


def get_game_event_service() -> GameEventService:
    global _default_service
    if _default_service is None:
        _default_service = GameEventService()
    return _default_service
