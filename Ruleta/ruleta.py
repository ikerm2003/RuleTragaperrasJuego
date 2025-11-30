"""Módulo de Ruleta - Implementación completa del juego de ruleta europea.

Este módulo es el punto de entrada legacy para el juego de ruleta.
La implementación completa está en:
- ruleta_logic.py: Lógica del juego
- ruleta_ui.py: Interfaz de usuario
- ruleta_main.py: Punto de entrada principal
"""

from ..Ruleta.ruleta_logic import BetType, RouletteGame

# Re-exportar para compatibilidad
from ..Ruleta.ruleta_main import main, open_roulette_window

__all__ = ["main", "open_roulette_window", "RouletteGame", "BetType"]
