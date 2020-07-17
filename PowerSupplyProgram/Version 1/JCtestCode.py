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

from unittest import TestCase, main
# from click.testing import CliRunner
import Tkinter
from Tkinter import *
import tkMessageBox
import datetime
import time

from koradserial import KoradSerial, OnOffState, OutputMode
# from koradcli import korad

# Definition of serial ports for 2 power supplies
ps1serialPort = 'COM4' #change this to the serialport number..this was for my computer
ps2serialPort = 'COM5' #change this to the serialport number..this was for my computer

ps1 = KoradSerial(ps1serialPort) # handle def
ps2 = KoradSerial(ps2serialPort) # handle ref

class simpleapp_tk(Tkinter.Tk):
    def __init__(root,parent):
        Tkinter.Tk.__init__(root,parent)
        root.parent = parent
        root.initialize()

    def initialize(root): # initialize GUI
       root.grid() # Layout manager

       # Graphic definition of SETTINGS button
       f = Frame(root, height = 100, width = 100)
       f.pack_propagate(0)
       f.pack()

       settingsButton = Tkinter.Button(f, text = "SETTINGS", command = root.Settings) # Button uses the settings function
       settingsButton.grid(column=1,row=150,sticky='W')

       # Graphic definition of START button
       runStart = Tkinter.Button(root, text = "START", command = Start) # Button uses the Start function
       runStart.pack()

       # Graphical definition of STOP button
       runStop = Tkinter.Button(root, text = "STOP", command = Stop) # Button uses the Stop function
       runStop.pack()

   # COMMANDS Definition
   # Graphical definition of Settings button
   
    def Settings():  # Defines what SETTINGS button does
      psSettings = Tk()
      psSettings.geometry('250x250')
      psSettings.title("MECs Power Supply Configuration")
      # tkMessageBox.showinfo( "Parameter Settings", " Great job, Sir! ")


    def Stop():  #defines what a button does
      STOP = True
      print STOP

    def Start():  #defines START button does
       ps1voltageActual = ps1.voltage_actual #actual voltage being given out
       ps1currentActual = ps1.current_actual #actual current being given out
       ps1voltageRead = ps1.voltage_set   #read what you previously set
       ps1currentRead = ps1.current_set   #read what you previously set
       ps1deviceStatus = ps1.status
       print ps1voltageActual  #actual voltage being given out
       print ps1currentActual  #actual current being given out
       print ps1voltageRead    #voltage set by the program
       print ps1currentRead    #current set by the program
       print ps1deviceStatus   #device status during operation
       #print current_CH1     #print the current in M1
       #print voltage_CH1      #print the voltage in M1
       time.sleep(1)

       ps2voltageActual = ps2.voltage_actual #actual voltage being given out
       ps2currentActual = ps2.current_actual #actual current being given out
       ps2voltageRead = ps2.voltage_set   #read what you previously set
       ps2currentRead = ps2.current_set   #read what you previously set
       ps2deviceStatus = ps2.status
       print ps2voltageActual  #actual voltage being given out
       print ps2currentActual  #actual current being given out
       print ps2voltageRead    #voltage set by the program
       print ps2currentRead    #current set by the program
       print ps2deviceStatus   #device status during operation
       time.sleep(1)
       #ps.current = 0
       #ps.voltage = 0
       ps1.close()
       ps2.close()   

# Setting the electrical parameters and power source configuration
ps1.current = 5.0 #set current
ps1.voltage = 1.4 #set voltage
ps1.ovp = 'off'
ps1.ocp = 'on'
ps1.cv = 'on'

ps2.current = 5.0 #set current
ps2.voltage = 1.4 #set voltage
ps2.ovp = 'off'
ps2.ocp = 'off'
ps2.cv = 'on'

#ps.save_to_memory(1) #save this values to memory 1 of the PS
#ps.recall_from_memory(1) #recall the values from memory 1 of the PS
#current_CH1, voltage_CH1 = ps.current_set, ps.voltage_set
#ps.save_to_memory(1)
ps1.output = 'off'
ps2.output = 'off'

# Defining the main window for Power Supplies (PS) Remote Operation
root = Tk()
psSettings = Tk()
root.geometry('500x500')
root.title("MECs Power Supply Remote Operation")
global STOP
STOP = False

# Graphical definition of Settings button
f = Frame(root, height = 100, width = 100)
f.pack_propagate(0)
f.pack()

def Settings():  # Defines what SETTINGS button does
   psSettings = Tk()
   psSettings.geometry('250x250')
   psSettings.title("MECs Power Supply Configuration")
   # tkMessageBox.showinfo( "Parameter Settings", " Great job, Sir! ")

B = Tkinter.Button(f, text = "SETTINGS", command = Settings) # Button uses the settings function
B.grid(column=1,row=150,sticky='W')

def SetV1():  # Defines what SETTINGS button does
   ps2.current = 5.0 #set current
   ps2.voltage = 2.8 #set voltage

B = Tkinter.Button(psSettings, text = "SET", command = SetV1) # Button uses the SetV1 function
B.pack()

def Start():  #defines START button does
       # tkMessageBox.showinfo( "Parameter", " Great job! ")
        ps1voltageActual = ps1.voltage_actual #actual voltage being given out
        ps1currentActual = ps1.current_actual #actual current being given out
        ps1voltageRead = ps1.voltage_set   #read what you previously set
        ps1currentRead = ps1.current_set   #read what you previously set
        ps1deviceStatus = ps1.status
        print ps1voltageActual  #actual voltage being given out
        print ps1currentActual  #actual current being given out
        print ps1voltageRead    #voltage set by the program
        print ps1currentRead    #current set by the program
        print ps1deviceStatus   #device status during operation
        #print current_CH1     #print the current in M1
        #print voltage_CH1      #print the voltage in M1
        time.sleep(1)

        ps2voltageActual = ps2.voltage_actual #actual voltage being given out
        ps2currentActual = ps2.current_actual #actual current being given out
        ps2voltageRead = ps2.voltage_set   #read what you previously set
        ps2currentRead = ps2.current_set   #read what you previously set
        ps2deviceStatus = ps2.status
        print ps2voltageActual  #actual voltage being given out
        print ps2currentActual  #actual current being given out
        print ps2voltageRead    #voltage set by the program
        print ps2currentRead    #current set by the program
        print ps2deviceStatus   #device status during operation
        #print current_CH1     #print the current in M1
        #print voltage_CH1      #print the voltage in M1
        time.sleep(1)
        #ps.current = 0
        #ps.voltage = 0
    
        # ps1.close()
        # ps2.close()

# Graphical definition of START button
B = Tkinter.Button(root, text = "START", command = Start) # Button uses the Start function
B.pack()

def Stop():  #defines what a button does
    STOP = True
    print STOP

# Graphical definition of STOP button
B = Tkinter.Button(root, text = "STOP", command = Stop) # Button uses the Stop function
B.pack()

root.mainloop()
