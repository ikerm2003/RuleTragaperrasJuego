"""Interfaz de usuario para el juego de la Ruleta.

Implementa la UI completa con:
* Mesa de ruleta con números y diseño europeo
* Controles de apuestas
* Animación del giro
* Visualización de resultados
* Historial de números
"""

import math
import sys
from pathlib import Path
from typing import Optional

from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QPainter, QPalette, QPen
from PyQt6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

# Add parent directory to path for imports
parent_dir = Path(__file__).resolve().parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from Ruleta.ruleta_logic import BLACK_NUMBERS, RED_NUMBERS, BetType, RouletteGame


class RouletteWheel(QWidget):
    """Widget que muestra la ruleta giratoria"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(300, 300)
        self.rotation = 0
        self.spinning = False
        self.target_rotation = 0
        self.winning_number: Optional[int] = None

        # Timer para animación
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_spin)

    def spin_to_number(self, number: int):
        """Inicia la animación de giro hacia un número"""
        self.winning_number = number
        self.spinning = True

        # Calcular rotación objetivo (múltiples vueltas + posición final)
        rotations = 5  # 5 vueltas completas
        angle_per_number = 360 / 37  # 37 números (0-36)
        target_angle = number * angle_per_number
        self.target_rotation = int(self.rotation + (rotations * 360) + target_angle)

        self.timer.start(20)  # 50 FPS

    def animate_spin(self):
        """Anima el giro de la ruleta"""
        if self.spinning:
            diff = self.target_rotation - self.rotation

            if abs(diff) < 2:
                self.rotation = self.target_rotation
                self.spinning = False
                self.timer.stop()
            else:
                # Desaceleración suave
                self.rotation += int(diff * 0.05)

            self.update()

    def paintEvent(self, a0):
        """Dibuja la ruleta"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Centro del widget
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(center_x, center_y) - 10

        # Dibujar fondo
        painter.setBrush(QBrush(QColor("#1a1a1a")))
        painter.setPen(QPen(QColor("#FFD700"), 3))
        painter.drawEllipse(QPointF(center_x, center_y), radius, radius)

        # Dibujar sectores
        angle_per_number = 360 / 37

        # Orden de números en la ruleta europea
        wheel_numbers = [
            0,
            32,
            15,
            19,
            4,
            21,
            2,
            25,
            17,
            34,
            6,
            27,
            13,
            36,
            11,
            30,
            8,
            23,
            10,
            5,
            24,
            16,
            33,
            1,
            20,
            14,
            31,
            9,
            22,
            18,
            29,
            7,
            28,
            12,
            35,
            3,
            26,
        ]

        painter.save()
        painter.translate(center_x, center_y)
        painter.rotate(self.rotation)

        for i, number in enumerate(wheel_numbers):
            start_angle = i * angle_per_number

            # Color del sector
            if number == 0:
                color = QColor("#006400")
            elif number in RED_NUMBERS:
                color = QColor("#8B0000")
            else:
                color = QColor("#000000")

            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("#FFD700"), 1))
            painter.drawPie(
                QRectF(-radius, -radius, radius * 2, radius * 2),
                int(start_angle * 16),
                int(angle_per_number * 16),
            )

        painter.restore()

        # Dibujar indicador
        painter.setPen(QPen(QColor("#FFD700"), 4))
        painter.drawLine(center_x, 10, center_x, 30)


class RouletteTable(QWidget):
    """Widget que muestra la mesa de apuestas"""

    number_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz de la mesa"""
        layout = QGridLayout(self)
        layout.setSpacing(2)

        # Crear botones para cada número (0-36)
        # Fila del 0
        zero_btn = self.create_number_button(0, "green")
        layout.addWidget(zero_btn, 0, 0, 3, 1)

        # Números 1-36 en 3 filas
        for num in range(1, 37):
            row = 3 - ((num - 1) % 3 + 1)  # Fila invertida (3 arriba, 1 abajo)
            col = (num - 1) // 3 + 1

            color = "red" if num in RED_NUMBERS else "black"
            btn = self.create_number_button(num, color)
            layout.addWidget(btn, row, col)

        # Apuestas externas
        # Columnas
        for i in range(3):
            col_btn = self.create_special_button(f"Columna {i+1}", f"column_{i+1}")
            layout.addWidget(col_btn, i, 13)

        # Docenas y otras apuestas externas
        dozen_row = 3
        self.dozen1_btn = self.create_special_button("1-12", "dozen_1")
        self.dozen2_btn = self.create_special_button("13-24", "dozen_2")
        self.dozen3_btn = self.create_special_button("25-36", "dozen_3")
        layout.addWidget(self.dozen1_btn, dozen_row, 1, 1, 4)
        layout.addWidget(self.dozen2_btn, dozen_row, 5, 1, 4)
        layout.addWidget(self.dozen3_btn, dozen_row, 9, 1, 4)

        # Apuestas simples
        simple_row = 4
        self.low_btn = self.create_special_button("1-18", "low")
        self.even_btn = self.create_special_button("Par", "even")
        self.red_btn = self.create_special_button("Rojo", "red")
        self.black_btn = self.create_special_button("Negro", "black")
        self.odd_btn = self.create_special_button("Impar", "odd")
        self.high_btn = self.create_special_button("19-36", "high")

        layout.addWidget(self.low_btn, simple_row, 1, 1, 2)
        layout.addWidget(self.even_btn, simple_row, 3, 1, 2)
        layout.addWidget(self.red_btn, simple_row, 5, 1, 2)
        layout.addWidget(self.black_btn, simple_row, 7, 1, 2)
        layout.addWidget(self.odd_btn, simple_row, 9, 1, 2)
        layout.addWidget(self.high_btn, simple_row, 11, 1, 2)

    def create_number_button(self, number: int, color: str) -> QPushButton:
        """Crea un botón para un número de la ruleta"""
        btn = QPushButton(str(number))
        btn.setFixedSize(40, 40)
        btn.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        # Estilos según color
        if color == "red":
            bg_color = "#DC2626"
        elif color == "black":
            bg_color = "#1F2937"
        else:  # green
            bg_color = "#059669"

        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: 2px solid #FCD34D;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {bg_color};
                border: 3px solid #FBBF24;
            }}
        """
        )

        btn.clicked.connect(lambda: self.number_clicked.emit(number))
        return btn

    def create_special_button(self, text: str, bet_id: str) -> QPushButton:
        """Crea un botón para apuestas especiales"""
        btn = QPushButton(text)
        btn.setMinimumHeight(35)
        btn.setFont(QFont("Arial", 9, QFont.Weight.Bold))

        # Color según tipo de apuesta
        if "red" in text.lower() or "rojo" in text.lower():
            bg_color = "#DC2626"
        elif "black" in text.lower() or "negro" in text.lower():
            bg_color = "#1F2937"
        else:
            bg_color = "#1E40AF"

        btn.setStyleSheet(
            f"""
            QPushButton {{
                background-color: {bg_color};
                color: white;
                border: 2px solid #FCD34D;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {bg_color};
                border: 3px solid #FBBF24;
            }}
        """
        )

        btn.setProperty("bet_id", bet_id)
        return btn


class RouletteWindow(QMainWindow):
    """Ventana principal del juego de ruleta"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.game = RouletteGame(initial_balance=1000)
        self.parent_window = parent
        self.current_chip_value = 10
        self.init_ui()

    def init_ui(self):
        """Inicializa la interfaz"""
        self.setWindowTitle("Ruleta Europea - Casino")
        self.setGeometry(100, 100, 1200, 800)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)

        # Header con balance
        header_layout = QHBoxLayout()
        self.balance_label = QLabel(f"Balance: ${self.game.balance}")
        self.balance_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.balance_label.setStyleSheet("color: #FFD700;")

        self.bet_total_label = QLabel("Total Apostado: $0")
        self.bet_total_label.setFont(QFont("Arial", 14))
        self.bet_total_label.setStyleSheet("color: white;")

        header_layout.addWidget(self.balance_label)
        header_layout.addStretch()
        header_layout.addWidget(self.bet_total_label)
        main_layout.addLayout(header_layout)

        # Layout principal con ruleta y mesa
        game_layout = QHBoxLayout()

        # Panel izquierdo con ruleta y controles
        left_panel = QVBoxLayout()

        self.wheel = RouletteWheel()
        left_panel.addWidget(self.wheel)

        # Resultado
        self.result_label = QLabel("¡Haz tus apuestas!")
        self.result_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setStyleSheet(
            """
            padding: 15px;
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            border-radius: 8px;
        """
        )
        left_panel.addWidget(self.result_label)

        # Historial
        history_label = QLabel("Historial:")
        history_label.setFont(QFont("Arial", 12))
        left_panel.addWidget(history_label)

        self.history_label = QLabel("No hay historial aún")
        self.history_label.setWordWrap(True)
        self.history_label.setFont(QFont("Arial", 10))
        self.history_label.setStyleSheet(
            "background-color: rgba(0, 0, 0, 0.5); padding: 10px; border-radius: 5px;"
        )
        left_panel.addWidget(self.history_label)

        game_layout.addLayout(left_panel, 1)

        # Panel derecho con mesa de apuestas
        right_panel = QVBoxLayout()

        # Controles de fichas
        chip_layout = QHBoxLayout()
        chip_label = QLabel("Valor de ficha:")
        chip_label.setFont(QFont("Arial", 12))

        self.chip_spinbox = QSpinBox()
        self.chip_spinbox.setMinimum(1)
        self.chip_spinbox.setMaximum(100)
        self.chip_spinbox.setValue(10)
        self.chip_spinbox.setSingleStep(5)
        self.chip_spinbox.setPrefix("$")
        self.chip_spinbox.valueChanged.connect(self.update_chip_value)

        chip_layout.addWidget(chip_label)
        chip_layout.addWidget(self.chip_spinbox)
        chip_layout.addStretch()
        right_panel.addLayout(chip_layout)

        # Mesa de apuestas en scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.table = RouletteTable()
        self.table.number_clicked.connect(self.place_number_bet)

        # Conectar botones especiales
        self.connect_special_buttons()

        scroll.setWidget(self.table)
        right_panel.addWidget(scroll)

        game_layout.addLayout(right_panel, 2)
        main_layout.addLayout(game_layout)

        # Botones de acción
        action_layout = QHBoxLayout()

        self.spin_button = QPushButton("GIRAR")
        self.spin_button.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.spin_button.setMinimumHeight(50)
        self.spin_button.setStyleSheet(
            """
            QPushButton {
                background-color: #059669;
                color: white;
                border: 3px solid #10B981;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #10B981;
            }
            QPushButton:disabled {
                background-color: #6B7280;
            }
        """
        )
        self.spin_button.clicked.connect(self.spin_wheel)

        clear_button = QPushButton("Limpiar Apuestas")
        clear_button.setFont(QFont("Arial", 12))
        clear_button.clicked.connect(self.clear_bets)

        back_button = QPushButton("Volver al Menú")
        back_button.setFont(QFont("Arial", 12))
        back_button.clicked.connect(self.close)

        action_layout.addWidget(clear_button)
        action_layout.addWidget(self.spin_button)
        action_layout.addWidget(back_button)
        main_layout.addLayout(action_layout)

        # Estilo de fondo
        self.setStyleSheet(
            """
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                           stop:0 rgba(21, 101, 52, 1),
                           stop:1 rgba(5, 46, 22, 1));
            }
        """
        )

    def connect_special_buttons(self):
        """Conecta los botones de apuestas especiales"""
        # Docenas
        self.table.dozen1_btn.clicked.connect(lambda: self.place_dozen_bet(1))
        self.table.dozen2_btn.clicked.connect(lambda: self.place_dozen_bet(2))
        self.table.dozen3_btn.clicked.connect(lambda: self.place_dozen_bet(3))

        # Apuestas simples
        self.table.low_btn.clicked.connect(lambda: self.place_simple_bet("low"))
        self.table.high_btn.clicked.connect(lambda: self.place_simple_bet("high"))
        self.table.even_btn.clicked.connect(lambda: self.place_simple_bet("even"))
        self.table.odd_btn.clicked.connect(lambda: self.place_simple_bet("odd"))
        self.table.red_btn.clicked.connect(lambda: self.place_simple_bet("red"))
        self.table.black_btn.clicked.connect(lambda: self.place_simple_bet("black"))

    def update_chip_value(self, value: int):
        """Actualiza el valor de la ficha actual"""
        self.current_chip_value = value

    def place_number_bet(self, number: int):
        """Coloca una apuesta a un número específico"""
        bet = self.game.create_straight_up_bet(number, self.current_chip_value)
        if bet and self.game.place_bet(bet):
            self.update_display()
            self.result_label.setText(
                f"Apuesta ${self.current_chip_value} al número {number}"
            )
        else:
            QMessageBox.warning(self, "Error", "No puedes colocar esta apuesta.")

    def place_dozen_bet(self, dozen: int):
        """Coloca una apuesta a una docena"""
        bet = self.game.create_dozen_bet(dozen, self.current_chip_value)
        if bet and self.game.place_bet(bet):
            self.update_display()
            ranges = {1: "1-12", 2: "13-24", 3: "25-36"}
            self.result_label.setText(
                f"Apuesta ${self.current_chip_value} a docena {ranges[dozen]}"
            )
        else:
            QMessageBox.warning(self, "Error", "No puedes colocar esta apuesta.")

    def place_simple_bet(self, bet_type: str):
        """Coloca una apuesta simple"""
        bet = None
        desc = ""

        if bet_type == "red":
            bet = self.game.create_color_bet("red", self.current_chip_value)
            desc = "Rojo"
        elif bet_type == "black":
            bet = self.game.create_color_bet("black", self.current_chip_value)
            desc = "Negro"
        elif bet_type == "even":
            bet = self.game.create_even_odd_bet(True, self.current_chip_value)
            desc = "Par"
        elif bet_type == "odd":
            bet = self.game.create_even_odd_bet(False, self.current_chip_value)
            desc = "Impar"
        elif bet_type == "low":
            bet = self.game.create_high_low_bet(False, self.current_chip_value)
            desc = "1-18"
        elif bet_type == "high":
            bet = self.game.create_high_low_bet(True, self.current_chip_value)
            desc = "19-36"

        if bet and self.game.place_bet(bet):
            self.update_display()
            self.result_label.setText(f"Apuesta ${self.current_chip_value} a {desc}")
        else:
            QMessageBox.warning(self, "Error", "No puedes colocar esta apuesta.")

    def clear_bets(self):
        """Limpia todas las apuestas"""
        self.game.clear_bets()
        self.update_display()
        self.result_label.setText("Apuestas limpiadas. ¡Haz tus apuestas!")

    def spin_wheel(self):
        """Gira la ruleta"""
        if not self.game.bets:
            QMessageBox.warning(self, "Error", "Debes hacer al menos una apuesta.")
            return

        self.spin_button.setEnabled(False)
        self.result_label.setText("¡Girando la ruleta!")

        # Girar la ruleta
        winning_number, total_winnings = self.game.spin()

        # Animar el giro
        self.wheel.spin_to_number(winning_number)

        # Mostrar resultado después de la animación
        QTimer.singleShot(
            3000, lambda: self.show_result(winning_number, total_winnings)
        )

    def show_result(self, winning_number: int, total_winnings: int):
        """Muestra el resultado del giro"""
        color = self.game.get_number_color(winning_number)
        color_text = {"red": "ROJO", "black": "NEGRO", "green": "VERDE"}[color]

        if total_winnings > 0:
            result_text = (
                f"¡Ganó el {winning_number} {color_text}!\n¡Ganaste ${total_winnings}!"
            )
        else:
            result_text = (
                f"Ganó el {winning_number} {color_text}.\nPerdiste esta ronda."
            )

        self.result_label.setText(result_text)
        self.update_display()
        self.spin_button.setEnabled(True)

    def update_display(self):
        """Actualiza la visualización de balance y apuestas"""
        self.balance_label.setText(f"Balance: ${self.game.balance}")
        total_bet = self.game.get_total_bet()
        self.bet_total_label.setText(f"Total Apostado: ${total_bet}")

        # Actualizar historial
        if self.game.history:
            history_text = "Últimos números: " + " - ".join(
                f"{n}" for n in reversed(self.game.history[-10:])
            )
            self.history_label.setText(history_text)

    def closeEvent(self, a0):
        """Maneja el cierre de la ventana"""
        if self.parent_window:
            self.parent_window.show()
        a0.accept()
