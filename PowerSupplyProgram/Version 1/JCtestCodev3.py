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
import datetime
import time
from unittest import TestCase, main
import os
import sys
# from click.testing import CliRunner
import tkMessageBox
import threading

from koradserial import KoradSerial, OnOffState, OutputMode
# from koradcli import korad

# Definition of serial ports for 2 power supplies
ps1serialPort = 'COM4' # COMM PORT 1 
ps2serialPort = 'COM7' # COMM PORT 2

# Variable definitions
global ps1
global ps2
global ps1output
global ps2output

ps1 = KoradSerial(ps1serialPort) # handle def
ps2 = KoradSerial(ps2serialPort) # handle def
ps1.output = 'off'
ps2.output = 'off'

# Acquiring initial readings from PS1
ps1voltageActual  = ps1.voltage_actual    # actual voltage being given out
ps1currentActual  = ps1.current_actual    # actual current being given out
ps1voltageRead    = ps1.voltage_set         # read what you previously set
ps1currentRead    = ps1.current_set         # read what you previously set
ps1deviceStatus   = ps1.status
#print current_CH1        # print the current in M1
#print voltage_CH1        # print the voltage in M1
# time.sleep(1)

# Acquiring initial readings from PS2
ps2voltageActual  = ps2.voltage_actual    # actual voltage being given out
ps2currentActual  = ps2.current_actual    # actual current being given out
ps2voltageRead    = ps2.voltage_set         # read what you previously set
ps2currentRead    = ps2.current_set         # read what you previously set
ps2deviceStatus   = ps2.status
ps2output         = ps2.output
time.sleep(1)
# ps.current = 0
# ps.voltage = 0

global ps1Voltage
global ps2Voltage
global ps1maxCurrent
global ps2maxCurrent
global userdefined_MaxPS1Voltage
global userdefined_MaxPS2Voltage
global userdefined_MaxPS1Current
global userdefined_MaxPS2Current
global maxPSV
global maxPSI

ps1Voltage     = ps1voltageRead     # Initial voltage definition for PS1
ps1maxCurrent  = ps1currentRead  # Initial current definition for PS1
ps2Voltage     = ps2voltageRead     # Initial voltage definition for PS1
ps2maxCurrent  = ps2currentRead  # Initial current definition for PS1
userdefined_MaxPS1Voltage = 2.0
userdefined_MaxPS2Voltage = 2.0
userdefined_MaxPS1Current = 2.0
userdefined_MaxPS2Current = 2.0
maxPSV = 5.0
maxPSI = 5.0

global daqInterval
global fileName

daqInterval = 0.1
fileName = 'Datalogging.txt'

dAcqFlag = False

class simpleapp_tk(Tkinter.Tk):
   def __init__(self, master):
      global fileName
      global daqInterval
      self.master = master
      master.title('Por fin')

      # Graphic definition of SETTINGS button
      self.settingsButton = Tkinter.Button(master, text = "SETTINGS", command = self.Settings) # Button uses the settings function
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.settingsButton.pack()
      
      # Graphic definition of START button
      self.startButton = Tkinter.Button(master, text = "START", command = self.Start) # Button uses the Start function
      self.startButton.pack()

      # Graphical definition of STOP button
      self.stopButton = Tkinter.Button(master, text = "STOP", command = self.Stop) # Button uses the Stop function
      self.stopButton.pack()

      # ------------------------------------------------------------------------
      # Displaying PS1 status (ON/OFF) on master
      # ------------------------------------------------------------------------
      # Graphical definition of PS1 ON/OFF label
      self.onoffPS1Variable = Tkinter.StringVar() # variable to call label
      # defaultbg = self.cget('bg')
      self.onoffPS1Label = Tkinter.Label(master,textvariable=self.onoffPS1Variable,
                              anchor="w",fg="black")
      self.onoffPS1Label.grid(column=0,row=2,columnspan=1,sticky='W')   # label position
      self.onoffPS1Variable.set(u"PS1: OFF")      
      self.onoffPS1Label.pack()
      
      # ------------------------------------------------------------------------
      # Displaying PS1 voltage
      # ------------------------------------------------------------------------
      # Graphical definition of label
      self.ps1voltageVariable = Tkinter.StringVar() #variable to call label
      self.ps1voltageLabel = Tkinter.Label(master,textvariable=self.ps1voltageVariable,
                              anchor="w",fg="black")
      self.ps1voltageLabel.grid(column=0,row=2,columnspan=1,sticky='W')   # label position
      self.ps1voltageVariable.set(u"PS1 Voltage:")    # default value in display
      self.ps1voltageLabel.pack()

      self.ps1VdisplayVariable = Tkinter.StringVar() # variable to call label
      global vsetPS1
      vsetPS1 = self.ps1VdisplayVariable
      self.ps1VdisplayLabel = Tkinter.Label(master,textvariable=self.ps1VdisplayVariable,
                                         anchor="w",fg="black",bg="ivory")
      self.ps1VdisplayLabel.grid(column=2,row=4,columnspan=1,sticky='EW') #label position
      self.ps1VdisplayVariable.set(str(ps1voltageRead)) #default value in display
      self.ps1VdisplayLabel.pack()

      # ------------------------------------------------------------------------
      # Displaying PS1 durrent
      # ------------------------------------------------------------------------
      # Graphical definition of label
      self.ps1currentVariable = Tkinter.StringVar() #variable to call label
      self.ps1currentLabel = Tkinter.Label(master,textvariable=self.ps1currentVariable,
                              anchor="w",fg="black")
      self.ps1currentLabel.grid(column=0,row=2,columnspan=1,sticky='W')   # label position
      self.ps1currentVariable.set(u"PS1 Current:")    # default value in display
      self.ps1currentLabel.pack()

      self.ps1IdisplayVariable = Tkinter.StringVar() # variable to call label
      global isetPS1
      isetPS1 = self.ps1IdisplayVariable
      self.ps1IdisplayLabel = Tkinter.Label(master,textvariable=self.ps1IdisplayVariable,
                                         anchor="w",fg="black",bg="ivory")
      self.ps1IdisplayLabel.grid(column=2,row=4,columnspan=1,sticky='EW') #label position
      self.ps1IdisplayVariable.set(str(ps1currentActual)) #default value in display
      self.ps1IdisplayLabel.pack()

      # ------------------------------------------------------------------------
      # Displaying PS2 status (ON/OFF) on master
      # ------------------------------------------------------------------------
      # Graphical definition of PS2 ON/OFF label
      self.onoffPS2Variable = Tkinter.StringVar() # variable to call label
      # defaultbg = self.cget('bg')
      self.onoffPS2Label = Tkinter.Label(master,textvariable=self.onoffPS2Variable,
                              anchor="w",fg="black")
      self.onoffPS2Label.grid(column=0,row=2,columnspan=1,sticky='W')   # label position
      self.onoffPS2Variable.set(u"PS2: OFF")
      self.onoffPS2Label.pack()
      
      # ------------------------------------------------------------------------
      # Displaying PS2 voltage
      # ------------------------------------------------------------------------
      # Graphical definition of label
      self.ps2voltageVariable = Tkinter.StringVar() #variable to call label
      self.ps2voltageLabel = Tkinter.Label(master,textvariable=self.ps2voltageVariable,
                              anchor="w",fg="black")
      self.ps2voltageLabel.grid(column=0,row=2,columnspan=1,sticky='W')   # label position
      self.ps2voltageVariable.set(u"PS2 Voltage:")    # default value in display
      self.ps2voltageLabel.pack()

      self.ps2displayVariable = Tkinter.StringVar() # variable to call label
      global vsetPS2
      vsetPS2 = self.ps2displayVariable
      self.ps2displayLabel = Tkinter.Label(master,textvariable=self.ps2displayVariable,
                                         anchor="w",fg="black",bg="ivory")
      self.ps2displayLabel.grid(column=2,row=4,columnspan=1,sticky='EW') #label position
      self.ps2displayVariable.set(str(ps2voltageRead)) #default value in display
      self.ps2displayLabel.pack()
      
      
   # COMMANDS Definition
   # Graphical definition of Settings button
   def Settings(self):  # Defines what SETTINGS button does
      global daqInterval
      global fileName
      self.Settings = Tkinter.Toplevel()
      self.Settings.geometry('250x750')
      self.Settings.title("MECs Power Supply Configuration")
      # tkMessageBox.showinfo( "Parameter Settings", " Great job, Sir! ")

      # ------------------------------------------------------------------------
      # Filename definition
      # ------------------------------------------------------------------------
      # Graphical definition of Filename label
      self.Settings.filenameVariable = Tkinter.StringVar() # variable to call label
      # defaultbg = self.cget('bg')
      self.Settings.filenameLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.filenameVariable,
                              anchor="w",fg="black")
      self.Settings.filenameLabel.grid(column=0,row=2,columnspan=1,sticky='W')   # label position
      self.Settings.filenameVariable.set(u"Filename:")    # default value in display

      # Graphical definition of Filename text entry
      self.Settings.filename = Tkinter.StringVar()    # variable to call text entry
      self.Settings.filenameEntry = Tkinter.Entry(self.Settings,textvariable=self.Settings.filename)    # text entry
      self.Settings.filenameEntry.grid(column=1,row=2,sticky='W')   # test entry location
      self.Settings.filename.set(fileName)     # default text prompt
      fileName = str(self.Settings.filename.get())

      self.Settings.filenameLabel.pack()
      self.Settings.filenameEntry.pack()

      # ------------------------------------------------------------------------
      # Setting the filename for data acquisition
      # Graphic definition of SET button
      self.Settings.setFilename = Tkinter.Button(self.Settings, text = "SET", command = self.setFilename) # Button uses the settings function
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.setFilename.pack()
      
      # ------------------------------------------------------------------------
      # Configuration of voltage, current and status (ON/OFF) of PS1      
      # ------------------------------------------------------------------------
      
      ps1Voltage     = ps1.voltage_set       # Initial voltage definition for PS1
      ps1maxCurrent  = ps1.current_set       # Initial current definition for PS1

      # ------------------------------------------------------------------------
      # PS1 Voltage
      self.Settings.ps1V = Tkinter.StringVar()  # variable to call label
      self.Settings.ps1VLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps1V,
                              anchor="w",fg="black")
      self.Settings.ps1VLabel.grid(column=0,row=0,columnspan=1,sticky='EW')   # label position
      self.Settings.ps1V.set(u"PS1 Voltage")       # Default value in display
      self.Settings.ps1Vv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps1VValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps1Vv) # text entry
      self.Settings.ps1VValue.grid(column=0,row=0,columnspan=1,sticky='EW')   # text entry position
      self.Settings.ps1Vv.set(str(ps1Voltage))     # Default text prompt
       
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.ps1VLabel.pack()
      self.Settings.ps1VValue.pack()

      # Max PS1 Voltage
      self.Settings.ps1Vmax = Tkinter.StringVar()  # variable to call label
      self.Settings.ps1VmaxLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps1Vmax,
                              anchor="w",fg="black")
      self.Settings.ps1VmaxLabel.grid(column=0,row=0,columnspan=1,sticky='EW')   # label position
      self.Settings.ps1Vmax.set(u"PS1 Max. Voltage")       # Default value in display
      self.Settings.ps1Vmaxv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps1VmaxValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps1Vmaxv) # text entry
      self.Settings.ps1VmaxValue.grid(column=0,row=0,columnspan=1,sticky='EW')   # text entry position
      self.Settings.ps1Vmaxv.set(str(userdefined_MaxPS1Voltage))     # Default text prompt
       
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.ps1VmaxLabel.pack()
      self.Settings.ps1VmaxValue.pack()
      
      # ------------------------------------------------------------------------
      # PS1 Current
      self.Settings.ps1I = Tkinter.StringVar()  # variable to call label
      self.Settings.ps1ILabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps1I,
                              anchor="w",fg="black")
      self.Settings.ps1ILabel.grid(column=0,row=0,columnspan=1,sticky='EW')   # label position
      self.Settings.ps1I.set(u"PS1 Max. Current")       # Default value in display
      self.Settings.ps1Iv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps1IValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps1Iv) # text entry
      self.Settings.ps1IValue.grid(column=0,row=0,columnspan=1,sticky='EW')   # text entry position
      self.Settings.ps1Iv.set(str(ps1maxCurrent))     # Default text prompt
       
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.ps1ILabel.pack()
      self.Settings.ps1IValue.pack()

      # Max PS1 Current
      self.Settings.ps1Imax = Tkinter.StringVar()  # variable to call label
      self.Settings.ps1ImaxLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps1Imax,
                              anchor="w",fg="black")
      self.Settings.ps1ImaxLabel.grid(column=0,row=0,columnspan=1,sticky='EW')   # label position
      self.Settings.ps1Imax.set(u"PS1 Max. Current")       # Default value in display
      self.Settings.ps1Imaxv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps1ImaxValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps1Imaxv) # text entry
      self.Settings.ps1ImaxValue.grid(column=0,row=0,columnspan=1,sticky='EW')   # text entry position
      self.Settings.ps1Imaxv.set(str(userdefined_MaxPS1Current))     # Default text prompt
       
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.ps1ImaxLabel.pack()
      self.Settings.ps1ImaxValue.pack()
      
      # ------------------------------------------------------------------------
      # Setting the voltage and current to PS1
      # Graphic definition of SET button
      self.Settings.setPS1 = Tkinter.Button(self.Settings, text = "SET", command = self.setPS1) # Button uses the settings function
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.setPS1.pack()
      
      # ------------------------------------------------------------------------
      # Turning PS1 ON
      # Graphic definition of ON button for PS1
      self.Settings.onPS1 = Tkinter.Button(self.Settings, text = "ON", command = self.onPS1) # Button uses the settings function
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.onPS1.pack()
      
      # ------------------------------------------------------------------------
      # Turning PS1 OFF
      # Graphic definition of ON button for PS1
      self.Settings.offPS1 = Tkinter.Button(self.Settings, text = "OFF", command = self.offPS1) # Button uses the settings function
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.offPS1.pack()


      # ------------------------------------------------------------------------
      # Configuration of voltage, current and status (ON/OFF) of PS2
      # ------------------------------------------------------------------------

      ps2Voltage     = ps2.voltage_set       # Initial voltage definition for PS1
      ps2maxCurrent  = ps2.current_set       # Initial current definition for PS1

      # ------------------------------------------------------------------------
      # PS2 Voltage
      self.Settings.ps2V = Tkinter.StringVar()  # variable to call label
      self.Settings.ps2VLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps2V,
                              anchor="w",fg="black")
      self.Settings.ps2VLabel.grid(column=0,row=0,columnspan=1,sticky='EW')   # label position
      self.Settings.ps2V.set(u"PS2 Voltage")       # Default value in display
      self.Settings.ps2Vv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps2VValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps2Vv) # text entry
      self.Settings.ps2VValue.grid(column=0,row=0,columnspan=1,sticky='EW')   # text entry position
      self.Settings.ps2Vv.set(str(ps2Voltage))     # Default text prompt
       
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.ps2VLabel.pack()
      self.Settings.ps2VValue.pack()

      # Max PS2 Voltage
      self.Settings.ps2Vmax = Tkinter.StringVar()  # variable to call label
      self.Settings.ps2VmaxLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps2Vmax,
                              anchor="w",fg="black")
      self.Settings.ps2VmaxLabel.grid(column=0,row=0,columnspan=1,sticky='EW')   # label position
      self.Settings.ps2Vmax.set(u"PS2 Max. Voltage")       # Default value in display
      self.Settings.ps2Vmaxv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps2VmaxValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps2Vmaxv) # text entry
      self.Settings.ps2VmaxValue.grid(column=0,row=0,columnspan=1,sticky='EW')   # text entry position
      self.Settings.ps2Vmaxv.set(str(userdefined_MaxPS2Voltage))     # Default text prompt
       
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.ps2VmaxLabel.pack()
      self.Settings.ps2VmaxValue.pack()

      # ------------------------------------------------------------------------
      # PS2 Current
      self.Settings.ps2I = Tkinter.StringVar()  # variable to call label
      self.Settings.ps2ILabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps2I,
                              anchor="w",fg="black")
      self.Settings.ps2ILabel.grid(column=0,row=0,columnspan=1,sticky='EW')   # label position
      self.Settings.ps2I.set(u"PS2 Max. Current")       # Default value in display
      self.Settings.ps2Iv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps2IValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps2Iv) # text entry
      self.Settings.ps2IValue.grid(column=0,row=0,columnspan=1,sticky='EW')   # text entry position
      self.Settings.ps2Iv.set(str(ps2maxCurrent))     # Default text prompt
       
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.ps2ILabel.pack()
      self.Settings.ps2IValue.pack()

      # Max PS2 Current
      self.Settings.ps2Imax = Tkinter.StringVar()  # variable to call label
      self.Settings.ps2ImaxLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.ps2Imax,
                              anchor="w",fg="black")
      self.Settings.ps2ImaxLabel.grid(column=0,row=0,columnspan=1,sticky='EW')   # label position
      self.Settings.ps2Imax.set(u"PS2 Max. Current")       # Default value in display
      self.Settings.ps2Imaxv = Tkinter.StringVar()    # variable to call text entry
      self.Settings.ps2ImaxValue = Tkinter.Entry(self.Settings,textvariable=self.Settings.ps2Imaxv) # text entry
      self.Settings.ps2ImaxValue.grid(column=0,row=0,columnspan=1,sticky='EW')   # text entry position
      self.Settings.ps2Imaxv.set(str(userdefined_MaxPS2Current))     # Default text prompt
       
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.ps2ImaxLabel.pack()
      self.Settings.ps2ImaxValue.pack()

      # ------------------------------------------------------------------------
      # Setting the voltage and current to PS2
      # Graphic definition of SET button
      self.Settings.setPS2 = Tkinter.Button(self.Settings, text = "SET", command = self.setPS2) # Button uses the settings function
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.setPS2.pack()
      
      # ------------------------------------------------------------------------
      # Turning PS2 ON
      # Graphic definition of ON button for PS1
      self.Settings.onPS2 = Tkinter.Button(self.Settings, text = "ON", command = self.onPS2) # Button uses the settings function
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.onPS2.pack()
      
      # ------------------------------------------------------------------------
      # Turning PS2 OFF
      # Graphic definition of ON button for PS1
      self.Settings.offPS2 = Tkinter.Button(self.Settings, text = "OFF", command = self.offPS2) # Button uses the settings function
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.offPS2.pack()

      # ------------------------------------------------------------------------
      # Graphical definition of DAQ interval label
      self.Settings.daqintervalVariable = Tkinter.StringVar() # variable to call label
      # defaultbg = self.cget('bg')
      self.Settings.daqintervalLabel = Tkinter.Label(self.Settings,textvariable=self.Settings.daqintervalVariable,
                              anchor="w",fg="black")
      self.Settings.daqintervalLabel.grid(column=0,row=2,columnspan=1,sticky='W')   # label position
      self.Settings.daqintervalVariable.set(u"Log interval [min]:")    # default value in display
      self.Settings.daqintervalLabel.pack()

      # Graphical definition of DAQ text entry
      self.Settings.daqinterval = Tkinter.StringVar()    # variable to call text entry
      self.Settings.daqintervalEntry = Tkinter.Entry(self.Settings,textvariable=self.Settings.daqinterval)    # text entry
      self.Settings.daqintervalEntry.grid(column=1,row=2,sticky='W')   # test entry location
      self.Settings.daqinterval.set(str(daqInterval))     # default text prompt
      self.Settings.daqintervalEntry.pack()
      
      # ------------------------------------------------------------------------
      # Setting the data acquisition interval
      # Graphic definition of SET button
      self.Settings.setdAcqInterval = Tkinter.Button(self.Settings, text = "SET", command = self.setdAcqInterval) # Button uses the settings function
      # self.settingsButton.grid(column=1,row=150,sticky='W')
      self.Settings.setdAcqInterval.pack()
      
      
   # ------------------------------------------------------------------------

   def setFilename(self):
      global fileName
      self.Settings.filename.set(self.Settings.filename.get())
      fileName = self.Settings.filename.get()

   def setPS1(self):
      # PS1 Voltage 
      self.Settings.ps1Vv.set(self.Settings.ps1Vv.get())
      ps1Voltage = float(self.Settings.ps1Vv.get())
      userdefined_MaxPS1Voltage = float(self.Settings.ps1Vmaxv.get())   

      if userdefined_MaxPS1Voltage > maxPSV:
         tkMessageBox.showinfo( "Alert", " Specified Max SP for PS1 voltage is greater than PS tolerance ", )
         userdefined_MaxPS1Voltage = max(0,min(userdefined_MaxPS1Voltage,maxPSV))
      self.Settings.ps1Vmaxv.set(userdefined_MaxPS1Voltage)

      if ps1Voltage > userdefined_MaxPS1Voltage:
         tkMessageBox.showinfo( "Alert", " Specified voltage SP for PS1 is greater than the defined maximum ", )
         ps1Voltage = ps1.voltage_set
      ps1.voltage = max(0,min(ps1Voltage,userdefined_MaxPS1Voltage)) # set voltage
      ps1voltageRead = ps1.voltage_set         # read what you previously set
      self.Settings.ps1Vv.set(ps1voltageRead)
      vsetPS1.set(str(ps1voltageRead))
      
      # PS1 Current
      self.Settings.ps1Iv.set(self.Settings.ps1Iv.get())
      ps1Current = float(self.Settings.ps1Iv.get())
      userdefined_MaxPS1Current = float(self.Settings.ps1Imaxv.get())

      if userdefined_MaxPS1Current > maxPSI:
         tkMessageBox.showinfo( "Alert", " Specified Max SP for PS1 current is greater than PS tolerance ", )
         userdefined_MaxPS1Current = max(0,min(userdefined_MaxPS1Current,maxPSV))
      self.Settings.ps1Imaxv.set(userdefined_MaxPS1Current)

      if ps1Current > userdefined_MaxPS1Current:
         tkMessageBox.showinfo( "Alert", " Specified current SP for PS1 is greater than the defined maximum ", )
         ps1Current = ps1.current_set
      ps1.current = max(0,min(ps1Current,userdefined_MaxPS1Current)) # set voltage
      ps1currentRead = ps1.current_set         # read what you previously set
      self.Settings.ps1Iv.set(ps1currentRead)

   def onPS1(self):
      ps1.ovp = 'off'
      ps1.ocp = 'on'
      ps1.cv = 'on'
      ps1.output = 'on'
      
      while ps1.output == 'off':
         ps1.output = 'on'
         if ps1.output == 'on':
            break
      if ps1.output == 'on':
         self.onoffPS1Variable.set(u"PS1: ON")    # default value in display
      # self.ps1voltage.set(str(ps1.voltage_actual))     # default text prompt

   def offPS1(self):
      ps1.ovp = 'off'
      ps1.ocp = 'on'
      ps1.cv = 'off'
      ps1.output = 'off'
      
      while ps1.output == 'on':
         ps1.output = 'off'
         if ps1.output == 'off':
            break
      if ps1.output == 'off':
         self.onoffPS1Variable.set(u"PS1: OFF")    # default value in display

   # ------------------------------------------------------------------------
   def setPS2(self):
      # PS2 Voltage 
      self.Settings.ps2Vv.set(self.Settings.ps2Vv.get())
      ps2Voltage = float(self.Settings.ps2Vv.get())
      userdefined_MaxPS2Voltage = float(self.Settings.ps2Vmaxv.get())   

      if userdefined_MaxPS2Voltage > maxPSV:
         tkMessageBox.showinfo( "Alert", " Specified Max SP for PS2 voltage is greater than PS tolerance ", )
         userdefined_MaxPS2Voltage = max(0,min(userdefined_MaxPS2Voltage,maxPSV))
      self.Settings.ps2Vmaxv.set(userdefined_MaxPS2Voltage)

      if ps2Voltage > userdefined_MaxPS2Voltage:
         tkMessageBox.showinfo( "Alert", " Specified voltage SP for PS2 is greater than the defined maximum ", )
         ps2Voltage = ps2.voltage_set
      ps2.voltage = max(0,min(ps2Voltage,userdefined_MaxPS2Voltage)) # set voltage
      ps2voltageRead = ps2.voltage_set         # read what you previously set
      self.Settings.ps2Vv.set(ps2voltageRead)
      vsetPS2.set(str(ps2voltageRead))
      
      # PS2 Current
      self.Settings.ps2Iv.set(self.Settings.ps2Iv.get())
      ps2Current = float(self.Settings.ps2Iv.get())
      userdefined_MaxPS2Current = float(self.Settings.ps2Imaxv.get())

      if userdefined_MaxPS2Current > maxPSI:
         tkMessageBox.showinfo( "Alert", " Specified Max SP for PS2 current is greater than PS tolerance ", )
         userdefined_MaxPS2Current = max(0,min(userdefined_MaxPS2Current,maxPSV))
      self.Settings.ps2Imaxv.set(userdefined_MaxPS2Current)

      if ps2Current > userdefined_MaxPS2Current:
         tkMessageBox.showinfo( "Alert", " Specified current SP for PS2 is greater than the defined maximum ", )
         ps2Current = ps2.current_set
      ps2.current = max(0,min(ps2Current,userdefined_MaxPS2Current)) # set voltage
      ps2currentRead = ps2.current_set         # read what you previously set
      self.Settings.ps2Iv.set(ps2currentRead)

   def onPS2(self):
      ps2.ovp = 'off'
      ps2.ocp = 'on'
      ps2.cv = 'on'
      ps2.output = 'on'

      while ps2.output == 'off':
         ps2.output = 'on'
         if ps2.output == 'on':
            break
      if ps2.output == 'on':
         self.onoffPS2Variable.set(u"PS2: ON")    # default value in display
         self.ps1VdisplayVariable.set(str(ps1.voltage_set))

   def offPS2(self):
      ps2.ovp = 'off'
      ps2.ocp = 'on'
      ps2.cv = 'on'
      ps2.output = 'off'

      while ps2.output == 'on':
         ps2.output = 'off'
         if ps2.output == 'off':
            break
      if ps2.output == 'off':
         self.onoffPS2Variable.set(u"PS2: OFF")    # default value in display
         
   # ------------------------------------------------------------------------
   def setdAcqInterval(self):
      global daqInterval
      self.Settings.daqinterval.set(self.Settings.daqinterval.get())
      daqInterval = float(self.Settings.daqinterval.get())
      self.Settings.daqinterval.set(daqInterval)
      print self.Settings.daqinterval.get()
      
   # ------------------------------------------------------------------------
   def Stop(self):  #defines what a button does
      global dAcqFlag
      dAcqFlag = False
      # ps1.output = 'off'
      # ps2.output = 'off'

      # self.onoffPS1Variable.set(u"PS1: OFF")    # default value in display
      # self.onoffPS2Variable.set(u"PS2: OFF")    # default value in display
         
   # ------------------------------------------------------------------------
   def Start(self):  #defines START button does
      global dAcqFlag
      dAcqFlag = True
      ps1.ovp = 'off'
      ps1.ocp = 'on'
      ps1.cv = 'on'

      ps2.ovp = 'off'
      ps2.ocp = 'off'
      ps2.cv = 'on'

      #ps.save_to_memory(1)
      # ps1.output = 'on'
      # ps2.output = 'on'

      # self.onoffPS1Variable.set(u"PS1: ON")    # default value in display
      # self.onoffPS2Variable.set(u"PS2: ON")    # default value in display
      
# ------------------------------------------------------------------------
root = Tk()
my_gui = simpleapp_tk(root)


if not os.path.exists('/Python27/PS Development/psDatalogging'):
   os.makedirs('/Python27/PS Development/psDatalogging') #create folder for documents if it doesnt exist
   os.chdir('/Python27/PS Development/psDatalogging') #change directory to this new folder and save files here

def maincode():
   global dAcqFlag
   global fileName
   global daqInterval
   global vsetPS1
   programStarttime = str(datetime.datetime.now()) #get date and time program starts
   programStart = time.time()
   saveFile = open(fileName,"a") #for calling the filename where data has been saved
   headers = ['Date', 'Vps1', 'Ips1', 'Vps2','Ips2']
   headers = ' '.join(headers)
   saveFile.write(headers +'\n') #write headers to file
   saveFile.close()                    

   now = time.time()
   previous_now = now
   firstTime = True

   while True:
      now = time.time()
      if dAcqFlag:
         dAcqTimer = max(0,(previous_now + daqInterval * 60) - now)
      if not dAcqFlag:
         dAcqTimer = 0
      time.sleep(0.5)
      # print dAcqTimer
      if (now - previous_now) >= (daqInterval * 60) and dAcqFlag:
         time.sleep(1)
         print str(datetime.datetime.now())
         previous_now = now
         saveFile = open(fileName,"a") #for calling the filename where data has been saved
         data = [str(datetime.datetime.now()),str(ps1.voltage_set),str(ps1.current_actual),str(ps2.voltage_set),str(ps2.current_actual)]
         data = ' '.join(data)
         saveFile.write(data +'\n') # write data to file
         saveFile.close()  
         time.sleep(0.2)

thread = threading.Thread(target=maincode)
#make measuring thread terminate when the user exits the window
thread.daemon = True 
thread.start()

root.mainloop()
ps1.close()
ps2.close()
