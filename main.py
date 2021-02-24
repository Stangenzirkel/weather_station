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

from measure import *

import warnings
warnings.filterwarnings("ignore")

MEASURE_FREQUENCIES = 60


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('ws_ui.ui', self)
        self.con = sqlite3.connect("ws_database.db")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.create_linechart()
        self.tmp, self.hmd, self.prs = 0, 0, 0
        self.make_measure()

        self.measure_timer = QTimer(self)
        self.measure_timer.setInterval(MEASURE_FREQUENCIES * 1000)
        self.measure_timer.timeout.connect(self.make_measure)
        self.measure_timer.start()

        self.update_timer = QTimer(self)
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self.update_labels)
        self.update_timer.start()

        self.update_labels()

    def quit(self):
        self.destroy()
        quit()

    def make_measure(self):
        self.tmp, self.hmd, self.prs = sensor_measure()
        time = int(dt.datetime.now().timestamp())

        req = """
              INSERT INTO short_term_data(tmp, hmd, prs, time_from_epoch)
              VALUES(?,?,?,?)
              """

        self.con.execute(req, (self.tmp, self.hmd, self.prs, time))
        self.con.commit()

        self.update_linechart()

    def update_labels(self):
        self.time_label.setText(dt.datetime.now().strftime('%H:%M'))
        self.tmp_label.setText('{} C'.format(self.tmp))
        self.hmd_label.setText('{} %'.format(self.hmd))
        self.prs_label.setText('{} КПа'.format(self.prs))

    def create_linechart(self):
        self.chart = QChart()
        self.chart.legend().hide()

        self.series = QLineSeries()

        self.axisValue = QValueAxis()
        self.axisCurrentTime = QValueAxis()
        self.axisTime = QDateTimeAxis()
        self.axisTime.setFormat("hh:mm")

        self.chartview = QChartView(self.chart, self.groupBox)
        self.chartview.resize(540, 460)
        self.chartview.move(0, 0)
        self.chartview.setRenderHint(QPainter.Antialiasing)

    def update_linechart(self):
        if self.axisTime in self.chart.axes():
            self.chart.removeAxis(self.axisTime)

        if self.axisCurrentTime in self.chart.axes():
            self.chart.removeAxis(self.axisCurrentTime)

        if self.axisValue in self.chart.axes():
            self.chart.removeAxis(self.axisValue)

        if self.series in self.chart.series():
            self.chart.removeSeries(self.series)

        self.series.clear()

        self.axisValue.setMax(50)
        self.axisValue.setMin(-50)

        req = """
              SELECT tmp, time_from_epoch
              FROM short_term_data
              WHERE (time_from_epoch - ?) < 86400 AND NOT tmp = ?
              """

        cur = self.con.cursor()
        result = list(cur.execute(req, (int(dt.datetime.now().timestamp()), ERROR_CODE)))

        for measure in result:
            self.series.append(measure[1] * 1000, measure[0])

        self.axisTime.setMin(QDateTime.fromMSecsSinceEpoch(int(dt.datetime.now().timestamp()) * 1000 - 86390000))
        self.axisTime.setMax(QDateTime.fromMSecsSinceEpoch(int(dt.datetime.now().timestamp()) * 1000))

        self.chart.addSeries(self.series)
        self.chart.addAxis(self.axisTime, Qt.AlignBottom)
        self.series.attachAxis(self.axisTime)
        self.chart.addAxis(self.axisValue, Qt.AlignLeft)
        self.series.attachAxis(self.axisValue)

        self.chart.setTitle('Температура')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.exit(app.exec_())
