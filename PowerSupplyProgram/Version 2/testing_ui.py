import sys
from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from pyqtgraph import PlotWidget
import pyqtgraph as pg


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2\RPi_GUI_v1-2.ui", self)

        self.setWindowTitle(u"KORAD Power Supply")

        self.onlineDisplay.textChanged.connect(self.check_onlineDisplay)

        self.onlineDisplay.setText(u"OFFLINE")

        color = self.palette().color(QtGui.QPalette.Window)  # Get the default window background,
        self.graphWidget.setBackground(color)
        # Add Title
        self.graphWidget.setTitle(u"MEC Measurements", color="k", size="12pt")
        # Add Axis Labels
        styles = {"color": "k", "font-size": "10pt"}
        # Making plot's axis lines black
        pen = pg.mkPen(color='k')
        self.graphWidget.plotItem.getAxis('left').setPen(pen)
        self.graphWidget.plotItem.getAxis('right').setPen(pen)
        self.graphWidget.plotItem.getAxis('bottom').setPen(pen)
        self.graphWidget.plotItem.showAxis('right', show=True)
        # sets axis Labels
        self.graphWidget.setLabel("bottom", "Time, date", **styles)
        self.graphWidget.setLabel("left", "Current, mA", **styles)
        self.graphWidget.setLabel("right", "Temperature, C", **styles)

        #Add legend
        self.graphWidget.addLegend()
        #Add grid
        self.graphWidget.showGrid(x=True, y=True)

    def check_onlineDisplay(self):
        if self.onlineDisplay.text() == 'OFFLINE':
            self.onlineDisplay.setStyleSheet("outline-color: red")
        else:
            self.onlineDisplay.setStyleSheet("background-color: green")


app = QApplication(sys.argv)
main = MainWindow()
main.show()
app.exec_()
