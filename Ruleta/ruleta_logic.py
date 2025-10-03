"""Módulo de lógica para el juego de la Ruleta.

Implementa la lógica completa de una ruleta europea (37 números: 0-36).
Incluye:
* Gestión de números y colores
* Tipos de apuestas: pleno, color, par/impar, docenas, columnas, etc.
* Cálculo de pagos según el tipo de apuesta
* Gestión de saldo y apuestas
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Optional, Dict


class BetType(Enum):
    """Tipos de apuesta en la ruleta"""
    STRAIGHT_UP = "straight_up"      # Pleno (1 número) - Paga 35:1
    SPLIT = "split"                   # Caballo (2 números) - Paga 17:1
    STREET = "street"                 # Transversal (3 números) - Paga 11:1
    CORNER = "corner"                 # Cuadro (4 números) - Paga 8:1
    SIX_LINE = "six_line"            # Línea (6 números) - Paga 5:1
    DOZEN = "dozen"                   # Docena (12 números) - Paga 2:1
    COLUMN = "column"                 # Columna (12 números) - Paga 2:1
    RED = "red"                       # Rojo - Paga 1:1
    BLACK = "black"                   # Negro - Paga 1:1
    EVEN = "even"                     # Par - Paga 1:1
    ODD = "odd"                       # Impar - Paga 1:1
    LOW = "low"                       # 1-18 - Paga 1:1
    HIGH = "high"                     # 19-36 - Paga 1:1


# Configuración de números rojos en la ruleta europea
RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}


@dataclass
class Bet:
    """Representa una apuesta en la ruleta"""
    bet_type: BetType
    numbers: List[int]  # Números cubiertos por la apuesta
    amount: int
    
    def get_payout_multiplier(self) -> int:
        """Devuelve el multiplicador de pago según el tipo de apuesta"""
        payouts = {
            BetType.STRAIGHT_UP: 35,
            BetType.SPLIT: 17,
            BetType.STREET: 11,
            BetType.CORNER: 8,
            BetType.SIX_LINE: 5,
            BetType.DOZEN: 2,
            BetType.COLUMN: 2,
            BetType.RED: 1,
            BetType.BLACK: 1,
            BetType.EVEN: 1,
            BetType.ODD: 1,
            BetType.LOW: 1,
            BetType.HIGH: 1,
        }
        return payouts.get(self.bet_type, 0)
    
    def check_win(self, winning_number: int) -> bool:
        """Verifica si la apuesta gana con el número ganador"""
        return winning_number in self.numbers
    
    def calculate_payout(self, winning_number: int) -> int:
        """Calcula el pago si la apuesta gana"""
        if self.check_win(winning_number):
            return self.amount * (self.get_payout_multiplier() + 1)  # +1 incluye la apuesta original
        return 0


class RouletteGame:
    """Gestiona la lógica del juego de la ruleta"""
    
    def __init__(self, initial_balance: int = 1000):
        self.balance = initial_balance
        self.bets: List[Bet] = []
        self.last_winning_number: Optional[int] = None
        self.history: List[int] = []  # Historial de números ganadores
    
    def get_number_color(self, number: int) -> str:
        """Devuelve el color de un número"""
        if number == 0:
            return "green"
        elif number in RED_NUMBERS:
            return "red"
        else:
            return "black"
    
    def place_bet(self, bet: Bet) -> bool:
        """Coloca una apuesta"""
        if bet.amount <= 0 or bet.amount > self.balance:
            return False
        
        self.bets.append(bet)
        self.balance -= bet.amount
        return True
    
    def get_total_bet(self) -> int:
        """Devuelve el total apostado"""
        return sum(bet.amount for bet in self.bets)
    
    def clear_bets(self):
        """Limpia todas las apuestas"""
        # Devolver dinero de apuestas no jugadas
        for bet in self.bets:
            self.balance += bet.amount
        self.bets = []
    
    def spin(self) -> Tuple[int, int]:
        """Gira la ruleta y devuelve (número ganador, ganancias totales)"""
        if not self.bets:
            return -1, 0
        
        # Generar número ganador (0-36)
        winning_number = random.randint(0, 36)
        self.last_winning_number = winning_number
        self.history.append(winning_number)
        
        # Limitar historial a últimos 20 números
        if len(self.history) > 20:
            self.history.pop(0)
        
        # Calcular ganancias
        total_winnings = 0
        for bet in self.bets:
            total_winnings += bet.calculate_payout(winning_number)
        
        self.balance += total_winnings
        self.bets = []  # Limpiar apuestas después del giro
        
        return winning_number, total_winnings
    
    def create_straight_up_bet(self, number: int, amount: int) -> Optional[Bet]:
        """Crea una apuesta a pleno (un número)"""
        if number < 0 or number > 36:
            return None
        return Bet(BetType.STRAIGHT_UP, [number], amount)
    
    def create_split_bet(self, numbers: List[int], amount: int) -> Optional[Bet]:
        """Crea una apuesta a caballo (dos números adyacentes)"""
        if len(numbers) != 2 or not all(0 <= n <= 36 for n in numbers):
            return None
        return Bet(BetType.SPLIT, numbers, amount)
    
    def create_street_bet(self, first_number: int, amount: int) -> Optional[Bet]:
        """Crea una apuesta a transversal (tres números en fila)"""
        if first_number < 1 or first_number > 34 or first_number % 3 != 1:
            return None
        numbers = [first_number, first_number + 1, first_number + 2]
        return Bet(BetType.STREET, numbers, amount)
    
    def create_corner_bet(self, top_left: int, amount: int) -> Optional[Bet]:
        """Crea una apuesta a cuadro (cuatro números en cuadrado)"""
        numbers = [top_left, top_left + 1, top_left + 3, top_left + 4]
        if not all(1 <= n <= 36 for n in numbers):
            return None
        return Bet(BetType.CORNER, numbers, amount)
    
    def create_six_line_bet(self, first_number: int, amount: int) -> Optional[Bet]:
        """Crea una apuesta a línea (seis números en dos filas)"""
        if first_number < 1 or first_number > 31 or first_number % 3 != 1:
            return None
        numbers = list(range(first_number, first_number + 6))
        return Bet(BetType.SIX_LINE, numbers, amount)
    
    def create_dozen_bet(self, dozen: int, amount: int) -> Optional[Bet]:
        """Crea una apuesta a docena (1-12, 13-24, 25-36)"""
        if dozen not in [1, 2, 3]:
            return None
        start = (dozen - 1) * 12 + 1
        numbers = list(range(start, start + 12))
        return Bet(BetType.DOZEN, numbers, amount)
    
    def create_column_bet(self, column: int, amount: int) -> Optional[Bet]:
        """Crea una apuesta a columna (1, 2, 3)"""
        if column not in [1, 2, 3]:
            return None
        numbers = list(range(column, 37, 3))
        return Bet(BetType.COLUMN, numbers, amount)
    
    def create_color_bet(self, color: str, amount: int) -> Optional[Bet]:
        """Crea una apuesta a color (rojo o negro)"""
        if color.lower() == "red":
            return Bet(BetType.RED, list(RED_NUMBERS), amount)
        elif color.lower() == "black":
            return Bet(BetType.BLACK, list(BLACK_NUMBERS), amount)
        return None
    
    def create_even_odd_bet(self, even: bool, amount: int) -> Bet:
        """Crea una apuesta a par o impar"""
        if even:
            numbers = [n for n in range(2, 37, 2)]
            return Bet(BetType.EVEN, numbers, amount)
        else:
            numbers = [n for n in range(1, 37, 2)]
            return Bet(BetType.ODD, numbers, amount)
    
    def create_high_low_bet(self, high: bool, amount: int) -> Bet:
        """Crea una apuesta a alto (19-36) o bajo (1-18)"""
        if high:
            numbers = list(range(19, 37))
            return Bet(BetType.HIGH, numbers, amount)
        else:
            numbers = list(range(1, 19))
            return Bet(BetType.LOW, numbers, amount)
    
    def get_statistics(self) -> Dict[str, int]:
        """Devuelve estadísticas del historial"""
        if not self.history:
            return {
                "total_spins": 0,
                "red_count": 0,
                "black_count": 0,
                "zero_count": 0,
                "even_count": 0,
                "odd_count": 0,
            }
        
        return {
            "total_spins": len(self.history),
            "red_count": sum(1 for n in self.history if n in RED_NUMBERS),
            "black_count": sum(1 for n in self.history if n in BLACK_NUMBERS),
            "zero_count": sum(1 for n in self.history if n == 0),
            "even_count": sum(1 for n in self.history if n > 0 and n % 2 == 0),
            "odd_count": sum(1 for n in self.history if n > 0 and n % 2 == 1),
        }
