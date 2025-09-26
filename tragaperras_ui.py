from PyQt6.QtGui import QAction
"""
UI components for the slot machine game using PyQt6
"""
from PyQt6.QtWidgets import QMainWindow, QMenuBar, QMenu
from PyQt6.QtCore import Qt

from config_manager import ConfigManager
from localization import get_text

class SlotMachineUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Tragaperras")
        self.setGeometry(100, 100, 800, 600)
        
        # Menu Bar
        menubar: QMenuBar = self.menuBar()
        
        # Game menu
        game_menu: QMenu = menubar.addMenu(get_text('game'))
        
        new_game_action: QAction = game_menu.addAction(get_text('new_game'))
        new_game_action.triggered.connect(self.start_new_game)
        
        game_menu.addSeparator()
        
        exit_action: QAction = game_menu.addAction(get_text('exit'))
        exit_action.triggered.connect(self.close)
        
        self.setMenuBar(menubar)
        

