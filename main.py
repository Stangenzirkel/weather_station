from PyQt5.QtWidgets import QApplication, QWidget, QTableWidgetItem, QPushButton, QMessageBox
from PyQt5.QtChart import QChart, QChartView, QValueAxis,\
    QLineSeries
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5 import uic
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QTimer
import sys
from measure_temperature import *


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ws_ui.ui', self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.quitButton.clicked.connect(self.quit)
        self.temps = []
        self.create_linechart()
        self.make_measure()

        self.timer = QTimer(self)
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.make_measure)
        self.timer.start()

        self.temp_sensor = sensor

    def quit(self):
        self.destroy()
        quit()

    def make_measure(self):
        self.temps.append(temp(self.temp_sensor))
        self.update_linechart()

    def create_linechart(self):
        self.series = QLineSeries()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        # self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.axisValue = QValueAxis()
        self.axisTime = QValueAxis()

        self.chart.legend().hide()

        self.chartview = QChartView(self.chart, self.groupBox)
        self.chartview.resize(780, 420)
        self.chartview.move(0, 0)
        self.chartview.setRenderHint(QPainter.Antialiasing)

    def update_linechart(self):
        self.chart.removeAxis(self.axisTime)
        self.chart.removeAxis(self.axisValue)
        self.chart.removeSeries(self.series)

        self.series.clear()

        for i, res in enumerate(self.temps):
            self.series.append(i, res)

        self.chart.addSeries(self.series)
        self.chart.addAxis(self.axisTime, Qt.AlignBottom)
        self.series.attachAxis(self.axisTime)

        self.chart.addAxis(self.axisValue, Qt.AlignLeft)
        self.series.attachAxis(self.axisValue)
        # self.axisValue.applyNiceNumbers()

        self.axisValue.setMax(50)
        self.axisValue.setMin(-50)

        if len(self.temps) < 20:
            self.axisTime.setMax(20)
            self.axisTime.setMin(0)

        else:
            self.axisTime.setMax(len(self.temps) - 1)
            self.axisTime.setMin(len(self.temps) - 21)

        self.chart.setTitle('Температура')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())