import matplotlib
matplotlib.use ("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation

import Tkinter
from Tkinter import *
import tkMessageBox
import datetime
import os
import random
import time #use time.time() as eqivalent of tic and toc in matlab; time.sleep(1) as equivalent of pause
import numpy as np #for mathematical calculations
# from scipy.integrate import simps #for mathematical calculations
from numpy import trapz #for mathematical calculations
import threading
import ConfigParser
from ConfigParser import SafeConfigParser


#----------------------------------------------------------------------------------------------------------------------------------
# DEFINE VALUES/IMPORT INI FILE

parser=SafeConfigParser()
#parser.read ("/home/pi/Documents/OnlineBiosensor/Configuration/biosensorconfig.ini") #location of biosensor configuration/parameters

tolerance=0.0005 #value to change
ylimit=5
y2limit=5
coundowntimer=60
ps1value=0
ps2value=0


global ps1v


class simpleapp_tk(Tkinter.Tk):
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent=parent
        self.initialize()
        #self.geometry('500x450')
        self.configure(background='lightgray') 
        
    def initialize(self): #initialize GUI
        self.grid() #Initialize GRID



#----------------------------------------------------------------------------------------------------------------------------------
# MAIN SCREEN

        #---------------------------------------------------------
        #BUTTONS & LABELS
        #POWER SUPPLY SETTINGS
        settings_button =Tkinter.Button(self,text=u"SETTINGS",
                               command=self.OnSettingsClick,font=("Helvetica", 16)) #button entry  
        settings_button.grid(column=2,row=10,sticky='EW') #button entry location

        #COUNTDOWNTIMERLABEL
        self.countdowntimerlabelvariable = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        countdown_label = Tkinter.Label(self,textvariable=self.countdowntimerlabelvariable,
                              anchor="w",fg="brown",bg="lightgray",font=("Helvetica", 14)) 
        countdown_label.grid(column=0,row=1,sticky='E', pady=10) #label position
        self.countdowntimerlabelvariable.set(b"Countdown to next reading:") #default value in display
        #COUNTDOWN DISPLAY
        self.countdowntimerdisplayvariable = Tkinter.StringVar() #variable to call label
        global countdowntime
        countdowntime = self.countdowntimerdisplayvariable
        countdowntime_label = Tkinter.Label(self,textvariable=self.countdowntimerdisplayvariable,
                                         anchor="w",fg="black",bg="lightgray", width=6, font=("Helvetica", 16))
        countdowntime_label.grid(column = 1,row = 1,sticky = 'NESW') #label position
        self.countdowntimerdisplayvariable.set(str(coundowntimer)) #default value in display

        #PS1V LABEL
        self.ps1vlabelvariable = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        ps1v_label = Tkinter.Label(self,textvariable=self.ps1vlabelvariable,
                              anchor="w",fg="black",bg="lightgray",font=("Arial", 14)) 
        ps1v_label.grid(column=0,row=2,sticky='NESW') #label position
        self.ps1vlabelvariable.set(b"PS1 applied voltage:") #default value in display
        #PS1V DISPLAY
        self.ps1vdisplayvariable = Tkinter.StringVar() #variable to call label
        global ps1v
        ps1v = self.ps1vdisplayvariable
        ps1v_label = Tkinter.Label(self,textvariable=self.ps1vdisplayvariable,
                                         anchor="w",fg="black",bg="lightgray", width=6,font=("Helvetica", 16))
        ps1v_label.grid(column=1,row=2,sticky='W') #label position
        self.ps1vdisplayvariable.set(str(ps1value)) #default value in display


        #PS2V LABEL
        self.ps2vlabelvariable = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        ps2v_label = Tkinter.Label(self,textvariable=self.ps2vlabelvariable,
                              anchor="w",fg="black",bg="lightgray",font=("Arial", 14)) 
        ps2v_label.grid(column=3,row=2,sticky='EW',) #label position
        self.ps2vlabelvariable.set(b"PS2 applied voltage:") #default value in display
        #PS2V DISPLAY
        self.ps2vdisplayvariable = Tkinter.StringVar() #variable to call label
        global ps2v
        ps2v = self.ps1vdisplayvariable
        ps2v_label = Tkinter.Label(self,textvariable=self.ps2vdisplayvariable,
                                         anchor="w",fg="black",bg="lightgray", width=6,font=("Helvetica", 16))
        ps2v_label.grid(column=4,row=2,sticky='EW',padx=5) #label position
        self.ps2vdisplayvariable.set(str(ps2value)) #default value in display
        

        #PS1C LABEL
        self.ps1clabelvariable = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        ps1c_label = Tkinter.Label(self,textvariable=self.ps1clabelvariable,
                              anchor="w",fg="black",bg="lightgray",font=("Arial", 14)) 
        ps1c_label.grid(column=0,row=3,sticky='NESW') #label position
        self.ps1clabelvariable.set(b"PS1 measured current:") #default value in display
        #PS1V DISPLAY
        self.ps1cdisplayvariable = Tkinter.StringVar() #variable to call label
        global ps1c
        ps1c = self.ps1vdisplayvariable
        ps1c_label = Tkinter.Label(self,textvariable=self.ps1cdisplayvariable,
                                         anchor="w",fg="black",bg="lightgray", width=6,font=("Helvetica", 16))
        ps1c_label.grid(column=1,row=3,sticky='W') #label position
        self.ps1cdisplayvariable.set(str(ps1value)) #default value in display


        #PS2C LABEL
        self.ps2clabelvariable = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        ps2c_label = Tkinter.Label(self,textvariable=self.ps2clabelvariable,
                              anchor="w",fg="black",bg="lightgray",font=("Arial", 14)) 
        ps2c_label.grid(column=3,row=3,sticky='EW') #label position
        self.ps2clabelvariable.set(b"PS2 measured current:") #default value in display
        #PS2C DISPLAY
        self.ps2cdisplayvariable = Tkinter.StringVar() #variable to call label
        global ps2c
        ps2c = self.ps1cdisplayvariable
        ps2c_label = Tkinter.Label(self,textvariable=self.ps2cdisplayvariable,
                                         anchor="w",fg="black",bg="lightgray", width=6,font=("Helvetica", 16))
        ps2c_label.grid(column=4,row=3,sticky='EW') #label position
        self.ps2cdisplayvariable.set(str(ps2value)) #default value in display   







        #---------------------------------------------------------
        #GRAPHS
        global f
        global f2

        f = Figure(figsize=(3,3), dpi=90, tight_layout=True)
        f2 = Figure(figsize=(3,3), dpi=90, tight_layout=True)
        
         
        #FIRST GRAPH
        a=f.add_subplot(111)
        a.set_title('PS1')
        a.set_xlabel('Process Time (h)')
        a.set_ylabel('Current (mA)')
        a.set_ylim([0,ylimit])
        global canvas
        canvas=FigureCanvasTkAgg (f, self)
        canvas.draw()
        canvas.get_tk_widget().grid(column=0,row=9,columnspan=3,padx=10, pady=10, sticky='W') #graph position
        canvas_frame=Frame(self)
        canvas_frame.grid(column=0,row=12,columnspan=2,sticky='W') 
        
##        toolbar_frame= Frame(self)   #New frame to bypass the pack limitation
##        toolbar_frame.grid(column=0,row=12,columnspan=1,sticky='NESW')
##        toolbar=NavigationToolbar2TkAgg(canvas,toolbar_frame)
##        toolbar.update()

        #SECOND GRAPH
        b=f2.add_subplot(111)
        b.set_title('PS2')
        b.set_xlabel('Process Time (h)')
        b.set_ylabel('Current (mA)')
        b.set_ylim([0,y2limit])
        #a.plot([],[])
        global canvas2
        canvas2=FigureCanvasTkAgg (f2, self)
        canvas2.draw()
        canvas2.get_tk_widget().grid(column=3,row=9,columnspan=2,padx=10, pady=10,sticky='W') #graph position
##        toolbar_frame2= Frame(self)   #New frame to bypass the pack limitation
##        toolbar_frame2.grid(column=4,row=12,columnspan=1,sticky='NESW')
##        toolbar2=NavigationToolbar2TkAgg(canvas2,toolbar_frame2)



        #POWER SUPPLIES STATUS DISPLAY
        self.sensordisplay = Tkinter.StringVar() #variable to call label
        global statusdisplay
        statusdisplay=self.sensordisplay
        sensordisplaylabel = Tkinter.Label(self,textvariable=self.sensordisplay,
                              anchor="center",fg="white",bg="black",font=("Helvetica", 14)) #putting a label behind the labels. Labels display text
        sensordisplaylabel.grid(column=0,row=25,columnspan=8,sticky='NESW',padx=10, pady=10) #label position
        self.sensordisplay.set(u"POWER SUPPLY 1 & 2 OFF") #default value in display



        #SIZING PARAMETERS  
        #self.grid_columnconfigure(0,weight=1) #configure column 0 to resize with a weight of 1
        self.resizable(False,False) #a constraints allowing resizeable along horizontally(column)
                                    #(false) and not vertically(rows)--false)
        self.update()
        self.geometry(self.geometry())       #prevents the window from resizing all the time


#----------------------------------------------------------------------------------------------------------------------------------
# SETTINGS SCREEN
    def OnSettingsClick(self): #w
        self.settings=Tkinter.Toplevel()
        self.settings.title("Control Parameters")
        self.settings.geometry('250x300')

        #FILENAME
        self.settings.filename = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        settings_label = Tkinter.Label(self.settings,textvariable=self.settings.filename,
                              anchor="w",fg="black",bg=defaultbg) 
        settings_label.grid(column=0,row=0,columnspan=1,sticky='EW') #label position
        self.settings.filename.set(u"Filename") #default value in display
        self.settings.filenamev = Tkinter.StringVar() #variable to call text entry
        settings_value= Tkinter.Entry(self.settings,textvariable=self.settings.filenamev) #text entry
        settings_value.grid(column=1,row=0,sticky='NW') #text entry location
        self.settings.filenamev.set(u"MEC_Data.txt") #default text prompt


        #TOLERANCE
        self.settings.tolerance = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        settings_label = Tkinter.Label(self.settings,textvariable=self.settings.tolerance,
                              anchor="w",fg="black",bg=defaultbg) 
        settings_label.grid(column=0,row=1,columnspan=1,sticky='EW') #label position
        self.settings.tolerance.set(u"Tolerance") #default value in display
        self.settings.tolerancev = Tkinter.StringVar() #variable to call text entry
        settings_value= Tkinter.Entry(self.settings,textvariable=self.settings.tolerancev) #text entry
        settings_value.grid(column=1,row=1,sticky='NW') #text entry location
        self.settings.tolerancev.set(str(tolerance)) #default text prompt
        

        



if __name__ == "__main__": #creation of main. This is where you put your main code
    app = simpleapp_tk(None)
    app.title('MEC POWER SUPPLY PROGRAM') #title of application



app.mainloop()
    

