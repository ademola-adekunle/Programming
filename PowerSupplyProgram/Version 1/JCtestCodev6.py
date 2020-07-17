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
ps2serialPort = 'COM5' # COMM PORT 2

# Creating a folder for the INI file (startup)
if not os.path.exists('C:/Python27/PS Development/JC_Code/INI'):
   os.makedirs('C:/Python27/PS Development/JC_Code/INI')    # Folder and location for INI file
   os.chdir('C:/Python27/PS Development/JC_Code/INI')       # change directory to this if needed? INI file can be in another directory

if not os.path.exists("C:/Python27/PS Development/JC_Code/INI/psSettings.ini"):
   cfgfile = open("C:/Python27/PS Development/JC_Code/INI/psSettings.ini",'w') #INI file creation. I would take this from the final code. This is just for the test
   parser = SafeConfigParser()
   parser.read("C:/Python27/PS Development/JC_Code/INI/psSettings.ini")
   parser.add_section('Settings')
   parser.set('Settings', 'ps1Voltage', '1.4')
   parser.set('Settings', 'ps2Voltage', '1.4')
   parser.set('Settings', 'ps1Current', '2.0')
   parser.set('Settings', 'ps2Current', '2.0')
   parser.set('Settings', 'userdefined_MaxPS1Voltage', '3.0')
   parser.set('Settings', 'userdefined_MaxPS2Voltage', '3.0')
   parser.set('Settings', 'runPS1', 'False')
   parser.set('Settings', 'runPS2', 'False')
   parser.set('Settings', 'dAqInterval', '20')
   with open("C:/Python27/PS Development/JC_Code/INI/pssettings.ini",'wb') as configfile:
      parser.write(configfile)
   configfile.close()

cfgfile = open("C:/Python27/PS Development/JC_Code/INI/psSettings.ini",'r') #INI file creation. I would take this from the final code. This is just for the test
parser = SafeConfigParser()
parser.read("C:/Python27/PS Development/JC_Code/INI/psSettings.ini")

# Variable definitions
global ps1
global ps2
global ps1Voltage
global ps2Voltage
global ps1maxCurrent
global ps2maxCurrent
global userdefined_MaxPS1Voltage
global userdefined_MaxPS2Voltage
global maxPSV
global maxPSI
global daqInterval
global fileName
global isetPS1
global isetPS2
global tGraphic
global i1Graphic
global i2Graphic

# .ini variables
global ps1Vini
global ps2Vini
global ps1Vmaxini
global ps2Vmaxini
global ps1Imaxini
global ps2Imaxini
global runPS1
global runPS2

maxPSV = 5.0
maxPSI = 5.0
ps1 = KoradSerial(ps1serialPort) # handle def
ps2 = KoradSerial(ps2serialPort) # handle def

# Acquiring initial readings from PS1
ps1currentActual  = ps1.current_actual    # actual current being given out
ps1currentRead    = ps1.current_set         # read what you previously set
ps1deviceStatus   = ps1.status

# Acquiring initial readings from PS2
ps2currentActual  = ps2.current_actual    # actual current being given out
ps2voltageRead    = ps2.voltage_set         # read what you previously set
ps2currentRead    = ps2.current_set         # read what you previously set
ps2deviceStatus   = ps2.status

# Acquiring the values from the INI file
ps1Voltage     = float(parser.get("Settings", 'ps1Voltage'))      # Initial voltage definition for PS1
ps1maxCurrent  = float(parser.get("Settings", 'ps1Current'))     # Initial current definition for PS1
ps2Voltage     = float(parser.get("Settings", 'pS2Voltage'))     # Initial voltage definition for PS1
ps2maxCurrent  = float(parser.get("Settings", 'ps2Current'))     # Initial current definition for PS1
userdefined_MaxPS1Voltage = float(parser.get("Settings", 'userdefined_MaxPS1Voltage'))
userdefined_MaxPS2Voltage = float(parser.get("Settings", 'userdefined_MaxPS2Voltage'))
ps1Vini = str(ps1Voltage)
ps1Vmaxini = str(userdefined_MaxPS1Voltage)
ps1Imaxini = str(ps1maxCurrent)
ps2Vini = str(ps2Voltage)
ps2Vmaxini = str(userdefined_MaxPS2Voltage)
ps2Imaxini = str(ps2maxCurrent)

runPS1 = parser.get("Settings", 'runPS1')
runPS2 = parser.get("Settings", 'runPS2')
daqInterval = float(parser.get("Settings", 'dAqInterval'))

# Closing the INI file
cfgfile.close()

# Assigning the values to the PS
if runPS1 == 'False':
   ps1.output = 'off'
else:
   ps1.output = 'on'
if runPS2 == 'False':
   ps2.output = 'off'
else:
   ps2.output = 'on'

ps1.voltage = ps1Voltage
ps1.current = ps1maxCurrent
ps2.voltage = ps2Voltage
ps2.current = ps2maxCurrent

dAcqFlag = False
fileName = 'Datalogging.txt'
isetPS1 = ps1currentActual
isetPS2 = ps2currentActual

class simpleapp_tk(Tkinter.Tk):
   def __init__(self, master):
      global fileName
      global daqInterval
      
      self.master = master
      master.title('MEC Power Supply Monitoring')
      master.geometry('250x250+200+200')

      # ------------------------------------------------------------------------
      # Displaying the filename
      # ------------------------------------------------------------------------
      # Graphical definition of label
      self.filenameVariable = Tkinter.StringVar() #variable to call label
      self.filenameLabel = Tkinter.Label(master,textvariable=self.filenameVariable,
                              anchor="w",fg="black")
      self.filenameVariable.set(u"Datalogging file:")    # default value in display
      self.filenameLabel.pack()
      self.filenameLabel.place(x = 10, y = 0, width = 100, height = 25) 

      self.filenamedisplayVariable = Tkinter.StringVar() # variable to call label
      global vsetfileName
      vsetfileName = self.filenamedisplayVariable
      self.filenamedisplayLabel = Tkinter.Label(master,textvariable=self.filenamedisplayVariable,
                                         anchor="center",fg="black",bg="ivory")
      self.filenamedisplayVariable.set(fileName) #default value in display
      self.filenamedisplayLabel.pack()
      self.filenamedisplayLabel.place(x = 110, y = 0, width = 100, height = 25) 

      # ------------------------------------------------------------------------
      # BUTTONS Definitions
      # ------------------------------------------------------------------------

      # Graphic definition of SETTINGS button
      self.settingsButton = Tkinter.Button(master, text = "SETTINGS", command = self.Settings,
                              anchor="center",fg="black") # Button uses the settings function
      self.settingsButton.pack()
      self.settingsButton.place(x = 85, y = 100, width = 80, height = 25) 
      
      # Graphic definition of START button
      self.startButton = Tkinter.Button(master, text = "START", command = self.Start,
                              anchor="center",fg="black") # Button uses the Start function
      self.startButton.pack()
      self.startButton.place(x = 85, y = 125, width = 80, height = 25)
      
      # Graphical definition of STOP button
      self.stopButton = Tkinter.Button(master, text = "STOP", command = self.Stop) # Button uses the Stop function
      self.stopButton.pack()
      self.stopButton.place(x = 85, y = 150, width = 80, height = 25)

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
                              anchor="center",fg="black")
      self.onoffPS1Label.pack()
      self.onoffPS1Label.place(x = 10, y = 75, width = 80, height = 25)  
      
      # ------------------------------------------------------------------------
      # Displaying PS1 voltage
      # ------------------------------------------------------------------------
      # Graphical definition of label
      self.ps1voltageVariable = Tkinter.StringVar() #variable to call label
      self.ps1voltageLabel = Tkinter.Label(master,textvariable=self.ps1voltageVariable,
                              anchor="w",fg="black")
      self.ps1voltageVariable.set(u"PS1 Voltage:")    # default value in display
      self.ps1voltageLabel.pack()
      self.ps1voltageLabel.place(x = 10, y = 25, width = 80, height = 25)

      self.ps1VdisplayVariable = Tkinter.StringVar() # variable to call label
      global vsetPS1
      vsetPS1 = self.ps1VdisplayVariable
      self.ps1VdisplayLabel = Tkinter.Label(master,textvariable=self.ps1VdisplayVariable,
                                         anchor="e",fg="black",bg="ivory")
      self.ps1VdisplayVariable.set(str(ps1Voltage)) #default value in display
      self.ps1VdisplayLabel.pack()
      self.ps1VdisplayLabel.place(x = 90, y = 25, width = 30, height = 25)

      # ------------------------------------------------------------------------
      # Displaying PS1 current
      # ------------------------------------------------------------------------
      # Graphical definition of label
      self.ps1currentVariable = Tkinter.StringVar() #variable to call label
      self.ps1currentLabel = Tkinter.Label(master,textvariable=self.ps1currentVariable,
                              anchor="w",fg="black")
      self.ps1currentVariable.set(u"PS1 Current:")    # default value in display
      self.ps1currentLabel.pack()
      self.ps1currentLabel.place(x = 10, y = 50, width = 80, height = 25)

      self.ps1IdisplayVariable = Tkinter.StringVar() # variable to call label
      global isetPS1
      time.sleep(1)
      isetPS1 = self.ps1IdisplayVariable
      self.ps1IdisplayLabel = Tkinter.Label(master,textvariable=self.ps1IdisplayVariable,
                                         anchor="e",fg="black",bg="ivory")
      self.ps1IdisplayVariable.set(str(ps1currentActual)) #default value in display
      self.ps1IdisplayLabel.pack()
      self.ps1IdisplayLabel.place(x = 90, y = 50, width = 30, height = 25)

      # ------------------------------------------------------------------------
      # Displaying PS2 status (ON/OFF) on master
      # ------------------------------------------------------------------------
      # Graphical definition of PS2 ON/OFF label
      self.onoffPS2Variable = Tkinter.StringVar() # variable to call label
      self.onoffPS2Label = Tkinter.Label(master,textvariable=self.onoffPS2Variable,
                                            anchor="center",fg="black")
      if runPS2 == 'False':
         self.onoffPS2Variable.set(u"PS2: OFF")
      else:
         self.onoffPS2Variable.set(u"PS2: ON")
      self.onoffPS2Label.pack()
      self.onoffPS2Label.place(x = 135, y = 75, width = 80, height = 25)
      
      # ------------------------------------------------------------------------
      # Displaying PS2 voltage
      # ------------------------------------------------------------------------
      # Graphical definition of label
      self.ps2voltageVariable = Tkinter.StringVar() #variable to call label
      self.ps2voltageLabel = Tkinter.Label(master,textvariable=self.ps2voltageVariable,
                              anchor="w",fg="black")
      self.ps2voltageVariable.set(u"PS2 Voltage:")    # default value in display
      self.ps2voltageLabel.pack()
      self.ps2voltageLabel.place(x = 135, y = 25, width = 80, height = 25)
      
      self.ps2displayVariable = Tkinter.StringVar() # variable to call label
      global vsetPS2
      vsetPS2 = self.ps2displayVariable
      self.ps2displayLabel = Tkinter.Label(master,textvariable=self.ps2displayVariable,
                                         anchor="e",fg="black",bg="ivory")
      self.ps2displayVariable.set(str(ps2Voltage)) #default value in display
      self.ps2displayLabel.pack()
      self.ps2displayLabel.place(x = 215, y = 25, width = 30, height = 25)
      
      # ------------------------------------------------------------------------
      # Displaying PS2 current
      # ------------------------------------------------------------------------
      # Graphical definition of label
      self.ps2currentVariable = Tkinter.StringVar() #variable to call label
      self.ps2currentLabel = Tkinter.Label(master,textvariable=self.ps2currentVariable,
                              anchor="w",fg="black")
      self.ps2currentVariable.set(u"PS2 Current:")    # default value in display
      self.ps2currentLabel.pack()
      self.ps2currentLabel.place(x = 135, y = 50, width = 80, height = 25)

      self.ps2IdisplayVariable = Tkinter.StringVar() # variable to call label
      global isetPS2
      time.sleep(1)
      isetPS2 = self.ps2IdisplayVariable
      self.ps2IdisplayLabel = Tkinter.Label(master,textvariable=self.ps2IdisplayVariable,
                                         anchor="e",fg="black",bg="ivory")
      self.ps2IdisplayVariable.set(str(ps2currentActual)) #default value in display
      self.ps2IdisplayLabel.pack()
      self.ps2IdisplayLabel.place(x = 215, y = 50, width = 30, height = 25)

      # ------------------------------------------------------------------------
      # Displaying last data acquisition
      # ------------------------------------------------------------------------
      # Graphical definition of label
      self.lastdAcqVariable = Tkinter.StringVar() #variable to call label
      self.lastdAcqLabel = Tkinter.Label(master,textvariable=self.lastdAcqVariable,
                              anchor="w",fg="black")
      self.lastdAcqVariable.set(u"Last datalog:")    # default value in display
      self.lastdAcqLabel.pack()
      self.lastdAcqLabel.place(x = 0, y = 185, width = 80, height = 25)

      self.lastdAcqdisplayVariable = Tkinter.StringVar() # variable to call label
      global lastdAcq
      time.sleep(1)
      lastdAcq = self.lastdAcqdisplayVariable
      self.lastdAcqdisplayLabel = Tkinter.Label(master,textvariable=self.lastdAcqdisplayVariable,
                                         anchor="w",fg="black",bg="ivory")
      self.lastdAcqdisplayVariable.set(str(' ')) #default value in display
      self.lastdAcqdisplayLabel.pack()
      self.lastdAcqdisplayLabel.place(x = 80, y = 185, width = 160, height = 25)

      # ------------------------------------------------------------------------
      # Displaying Timer
      # ------------------------------------------------------------------------
      # Graphical definition of label
      self.timerVariable = Tkinter.StringVar() #variable to call label
      self.timerLabel = Tkinter.Label(master,textvariable=self.timerVariable,
                              anchor="w",fg="black")
      self.timerVariable.set(u"Time before next datalog:")    # default value in display
      self.timerLabel.pack()
      self.timerLabel.place(x = 0, y = 210, width = 150, height = 25)

      self.timerdisplayVariable = Tkinter.StringVar() # variable to call label
      global timer
      time.sleep(1)
      timer = self.timerdisplayVariable
      self.timerdisplayLabel = Tkinter.Label(master,textvariable=self.timerdisplayVariable,
                                         anchor="w",fg="black",bg="ivory")
      self.timerdisplayVariable.set(str(' ')) #default value in display
      self.timerdisplayLabel.pack()
      self.timerdisplayLabel.place(x = 190, y = 210, width = 50, height = 25)
      
   # COMMANDS Definition
   # Graphical definition of Settings button
   def Settings(self):  # Defines what SETTINGS button does
      global daqInterval
      global fileName
      global ps1Voltage
      global ps1maxCurrent
      global ps2Voltage
      global ps2maxCurrent
      
      self.Settings = Tkinter.Toplevel()
      self.Settings.geometry('410x235+500+200')
      self.Settings.title("MECs Power Supply Settings")

      # ------------------------------------------------------------------------
      # Filename definition
      # ------------------------------------------------------------------------
      # Graphical definition of Filename label
      self.Settings.filenameVariable = Tkinter.StringVar() # variable to call label
      self.Settings.filenameLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.filenameVariable,
                              anchor="w",fg="black")
      self.Settings.filenameVariable.set(u"Filename:")    # default value in display

      # Graphical definition of Filename text entry
      self.Settings.filename = Tkinter.StringVar()    # variable to call text entry
      self.Settings.filenameEntry = Tkinter.Entry(self.Settings,textvariable=self.Settings.filename)    # text entry
      self.Settings.filename.set(fileName)     # default text prompt
      fileName = str(self.Settings.filename.get())

      self.Settings.filenameLabel.pack()
      self.Settings.filenameLabel.place(x = 10, y = 0, width = 70, height = 25)
      self.Settings.filenameEntry.pack()
      self.Settings.filenameEntry.place(x = 80, y = 0, width = 100, height = 25)

      # ------------------------------------------------------------------------
      # Setting the filename for data acquisition
      # Graphic definition of SET button
      self.Settings.setFilename = Tkinter.Button(self.Settings, text = "SET", command = self.setFilename,
                              anchor="center",fg="black") # Button uses the settings function
      self.Settings.setFilename.pack()
      self.Settings.setFilename.place(x = 190, y = 0, width = 30, height = 25)
      
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
                              anchor="w",fg="black")
      self.Settings.ps1V.set(u"PS1 Set Voltage:")       # Default value in display
      self.Settings.ps1Vv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps1VValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps1Vv) # text entry
      self.Settings.ps1Vv.set(str(ps1Voltage))     # Default text prompt
       
      self.Settings.ps1VLabel.pack()
      self.Settings.ps1VLabel.place(x = 10, y = 25, width = 120, height = 25)
      self.Settings.ps1VValue.pack()
      self.Settings.ps1VValue.place(x = 140, y = 25, width = 30, height = 25)

      # Max PS1 Voltage
      self.Settings.ps1Vmax = Tkinter.StringVar()  # variable to call label
      self.Settings.ps1VmaxLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps1Vmax,
                              anchor="w",fg="black")
      self.Settings.ps1Vmax.set(u"PS1 Max. Voltage:")       # Default value in display
      self.Settings.ps1Vmaxv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps1VmaxValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps1Vmaxv) # text entry
      self.Settings.ps1Vmaxv.set(str(userdefined_MaxPS1Voltage))     # Default text prompt
       
      self.Settings.ps1VmaxLabel.pack()
      self.Settings.ps1VmaxLabel.place(x = 180, y = 25, width = 120, height = 25)
      self.Settings.ps1VmaxValue.pack()
      self.Settings.ps1VmaxValue.place(x = 310, y = 25, width = 30, height = 25)
      
      # ------------------------------------------------------------------------
      # PS1 Current
      self.Settings.ps1I = Tkinter.StringVar()  # variable to call label
      self.Settings.ps1ILabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps1I,
                              anchor="w",fg="black")
      self.Settings.ps1I.set(u"PS1 Set Max. Current:")       # Default value in display
      self.Settings.ps1Iv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps1IValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps1Iv) # text entry
      self.Settings.ps1Iv.set(str(ps1maxCurrent))     # Default text prompt
       
      self.Settings.ps1ILabel.pack()
      self.Settings.ps1ILabel.place(x = 10, y = 50, width = 120, height = 25)
      self.Settings.ps1IValue.pack()
      self.Settings.ps1IValue.place(x = 140, y = 50, width = 30, height = 25)
  
      # ------------------------------------------------------------------------
      # Setting the voltage and current to PS1
      # Graphic definition of SET button
      self.Settings.setPS1 = Tkinter.Button(self.Settings, text = "SET", command = self.setPS1) # Button uses the settings function
      self.Settings.setPS1.pack()
      self.Settings.setPS1.place(x = 310, y = 75, width = 30, height = 25)
      
      # ------------------------------------------------------------------------
      # Turning PS1 ON
      # Graphic definition of ON button for PS1
      self.Settings.onPS1 = Tkinter.Button(self.Settings, text = "ON", command = self.onPS1) # Button uses the settings function
      self.Settings.onPS1.pack()
      self.Settings.onPS1.place(x = 350, y = 25, width = 30, height = 25)
   
      # ------------------------------------------------------------------------
      # Turning PS1 OFF
      # Graphic definition of ON button for PS1
      self.Settings.offPS1 = Tkinter.Button(self.Settings, text = "OFF", command = self.offPS1) # Button uses the settings function
      self.Settings.offPS1.pack()
      self.Settings.offPS1.place(x = 350, y = 50, width = 30, height = 25)

      # ------------------------------------------------------------------------
      # Configuration of voltage, current and status (ON/OFF) of PS2
      # ------------------------------------------------------------------------

      try:
         ps2Voltage = ps2.voltage_set       # Initial voltage definition for PS2
      except Exception:
         ps2Voltage = ps2Voltage
         pass

      try:
         ps2maxCurrent = ps2.current_set       # Initial current definition for PS2
      except Exception:
         ps2maxCurrent = ps2maxCurrent
         pass

      # ------------------------------------------------------------------------
      # PS2 Voltage
      self.Settings.ps2V = Tkinter.StringVar()  # variable to call label
      self.Settings.ps2VLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps2V,
                              anchor="w",fg="black")
      self.Settings.ps2V.set(u"PS2 Set Voltage:")       # Default value in display
      self.Settings.ps2Vv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps2VValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps2Vv) # text entry
      self.Settings.ps2Vv.set(str(ps2Voltage))     # Default text prompt
       
      self.Settings.ps2VLabel.pack()
      self.Settings.ps2VLabel.place(x = 10, y = 100, width = 120, height = 25)
      self.Settings.ps2VValue.pack()
      self.Settings.ps2VValue.place(x = 140, y = 100, width = 30, height = 25)

      # Max PS2 Voltage
      self.Settings.ps2Vmax = Tkinter.StringVar()  # variable to call label
      self.Settings.ps2VmaxLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps2Vmax,
                              anchor="w",fg="black")
      self.Settings.ps2Vmax.set(u"PS2 Max. Voltage:")       # Default value in display
      self.Settings.ps2Vmaxv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps2VmaxValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps2Vmaxv) # text entry
      self.Settings.ps2Vmaxv.set(str(userdefined_MaxPS2Voltage))     # Default text prompt
       
      self.Settings.ps2VmaxLabel.pack()
      self.Settings.ps2VmaxLabel.place(x = 180, y = 100, width = 120, height = 25)
      self.Settings.ps2VmaxValue.pack()
      self.Settings.ps2VmaxValue.place(x = 310, y = 100, width = 30, height = 25)

      # ------------------------------------------------------------------------
      # PS2 Current
      self.Settings.ps2I = Tkinter.StringVar()  # variable to call label
      self.Settings.ps2ILabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps2I,
                              anchor="w",fg="black")
      self.Settings.ps2I.set(u"PS2 Max. Current")       # Default value in display
      self.Settings.ps2Iv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps2IValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps2Iv) # text entry
      self.Settings.ps2Iv.set(str(ps2maxCurrent))     # Default text prompt
       
      self.Settings.ps2ILabel.pack()
      self.Settings.ps2ILabel.place(x = 10, y = 125, width = 120, height = 25)      
      self.Settings.ps2IValue.pack()
      self.Settings.ps2IValue.place(x = 140, y = 125, width = 30, height = 25)        

     # ------------------------------------------------------------------------
      # Setting the voltage and current to PS2
      # Graphic definition of SET button
      self.Settings.setPS2 = Tkinter.Button(self.Settings, text = "SET", command = self.setPS2) # Button uses the settings function
      self.Settings.setPS2.pack()
      self.Settings.setPS2.place(x = 310, y = 150, width = 30, height = 25)
      
      # ------------------------------------------------------------------------
      # Turning PS2 ON
      # Graphic definition of ON button for PS1
      self.Settings.onPS2 = Tkinter.Button(self.Settings, text = "ON", command = self.onPS2) # Button uses the settings function
      self.Settings.onPS2.pack()
      self.Settings.onPS2.place(x = 350, y = 100, width = 30, height = 25)
      
      # ------------------------------------------------------------------------
      # Turning PS2 OFF
      # Graphic definition of ON button for PS1
      self.Settings.offPS2 = Tkinter.Button(self.Settings, text = "OFF", command = self.offPS2) # Button uses the settings function
      self.Settings.offPS2.pack()
      self.Settings.offPS2.place(x = 350, y = 125, width = 30, height = 25)

      # ------------------------------------------------------------------------
      # Graphical definition of DAQ interval label
      self.Settings.daqintervalVariable = Tkinter.StringVar() # variable to call label
      self.Settings.daqintervalLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.daqintervalVariable,
                              anchor="center",fg="black")
      self.Settings.daqintervalVariable.set(u"Log interval [min]:")    # default value in display
      self.Settings.daqintervalLabel.pack()
      self.Settings.daqintervalLabel.place(x = 230, y = 0, width = 100, height = 25)

      # Graphical definition of DAQ text entry
      self.Settings.daqinterval = Tkinter.StringVar()    # variable to call text entry
      self.Settings.daqintervalEntry = Tkinter.Entry(self.Settings,textvariable=self.Settings.daqinterval)    # text entry
      self.Settings.daqinterval.set(str(daqInterval))     # default text prompt
      self.Settings.daqintervalEntry.pack()
      self.Settings.daqintervalEntry.place(x = 330, y = 0, width = 30, height = 25)
      
      # ------------------------------------------------------------------------
      # Setting the data acquisition interval
      # Graphic definition of SET button
      self.Settings.setdAcqInterval = Tkinter.Button(self.Settings, text = "SET", command = self.setdAcqInterval) # Button uses the settings function
      self.Settings.setdAcqInterval.pack()
      self.Settings.setdAcqInterval.place(x = 370, y = 0, width = 30, height = 25)     
   
      def on_closing():
         global ps1Vini
         global ps1Vmaxini
         global ps1Imaxini
         global ps2Vini
         global ps2Vmaxini
         global ps2Imaxini
         global runPS1
         global runPS2
         global daqInterval

         cfgfile = open("C:/Python27/PS Development/JC_Code/INI/psSettings.ini",'w') #INI file creation. I would take this from the final code. This is just for the test
         parser = SafeConfigParser()

         parser.read("C:/Python27/PS Development/JC_Code/INI/psSettings.ini")
         parser.add_section('Settings')
         parser.set('Settings', 'ps1Voltage', ps1Vini)
         parser.set('Settings', 'ps2Voltage', ps2Vini)
         parser.set('Settings', 'ps1Current', ps1Imaxini)
         parser.set('Settings', 'ps2Current', ps2Imaxini)
         parser.set('Settings', 'userdefined_MaxPS1Voltage', ps1Vmaxini)
         parser.set('Settings', 'userdefined_MaxPS2Voltage', ps2Vmaxini)
         parser.set('Settings', 'runPS1', runPS1)
         parser.set('Settings', 'runPS2', runPS2)
         parser.set('Settings', 'dAqInterval', str(daqInterval))
         with open("C:/Python27/PS Development/JC_Code/INI/pssettings.ini",'wb') as configfile:
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
      time.sleep(0.1)
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
      time.sleep(0.1)
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
   def setPS2(self):
      global ps2Vini
      global ps2Vmaxini
      global ps2Imaxini
      
      time.sleep(1)
      # PS2 Voltage 
      self.Settings.ps2Vv.set(self.Settings.ps2Vv.get())
      ps2Voltage = float(self.Settings.ps2Vv.get())
      userdefined_MaxPS2Voltage = float(self.Settings.ps2Vmaxv.get())   

      if userdefined_MaxPS2Voltage > maxPSV:
         tkMessageBox.showinfo( "Alert", " Specified Max SP for PS2 voltage is greater than PS tolerance ", )
         userdefined_MaxPS2Voltage = max(0,min(userdefined_MaxPS2Voltage,maxPSV))
      self.Settings.ps2Vmaxv.set(userdefined_MaxPS2Voltage)
      ps2Vmaxini = str(self.Settings.ps2Vmaxv.get())
      
      if ps2Voltage > userdefined_MaxPS2Voltage:
         tkMessageBox.showinfo( "Alert", " Specified voltage SP for PS2 is greater than the defined maximum ", )
         time.sleep(0.1)
         ps2Voltage = ps2.voltage_set
      ps2.voltage = max(0,min(ps2Voltage,userdefined_MaxPS2Voltage)) # set voltage
      time.sleep(0.1)
      ps2voltageRead = ps2.voltage_set         # read what you previously set
      self.Settings.ps2Vv.set(ps2voltageRead)
      time.sleep(0.1)
      ps2Vini = str(self.Settings.ps2Vv.get())
      vsetPS2.set(str(ps2voltageRead))
      
      # PS2 Current
      self.Settings.ps2Iv.set(self.Settings.ps2Iv.get())
      ps2Current = float(self.Settings.ps2Iv.get())

      if ps2Current > maxPSI:
         tkMessageBox.showinfo( "Alert", " Specified Max SP for PS2 current is greater than PS tolerance ", )
         time.sleep(0.1)
         ps2Current = ps2.current_set
      ps2.current = max(0,min(ps2Current,maxPSI)) # set voltage
      time.sleep(0.1)
      ps2currentRead = ps2.current_set         # read what you previously set
      self.Settings.ps2Iv.set(ps2currentRead)
      ps2Imaxini = str(self.Settings.ps2Iv.get())

   def onPS2(self):
      global a
      global runPS2
      try:
         ps2.ovp = 'off'
         ps2.ocp = 'on'
         ps2.cv = 'on'
         ps2.output = 'on'
         time.sleep(1)
         self.onoffPS2Variable.set(u"PS2: ON")    # default value in display
         a = "PS2: ON"
         runPS2 = 'True'
      except Exception:
         pass

   def offPS2(self):
      global runPS2
      try:
         ps2.ovp = 'off'
         ps2.ocp = 'on'
         ps2.cv = 'on'      
         ps2.output = 'off'
         time.sleep(1)
         self.onoffPS2Variable.set(u"PS2: OFF")    # default value in display
         runPS2 = 'False'
      except Exception:
         pass
         
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
      dAcqFlag = False
         
   # ------------------------------------------------------------------------
   def Start(self):  #defines START button does
      time.sleep(1)
      global dAcqFlag
      dAcqFlag = True
      ps1.ovp = 'off'
      ps1.ocp = 'on'
      ps1.cv = 'on'

      ps2.ovp = 'off'
      ps2.ocp = 'off'
      ps2.cv = 'on'

def on_closing_Main():
   global ps1Vini
   global ps1Vmaxini
   global ps1Imaxini
   global ps2Vini
   global ps2Vmaxini
   global ps2Imaxini
   global daqInterval
   global runPS1
   global runPS2
   cfgfile = open("C:/Python27/PS Development/JC_Code/INI/psSettings.ini",'w') #INI file creation. I would take this from the final code. This is just for the test
   parser = SafeConfigParser()
   parser.read("C:/Python27/PS Development/JC_Code/INI/psSettings.ini")
   parser.add_section('Settings')
   parser.set('Settings', 'ps1Voltage', ps1Vini)
   parser.set('Settings', 'ps2Voltage', ps2Vini)
   parser.set('Settings', 'ps1Current', ps1Imaxini)
   parser.set('Settings', 'ps2Current', ps2Imaxini)
   parser.set('Settings', 'userdefined_MaxPS1Voltage', ps1Vmaxini)
   parser.set('Settings', 'userdefined_MaxPS2Voltage', ps2Vmaxini)
   parser.set('Settings', 'runPS1', runPS1)
   parser.set('Settings', 'runPS2', runPS2)
   parser.set('Settings', 'dAqInterval', str(daqInterval))
   with open("C:/Python27/PS Development/JC_Code/INI/pssettings.ini",'wb') as configfile:
      parser.write(configfile)
   configfile.close()
   root.destroy()
      
# ------------------------------------------------------------------------
root = Tk()
my_gui = simpleapp_tk(root)

global tGraphic
global i1Graphic
global i2Graphic
global a
tGraphic = []
i1Graphic = []
i2Graphic = []
a = 0

if not os.path.exists('/Python27/PS Development/JC_Code/psDatalogging'):
   os.makedirs('/Python27/PS Development/JC_Code/psDatalogging') #create folder for documents if it doesnt exist
   os.chdir('/Python27/PS Development/JC_Code/psDatalogging') #change directory to this new folder and save files here

def maincode():
   global dAcqFlag
   global fileName
   global daqInterval
   global isetPS1
   global isetPS2
   global timer
   global tGraphic
   global i1Graphic
   global i2Graphic
   global a
   programStarttime = str(datetime.datetime.now()) #get date and time program starts
   programStart = time.time()

   now = time.time()
   previous_now = now
   firstTime = True

   while True:
      os.chdir('/Python27/PS Development/JC_Code/psDatalogging') #change directory to this new folder and save files here
      now = time.time()
      try:
         isetPS1.set(str(ps1.current_actual))
      except Exception:
         pass
      try:
         isetPS2.set(str(ps2.current_actual))
      except Exception:
         pass        
      if dAcqFlag:
         dAcqTimer = round(max(0,((previous_now + daqInterval * 60) - now)/60),2)
         timer.set(str(dAcqTimer))
      if not dAcqFlag:
         dAcqTimer = 0         
      time.sleep(0.5)
      try:
         date = datetime.datetime.now()
         ps1V = ps1.voltage_set
         ps1C = ps1.current_actual
         ps2V = ps2.voltage_set
         ps2C = ps2.current_actual
         time.sleep(1)
      except Exception:
         pass
    
      if firstTime and dAcqFlag:
         saveFile = open(fileName,"a") #for calling the filename where data has been saved
         headers = ['Date', 'Vps1', 'Ips1', 'Vps2','Ips2']
         headers = ' '.join(headers)
         saveFile.write(headers +'\n') #write headers to file
         data = [str(date),str(ps1V),str(ps1C),str(ps2V),str(ps2C)]
         data = ' '.join(data)
         saveFile.write(data + '\n') # write data to file
         saveFile.close()
         lastdAcq.set(str(datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")))
         firstTime = False
         tGraphic = tGraphic + [a]
         i1Graphic = i1Graphic + [float(ps1C)]
         i2Graphic = i2Graphic + [float(ps2C)]
            
      if (now - previous_now) >= (daqInterval * 60) and dAcqFlag:
         previous_now = now         
         saveFile = open(fileName,"a") #for calling the filename where data has been saved
         data = [str(date),str(ps1V),str(ps1C),str(ps2V),str(ps2C)]
         data = ' '.join(data)
         saveFile.write(data +'\n') # write data to file
         saveFile.close()
         lastdAcq.set(str(datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")))
         a += float(daqInterval) / 60.0
         if (len(tGraphic) >= int(round(24.0 / (float(daqInterval) / 60.0)))):
            del tGraphic[0]
            del i1Graphic[0]
            del i2Graphic[0]
         tGraphic = tGraphic + [a]
         i1Graphic = i1Graphic + [float(ps1C)]
         i2Graphic = i2Graphic + [float(ps2C)]
         time.sleep(0.1)

      print tGraphic
      print i1Graphic
      print i2Graphic

root.update_idletasks()
thread = threading.Thread(target=maincode)
#make measuring thread terminate when the user exits the window
thread.daemon = True 
thread.start()

root.protocol("WM_DELETE_WINDOW", on_closing_Main)
root.mainloop()
ps1.output = 'off'
ps2.output = 'off'
ps1.close()
ps2.close()
