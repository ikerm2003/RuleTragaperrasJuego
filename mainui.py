from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget, QMessageBox
import sys

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Casino de tu mama")
        self.setGeometry(100, 100, 600, 400)
        
        

