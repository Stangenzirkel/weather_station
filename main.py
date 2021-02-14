from PyQt5.QtWidgets import QApplication, QWidget, QTableWidgetItem, QPushButton, QMessageBox
from PyQt5.QtChart import QChart, QChartView, QValueAxis, QLineSeries, QDateTimeAxis
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QDateTime, QDate, QTime
from PyQt5 import uic
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QTimer

import sys
import datetime as dt
import sqlite3

from measure_temperature import *

import warnings
warnings.filterwarnings("ignore")

MEASURE_FREQUENCIES = 1
RECORDING_FREQUENCIES = 10


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ws_ui.ui', self)
        self.con = sqlite3.connect("ws_database.db")
        self.temp_sensor = sensor
        self.linechart_mode = 1

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.quitButton.clicked.connect(self.quit)
        self.modeButton_1.clicked.connect(self.switch_linechart_mode)
        self.modeButton_2.clicked.connect(self.switch_linechart_mode)
        self.modeButton_3.clicked.connect(self.switch_linechart_mode)
        self.modeButton_4.clicked.connect(self.switch_linechart_mode)

        self.temps = []
        self.create_linechart()
        self.make_measure()

        self.timer = QTimer(self)
        self.timer.setInterval(MEASURE_FREQUENCIES * 1000)
        self.timer.timeout.connect(self.make_measure)
        self.timer.start()

    def quit(self):
        self.destroy()
        quit()

    def switch_linechart_mode(self):
        modes = {"За 10 минут": 1, "За 24 часа": 2, "За месяц": 3, "За год": 4}
        self.linechart_mode = modes[self.sender().text()]
        self.update_linechart()

    def make_measure(self):
        self.temps.append(temp(self.temp_sensor))

        if len(self.temps) >= RECORDING_FREQUENCIES // MEASURE_FREQUENCIES * 2 + 1:
            self.temps = self.temps[RECORDING_FREQUENCIES // MEASURE_FREQUENCIES:]

        if len(self.temps) == RECORDING_FREQUENCIES // MEASURE_FREQUENCIES + 1:
            max_t = float(max(self.temps))
            min_t = float(min(self.temps))
            time = int(dt.datetime.now().timestamp())

            req = """
                  INSERT INTO short_term_data(max_t, min_t, time_from_epoch)
                  VALUES(?,?,?)
                  """

            self.con.execute(req, (max_t, min_t, time))
            self.con.commit()

        self.update_linechart()

    def create_linechart(self):
        self.series = QLineSeries()
        self.chart = QChart()
        self.chart.addSeries(self.series)
        # self.chart.setAnimationOptions(QChart.SeriesAnimations)

        self.axisValue = QValueAxis()
        self.axisCurrentTime = QValueAxis()
        self.axisTime = QDateTimeAxis()
        self.axisTime.setFormat("dd MMM hh:mm")

        self.chart.legend().hide()

        self.chartview = QChartView(self.chart, self.groupBox)
        self.chartview.resize(780, 420)
        self.chartview.move(0, 0)
        self.chartview.setRenderHint(QPainter.Antialiasing)

    def update_linechart(self):
        if self.axisTime in self.chart.axes():
            self.chart.removeAxis(self.axisTime)

        if self.axisCurrentTime in self.chart.axes():
            self.chart.removeAxis(self.axisCurrentTime)

        if self.axisValue in self.chart.axes():
            self.chart.removeAxis(self.axisValue)

        self.chart.removeSeries(self.series)

        self.series.clear()

        self.axisValue.setMax(50)
        self.axisValue.setMin(-50)

        if self.linechart_mode == 1:
            for i, res in enumerate(self.temps):
                self.series.append(i, res)

            self.chart.addSeries(self.series)
            self.chart.addAxis(self.axisCurrentTime, Qt.AlignBottom)
            self.series.attachAxis(self.axisCurrentTime)

            self.chart.addAxis(self.axisValue, Qt.AlignLeft)
            self.series.attachAxis(self.axisValue)
            # self.axisValue.applyNiceNumbers()

            if len(self.temps) < RECORDING_FREQUENCIES // MEASURE_FREQUENCIES + 1:
                self.axisCurrentTime.setMax(RECORDING_FREQUENCIES // MEASURE_FREQUENCIES)
                self.axisCurrentTime.setMin(0)

            else:
                self.axisCurrentTime.setMax(len(self.temps) - 1)
                self.axisCurrentTime.setMin(len(self.temps) - RECORDING_FREQUENCIES // MEASURE_FREQUENCIES - 1)

        elif self.linechart_mode == 2:
            req = """
                  SELECT max_t, time_from_epoch
                  FROM short_term_data
                  WHERE (time_from_epoch - ?) < 86400
                  """

            cur = self.con.cursor()
            result = list(cur.execute(req, (int(dt.datetime.now().timestamp()), )))

            for measure in result:
                self.series.append(measure[1] * 1000, measure[0])

            self.axisTime.setMin(QDateTime.fromMSecsSinceEpoch(int(dt.datetime.now().timestamp()) * 1000 - 86390000))
            self.axisTime.setMax(QDateTime.fromMSecsSinceEpoch(int(dt.datetime.now().timestamp()) * 1000))

            self.chart.addSeries(self.series)
            self.chart.addAxis(self.axisTime, Qt.AlignBottom)
            self.series.attachAxis(self.axisTime)

            self.chart.addAxis(self.axisValue, Qt.AlignLeft)
            self.series.attachAxis(self.axisValue)

        self.chart.setTitle('Температура - ' + str(self.temps[-1]))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())