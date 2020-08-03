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

import sys, glob, serial
from PyQt5 import uic, QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QVBoxLayout
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import time
from unittest import TestCase, main
import datetime
import threading
from koradserial import KoradSerial, OnOffState, OutputMode
import os
import configparser
from configparser import ConfigParser
from random import randint # DEMO ONLY

global dAqInterval, dAqON, runPS1, fileName, koradports, ports

#------------------------------------------------------------------------------#
# FUNCTIONS
#------------------------------------------------------------------------------#
def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result

def INI_write(): # function to write an INI file
    global ps1Voltage, ps1CurrentMax, ps1VoltageMax, runPS1, dAqInterval, dAqON, cc_advset, cv_advset, ovp_advset, ocp_advset, koradports, fileName
    cfgfile = open(r"INI\psSettings.ini",'w') #INI file creation. I would take this from the final code. This is just for the test
    parser = ConfigParser()
    parser.read(r"INI\psSettings.ini")

    parser.add_section('Settings')
    parser.set('Settings', 'ps1Voltage', str(ps1Voltage))
    parser.set('Settings', 'ps1Current', str(ps1CurrentMax))
    parser.set('Settings', 'userdefined_MaxPS1Voltage', str(ps1VoltageMax))
    parser.set('Settings', 'runPS1', str(runPS1))
    parser.set('Settings', 'dAqInterval', str(dAqInterval))
    parser.set('Settings', 'dAqON', str(dAqON))
    parser.set('Settings', 'datalog filename', fileName)

    parser.add_section('Advanced Settings')
    parser.set('Advanced Settings', 'Constant Voltage (CV)', cv_advset)
    parser.set('Advanced Settings', 'Constant Current (CC)', cc_advset)
    parser.set('Advanced Settings', 'Over Voltage Protection (OVP)', ovp_advset)
    parser.set('Advanced Settings', 'Over Current Protection (OCP)', ocp_advset)

    parser.add_section('COM Ports')
    try: # exception catch in case there are no COM ports recognized
        for i in range(len(koradports)):
            parser.set('COM Ports', 'Korad port #%i' %i, str(koradports[i]))

    except Exception:
        pass

    with open(r"INI\psSettings.ini",'w') as configfile:
        parser.write(configfile)
    configfile.close()

def INI_read(): # function to read an INI file
    global ps1Voltage, ps1CurrentMax, ps1VoltageMax, runPS1, dAqInterval, dAqON, cc_advset, cv_advset, ocp_advset, ovp_advset, koradports, fileName
    cfgfile = open(r"INI\psSettings.ini",'r') #INI file creation. I would take this from the final code. This is just for the test
    parser = ConfigParser()
    parser.read(r"INI\psSettings.ini")

    # Acquiring the values from the INI file
    ps1Voltage = float(parser.get("Settings", 'ps1Voltage'))
    ps1CurrentMax = float(parser.get("Settings", 'ps1Current'))
    ps1VoltageMax = float(parser.get("Settings", 'userdefined_MaxPS1Voltage'))
    runPS1 = parser.get("Settings", 'runPS1')
    dAqInterval = float(parser.get("Settings", 'dAqInterval'))
    dAqON = parser.get("Settings", 'dAqON')
    fileName = parser.get("Settings", 'datalog filename')

    #ps1.cv = parser.get("Advanced Settings", 'Constant Voltage (CV)')
    cv_advset = parser.get("Advanced Settings", 'Constant Voltage (CV)')
    #ps1.cc = parser.get("Advanced Settings", 'Constant Current (CC)')
    cc_advset = parser.get("Advanced Settings", 'Constant Current (CC)')
    #ps1.ovp = parser.get("Advanced Settings", 'Over Voltage Protection (OVP)')
    ovp_advset = parser.get("Advanced Settings", 'Over Voltage Protection (OVP)')
    #ps1.ocp = parser.get("Advanced Settings", 'Over Current Protection (OCP)')
    ocp_advset = parser.get("Advanced Settings", 'Over Current Protection (OCP)')

    try:
        for i in range(len(ports)):
            koradports.append(parser.get("COM Ports", 'Korad Port #%i' %i))

    except Exception:
        pass

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
    global ps1, ps1Voltage, ps1CurrentMax
    ps1.voltage = ps1Voltage
    ps1.current = ps1CurrentMax # what is this doing? was in OG code

def PS_read():
    ps1CurrentAct = ps1.current_actual
    ps1CurrentSet = ps1.current_set
    ps1Status = ps1.status

def get_datalog():
    global fileName

    if not os.path.exists(r"Data_Logs"):
        os.makedirs(r"Data_Logs")

    os.chdir(r"Data_Logs")

    if not os.path.exists(fileName): #For a new file, the headers are added as the first line
        log = open(fileName, "a")
        headers = ['Date', 'Vps1', 'Ips1']
        headers = ' '.join(headers)
        log.write(headers +'\n') #write headers to file
        log.close()

    log = open(fileName, "a")

    return log
#------------------------------------------------------------------------------#
# START-UP ACTIONS
#------------------------------------------------------------------------------#
# Creating a folder for the INI file (startup)
global ports, koradports, koradserials

if not os.path.exists(r"Version 2"):
   os.makedirs(r"Version 2")    # Folder and location for INI file
   #os.chdir(r"INI")      # change directory to this if needed? INI file can be in another directory

if not os.path.exists(r"INI"):
   os.makedirs(r"INI")    # Folder and location for INI file
   #os.chdir(r"INI")      # change directory to this if needed? INI file can be in another directory

if not os.path.exists(r"INI\psSettings.ini"):
    ps1Voltage = 1.4
    ps1CurrentMax = 2.0
    ps1VoltageMax = 3.0
    dAqInterval = 20.0
    runPS1 = False
    dAqON = False
    fileName = 'DataLoggingFile.txt'
    cc_advset = 'on'
    cv_advset = 'off'
    ocp_advset = 'off'
    ovp_advset = 'on'

    ports = serial_ports()
    koradports = [] #???
    koradserials = []
    if ports: # if there are ports detected
        for coms in ports:
            try:
                KoradSerial(coms)
                koradserials.append(str(coms))

            except Exception:
                pass

        for i in range(len(koradserials)):
            koradports.append(str(koradserials[i])) #

    INI_write() # makes INI file with these standard initial conditions
    INI_read()

else:   #
    ports = serial_ports()
    koradports = [] #???
    koradserials = []
    if ports: # if there are ports detected
        for coms in ports:
            try:
                KoradSerial(coms)
                koradserials.append(str(coms))

            except Exception:
                pass

        for i in range(len(koradserials)):
            koradports.append(str(koradserials[i])) #

    INI_read()

cfgfile = open(r"INI\psSettings.ini",'r') #INI file creation. I would take this from the final code. This is just for the test
parser = ConfigParser()
parser.read(r"INI\psSettings.ini")

log = get_datalog() # makes datalog file on first run
log.close()

ps1Aval = PS_check()

if ps1Aval == True:
    PS_read()
    PS_write()

    if runPS1 == 'False':
        ps1.output = 'off'
    else:
        ps1.output = 'on'
#------------------------------------------------------------------------------#
# DIALONG BOXES
#------------------------------------------------------------------------------#
class AdvSettings(QDialog):
    global ps1, cc_advset, cv_advset, ocp_advset, ovp_advset

    def __init__(self, *args, **kwargs):
        super(AdvSettings, self).__init__(*args, **kwargs)
        uic.loadUi(r"Version 2\AdvSettings_v1-1.ui", self)

        self.setWindowTitle(u"Advanced PS Settings")

        self.cvCheckBox.stateChanged.connect(self.cv_state_change)
        self.ccCheckBox.stateChanged.connect(self.cc_state_change)
        self.ovpCheckBox.stateChanged.connect(self.ovp_state_changed)
        self.ocpCheckBox.stateChanged.connect(self.ocp_state_changed)

        self.advsetButtonBox.accepted.connect(self.accept)
        self.advsetButtonBox.rejected.connect(self.reject)

    def cv_state_change(self):
        if self.cvCheckBox.isChecked() == True:
            self.ccCheckBox.setChecked(False)
            self.ccCheckBox.setEnabled(False)

        else:
            self.ccCheckBox.setEnabled(True)

    def cc_state_change(self):
        if self.ccCheckBox.isChecked() == True:
            self.cvCheckBox.setChecked(False)
            self.cvCheckBox.setEnabled(False)

        else:
            self.cvCheckBox.setEnabled(True)

    def ovp_state_changed(self):
        if self.ovpCheckBox.isChecked() == True:
            self.ocpCheckBox.setChecked(False)
            self.ocpCheckBox.setEnabled(False)

        else:
            self.ocpCheckBox.setEnabled(True)

    def ocp_state_changed(self):
        if self.ocpCheckBox.isChecked() == True:
            self.ovpCheckBox.setChecked(False)
            self.ovpCheckBox.setEnabled(False)

        else:
            self.ovpCheckBox.setEnabled(True)

class DataLogSettings(QDialog):

    def __init__(self, *args, **kwargs):
        super(DataLogSettings, self).__init__(*args, **kwargs)
        uic.loadUi(r"Version 2\DataLogSettings_v1-1.ui", self)

        self.setWindowTitle("Data Log Settings")

        dispfileName = fileName.split('.txt') # gets the file ready to show without the .txt ending

        self.filenameLineEdit.setText(dispfileName[0])
        self.intervalLineEdit.setText(str(dAqInterval))

class StartUpDelay(QDialog):

    def __init__(self, *args, **kwargs):
        super(StartUpDelay, self).__init__(*args, **kwargs)

        self.setWindowTitle("Delay Timer")

        QBtn = QDialogButtonBox.Ok

        self.buttonbox = QDialogButtonBox(QBtn)
        self.buttonbox.accepted.connect(self.accept)

        self.delaytimerDisplay = QLabel()
        self.delaytimer = QtCore.QTimer(self)
        self.delaytimer.setInterval(1000)
        self.delaytimer.timeout.connect(self.delay_timeout)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.delaytimerDisplay)
        self.layout.addWidget(self.buttonbox)
        self.setLayout(self.layout)

        self.delay_start()
        self.update_gui()

    def delay_start(self):
        self.delaytimeleft = 30
        self.delaytimer.start()
        self.update_gui()

    def delay_timeout(self):
        self.delaytimeleft -= 1

        if self.delaytimeleft == 0:
            self.delaytimer.stop()
            self.close()

        self.update_gui()

    def update_gui(self):
        self.delaytimerDisplay.setText('Please wait %s seconds before using the program.' %str(self.delaytimeleft))

#------------------------------------------------------------------------------#
# MAIN WINDOW
#------------------------------------------------------------------------------#
class MainWindow(QMainWindow):
    global ps1, ps1Voltage, ps1CurrentMax, ps1VoltageMax

    def __init__(self, *args, **kwargs):
        global is_editing_setvals, koradports
        super(MainWindow, self).__init__(*args, **kwargs)
        uic.loadUi(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2\RPi_GUI_v1-3.ui", self)

        self.setWindowIcon(QIcon(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 2\lightning.png"))
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
        self.advsetButton.clicked.connect(self.on_advset_button_clicked)

        self.datalogButton.clicked.connect(self.on_datalog_button_clicked)
        self.plotsetButton.clicked.connect(self.timer_start) # should be on_plotset_button_clicked, timer for testing

        self.startButton.clicked.connect(self.on_start_button_clicked)

        self.findPSButton.clicked.connect(self.on_findPS_button_clicked)

        for i in range(len(ports)):
            self.comBox.addItem(str(koradports[i])) # use this to save them to INI too?

        self.statusbar.setStyleSheet('background-color: lightgray')

        # initialising the x and y plotting variables (1 = left axis, 2 = right axis)
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

    def on_findPS_button_clicked(self):
        global koradports, koradserials
        ports = serial_ports()

        ports = serial_ports()
        koradports = [] #
        koradserials = []
        if ports: # if there are ports detected
            for coms in ports:
                try:
                    KoradSerial(coms)
                    koradserials.append(str(coms))

                except Exception:
                    pass

            for i in range(len(koradserials)):
                koradports.append(str(koradserials[i])) #

            self.statusbar.showMessage("Serial ports detected!")

        else:
            self.statusbar.showMessage("No serial ports detected!")

    def on_setEdit_button_clicked(self):
        global is_editing_setvals
        is_editing_setvals = True

        displayfont = self.setvoltageDisplay.font()
        displayfont.setPointSize(10)

        self.setvoltageDisplay.setReadOnly(False)
        self.setvoltageDisplay.setStyleSheet("background-color: white")
        self.setvoltageDisplay.setFont(displayfont)
        self.maxvoltageDisplay.setReadOnly(False)
        self.maxvoltageDisplay.setStyleSheet("background-color: white")
        self.maxvoltageDisplay.setFont(displayfont)
        self.maxcurrentDisplay.setReadOnly(False)
        self.maxcurrentDisplay.setStyleSheet("background-color: white")
        self.maxcurrentDisplay.setFont(displayfont)

    def on_setOK_button_clicked(self):
        global is_editing_setvals, runPS1, dAqFlag

        if is_editing_setvals == False:
            pass
        elif self.setvoltageDisplay.text() > self.maxvoltageDisplay.text():
            self.statusbar.showMessage("Error: The set voltage must not be greater than the max voltage!")
        else:
            is_editing_setvals = False

            displayfont = self.setvoltageDisplay.font()
            displayfont.setPointSize(10)

            self.statusbar.clearMessage()
            self.setvoltageDisplay.setReadOnly(True)
            self.setvoltageDisplay.setStyleSheet("background-color: lightgray")
            self.setvoltageDisplay.setFont(displayfont)
            self.maxvoltageDisplay.setReadOnly(True)
            self.maxvoltageDisplay.setStyleSheet("background-color: lightgray")
            self.maxvoltageDisplay.setFont(displayfont)
            self.maxcurrentDisplay.setReadOnly(True)
            self.maxcurrentDisplay.setStyleSheet("background-color: lightgray")
            self.maxcurrentDisplay.setFont(displayfont)

            ps1Voltage = float(self.setvoltageDisplay.text())
            ps1VoltageMax = float(self.maxvoltageDisplay.text())
            ps1CurrentMax = float(self.maxcurrentDisplay.text())

            INI_write() # need a way to handle the last three variables - will want the settings editable during a run

    def on_advset_button_clicked(self):
        global ps1, cc_advset, cv_advset, ocp_advset, ovp_advset
        self.AdvSettings = AdvSettings()
        self.AdvSettings.show()

        INI_read() # updates advset strings

        if cc_advset == 'on':
            self.AdvSettings.ccCheckBox.setChecked(True)
            self.AdvSettings.cvCheckBox.setChecked(False) # settings these False may be a redundancy, kept to ensure cc and cv aren't on simultaneously

        elif cv_advset == 'on':
            self.AdvSettings.ccCheckBox.setChecked(False)
            self.AdvSettings.cvCheckBox.setChecked(True)

        else:
            self.AdvSettings.ccCheckBox.setChecked(False)
            self.AdvSettings.cvCheckBox.setChecked(False)

        if ocp_advset == 'on':
            self.AdvSettings.ocpCheckBox.setChecked(True)
            self.AdvSettings.ovpCheckBox.setChecked(False)

        elif ovp_advset == 'on':
            self.AdvSettings.ocpCheckBox.setChecked(False)
            self.AdvSettings.ovpCheckBox.setChecked(True)

        else:
            self.AdvSettings.ocpCheckBox.setChecked(False)
            self.AdvSettings.ovpCheckBox.setChecked(False)

        if self.AdvSettings.exec_(): # if the user clicks OK
            self.check_advset() # checks which boxes are selected, updates INI file

        else: # if the user clicks Cancel
            pass

    def check_advset(self):
        global ps1, cc_advset, cv_advset, ovp_advset, ocp_advset

        if self.AdvSettings.ccCheckBox.isChecked() == True:
            cc_advset = 'on'
            cv_advset = 'off'

        elif self.AdvSettings.cvCheckBox.isChecked() == True:
            cc_advset = 'off'
            cv_advset = 'on'

        else:
            cc_advset = 'off'
            cv_advset = 'off'

        if self.AdvSettings.ovpCheckBox.isChecked() == True:
            ovp_advset = 'on'
            ocp_advset = 'off'

        elif self.AdvSettings.ocpCheckBox.isChecked() == True:
            ovp_advset = 'off'
            ocp_advset = 'on'

        else:
            ovp_advset = 'off'
            ocp_advset = 'off'

        INI_write() # updates INI file

    def on_plotset_button_clicked(self):
        print("Click!")

    def on_datalog_button_clicked(self):
        global fileName, dAqInterval
        self.DataLogSettings = DataLogSettings()
        self.DataLogSettings.show()

        if self.DataLogSettings.exec_():
            fileName = self.DataLogSettings.filenameLineEdit.text()+'.txt'
            dAqInterval = float(self.DataLogSettings.intervalLineEdit.text())

            log = get_datalog()
            log.close()

            INI_write()

        else:
            pass

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

                        INI_read() # applies specifications stored in INI file

                        dAqON = True
                        runPS1 = True

                        PS_write(self)
                        PS_read(self)
                        timer_start(self)
                        update_timer(self) # Check if you really need this here or not

            else: # to stop:
                ps1.ovp = 'on'
                ps1.ocp = 'off'
                ps1.cv = 'off'
                ps1.output = 'off'

                dAqON = False
                runPS1 = False
                pass

        except Exception:
            pass

    def timer_start(self):
        self.time_left_int = int(dAqInterval * 0.1) # * 0.1 for DEMO, should be * 60 (minutes -> seconds)
        self.timer.start()
        self.update_timer_display()

    def on_timeout(self):
        self.time_left_int -= 1

        if self.time_left_int == 0:
            self.get_telem() # function call to retrieve the telemetry from the power source
            self.time_left_int = int(dAqInterval * 0.1) # * 0.1 for DEMO, should be * 60 (minutes -> seconds)
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

            data = [str(date),str(ps1V),str(ps1C)]
            data = ' '.join(data)

            log = get_datalog()
            log.write(data + '\n') # write data to file
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
delay = StartUpDelay()
delay.show()

if delay.exec_():
    main.show()
else:
    main.show()

app.exec_()
