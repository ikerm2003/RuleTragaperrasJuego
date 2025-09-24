from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Iterable, List, Sequence, Tuple

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QLabel,
    QFrame,
    QGridLayout,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QSizePolicy,
)


class BaseFourPlayerTable(QMainWindow, ABC):
    """Ventana base para mesas de cartas con 4 jugadores.

    Proporciona utilidades de escalado responsivo y la estructura grid
    estándar con posiciones predeterminadas para cuatro jugadores.
    Las subclases solo deben implementar los widgets específicos
    (info bar, cartas comunitarias, panel de acciones, etc.).
    """

    PLAYER_POSITIONS: Sequence[Tuple[int, int, str]] = (
        (3, 1, "bottom"),
        (2, 0, "left"),
        (1, 1, "top"),
        (2, 2, "right"),
    )

    def __init__(self, *, base_width: int = 1400, base_height: int = 900) -> None:
        super().__init__()
        self.base_width = base_width
        self.base_height = base_height
        self.current_scale = 1.0

        self.community_card_labels: List[QLabel] = []
        self.player_displays: List[QFrame] = []
        self.action_buttons: List[QPushButton] = []

        self._central_widget = QWidget()
        self.setCentralWidget(self._central_widget)
        self.main_layout = QVBoxLayout(self._central_widget)
        self.configure_main_layout()

        self.table_frame: QFrame | None = None
        self.table_layout: QGridLayout | None = None

    def configure_main_layout(
        self,
        spacing: int = 15,
        margins: Tuple[int, int, int, int] = (20, 20, 20, 20),
    ) -> None:
        """Configura separación y márgenes del layout principal."""
        self.main_layout.setSpacing(spacing)
        self.main_layout.setContentsMargins(*margins)

    def create_table_frame(
        self,
        *,
        min_height: int = 550,
        spacing: int = 20,
        margins: Tuple[int, int, int, int] = (40, 40, 40, 40),
    ) -> QFrame:
        """Crea el contenedor principal de la mesa y guarda su layout."""
        table = QFrame()
        table.setMinimumHeight(min_height)
        table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        layout = QGridLayout(table)
        layout.setSpacing(spacing)
        layout.setContentsMargins(*margins)

        self.table_frame = table
        self.table_layout = layout
        return table

    def populate_player_positions(self) -> None:
        """Crea y posiciona los paneles de jugador en la mesa."""
        if self.table_layout is None:
            raise RuntimeError("create_table_frame debe llamarse antes de populate_player_positions")

        # Limpiamos referencias anteriores para evitar duplicados.
        self.player_displays.clear()

        for index, (row, column, position) in enumerate(self.get_player_positions()):
            player_widget = self.create_player_display(index, position)
            self.player_displays.append(player_widget)
            self.table_layout.addWidget(player_widget, row, column, Qt.AlignmentFlag.AlignCenter)

    def get_player_positions(self) -> Iterable[Tuple[int, int, str]]:
        """Devuelve la distribución de jugadores; puede personalizarse en subclases."""
        return self.PLAYER_POSITIONS

    def register_action_buttons(self, *buttons: QPushButton) -> None:
        """Registra botones de acción para poder escalarlos posteriormente."""
        self.action_buttons.extend(buttons)

    # --- Escalado responsivo -------------------------------------------------
    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        new_scale = self.get_scale_factor()
        if abs(new_scale - self.current_scale) > 0.05:
            self.current_scale = new_scale
            self.update_ui_scaling()

    def get_scale_factor(self) -> float:
        """Calcula el factor de escala actual en función del tamaño de ventana."""
        current_size = self.size()
        width_scale = current_size.width() / self.base_width if self.base_width else 1.0
        height_scale = current_size.height() / self.base_height if self.base_height else 1.0
        return max(0.65, min(width_scale, height_scale, 2.0))

    def get_scaled_size(self, base_size: int) -> int:
        """Devuelve un tamaño escalado respetando el factor actual."""
        scale = self.get_scale_factor()
        return max(1, int(base_size * scale))

    def get_scaled_font(self, base_size: int, weight: QFont.Weight = QFont.Weight.Normal) -> QFont:
        """Devuelve una fuente escalada con un tamaño mínimo razonable."""
        scale = self.get_scale_factor()
        scaled_size = max(10, int(base_size * scale))
        return QFont("Arial", scaled_size, weight)

    # --- Métodos que deben definir las subclases ----------------------------
    @abstractmethod
    def create_player_display(self, player_index: int, position: str) -> QFrame:
        """Crea el widget correspondiente a un jugador."""

    @abstractmethod
    def update_ui_scaling(self) -> None:
        """Actualiza tamaños y fuentes cada vez que cambia el factor de escala."""
        