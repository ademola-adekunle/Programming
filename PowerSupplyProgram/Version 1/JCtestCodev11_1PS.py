## For first run on this machine, please follow Steps 1 to 3. Preferably run Python IDLE 2.7.x
# Step 1: Make sure pyserial module is installed.
# Step 2: Make sure click is installed
# Step 3: Open and run KoradCli.py
# Step 4: Open and run Koradserial.py


## Other details.
# Port open, close and flush are carried out by the wrapper module.
# Computer is automatically locked during remote control. No need to send command to lock.
# Port is released after a timeout of no command from the shell or once the program reaches EOL.
# Tested for one power supply as of Jan 31, 2019.

import matplotlib
matplotlib.use ("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation

import Tkinter
from Tkinter import *
import time
from unittest import TestCase, main
import datetime
import sys
import tkMessageBox
import threading
from koradserial import KoradSerial, OnOffState, OutputMode
import os
import ConfigParser
from ConfigParser import SafeConfigParser

# from koradcli import korad

# Definition of serial ports for 2 power supplies
ps1serialPort = 'COM4' # COMM PORT 1
# ps2serialPort = 'COM6' # COMM PORT 2

# Creating a folder for the INI file (startup)
if not os.path.exists(r'C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI'):
   os.makedirs(r'C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI')    # Folder and location for INI file
   os.chdir(r'C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI')       # change directory to this if needed? INI file can be in another directory

if not os.path.exists(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI"):
   cfgfile = open(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI\ps1Settings.ini",'w') #INI file creation. I would take this from the final code. This is just for the test
   parser = SafeConfigParser()
   parser.read(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI\ps1Settings.ini")
   parser.add_section('Settings')
   parser.set('Settings', 'ps1Voltage', '1.4')
   # parser.set('Settings', 'ps2Voltage', '1.4')
   parser.set('Settings', 'ps1Current', '2.0')
   # parser.set('Settings', 'ps2Current', '2.0')
   parser.set('Settings', 'userdefined_MaxPS1Voltage', '3.0')
   # parser.set('Settings', 'userdefined_MaxPS2Voltage', '3.0')
   parser.set('Settings', 'runPS1', 'False')
   # parser.set('Settings', 'runPS2', 'False')
   parser.set('Settings', 'dAqInterval', '20')
   parser.set('Settings', 'dAqON', 'False')
   with open("C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI\ps1Settings.ini",'wb') as configfile:
      parser.write(configfile)
   configfile.close()

cfgfile = open(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI\ps1Settings.ini",'r') #INI file creation. I would take this from the final code. This is just for the test
parser = SafeConfigParser()
parser.read(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI\ps1Settings.ini")

# Variable definitions
# ps1
global ps1
global ps1Aval
ps1Aval = False
global ps1Voltage
global ps1maxCurrent
global userdefined_MaxPS1Voltage
global isetPS1
global tGraphic
global i1Graphic

# ps2
# global ps2
# global ps2Aval
# ps2Aval = False
# global ps2Voltage
# global ps2maxCurrent
# global userdefined_MaxPS2Voltage
# global isetPS2
# global i2Graphic

global maxPSV
global maxPSI
global daqInterval
global fileName

# .ini variables
# ps1
global ps1Vini
global ps1Vmaxini
global ps1Imaxini
global runPS1

# ps2
# global ps2Vini
# global ps2Vmaxini
# global ps2Imaxini
# global runPS2

global dAqON
maxPSV = 5.0
maxPSI = 5.0

try:
   ps1 = KoradSerial(ps1serialPort) # handle def
   ps1Aval = True
except Exception:
   pass

# try:
   # ps2 = KoradSerial(ps2serialPort) # handle def
   # ps2Aval = True
# except Exception:
   # pass

# Acquiring the values from the INI file
ps1Voltage     = float(parser.get("Settings", 'ps1Voltage'))      # Initial voltage definition for PS1
ps1maxCurrent  = float(parser.get("Settings", 'ps1Current'))     # Initial current definition for PS1
# ps2Voltage     = float(parser.get("Settings", 'pS2Voltage'))     # Initial voltage definition for PS1
# ps2maxCurrent  = float(parser.get("Settings", 'ps2Current'))     # Initial current definition for PS1
userdefined_MaxPS1Voltage = float(parser.get("Settings", 'userdefined_MaxPS1Voltage'))
# userdefined_MaxPS2Voltage = float(parser.get("Settings", 'userdefined_MaxPS2Voltage'))
ps1Vini = str(ps1Voltage)
ps1Vmaxini = str(userdefined_MaxPS1Voltage)
ps1Imaxini = str(ps1maxCurrent)
# ps2Vini = str(ps2Voltage)
# ps2Vmaxini = str(userdefined_MaxPS2Voltage)
# ps2Imaxini = str(ps2maxCurrent)

runPS1 = parser.get("Settings", 'runPS1')
# runPS2 = parser.get("Settings", 'runPS2')
daqInterval = float(parser.get("Settings", 'dAqInterval'))
dAqON = parser.get("Settings", 'dAqON')

# Closing the INI file
cfgfile.close()

if ps1Aval == True:
   # Acquiring initial readings from PS1
   ps1currentActual  = 0.75 #ps1.current_actual    # actual current being given out
   ps1currentRead    = 0.73 #ps1.current_set         # read what you previously set
   ps1deviceStatus   = 0.0 #ps1.status

   # Assigning the values to PS1
   if runPS1 == 'False':
      ps1.output = 'off'
   else:
      ps1.output = 'on'

   ps1.voltage = ps1Voltage
   ps1.current = ps1maxCurrent
   isetPS1 = ps1currentActual

# if ps2Aval == True:
   # # Acquiring initial readings from PS2
   # ps2currentActual  = ps2.current_actual    # actual current being given out
   # ps2voltageRead    = ps2.voltage_set         # read what you previously set
   # ps2currentRead    = ps2.current_set         # read what you previously set
   # ps2deviceStatus   = ps2.status

   # # Assigning the values to the PS2
   # if runPS2 == 'False':
      # ps2.output = 'off'
   # else:
      # ps2.output = 'on'

   # ps2.voltage = ps2Voltage
   # ps2.current = ps2maxCurrent
   # isetPS2 = ps2currentActual

dAcqFlag = False
fileName = 'Datalogging1.txt'


class simpleapp_tk(Tkinter.Tk):
   def __init__(self, master):
      global fileName
      global daqInterval
      self.master = master
      master.title('MEC Power Supply Monitoring')
      # master.geometry('1000x850+200+200')
      master.configure(background='lightgray')
      master.grid() #Layout manager

      # ------------------------------------------------------------------------
      # Displaying the filename
      # ------------------------------------------------------------------------
      # Definition of label
      self.filenameVariable = Tkinter.StringVar() #variable to call label
      self.filenameLabel = Tkinter.Label(master,textvariable=self.filenameVariable,
                              anchor = "w", fg = "black", bg = 'lightgray', font = "Arial, 12")
      self.filenameVariable.set(u"Datalogging file:")    # default value in display
      self.filenameLabel.grid(column = 5, row = 6,columnspan = 1,sticky = 'NE') #label position

      self.filenamedisplayVariable = Tkinter.StringVar() # variable to call label
      global vsetfileName
      vsetfileName = self.filenamedisplayVariable
      self.filenamedisplayLabel = Tkinter.Label(master,textvariable=self.filenamedisplayVariable,
                                         anchor = "w", fg = "black", bg = "ivory", font = "Arial, 12")
      self.filenamedisplayVariable.set(fileName) #default value in display
      self.filenamedisplayLabel.grid(column = 6, row = 6,columnspan = 1, sticky = 'W')

      # ------------------------------------------------------------------------
      # BUTTONS Definitions
      # ------------------------------------------------------------------------

      # Graphic definition of SETTINGS button
      self.settingsButton = Tkinter.Button(master, text = "SETTINGS", command = self.Settings,
                              anchor = "center", fg = "black", bg = 'lightgray', font = "Arial, 12") # Button uses the settings function
      self.settingsButton.grid(column = 3, row = 2,columnspan = 1,sticky = 'NESW')

      # Graphic definition of START button
      self.startButton = Tkinter.Button(master, text = "START", command = self.Start,
                              anchor = "center", fg = "black", bg = 'lightgray', font = "Arial, 12") # Button uses the Start function
      self.startButton.grid(column = 3, row = 3,columnspan = 1,sticky = 'NESW')

      # Graphical definition of STOP button
      self.stopButton = Tkinter.Button(master, text = "STOP", command = self.Stop,
                                       anchor = "center", fg = "black", bg = 'lightgray', font = "Arial, 12") # Button uses the Stop function
      self.stopButton.grid(column = 3, row = 4,columnspan = 1,sticky = 'NESW')

      # ------------------------------------------------------------------------
      # Displaying PS1 status (ON/OFF) on master
      # ------------------------------------------------------------------------
      # Graphical definition of PS1 ON/OFF label
      self.onoffPS1Variable = Tkinter.StringVar() # variable to call label
      if runPS1 == 'False':
         self.onoffPS1Variable.set(u"PS1: OFF")
      else:
         self.onoffPS1Variable.set(u"PS1: ON")

      self.onoffPS1Label = Tkinter.Label(master,textvariable=self.onoffPS1Variable,
                              anchor = "center", fg = "black", bg = 'lightgray', font = "Arial, 12")
      self.onoffPS1Label.grid(column = 0, row = 0, columnspan = 1, sticky = 'W')

      # ------------------------------------------------------------------------
      # Displaying PS1 voltage
      # ------------------------------------------------------------------------
      # Graphical definition of label
      self.ps1voltageVariable = Tkinter.StringVar() #variable to call label
      self.ps1voltageLabel = Tkinter.Label(master,textvariable=self.ps1voltageVariable,
                              anchor = "w", fg = "black", bg = 'lightgray', font = "Arial, 12")
      self.ps1voltageVariable.set(u"PS1 Voltage [V]:")    # default value in display
      self.ps1voltageLabel.grid(column = 0, row = 2, columnspan = 1, sticky = 'W')

      self.ps1VdisplayVariable = Tkinter.StringVar() # variable to call label
      global vsetPS1
      vsetPS1 = self.ps1VdisplayVariable
      self.ps1VdisplayLabel = Tkinter.Label(master,textvariable=self.ps1VdisplayVariable,
                                         anchor = "e", fg = "black", bg = "ivory", font = "Arial, 12")
      self.ps1VdisplayVariable.set(str(ps1Voltage)) #default value in display
      self.ps1VdisplayLabel.grid(column = 1, row = 2, columnspan = 1, sticky = 'W')

      # ------------------------------------------------------------------------
      # Displaying PS1 current
      # ------------------------------------------------------------------------
      # Graphical definition of label
      self.ps1currentVariable = Tkinter.StringVar() #variable to call label
      self.ps1currentLabel = Tkinter.Label(master,textvariable=self.ps1currentVariable,
                              anchor = "w", fg = "black", bg = 'lightgray', font = "Arial, 12")
      self.ps1currentVariable.set(u"PS1 Current [mA]:")    # default value in display
      self.ps1currentLabel.grid(column = 0, row = 3, columnspan = 1, sticky = 'W')

      self.ps1IdisplayVariable = Tkinter.StringVar() # variable to call label
      global isetPS1
      isetPS1 = self.ps1IdisplayVariable
      self.ps1IdisplayLabel = Tkinter.Label(master,textvariable=self.ps1IdisplayVariable,
                                         anchor = "e", fg = "black", bg = "ivory", font = "Arial, 12")
      #self.ps1IdisplayVariable.set(str(float(ps1currentActual * 1000))) #default value in display
      self.ps1IdisplayLabel.grid(column = 1, row = 3, columnspan = 1, sticky = 'W')

      # ------------------------------------------------------------------------
      # Displaying PS2 status (ON/OFF) on master
      # ------------------------------------------------------------------------
      # # Graphical definition of PS2 ON/OFF label
      # self.onoffPS2Variable = Tkinter.StringVar() # variable to call label
      # self.onoffPS2Label = Tkinter.Label(master,textvariable=self.onoffPS2Variable,
      #                                    anchor = "center", fg = "black", bg = 'lightgray', font = "Arial, 12")
      # if runPS2 == 'False':
      #    self.onoffPS2Variable.set(u"PS2: OFF")
      # else:
      #    self.onoffPS2Variable.set(u"PS2: ON")
      # self.onoffPS2Label.grid(column = 5, row = 0, columnspan = 1, sticky = 'W')

      # ------------------------------------------------------------------------
      # Displaying PS2 voltage
      # ------------------------------------------------------------------------
      # # Graphical definition of label
      # self.ps2voltageVariable = Tkinter.StringVar() #variable to call label
      # self.ps2voltageLabel = Tkinter.Label(master,textvariable=self.ps2voltageVariable,
      #                         anchor = "w", fg = "black", bg = 'lightgray', font = "Arial, 12")
      # self.ps2voltageVariable.set(u"PS2 Voltage [V]:")    # default value in display
      # self.ps2voltageLabel.grid(column = 6, row = 2, columnspan = 1, sticky = 'E')

      # self.ps2displayVariable = Tkinter.StringVar() # variable to call label
      # global vsetPS2
      # vsetPS2 = self.ps2displayVariable
      # self.ps2displayLabel = Tkinter.Label(master,textvariable=self.ps2displayVariable,
      #                                    anchor = "e", fg = "black", bg = "ivory", font = "Arial, 12")
      # self.ps2displayVariable.set(str(ps2Voltage)) #default value in display
      # self.ps2displayLabel.grid(column = 7, row = 2, columnspan = 1, sticky = 'E')

      # ------------------------------------------------------------------------
      # Displaying PS2 current
      # ------------------------------------------------------------------------
      # Graphical definition of label
      # self.ps2currentVariable = Tkinter.StringVar() #variable to call label
      # self.ps2currentLabel = Tkinter.Label(master,textvariable=self.ps2currentVariable,
      #                         anchor = "w", fg = "black", bg = 'lightgray', font = "Arial, 12")
      # self.ps2currentVariable.set(u"PS2 Current [mA]:")    # default value in display
      # self.ps2currentLabel.grid(column = 6, row = 3, columnspan = 1, sticky = 'E')

      # self.ps2IdisplayVariable = Tkinter.StringVar() # variable to call label
      # global isetPS2
      # isetPS2 = self.ps2IdisplayVariable
      # self.ps2IdisplayLabel = Tkinter.Label(master,textvariable=self.ps2IdisplayVariable,
      #                                    anchor = "e", fg = "black", bg = "ivory", font = "Arial, 12")
      # self.ps2IdisplayVariable.set(str(float(ps2currentActual * 1000))) #default value in display
      # self.ps2IdisplayLabel.grid(column = 7, row = 3, columnspan = 1, sticky = 'E')

      # ------------------------------------------------------------------------
      # Displaying last data acquisition
      # ------------------------------------------------------------------------
      # Graphical definition of label
      self.lastdAcqVariable = Tkinter.StringVar() #variable to call label
      self.lastdAcqLabel = Tkinter.Label(master,textvariable=self.lastdAcqVariable,
                              anchor = "w", fg = "black", bg = 'lightgray', font = "Arial, 12")
      self.lastdAcqVariable.set(u"Last datalog:")    # default value in display
      self.lastdAcqLabel.grid(column = 0, row = 5, columnspan = 1, sticky = 'W')

      self.lastdAcqdisplayVariable = Tkinter.StringVar() # variable to call label
      global lastdAcq
      lastdAcq = self.lastdAcqdisplayVariable
      self.lastdAcqdisplayLabel = Tkinter.Label(master,textvariable=self.lastdAcqdisplayVariable,
                                         anchor = "w", fg = "black", bg = "ivory", font = "Arial, 12")
      self.lastdAcqdisplayVariable.set(str(' ')) #default value in display
      self.lastdAcqdisplayLabel.grid(column = 1, row = 5, columnspan = 1, sticky = 'W')

      # ------------------------------------------------------------------------
      # Displaying Timer
      # ------------------------------------------------------------------------
      # Graphical definition of label
      self.timerVariable = Tkinter.StringVar() # variable to call label
      self.timerLabel = Tkinter.Label(master,textvariable=self.timerVariable,
                              anchor = "w", fg = "black", bg = 'lightgray', font = "Arial, 12")
      self.timerVariable.set(u"Datalog timer [min]:")    # default value in display
      self.timerLabel.grid(column = 0, row = 6, columnspan = 1, sticky = 'W')

      self.timerdisplayVariable = Tkinter.StringVar() # variable to call label
      global timer
      timer = self.timerdisplayVariable
      self.timerdisplayLabel = Tkinter.Label(master,textvariable=self.timerdisplayVariable,
                                         anchor = "e", fg = "black", bg = "ivory", font = "Arial, 12")
      self.timerdisplayVariable.set(str(' ')) # default value in display
      self.timerdisplayLabel.grid(column = 1, row = 6, sticky = 'E')

      # ------------------------------------------------------------------------
      # Displaying Graphic trends for PSx currents
      # ------------------------------------------------------------------------

      global f1
      # global f2
      global var1
      # global var2
      global canvas1
      # global canvas2
      f1 = Figure(figsize = (3,3), dpi = 90, tight_layout = True)
      # f2 = Figure(figsize = (3,3), dpi = 90, tight_layout = True)
      var1 = f1.add_subplot(111)
      # var2 = f2.add_subplot(111)
      var1.set_title('PS1 Current')
      # var2.set_title('PS2 Current')
      var1.set_xlabel('t [h]')
      # var2.set_xlabel('t [h]')
      var1.set_ylabel('I [mA]')
      # var2.set_ylabel('I [mA]')
      # var1.set_xlim((0,24))
      # var2.set_xlim((0,24))
      # var1.set_ylim((0,500))
      # var2.set_ylim((0,500))
      var1.plot([],[])
      # var2.plot([],[])
      canvas1 = FigureCanvasTkAgg(f1, master)
      # canvas2 = FigureCanvasTkAgg(f2, master)
      canvas1.show()
      # canvas2.show()
      canvas1.get_tk_widget().grid(column = 0, row = 1, columnspan = 3, padx = 10, pady = 10, sticky = 'W') #graph position
      # canvas2.get_tk_widget().grid(column = 5, row = 1, columnspan = 3, padx = 10, pady = 10, sticky = 'W') #graph position

      master.grid_columnconfigure(0,weight=1) #configure column 0 to resize with a weight of 1
      master.resizable(False,False) # a constraints allowing resizeable along horizontally(column)
                                    # (false) and not vertically(rows)--false)
      master.update()
      master.geometry(master.geometry())       #prevents the window from resizing all the time

   global animate
   def animate(i):
      global tGraphic
      global i1Graphic
      # global i2Graphic
      global var1
      # global var2

      var1.clear()
      var1.plot(tGraphic,i1Graphic)
      # var2.clear()
      # var2.plot(tGraphic,i2Graphic)

   # COMMANDS Definition
   # Graphical definition of Settings button
   def Settings(self):  # Defines what SETTINGS button does
      global daqInterval
      global fileName
      global ps1Voltage
      global ps1maxCurrent
      # global ps2Voltage
      # global ps2maxCurrent

      self.Settings = Tkinter.Toplevel()
      self.Settings.configure(background='lightgray')
      # self.Settings.geometry('410x235+500+200')
      self.Settings.title("MECs Power Supply Settings")
      self.Settings.grid() # Initializing grid

      # ------------------------------------------------------------------------
      # Filename definition
      # ------------------------------------------------------------------------
      # Graphical definition of Filename label
      self.Settings.filenameVariable = Tkinter.StringVar() # variable to call label
      self.Settings.filenameLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.filenameVariable,
                              anchor = "w", fg = "black", bg = 'lightgray', font = "Arial, 12")
      self.Settings.filenameVariable.set(u"Filename:")    # default value in display

      # Graphical definition of Filename text entry
      self.Settings.filename = Tkinter.StringVar()    # variable to call text entry
      self.Settings.filenameEntry = Tkinter.Entry(self.Settings,textvariable=self.Settings.filename,
                                                  font = ('Arial', 10), width = 15, justify = 'center')    # text entry
      self.Settings.filename.set(fileName)     # default text prompt
      fileName = str(self.Settings.filename.get())

      self.Settings.filenameLabel.grid(column = 0, row = 0, columnspan = 1, sticky = 'W')
      self.Settings.filenameEntry.grid(column = 1, row = 0, columnspan = 1, sticky = 'W')

      # ------------------------------------------------------------------------
      # Setting the filename for data acquisition
      # Graphic definition of SET button
      self.Settings.setFilename = Tkinter.Button(self.Settings, text = "SET", command = self.setFilename,
                              anchor = "center", fg = "black", bg = 'lightgray', font = "Arial, 12") # Button uses the settings function
      self.Settings.setFilename.grid(column = 2, row = 0, columnspan = 1, sticky = 'W')

      # ------------------------------------------------------------------------
      # Configuration of voltage, current and status (ON/OFF) of PS1
      # ------------------------------------------------------------------------

      try:
         ps1Voltage = ps1.voltage_set       # Initial voltage definition for PS1
      except Exception:
         ps1Voltage = ps1Voltage
         pass

      try:
         ps1maxCurrent = ps1.current_set       # Initial current definition for PS1
      except Exception:
         ps1maxCurrent = ps1maxCurrent
         pass

      # ------------------------------------------------------------------------
      # PS1 Voltage
      self.Settings.ps1V = Tkinter.StringVar()  # variable to call label
      self.Settings.ps1VLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps1V,
                              anchor = "w", fg = "black", bg = 'lightgray', font = "Arial, 12")
      self.Settings.ps1V.set(u"PS1 Set Voltage:")       # Default value in display
      self.Settings.ps1Vv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps1VValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps1Vv,
                                                  font = ('Arial', 10), width = 5, justify = 'center') # text entry
      self.Settings.ps1Vv.set(str(ps1Voltage))     # Default text prompt

      self.Settings.ps1VLabel.grid(column = 0, row = 2, columnspan = 1, sticky = 'W')
      self.Settings.ps1VValue.grid(column = 1, row = 2, columnspan = 1, sticky = 'W')

      # Max PS1 Voltage
      self.Settings.ps1Vmax = Tkinter.StringVar()  # variable to call label
      self.Settings.ps1VmaxLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps1Vmax,
                              anchor = "w", fg = "black", bg = 'lightgray', font = "Arial, 12")
      self.Settings.ps1Vmax.set(u"PS1 Max. Voltage:")       # Default value in display
      self.Settings.ps1Vmaxv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps1VmaxValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps1Vmaxv,
                                                  font = ('Arial', 10), width = 5, justify = 'center') # text entry
      self.Settings.ps1Vmaxv.set(str(userdefined_MaxPS1Voltage))     # Default text prompt

      self.Settings.ps1VmaxLabel.grid(column = 2, row = 2, columnspan = 1, sticky = 'W')
      self.Settings.ps1VmaxValue.grid(column = 3, row = 2, columnspan = 1, sticky = 'W')

      # ------------------------------------------------------------------------
      # PS1 Current
      self.Settings.ps1I = Tkinter.StringVar()  # variable to call label
      self.Settings.ps1ILabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps1I,
                              anchor = "w", fg = "black", bg = 'lightgray', font = "Arial, 12")
      self.Settings.ps1I.set(u"PS1 Set Max. Current:")       # Default value in display
      self.Settings.ps1Iv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps1IValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps1Iv,
                                                  font = ('Arial', 10), width = 5, justify = 'center') # text entry
      self.Settings.ps1Iv.set(str(ps1maxCurrent))     # Default text prompt

      self.Settings.ps1ILabel.grid(column = 0, row = 3, columnspan = 1, sticky = 'W')
      self.Settings.ps1IValue.grid(column = 1, row = 3, columnspan = 1, sticky = 'W')

      # ------------------------------------------------------------------------
      # Setting the voltage and current to PS1
      # Graphic definition of SET button
      self.Settings.setPS1 = Tkinter.Button(self.Settings, text = "SET", command = self.setPS1,
                              anchor = "center", fg = "black", bg = 'lightgray', font = "Arial, 12") # Button uses the settings function
      self.Settings.setPS1.grid(column = 2, row = 4, columnspan = 1, sticky = 'W')

      # ------------------------------------------------------------------------
      # Turning PS1 ON
      # Graphic definition of ON button for PS1
      self.Settings.onPS1 = Tkinter.Button(self.Settings, text = "ON", command = self.onPS1,
                              anchor = "center", fg = "black", bg = 'lightgray', font = "Arial, 12") # Button uses the settings function
      self.Settings.onPS1.grid(column = 4, row = 2, columnspan = 1, sticky = 'NESW')
      # ------------------------------------------------------------------------
      # Turning PS1 OFF
      # Graphic definition of ON button for PS1
      self.Settings.offPS1 = Tkinter.Button(self.Settings, text = "OFF", command = self.offPS1,
                              anchor = "center", fg = "black", bg = 'lightgray', font = "Arial, 12") # Button uses the settings function
      self.Settings.offPS1.grid(column = 4, row = 3, columnspan = 1, sticky = 'NESW')

      # ------------------------------------------------------------------------
      # Configuration of voltage, current and status (ON/OFF) of PS2
      # ------------------------------------------------------------------------

      # try:
         # ps2Voltage = ps2.voltage_set       # Initial voltage definition for PS2
      # except Exception:
         # ps2Voltage = ps2Voltage
         # pass

      # try:
         # ps2maxCurrent = ps2.current_set       # Initial current definition for PS2
      # except Exception:
         # ps2maxCurrent = ps2maxCurrent
         # pass

      # ------------------------------------------------------------------------
      # PS2 Voltage
      # self.Settings.ps2V = Tkinter.StringVar()  # variable to call label
      # self.Settings.ps2VLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps2V,
      #                         anchor = "w", fg = "black", bg = 'lightgray', font = "Arial, 12")
      # self.Settings.ps2V.set(u"PS2 Set Voltage:")       # Default value in display
      # self.Settings.ps2Vv = Tkinter.StringVar()    # variable to call text entry
      # self.Settings.ps2VValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps2Vv,
      #                                             font = ('Arial', 10), width = 5, justify = 'center') # text entry
      # self.Settings.ps2Vv.set(str(ps2Voltage))     # Default text prompt
      #
      # self.Settings.ps2VLabel.grid(column = 0, row = 5, columnspan = 1, sticky = 'W')
      # self.Settings.ps2VValue.grid(column = 1, row = 5, columnspan = 1, sticky = 'W')

      # Max PS2 Voltage
      # self.Settings.ps2Vmax = Tkinter.StringVar()  # variable to call label
      # self.Settings.ps2VmaxLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps2Vmax,
      #                         anchor = "w", fg = "black", bg = 'lightgray', font = "Arial, 12")
      # self.Settings.ps2Vmax.set(u"PS2 Max. Voltage:")       # Default value in display
      # self.Settings.ps2Vmaxv = Tkinter.StringVar()    # variable to call text entry
      # self.Settings.ps2VmaxValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps2Vmaxv,
      #                                             font = ('Arial', 10), width = 5, justify = 'center') # text entry
      # self.Settings.ps2Vmaxv.set(str(userdefined_MaxPS2Voltage))     # Default text prompt
      #
      # self.Settings.ps2VmaxLabel.grid(column = 2, row = 5, columnspan = 1, sticky = 'W')
      # self.Settings.ps2VmaxValue.grid(column = 3, row = 5, columnspan = 1, sticky = 'W')

      # ------------------------------------------------------------------------
      # PS2 Current
      # self.Settings.ps2I = Tkinter.StringVar()  # variable to call label
      # self.Settings.ps2ILabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps2I,
      #                         anchor = "w", fg = "black", bg = 'lightgray', font = "Arial, 12")
      # self.Settings.ps2I.set(u"PS2 Max. Current")       # Default value in display
      # self.Settings.ps2Iv = Tkinter.StringVar()    # variable to call text entry
      # self.Settings.ps2IValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps2Iv,
      #                                             font = ('Arial', 10), width = 5, justify = 'center') # text entry
      # self.Settings.ps2Iv.set(str(ps2maxCurrent))     # Default text prompt

      # self.Settings.ps2ILabel.grid(column = 0, row = 6, columnspan = 1, sticky = 'W')
      # self.Settings.ps2IValue.grid(column = 1, row = 6, columnspan = 1, sticky = 'W')

     # ------------------------------------------------------------------------
      # Setting the voltage and current to PS2
      # Graphic definition of SET button
      # self.Settings.setPS2 = Tkinter.Button(self.Settings, text = "SET", command = self.setPS2,
      #                         anchor = "center", fg = "black", bg = 'lightgray', font = "Arial, 12") # Button uses the settings function
      # self.Settings.setPS2.grid(column = 2, row = 7, columnspan = 1, sticky = 'W')

      # ------------------------------------------------------------------------
      # Turning PS2 ON
      # Graphic definition of ON button for PS1
      # self.Settings.onPS2 = Tkinter.Button(self.Settings, text = "ON", command = self.onPS2,
      #                         anchor = "center", fg = "black", bg = 'lightgray', font = "Arial, 12") # Button uses the settings function
      # self.Settings.onPS2.grid(column = 4, row = 5, columnspan = 1, sticky = 'NESW')
      # ------------------------------------------------------------------------
      # Turning PS2 OFF
      # Graphic definition of ON button for PS1
      # self.Settings.offPS2 = Tkinter.Button(self.Settings, text = "OFF", command = self.offPS2,
      #                         anchor = "center", fg = "black", bg = 'lightgray', font = "Arial, 12") # Button uses the settings function
      # self.Settings.offPS2.grid(column = 4, row = 6, columnspan = 1, sticky = 'NESW')

      # ------------------------------------------------------------------------
      # Definition of DAQ interval label
      self.Settings.daqintervalVariable = Tkinter.StringVar() # variable to call label
      self.Settings.daqintervalLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.daqintervalVariable,
                              anchor = "center", fg  = "black", bg = 'lightgray', font = "Arial, 12")
      self.Settings.daqintervalVariable.set(u"Log interval [min]:")    # default value in display
      self.Settings.daqintervalLabel.grid(column = 0, row = 1, columnspan = 1, sticky = 'W')

      # Definition of DAQ text entry
      self.Settings.daqinterval = Tkinter.StringVar()    # variable to call text entry
      self.Settings.daqintervalEntry = Tkinter.Entry(self.Settings,textvariable=self.Settings.daqinterval,
                                                  font = ('Arial', 10), width = 5, justify = 'center')    # text entry
      self.Settings.daqinterval.set(str(daqInterval))     # default text prompt
      self.Settings.daqintervalEntry.grid(column = 1, row = 1, columnspan = 1, sticky = 'W')

      # ------------------------------------------------------------------------
      # Setting the data acquisition interval
      # Graphic definition of SET button
      self.Settings.setdAcqInterval = Tkinter.Button(self.Settings, text = "SET", command = self.setdAcqInterval,
                              anchor = "center", fg = "black", bg = 'lightgray', font = "Arial, 12") # Button uses the settings function
      self.Settings.setdAcqInterval.grid(column = 2, row = 1, columnspan = 1, sticky = 'W')

      def on_closing():
         global ps1Vini
         global ps1Vmaxini
         global ps1Imaxini
         # global ps2Vini
         # global ps2Vmaxini
         # global ps2Imaxini
         global runPS1
         # global runPS2
         global daqInterval

         cfgfile = open("C:/Python2716/PS Development/JC_Code/INI/ps1Settings.ini",'w') #INI file creation. I would take this from the final code. This is just for the test
         parser = SafeConfigParser()

         parser.read(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI\ps1Settings.ini")
         parser.add_section('Settings')
         parser.set('Settings', 'ps1Voltage', ps1Vini)
         # parser.set('Settings', 'ps2Voltage', ps2Vini)
         parser.set('Settings', 'ps1Current', ps1Imaxini)
         # parser.set('Settings', 'ps2Current', ps2Imaxini)
         parser.set('Settings', 'userdefined_MaxPS1Voltage', ps1Vmaxini)
         # parser.set('Settings', 'userdefined_MaxPS2Voltage', ps2Vmaxini)
         parser.set('Settings', 'runPS1', runPS1)
         # parser.set('Settings', 'runPS2', runPS2)
         parser.set('Settings', 'dAqInterval', str(daqInterval))
         parser.set('Settings', 'dAqON', dAqON)
         with open(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI\ps1Settings.ini",'wb') as configfile:
            parser.write(configfile)
         configfile.close()
         self.Settings.destroy()

      self.Settings.protocol("WM_DELETE_WINDOW", on_closing)

   # ------------------------------------------------------------------------
   def setFilename(self):
      time.sleep(1)
      global fileName
      global vsetfileName
      self.Settings.filename.set(self.Settings.filename.get())
      fileName = self.Settings.filename.get()
      time.sleep(1)
      vsetfileName.set(fileName)

   def setPS1(self):
      global ps1Voltage
      global userdefined_MaxPS1Voltage
      global maxPSV
      global ps1Vini
      global ps1Vmaxini
      global ps1Imaxini

      # PS1 Voltage
      self.Settings.ps1Vv.set(self.Settings.ps1Vv.get())
      ps1Voltage = float(self.Settings.ps1Vv.get())
      userdefined_MaxPS1Voltage = float(self.Settings.ps1Vmaxv.get())

      if userdefined_MaxPS1Voltage > maxPSV:
         tkMessageBox.showinfo( "Alert", " Specified Max SP for PS1 voltage is greater than PS tolerance ", )
         userdefined_MaxPS1Voltage = max(0,min(userdefined_MaxPS1Voltage,maxPSV))
      self.Settings.ps1Vmaxv.set(userdefined_MaxPS1Voltage)
      ps1Vmaxini = str(self.Settings.ps1Vmaxv.get())

      if ps1Voltage > userdefined_MaxPS1Voltage:
         time.sleep(0.1)
         tkMessageBox.showinfo( "Alert", " Specified voltage SP for PS1 is greater than the defined maximum ", )
         try:
            ps1Voltage = ps1.voltage_set
         except Exception:
           pass

      ps1.voltage = max(0,min(ps1Voltage,userdefined_MaxPS1Voltage)) # set voltage
      time.sleep(0.5)
      try:
         ps1Voltage = ps1.voltage_set         # read what you previously set
      except Exception:
         pass

      self.Settings.ps1Vv.set(ps1Voltage)
      time.sleep(0.1)
      ps1Vini = str(self.Settings.ps1Vv.get())
      vsetPS1.set(str(ps1Voltage))

      # PS1 Current
      self.Settings.ps1Iv.set(self.Settings.ps1Iv.get())
      ps1Current = float(self.Settings.ps1Iv.get())

      if ps1Current > maxPSI:
         tkMessageBox.showinfo( "Alert", " Specified Max SP for PS1 current is greater than PS tolerance ", )
         time.sleep(0.1)
         ps1Current = ps1.current_set
      ps1.current = max(0,min(ps1Current,maxPSI)) # set voltage
      ps1currentRead = ps1.current_set         # read what you previously set
      time.sleep(1)
      self.Settings.ps1Iv.set(ps1currentRead)
      ps1Imaxini = str(self.Settings.ps1Iv.get())

   def onPS1(self):
      global runPS1
      try:
         ps1.ovp = 'off'
         ps1.ocp = 'on'
         ps1.cv = 'on'
         ps1.output = 'on'
         time.sleep(1)
         self.onoffPS1Variable.set(u"PS1: ON")    # default value in display
         runPS1 = 'True'
      except Exception:
         pass

   def offPS1(self):
      global runPS1
      try:
         ps1.ovp = 'off'
         ps1.ocp = 'on'
         ps1.cv = 'off'
         ps1.output = 'off'
         time.sleep(1)
         self.onoffPS1Variable.set(u"PS1: OFF")    # default value in display
         runPS1 = 'False'
      except Exception:
         pass

   # ------------------------------------------------------------------------
   # def setPS2(self):
      # global ps2Vini
      # global ps2Vmaxini
      # global ps2Imaxini

      # time.sleep(1)
      # # PS2 Voltage
      # self.Settings.ps2Vv.set(self.Settings.ps2Vv.get())
      # ps2Voltage = float(self.Settings.ps2Vv.get())
      # userdefined_MaxPS2Voltage = float(self.Settings.ps2Vmaxv.get())

      # if userdefined_MaxPS2Voltage > maxPSV:
         # tkMessageBox.showinfo( "Alert", " Specified Max SP for PS2 voltage is greater than PS tolerance ", )
         # userdefined_MaxPS2Voltage = max(0,min(userdefined_MaxPS2Voltage,maxPSV))
      # self.Settings.ps2Vmaxv.set(userdefined_MaxPS2Voltage)
      # ps2Vmaxini = str(self.Settings.ps2Vmaxv.get())

      # if ps2Voltage > userdefined_MaxPS2Voltage:
         # tkMessageBox.showinfo( "Alert", " Specified voltage SP for PS2 is greater than the defined maximum ", )
         # time.sleep(0.1)
         # ps2Voltage = ps2.voltage_set
      # ps2.voltage = max(0,min(ps2Voltage,userdefined_MaxPS2Voltage)) # set voltage
      # time.sleep(0.1)
      # ps2voltageRead = ps2.voltage_set         # read what you previously set
      # self.Settings.ps2Vv.set(ps2voltageRead)
      # time.sleep(0.1)
      # ps2Vini = str(self.Settings.ps2Vv.get())
      # vsetPS2.set(str(ps2voltageRead))

      # # PS2 Current
      # self.Settings.ps2Iv.set(self.Settings.ps2Iv.get())
      # ps2Current = float(self.Settings.ps2Iv.get())

      # if ps2Current > maxPSI:
         # tkMessageBox.showinfo( "Alert", " Specified Max SP for PS2 current is greater than PS tolerance ", )
         # time.sleep(0.1)
         # ps2Current = ps2.current_set
      # ps2.current = max(0,min(ps2Current,maxPSI)) # set voltage
      # time.sleep(0.1)
      # ps2currentRead = ps2.current_set         # read what you previously set
      # self.Settings.ps2Iv.set(ps2currentRead)
      # ps2Imaxini = str(self.Settings.ps2Iv.get())

   # def onPS2(self):
      # global runPS2
      # try:
         # ps2.ovp = 'off'
         # ps2.ocp = 'on'
         # ps2.cv = 'on'
         # ps2.output = 'on'
         # time.sleep(1)
         # self.onoffPS2Variable.set(u"PS2: ON")    # default value in display
         # runPS2 = 'True'
      # except Exception:
         # pass

   # def offPS2(self):
      # global runPS2
      # try:
         # ps2.ovp = 'off'
         # ps2.ocp = 'on'
         # ps2.cv = 'on'
         # ps2.output = 'off'
         # time.sleep(1)
         # self.onoffPS2Variable.set(u"PS2: OFF")    # default value in display
         # runPS2 = 'False'
      # except Exception:
         # pass

   # ------------------------------------------------------------------------
   def setdAcqInterval(self):
      time.sleep(1)
      global daqInterval
      self.Settings.daqinterval.set(self.Settings.daqinterval.get())
      daqInterval = float(self.Settings.daqinterval.get())
      self.Settings.daqinterval.set(daqInterval)

   # ------------------------------------------------------------------------
   def Stop(self):  #defines what a button does
      time.sleep(1)
      global dAcqFlag
      global dAqON
      dAcqFlag = False
      dAqON = 'False'
      self.write_ini()

   # ------------------------------------------------------------------------

   def Start(self):  #defines START button does
      time.sleep(1)
      global dAcqFlag
      global tGraphic
      global i1Graphic
      global i2Graphic
      global dAqON
      dAcqFlag = True
      dAqON = 'True'

      ps1.ovp = 'off'
      ps1.ocp = 'on'
      ps1.cv = 'on'

      # ps2.ovp = 'off'
      # ps2.ocp = 'off'
      # ps2.cv = 'on'

      tGraphic = []
      i1Graphic = []
      # i2Graphic = []
      self.write_ini()

   def write_ini(self):
      global ps1Vini
      global ps1Vmaxini
      global ps1Imaxini
      # global ps2Vini
      # global ps2Vmaxini
      # global ps2Imaxini
      global daqInterval
      global runPS1
      # global runPS2
      cfgfile = open(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI\ps1Settings.ini",'w') #INI file creation. I would take this from the final code. This is just for the test
      parser = SafeConfigParser()
      parser.read(r"C:\Users\adekunlea\Documents\Programming\PowerSup\plyProgram\Version 1\INI\ps1Settings.ini")
      parser.add_section('Settings')
      parser.set('Settings', 'ps1Voltage', ps1Vini)
      # parser.set('Settings', 'ps2Voltage', ps2Vini)
      parser.set('Settings', 'ps1Current', ps1Imaxini)
      # parser.set('Settings', 'ps2Current', ps2Imaxini)
      parser.set('Settings', 'userdefined_MaxPS1Voltage', ps1Vmaxini)
      # parser.set('Settings', 'userdefined_MaxPS2Voltage', ps2Vmaxini)
      parser.set('Settings', 'runPS1', runPS1)
      # parser.set('Settings', 'runPS2', runPS2)
      parser.set('Settings', 'dAqInterval', str(daqInterval))
      parser.set('Settings', 'dAqON', dAqON)
      with open(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI\ps1Settings.ini",'wb') as configfile:
         parser.write(configfile)
      configfile.close()


def on_closing_Main():
   global ps1Vini
   global ps1Vmaxini
   global ps1Imaxini
   # global ps2Vini
   # global ps2Vmaxini
   # global ps2Imaxini
   global daqInterval
   global runPS1
   # global runPS2
   cfgfile = open(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI\ps1Settings.ini",'w') #INI file creation. I would take this from the final code. This is just for the test
   parser = SafeConfigParser()
   parser.read(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI\ps1Settings.ini")
   parser.add_section('Settings')
   parser.set('Settings', 'ps1Voltage', ps1Vini)
   # parser.set('Settings', 'ps2Voltage', ps2Vini)
   parser.set('Settings', 'ps1Current', ps1Imaxini)
   # parser.set('Settings', 'ps2Current', ps2Imaxini)
   parser.set('Settings', 'userdefined_MaxPS1Voltage', ps1Vmaxini)
   # parser.set('Settings', 'userdefined_MaxPS2Voltage', ps2Vmaxini)
   parser.set('Settings', 'runPS1', runPS1)
   # parser.set('Settings', 'runPS2', runPS2)
   parser.set('Settings', 'dAqInterval', str(daqInterval))
   parser.set('Settings', 'dAqON', dAqON)
   with open(r"C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\INI\ps1Settings.ini",'wb') as configfile:
      parser.write(configfile)
   configfile.close()
   root.destroy()

# ------------------------------------------------------------------------
root = Tk()
my_gui = simpleapp_tk(root)

global a
tGraphic = []
i1Graphic = []
# i2Graphic = []
a = 0
tupdate = int(float(daqInterval) * 60 * 1000) # ms

if not os.path.exists(r'C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\ps1Datalogging'):
   os.makedirs(r'C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\ps1Datalogging') #create folder for documents if it doesnt exist
   os.chdir(r'C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\ps1Datalogging') #change directory to this new folder and save files here

def maincode():
   global dAcqFlag
   global fileName
   global daqInterval
   global isetPS1
   # global isetPS2
   global timer
   global tGraphic
   global i1Graphic
   # global i2Graphic
   global a
   global animate
   global f1
   # global f2
   global dAqON
   global var1
   # global var2
   global canvas1
   # global canvas2

   programStarttime = str(datetime.datetime.now()) #get date and time program starts
   programStart = time.time()

   now = time.time()
   previous_now = now
   firstTime = True

   while True:
      os.chdir(r'C:\Users\adekunlea\Documents\Programming\PowerSupplyProgram\Version 1\ps1Datalogging') #change directory to this new folder and save files here
      tupdate = int(float(daqInterval) * 60 * 1000) # ms
      now = time.time()
      if dAqON == 'True':
         dAcqFlag = True
      try:
         isetPS1.set(str(float(ps1.current_actual * 1000)))
      except Exception:
         pass
      # try:
         # isetPS2.set(str(float(ps2.current_actual * 1000)))
      # except Exception:
         # pass
      if dAcqFlag:
         dAcqTimer = round(max(0,((previous_now + daqInterval * 60) - now)/60),2)
         timer.set(str(dAcqTimer))
      if not dAcqFlag:
         dAcqTimer = 0
      # 2 different communication attempts are necessary, so if 1 power supply does not work,
      # we can keep on working with the second
      try:
         date = datetime.datetime.now()
         ps1V = ps1.voltage_set
         ps1C = ps1.current_actual
         time.sleep(1)
      except Exception:
         pass
      # try:
         # date = datetime.datetime.now()
         # ps2V = ps2.voltage_set
         # ps2C = ps2.current_actual
         # time.sleep(1)
      # except Exception:
         # pass

      if firstTime and dAcqFlag:
         saveFile = open(fileName,"a") #for calling the filename where data has been saved
         # headers = ['Date', 'Vps1', 'Ips1', 'Vps2','Ips2']
         headers = ['Date', 'Vps1', 'Ips1']
         headers = ' '.join(headers)
         saveFile.write(headers +'\n') #write headers to file
         # data = [str(date),str(ps1V),str(ps1C),str(ps2V),str(ps2C)]
         data = [str(date),str(ps1V),str(ps1C)]
         data = ' '.join(data)
         saveFile.write(data + '\n') # write data to file
         saveFile.close()
         lastdAcq.set(str(datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")))
         firstTime = False
         tGraphic = tGraphic + [a]
         i1Graphic = i1Graphic + [float(ps1C) * 1000]
         # i2Graphic = i2Graphic + [float(ps2C) * 1000]
         var1 = f1.add_subplot(111)
         # var2 = f2.add_subplot(111)
         var1.clear()
         # var2.clear()
         var1.plot(tGraphic,i1Graphic, 'k:', ls=':', marker='o', color='darkblue')
         # var2.plot(tGraphic,i2Graphic, 'k:', ls=':', marker='o', color='darkblue')
         var1.set_title('PS1 Current')
         # var2.set_title('PS2 Current')
         var1.set_xlabel('t [h]')
         # var2.set_xlabel('t [h]')
         var1.set_ylabel('I [mA]')
         # var2.set_ylabel('I [mA]')
         # var1.set_xlim((0,24))
         # var2.set_xlim((0,24))
         # var1.set_ylim((0,500))
         # var2.set_ylim((0,500))
         var1.plot([],[])
         # var2.plot([],[])
         canvas1.show()
         # canvas2.show()
         canvas1.get_tk_widget().grid(column = 0, row = 1, columnspan = 3, padx = 10, pady = 10, sticky = 'W') #graph position
         # canvas2.get_tk_widget().grid(column = 5, row = 1, columnspan = 3, padx = 10, pady = 10, sticky = 'W') #graph position


      if (now - previous_now) >= (daqInterval * 60) and dAcqFlag:
         previous_now = now
         saveFile = open(fileName,"a") #for calling the filename where data has been saved
         # data = [str(date),str(ps1V),str(ps1C),str(ps2V),str(ps2C)]
         data = [str(date),str(ps1V),str(ps1C)]
         data = ' '.join(data)
         saveFile.write(data +'\n') # write data to file
         saveFile.close()
         lastdAcq.set(str(datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")))
         a += float(daqInterval) / 60.0
         if (len(tGraphic) >= int(round(24.0 / (float(daqInterval) / 60.0)))):
            del tGraphic[0]
            del i1Graphic[0]
            # del i2Graphic[0]
         tGraphic = tGraphic + [a]
         i1Graphic = i1Graphic + [float(ps1C) * 1000]
         # i2Graphic = i2Graphic + [float(ps2C) * 1000]
         var1 = f1.add_subplot(111)
         # var2 = f2.add_subplot(111)
         var1.clear()
         # var2.clear()
         var1.plot(tGraphic,i1Graphic, 'k:', ls=':', marker='o', color='darkblue')
         # var2.plot(tGraphic,i2Graphic, 'k:', ls=':', marker='o', color='darkblue')
         var1.set_title('PS1 Current')
         # var2.set_title('PS2 Current')
         var1.set_xlabel('t [h]')
         # var2.set_xlabel('t [h]')
         var1.set_ylabel('I [mA]')
         # var2.set_ylabel('I [mA]')
         # var1.set_xlim((0,24))
         # var2.set_xlim((0,24))
         # var1.set_ylim((0,500))
         # var2.set_ylim((0,500))
         var1.plot([],[])
         # var2.plot([],[])
         canvas1.show()
         # canvas2.show()
         canvas1.get_tk_widget().grid(column = 0, row = 1, columnspan = 3, padx = 10, pady = 10, sticky = 'W') #graph position
         # canvas2.get_tk_widget().grid(column = 5, row = 1, columnspan = 3, padx = 10, pady = 10, sticky = 'W') #graph position

      #ani1 = animation.FuncAnimation(f1, animate, interval = tupdate)
      #ani2 = animation.FuncAnimation(f2, animate, interval = tupdate)
      # print tupdate

root.update_idletasks()
thread = threading.Thread(target = maincode)
#make measuring thread terminate when the user exits the window
thread.daemon = True
thread.start()

root.protocol("WM_DELETE_WINDOW", on_closing_Main)
root.mainloop()

# ps1.output = 'off'
# ps2.output = 'off'
ps1.close()
# ps2.close()
