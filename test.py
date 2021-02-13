from PyQt5.QtWidgets import QApplication, QWidget, QTableWidgetItem, QPushButton, QMessageBox
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
import sys


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ws_ui.ui', self)


app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
sys.exit(app.exec_())