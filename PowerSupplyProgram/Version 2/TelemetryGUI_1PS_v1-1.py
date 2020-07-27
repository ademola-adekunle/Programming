## For first run on this machine, please follow Steps 1 to 3. Preferably run Python IDLE 2.7.x
# Step 1: Make sure pyserial module is installed.
# Step 2: Open and run KoradCli.py
# Step 3: Open and run Koradserial.py
# Step 4: Open and run setup.py in the main program

## Other details.
# Port open, close and flush are carried out by the wrapper module.
# Computer is automatically locked during remote control. No need to send command to lock.
# Port is released after a timeout of no command from the shell or once the program reaches EOL.
# Tested for one power supply as of Jan 31, 2019.

# All icons used are from https://p.yusukekamiyamane.com/

import sys
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLabel
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import time
from unittest import TestCase, main
import datetime
import sys
import threading
from koradserial import KoradSerial, OnOffState, OutputMode
import os
import configparser
from configparser import ConfigParser
from random import randint # DEMO ONLY


global dAqInterval, dAqON, runPS1, fileName

fileName = 'DataLoggingTest.txt'
#------------------------------------------------------------------------------#
# FUNCTIONS
#------------------------------------------------------------------------------#
def INI_write(psVoltage, psCurrent, psVoltageMax, runPS1, dAqInterval, dAqON): # function to write an INI file
    cfgfile = open(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2\INI\psSettings.ini",'w') #INI file creation. I would take this from the final code. This is just for the test
    parser = ConfigParser()
    parser.read(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2\INI\psSettings.ini")
    parser.add_section('Settings')
    parser.set('Settings', 'ps1Voltage', str(psVoltage))
    parser.set('Settings', 'ps1Current', str(psCurrent))
    parser.set('Settings', 'userdefined_MaxPS1Voltage', str(psVoltageMax))
    parser.set('Settings', 'runPS1', str(runPS1))
    parser.set('Settings', 'dAqInterval', str(dAqInterval))
    parser.set('Settings', 'dAqON', str(dAqON))
    with open(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2\INI\psSettings.ini",'w') as configfile:
        parser.write(configfile)
    configfile.close()

def INI_read(): # function to read an INI file
    global ps1Voltage, ps1CurrentMax, ps1VoltageMax, runPS1, dAqInterval, dAqON
    cfgfile = open(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2\INI\psSettings.ini",'r') #INI file creation. I would take this from the final code. This is just for the test
    parser = ConfigParser()
    parser.read(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2\INI\psSettings.ini")

    # Acquiring the values from the INI file
    ps1Voltage = float(parser.get("Settings", 'ps1Voltage'))
    ps1CurrentMax = float(parser.get("Settings", 'ps1Current'))
    ps1VoltageMax = float(parser.get("Settings", 'userdefined_MaxPS1Voltage'))
    runPS1 = parser.get("Settings", 'runPS1')
    dAqInterval = float(parser.get("Settings", 'dAqInterval'))
    dAqON = parser.get("Settings", 'dAqON')

    # Closing the INI file
    cfgfile.close()

def PS_check():
    global ps1
    try:
        ps1 = KoradSerial(self.comBox.currentText()) # sets serial port to be the COM1/2/3/4 selected by user in combobox
        ps1Aval = True
        return ps1Aval
    except Exception:
        ps1Aval = False
        return ps1Aval
        pass

def PS_write():
    global ps1
    ps1.voltage = ps1Voltage
    ps1.current = ps1CurrentMax # what is this doing? was in OG code

def PS_read():
    ps1CurrentAct = ps1.current_actual
    ps1CurrentSet = ps1.current_set
    ps1Status = ps1.status
#------------------------------------------------------------------------------#
# START-UP ACTIONS
#------------------------------------------------------------------------------#
# Creating a folder for the INI file (startup)
if not os.path.exists(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2\INI"):
   os.makedirs(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2\INI")    # Folder and location for INI file
   #os.chdir(r"C:\Users\matth\Documents\NRC\RPi\Telemetry_1PS\INI")      # change directory to this if needed? INI file can be in another directory

if not os.path.exists(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2\INI\psSettings.ini"):
    dAqInterval = 20.0
    runPS1 = False
    dAqON = False
    INI_write(1.4, 2.0, 3.0, runPS1, dAqInterval, dAqON) # makes INI file with these standard initial conditions
    INI_read()
else:
    INI_read()

cfgfile = open(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2\INI\psSettings.ini",'r') #INI file creation. I would take this from the final code. This is just for the test
parser = ConfigParser()
parser.read(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2\INI\psSettings.ini")

ps1Aval = PS_check()

if ps1Aval == True:
    PS_read()
    PS_write()

    if runPS1 == 'False':
       ps1.output = 'off'
    else:
       ps1.output = 'on'
#------------------------------------------------------------------------------#
# MAIN WINDOW
#------------------------------------------------------------------------------#
class MainWindow(QMainWindow):
    global ps1, ps1Voltage, ps1CurrentMax, ps1VoltageMax

    def __init__(self, *args, **kwargs):
        global is_editing_setvals
        super(MainWindow, self).__init__(*args, **kwargs)
        os.chdir(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2")
        uic.loadUi(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2\RPi_GUI_v1-2.ui", self)

        self.setWindowIcon(QIcon(r"Icon_Store\icons\lightning.png"))
        self.setWindowTitle(u"MEC Telemetry Application")

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(1000) # Timer counts down one second
        self.timer.timeout.connect(self.on_timeout)

        self.onlineDisplay.textChanged.connect(self.check_onlineDisplay)
        self.onlineDisplay.setText(u"OFFLINE") # sets onlineDisplay's default to say it's offline

        self.setvoltageDisplay.setText(str(ps1Voltage))
        self.maxvoltageDisplay.setText(str(ps1VoltageMax))
        self.maxcurrentDisplay.setText(str(ps1CurrentMax))

        self.setvoltageDisplay.setStyleSheet("background-color: lightgray")
        self.maxvoltageDisplay.setStyleSheet("background-color: lightgray")
        self.maxcurrentDisplay.setStyleSheet("background-color: lightgray")

        is_editing_setvals = False
        self.settingsEditButton.clicked.connect(self.on_setEdit_button_clicked)
        self.settingsOKButton.clicked.connect(self.on_setOK_button_clicked)

        self.datalogButton.clicked.connect(self.on_datalog_button_clicked)
        self.plotsetButton.clicked.connect(self.timer_start) # should be on_plotset_button_clicked, timer for testing

        self.startButton.clicked.connect(self.on_start_button_clicked)

        self.comBox.addItems(["COM1", "COM2", "COM3", "COM4"])

        # initialising the x and y plotting variables
        self.x = []
        self.y1 = []
        self.y2 = []

        color = self.palette().color(QtGui.QPalette.Window)  # Get the default window background,
        self.graphWidget.setBackground(color)
        # Add Title
        self.graphWidget.setTitle(u"MEC Telemetry", color="k", size="12pt")
        # Add Axis Labels
        styles = {"color": "k", "font-size": "10pt"}
        # Making plot's axis lines black
        axispen = pg.mkPen(color='k')
        self.graphWidget.plotItem.getAxis('left').setPen(axispen)
        self.graphWidget.plotItem.getAxis('right').setPen(axispen)
        self.graphWidget.plotItem.getAxis('bottom').setPen(axispen)
        self.graphWidget.plotItem.showAxis('right', show=True)
        # sets axis Labels
        self.graphWidget.setLabel("bottom", "Time, date", **styles)
        self.graphWidget.setLabel("left", "Current, mA", **styles)
        self.graphWidget.setLabel("right", "Temperature, C", **styles)

        #Add legend
        self.graphWidget.addLegend()
        #Add grid
        self.graphWidget.showGrid(x=True, y=True)

        pen1 = pg.mkPen(color = 'r', marker = '.')
        pen2 = pg.mkPen(color = 'b', marker = ',')
        self.data_line1 = self.graphWidget.plot(self.x, self.y1, pen = pen1)
        self.data_line2 = self.graphWidget.plot(self.x, self.y2, pen = pen2)

    def check_onlineDisplay(self):
        if self.onlineDisplay.text() == 'OFFLINE':
            self.onlineDisplay.setStyleSheet("background-color: red")
        else:
            self.onlineDisplay.setStyleSheet("background-color: green")

    def on_setEdit_button_clicked(self):
        global is_editing_setvals
        is_editing_setvals = True

        self.setvoltageDisplay.setReadOnly(False)
        self.setvoltageDisplay.setStyleSheet("background-color: white")
        self.maxvoltageDisplay.setReadOnly(False)
        self.maxvoltageDisplay.setStyleSheet("background-color: white")
        self.maxcurrentDisplay.setReadOnly(False)
        self.maxcurrentDisplay.setStyleSheet("background-color: white")

    def on_setOK_button_clicked(self):
        global is_editing_setvals, runPS1, dAqFlag

        if is_editing_setvals == False:
            pass
        elif self.setvoltageDisplay.text() > self.maxvoltageDisplay.text():
            self.statusbar.showMessage("Error: The set voltage must not be greater than the max voltage!")
        else:
            is_editing_setvals = False

            self.statusbar.clearMessage()
            self.setvoltageDisplay.setReadOnly(True)
            self.setvoltageDisplay.setStyleSheet("background-color: lightgray")
            self.maxvoltageDisplay.setReadOnly(True)
            self.maxvoltageDisplay.setStyleSheet("background-color: lightgray")
            self.maxcurrentDisplay.setReadOnly(True)
            self.maxcurrentDisplay.setStyleSheet("background-color: lightgray")

            ps1Voltage = float(self.setvoltageDisplay.text())
            ps1VoltageMax = float(self.maxvoltageDisplay.text())
            ps1CurrentMax = float(self.maxcurrentDisplay.text())

            INI_write(ps1Voltage, ps1CurrentMax, ps1VoltageMax, False, 20, False) # need a way to handle the last three variables - will want the settings editable during a run

    def on_plotset_button_clicked(self):
        print("Click!")

    def on_datalog_button_clicked(self):
        print("Click!")

    def on_start_button_clicked(self):
        global ps1, is_editing_setvals
        try:
            if self.startButton.isChecked() == True:
                if is_editing_setvals == True:
                    self.statusBar.showMessage("Can not start a run when editing the PS Settings!")

                else:
                    ps1Aval = PS_check(self)

                    if ps1Aval == False:
                        self.onlineDisplay.setText(u"OFFLINE")
                        self.statusbar.showMessage("Error: Can not connect to PS through specified COM port")
                        pass
                    else:
                        self.onlineDisplay.setText(u"ONLINE")

                        ps1.ovp = 'off'
                        ps1.ocp = 'on'
                        ps1.cv = 'on'

                        dAqON == True

                        PS_write(self)
                        PS_read(self)
                        timer_start(self)
                        update_timer(self) # Check if you really need this here or not

            else: # to stop:
                ps1.ovp = 'on'
                ps1.ocp = 'off'
                ps1.cv = 'off'

                dAqON == False
                pass

        except Exception:
            pass

    def timer_start(self):
        self.time_left_int = int(dAqInterval * 0.1) # * 0.1 for DEMO, should be * 60 (seconds -> minutes)
        self.timer.start()
        self.update_timer_display()

    def on_timeout(self):
        self.time_left_int -= 1

        if self.time_left_int == 0:
            self.get_telem() # function call to retrieve the telemetry from the power source
            self.time_left_int = int(dAqInterval * 0.1) # * 0.1 for DEMO, should be * 60 (seconds -> minutes)
            date = datetime.datetime.now()
            testy1 = randint(0,50) # DEMO ONLY
            testy2 = randint(0,50) # DEMO ONLY
            self.update_plot(date, testy1, testy2) # remove for real app!!! Demo only

        self.update_timer_display()

    def update_timer_display(self):
        self.timerLabel.setText(time.strftime('%M:%S', time.gmtime(self.time_left_int)))

    def get_telem(self):
        try:
            date = datetime.datetime.now()
            ps1V = ps1.voltage_set
            ps1C = ps1.current_actual

            if not os.path.exists(r"C:\Users\matth\Documents\NRC\RPi\Telemetry_1PS\Data_Logs"):
                os.makedirs(r"C:\Users\matth\Documents\NRC\RPi\Telemetry_1PS\Data_Logs")

            os.chdir(r"C:\Users\matth\Documents\NRC\RPi\Telemetry_1PS\Data_Logs")
            if not os.path.exists('fileName'): #For a new file, the headers are added as the first line
                log = open(fileName, "a")
                headers = ['Date', 'Vps1', 'Ips1']
                headers = ' '.join(headers)
                log.write(headers +'\n') #write headers to file
                log.close()

            log = open(fileName, "a")
            data = [str(date),str(ps1V),str(ps1C)]
            data = ' '.join(data)
            saveFile.write(data + '\n') # write data to file
            log.close()

            lastdAcq.set(str(datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")))

            self.update_plot(date, ps1C, ps1V)

        except Exception:
            pass

    def update_plot(self, date, ps1C, ps1V):
        self.stringaxis = pg.AxisItem(orientation='bottom')
        self.x.append(date.strftime("%b %d %Y %H:%M:%S"))
        self.xplot = dict(enumerate(self.x))
        self.stringaxis.setTicks([self.xplot.items()])
        self.graphWidget.plotItem.setAxisItems(axisItems = {'bottom' : self.stringaxis})
        self.xplot = list(self.xplot.keys())
        self.y1.append(ps1C)
        self.y2.append(ps1V)

        self.data_line1.setData(self.xplot, self.y1)
        self.data_line2.setData(self.xplot, self.y2)
#------------------------------------------------------------------------------#
# RUNNING THE APP
#------------------------------------------------------------------------------#
app = QApplication(sys.argv)
main = MainWindow()
main.show()
app.exec_()
