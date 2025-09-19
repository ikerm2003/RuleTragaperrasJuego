from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QLineEdit, QVBoxLayout, QWidget, QMessageBox
import sys

class MainUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple PyQt6 App")
        self.setGeometry(100, 100, 400, 200)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        
        self.label = QLabel("Enter your name:")
        self.layout.addWidget(self.label)
        
        self.textbox = QLineEdit(self)
        self.layout.addWidget(self.textbox)
        
        self.button = QPushButton("Greet Me", self)
        self.button.clicked.connect(self.greet_user)
        self.layout.addWidget(self.button)
        
        self.central_widget.setLayout(self.layout)

    def greet_user(self):
        name = self.textbox.text()
        if name:
            QMessageBox.information(self, "Greeting", f"Hello, {name}!")
        else:
            QMessageBox.warning(self, "Input Error", "Please enter your name.")