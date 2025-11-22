"""
Configuration dialog for the Casino game.
Provides UI for adjusting game settings.
"""
from typing import Optional, Dict, Any, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,
    QCheckBox, QComboBox, QSlider, QPushButton, QLabel, QSpacerItem,
    QSizePolicy, QMessageBox, QTabWidget, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from .config import (
    ConfigManager, Language, Resolution, AnimationSpeed, 
    get_text, config_manager
)


class ConfigDialog(QDialog):
    """Configuration dialog for game settings"""
    
    # Signal emitted when configuration changes are applied
    config_changed = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = config_manager
        self.temp_config = {}  # Temporary config changes
        
        self.setWindowTitle(get_text('settings'))
        self.setModal(True)
        self.setFixedSize(500, 600)
        
        self.init_ui()
        self.load_current_settings()
    
    def init_ui(self):
        """Initialize the dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Display settings tab
        display_tab = self.create_display_tab()
        tab_widget.addTab(display_tab, get_text('display', Language.ENGLISH) if get_text('display') == 'display' else "Pantalla")
        
        # Interface settings tab
        interface_tab = self.create_interface_tab()
        tab_widget.addTab(interface_tab, get_text('interface', Language.ENGLISH) if get_text('interface') == 'interface' else "Interfaz")
        
        # Gameplay settings tab
        gameplay_tab = self.create_gameplay_tab()
        tab_widget.addTab(gameplay_tab, "Juego")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = self.create_button_layout()
        layout.addLayout(button_layout)
    
    def create_display_tab(self) -> QWidget:
        """Create display settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Display group
        display_group = QGroupBox("Configuración de pantalla")
        display_layout = QGridLayout(display_group)
        
        # Fullscreen checkbox
        self.fullscreen_check = QCheckBox(get_text('fullscreen'))
        display_layout.addWidget(QLabel(get_text('fullscreen') + ":"), 0, 0)
        display_layout.addWidget(self.fullscreen_check, 0, 1)
        
        # Resolution combo
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItem("Automática", Resolution.AUTO.value)
        self.resolution_combo.addItem("HD (1280x720)", Resolution.HD.value)
        self.resolution_combo.addItem("Full HD (1920x1080)", Resolution.FULL_HD.value)
        self.resolution_combo.addItem("Ultra HD (2560x1440)", Resolution.ULTRA_HD.value)
        
        display_layout.addWidget(QLabel(get_text('resolution') + ":"), 1, 0)
        display_layout.addWidget(self.resolution_combo, 1, 1)
        
        # VSync checkbox
        self.vsync_check = QCheckBox("VSync")
        display_layout.addWidget(QLabel("VSync:"), 2, 0)
        display_layout.addWidget(self.vsync_check, 2, 1)
        
        layout.addWidget(display_group)
        layout.addStretch()
        
        return tab
    
    def create_interface_tab(self) -> QWidget:
        """Create interface settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Language group
        language_group = QGroupBox("Idioma")
        language_layout = QGridLayout(language_group)
        
        self.language_combo = QComboBox()
        self.language_combo.addItem("Español", Language.SPANISH.value)
        self.language_combo.addItem("English", Language.ENGLISH.value)
        self.language_combo.currentTextChanged.connect(self.on_language_changed)
        
        language_layout.addWidget(QLabel(get_text('language') + ":"), 0, 0)
        language_layout.addWidget(self.language_combo, 0, 1)
        
        layout.addWidget(language_group)
        
        # Animation group
        animation_group = QGroupBox("Animaciones")
        animation_layout = QGridLayout(animation_group)
        
        # Enable animations checkbox
        self.animations_check = QCheckBox(get_text('enable_animations'))
        animation_layout.addWidget(self.animations_check, 0, 0, 1, 2)
        
        # Animation speed
        self.speed_combo = QComboBox()
        self.speed_combo.addItem(get_text('disabled'), AnimationSpeed.DISABLED.value)
        self.speed_combo.addItem(get_text('slow'), AnimationSpeed.SLOW.value)
        self.speed_combo.addItem(get_text('normal'), AnimationSpeed.NORMAL.value)
        self.speed_combo.addItem(get_text('fast'), AnimationSpeed.FAST.value)
        
        animation_layout.addWidget(QLabel(get_text('animation_speed') + ":"), 1, 0)
        animation_layout.addWidget(self.speed_combo, 1, 1)
        
        # Connect animations checkbox to speed combo
        self.animations_check.toggled.connect(
            lambda enabled: self.speed_combo.setEnabled(enabled)
        )
        
        layout.addWidget(animation_group)
        
        # Other interface options
        other_group = QGroupBox("Otros")
        other_layout = QGridLayout(other_group)
        
        self.tooltips_check = QCheckBox("Mostrar tooltips")
        self.sound_check = QCheckBox(get_text('sound'))
        
        other_layout.addWidget(self.tooltips_check, 0, 0)
        other_layout.addWidget(self.sound_check, 1, 0)
        
        layout.addWidget(other_group)
        layout.addStretch()
        
        return tab
    
    def create_gameplay_tab(self) -> QWidget:
        """Create gameplay settings tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Gameplay group
        gameplay_group = QGroupBox("Configuración de juego")
        gameplay_layout = QGridLayout(gameplay_group)
        
        # Auto-fold timeout
        self.timeout_slider = QSlider(Qt.Orientation.Horizontal)
        self.timeout_slider.setRange(10, 120)
        self.timeout_slider.setValue(30)
        self.timeout_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.timeout_slider.setTickInterval(10)
        
        self.timeout_label = QLabel("30 segundos")
        self.timeout_slider.valueChanged.connect(
            lambda value: self.timeout_label.setText(f"{value} segundos")
        )
        
        gameplay_layout.addWidget(QLabel("Timeout para retirarse automáticamente:"), 0, 0)
        gameplay_layout.addWidget(self.timeout_slider, 1, 0)
        gameplay_layout.addWidget(self.timeout_label, 1, 1)
        
        # Confirm actions
        self.confirm_actions_check = QCheckBox("Confirmar acciones importantes")
        gameplay_layout.addWidget(self.confirm_actions_check, 2, 0, 1, 2)
        
        # Probability hints
        self.probability_hints_check = QCheckBox("Mostrar pistas de probabilidad")
        gameplay_layout.addWidget(self.probability_hints_check, 3, 0, 1, 2)
        
        layout.addWidget(gameplay_group)
        layout.addStretch()
        
        return tab
    
    def create_button_layout(self) -> QHBoxLayout:
        """Create button layout"""
        button_layout = QHBoxLayout()
        
        # Reset button
        reset_button = QPushButton(get_text('reset_defaults'))
        reset_button.clicked.connect(self.reset_to_defaults)
        
        # Cancel button
        cancel_button = QPushButton(get_text('cancel'))
        cancel_button.clicked.connect(self.reject)
        
        # Apply button
        apply_button = QPushButton(get_text('apply'))
        apply_button.clicked.connect(self.apply_settings)
        apply_button.setDefault(True)
        
        button_layout.addWidget(reset_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(apply_button)
        
        return button_layout
    
    def load_current_settings(self):
        """Load current settings into UI controls"""
        # Display settings
        self.fullscreen_check.setChecked(self.config.is_fullscreen())
        
        resolution = self.config.get_resolution()
        for i in range(self.resolution_combo.count()):
            if self.resolution_combo.itemData(i) == resolution:
                self.resolution_combo.setCurrentIndex(i)
                break
        
        self.vsync_check.setChecked(self.config.get('display', 'vsync', True))
        
        # Interface settings
        language = self.config.get_language()
        for i in range(self.language_combo.count()):
            if self.language_combo.itemData(i) == language.value:
                self.language_combo.setCurrentIndex(i)
                break
        
        self.animations_check.setChecked(self.config.are_animations_enabled())
        
        speed = self.config.get_animation_speed()
        for i in range(self.speed_combo.count()):
            if abs(self.speed_combo.itemData(i) - speed) < 0.1:
                self.speed_combo.setCurrentIndex(i)
                break
        
        self.speed_combo.setEnabled(self.animations_check.isChecked())
        
        self.tooltips_check.setChecked(self.config.get('interface', 'show_tooltips', True))
        self.sound_check.setChecked(self.config.get('interface', 'sound_enabled', True))
        
        # Gameplay settings
        timeout = self.config.get('gameplay', 'auto_fold_timeout', 30)
        self.timeout_slider.setValue(timeout)
        self.timeout_label.setText(f"{timeout} segundos")
        
        self.confirm_actions_check.setChecked(self.config.get('gameplay', 'confirm_actions', True))
        self.probability_hints_check.setChecked(self.config.get('gameplay', 'show_probability_hints', False))
    
    def on_language_changed(self):
        """Handle language change"""
        # Update dialog text immediately
        selected_lang_code = self.language_combo.currentData()
        if selected_lang_code:
            # This is a preview - actual change happens on apply
            pass
    
    def collect_settings(self) -> Dict[str, Any]:
        """Collect all settings from UI controls"""
        return {
            'display': {
                'fullscreen': self.fullscreen_check.isChecked(),
                'resolution': self.resolution_combo.currentData(),
                'vsync': self.vsync_check.isChecked(),
            },
            'interface': {
                'language': self.language_combo.currentData(),
                'animation_speed': self.speed_combo.currentData() if self.animations_check.isChecked() else 0.0,
                'card_animation_enabled': self.animations_check.isChecked(),
                'show_tooltips': self.tooltips_check.isChecked(),
                'sound_enabled': self.sound_check.isChecked(),
            },
            'gameplay': {
                'auto_fold_timeout': self.timeout_slider.value(),
                'confirm_actions': self.confirm_actions_check.isChecked(),
                'show_probability_hints': self.probability_hints_check.isChecked(),
            }
        }
    
    def apply_settings(self):
        """Apply the current settings"""
        settings = self.collect_settings()
        
        # Update config
        for section, values in settings.items():
            for key, value in values.items():
                self.config.set(section, key, value)
        
        # Save to file
        if self.config.save_config():
            self.config_changed.emit()
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "No se pudo guardar la configuración.")
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        reply = QMessageBox.question(
            self, 
            "Confirmar", 
            "¿Está seguro de que desea restaurar todos los valores predeterminados?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.config.reset_to_defaults()
            self.load_current_settings()