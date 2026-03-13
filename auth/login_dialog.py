"""
Login / Register dialog shown at Casino startup.

The user can:
  • Log in with an existing account (PostgreSQL).
  • Register a new account.
  • Continue without an account (offline / JSON mode).

Signals
-------
After dialog.exec() is accepted:
    dialog.user_data   – dict {'id': int, 'username': str}  or  None  (offline)
    dialog.offline_mode – True when the user chose the offline path
"""

from __future__ import annotations

import logging
from typing import Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from .auth_manager import AuthManager
from .database import is_db_available

log = logging.getLogger(__name__)

# ── Dark-gold stylesheet consistent with the rest of the casino ───────────────
_STYLE = """
QDialog, QWidget {
    background-color: #0f172a;
    color: #e2e8f0;
    font-family: Arial;
}
QTabWidget::pane {
    border: 1px solid #334155;
    border-radius: 6px;
    background: #0f172a;
}
QTabBar::tab {
    background: #1e293b;
    color: #94a3b8;
    padding: 9px 22px;
    border: 1px solid #334155;
    border-bottom: none;
    border-radius: 4px 4px 0 0;
    font-size: 13px;
}
QTabBar::tab:selected {
    background: #0f172a;
    color: #FFD700;
    font-weight: bold;
}
QLineEdit {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 6px;
    padding: 8px 12px;
    color: #e2e8f0;
    font-size: 14px;
}
QLineEdit:focus {
    border: 1px solid #FFD700;
}
QLabel {
    color: #cbd5e1;
    font-size: 13px;
}
QPushButton {
    background: #1d4ed8;
    color: white;
    border: none;
    border-radius: 6px;
    padding: 10px 20px;
    font-size: 14px;
    font-weight: bold;
}
QPushButton:hover  { background: #2563eb; }
QPushButton:pressed { background: #1e40af; }
QPushButton#offline_btn {
    background: transparent;
    color: #64748b;
    border: 1px solid #334155;
    font-size: 12px;
    font-weight: normal;
    padding: 8px 16px;
}
QPushButton#offline_btn:hover { color: #94a3b8; border-color: #475569; }
"""


class LoginDialog(QDialog):
    """Modal dialog for authentication shown before MainUI is constructed."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.user_data: Optional[dict] = None
        self.offline_mode: bool = False
        self._auth = AuthManager()
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self) -> None:
        self.setWindowTitle("Casino – Acceso")
        self.setModal(True)
        self.setFixedSize(420, 540)
        self.setStyleSheet(_STYLE)
        # Prevent accidental close from destroying the parent app
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, True)

        root = QVBoxLayout(self)
        root.setSpacing(14)
        root.setContentsMargins(32, 28, 32, 28)

        # ── Title ─────────────────────────────────────────────────────────
        title = QLabel("🎰  Casino")
        title.setFont(QFont("Arial", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: #FFD700;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        # ── Database status indicator ──────────────────────────────────────
        self._status_label = QLabel()
        self._status_label.setTextFormat(Qt.TextFormat.RichText)
        self._status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._status_label.setStyleSheet("font-size: 12px; margin-bottom: 4px;")
        self._refresh_status()
        root.addWidget(self._status_label)

        # ── Tabs ──────────────────────────────────────────────────────────
        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_login_tab(), "Iniciar Sesión")
        self._tabs.addTab(self._build_register_tab(), "Registrarse")
        root.addWidget(self._tabs)

        # ── Divider ───────────────────────────────────────────────────────
        sep = QLabel("──────────── o ────────────")
        sep.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sep.setStyleSheet("color: #334155; font-size: 11px;")
        root.addWidget(sep)

        # ── Offline button ────────────────────────────────────────────────
        offline_btn = QPushButton("Continuar sin cuenta  (modo offline)")
        offline_btn.setObjectName("offline_btn")
        offline_btn.clicked.connect(self._continue_offline)
        root.addWidget(offline_btn)

    def _refresh_status(self) -> None:
        if is_db_available():
            self._status_label.setText(
                "<span style='color:#22c55e;'>● PostgreSQL conectado</span>"
            )
        else:
            self._status_label.setText(
                "<span style='color:#ef4444;'>● Sin conexión a BD"
                " – solo modo offline disponible</span>"
            )

    # ── Login tab ─────────────────────────────────────────────────────────

    def _build_login_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(10)
        lay.setContentsMargins(12, 20, 12, 12)

        lay.addWidget(QLabel("Usuario"))
        self._login_user = QLineEdit()
        self._login_user.setPlaceholderText("Tu nombre de usuario")
        lay.addWidget(self._login_user)

        lay.addWidget(QLabel("Contraseña"))
        self._login_pass = QLineEdit()
        self._login_pass.setPlaceholderText("Tu contraseña")
        self._login_pass.setEchoMode(QLineEdit.EchoMode.Password)
        lay.addWidget(self._login_pass)

        self._login_error = QLabel("")
        self._login_error.setStyleSheet("color: #f87171; font-size: 12px;")
        self._login_error.setWordWrap(True)
        lay.addWidget(self._login_error)

        lay.addStretch()

        login_btn = QPushButton("Entrar")
        login_btn.clicked.connect(self._do_login)
        self._login_pass.returnPressed.connect(self._do_login)
        lay.addWidget(login_btn)

        return w

    # ── Register tab ──────────────────────────────────────────────────────

    def _build_register_tab(self) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(8)
        lay.setContentsMargins(12, 14, 12, 12)

        lay.addWidget(QLabel("Usuario  *"))
        self._reg_user = QLineEdit()
        self._reg_user.setPlaceholderText("Mínimo 3 caracteres, sin espacios")
        lay.addWidget(self._reg_user)

        lay.addWidget(QLabel("Correo electrónico  (opcional)"))
        self._reg_email = QLineEdit()
        self._reg_email.setPlaceholderText("tu@email.com")
        lay.addWidget(self._reg_email)

        lay.addWidget(QLabel("Contraseña  *"))
        self._reg_pass = QLineEdit()
        self._reg_pass.setPlaceholderText("Mínimo 6 caracteres")
        self._reg_pass.setEchoMode(QLineEdit.EchoMode.Password)
        lay.addWidget(self._reg_pass)

        lay.addWidget(QLabel("Confirmar contraseña  *"))
        self._reg_confirm = QLineEdit()
        self._reg_confirm.setPlaceholderText("Repite la contraseña")
        self._reg_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        lay.addWidget(self._reg_confirm)

        self._reg_error = QLabel("")
        self._reg_error.setStyleSheet("color: #f87171; font-size: 12px;")
        self._reg_error.setWordWrap(True)
        lay.addWidget(self._reg_error)

        reg_btn = QPushButton("Crear cuenta")
        reg_btn.clicked.connect(self._do_register)
        self._reg_confirm.returnPressed.connect(self._do_register)
        lay.addWidget(reg_btn)

        return w

    # ── Slot handlers ─────────────────────────────────────────────────────

    def _do_login(self) -> None:
        username = self._login_user.text().strip()
        password = self._login_pass.text()

        if not username or not password:
            self._login_error.setText("Completa todos los campos.")
            return

        self._login_error.setText("Verificando…")
        QApplication.processEvents()

        user_data, msg = self._auth.login(username, password)
        if user_data is None:
            self._login_error.setText(msg)
        else:
            self.user_data = user_data
            self.accept()

    def _do_register(self) -> None:
        username = self._reg_user.text().strip()
        email = self._reg_email.text().strip()
        password = self._reg_pass.text()
        confirm = self._reg_confirm.text()

        ok, msg = self._auth.register(username, password, email, confirm)
        if not ok:
            self._reg_error.setStyleSheet("color: #f87171; font-size: 12px;")
            self._reg_error.setText(msg)
            return

        # Auto-login immediately after successful registration
        user_data, login_msg = self._auth.login(username, password)
        if user_data:
            self.user_data = user_data
            self.accept()
        else:
            # Registration succeeded but auto-login failed; ask user to log in manually
            self._reg_error.setStyleSheet("color: #4ade80; font-size: 12px;")
            self._reg_error.setText(f"{msg}  Por favor inicia sesión.")
            self._tabs.setCurrentIndex(0)
            self._login_user.setText(username)

    def _continue_offline(self) -> None:
        self.user_data = None
        self.offline_mode = True
        self.accept()

    # ── Close guard ───────────────────────────────────────────────────────

    def closeEvent(self, event) -> None:  # type: ignore[override]
        """Ask for confirmation before closing without choosing an option."""
        reply = QMessageBox.question(
            self,
            "¿Salir?",
            "¿Deseas salir del casino?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.reject()
            event.accept()
        else:
            event.ignore()
