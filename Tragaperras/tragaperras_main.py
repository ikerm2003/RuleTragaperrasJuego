"""Punto de entrada para la aplicación de tragaperras."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Tuple, cast

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication


ROOT_DIR = Path(__file__).resolve().parents[1]
TRAGAPERRAS_DIR = ROOT_DIR / "Tragaperras"

for path in (ROOT_DIR, TRAGAPERRAS_DIR):
	str_path = str(path)
	if str_path not in sys.path:
		sys.path.insert(0, str_path)

if __package__:
	from .tragaperras_ui import SlotMachineWindow  # type: ignore
else:  # pragma: no cover - ejecución directa
	from Tragaperras.tragaperras_ui import SlotMachineWindow  # type: ignore


def create_slot_application() -> QApplication:
	"""Crea un :class:`QApplication` específico para la tragaperras."""

	app = QApplication(sys.argv)
	app.setApplicationName("RuleTragaperrasJuego - Slots")
	app.setApplicationVersion("1.0")
	app.setOrganizationName("RuleTragaperrasJuego")
	return app


def ensure_slot_application() -> Tuple[QApplication, bool]:
	"""Garantiza que exista una aplicación Qt y devuelve si es propia."""

	existing = QApplication.instance()
	if existing is not None:
		return cast(QApplication, existing), False
	return create_slot_application(), True


def _center_window_on_screen(window: SlotMachineWindow, app: QApplication) -> None:
	screen = app.primaryScreen()
	if screen is None:
		return
	geometry = screen.availableGeometry()
	window.move(
		(geometry.width() - window.width()) // 2,
		(geometry.height() - window.height()) // 2,
	)


def open_slot_window(
	*,
	parent=None,
	show_immediately: bool = True,
) -> Tuple[SlotMachineWindow, bool, QApplication]:
	"""Crea la ventana de tragaperras reutilizando la app existente si procede."""

	app, owns_app = ensure_slot_application()
	window = SlotMachineWindow(parent=parent)
	window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

	if show_immediately:
		window.show()
		_center_window_on_screen(window, app)

	return window, owns_app, app


def main() -> int:
	"""Función principal del módulo de tragaperras."""

	try:
		_, owns_app, app = open_slot_window()
		if owns_app:
			return app.exec()
		return 0
	except Exception as exc:  # pragma: no cover - registro defensivo
		print(f"Error al crear la ventana de tragaperras: {exc}")
		return 1


if __name__ == "__main__":
	sys.exit(main())

