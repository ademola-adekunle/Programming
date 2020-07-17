import matplotlib
matplotlib.use ("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import matplotlib.animation as animation

import Tkinter
from Tkinter import *
import datetime
import os
import random
import u3
import time #use time.time() as eqivalent of tic and toc in matlab; time.sleep(1) as equivalent of pause
import numpy as np #for mathematical calculations
from scipy.integrate import simps #for mathematical calculations
from numpy import trapz #for mathematical calculations
import threading
import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read ("/home/pi/Documents/OnlineBiosensor/Configuration/biosensorconfig.ini") #location of biosensor configuration/parameters



def ConfigSectionMap(section):  #define function for biosensorini parser
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

#read initialization file
tolerance=float(ConfigSectionMap ("Parameters")['tolerance']) #value to change
Vmin=float(ConfigSectionMap ("Parameters")['vmin'])#lower boundary
alpha1=float(ConfigSectionMap ("Parameters")['alpha1']) #voltage filter
graphspan=float(ConfigSectionMap ("Parameters")['graphspan']) #span of graph
filesaveflag=float(ConfigSectionMap ("Parameters")['filesaveflag']) #default is not to save
restarter=float(ConfigSectionMap ("Parameters")['restarter']) #does the program need to start acquisition?
delay=float(ConfigSectionMap ("Parameters")['delay'])#time to wait for signal to stabilize when connected
ylimit=float(ConfigSectionMap ("Parameters")['ylimit'])#ylim of graph
vminacq=float(ConfigSectionMap ("Parameters")['vminacq'])#vmin acq speed
vmaxacq=float(ConfigSectionMap ("Parameters")['vmaxacq'])#vmin acq speed
steadyrepeat=float(ConfigSectionMap ("Parameters")['steadyrepeat'])#repeat values n times to determine steady state for vmax
datalog=float(ConfigSectionMap ("Parameters")['datalog']) #datalog in s
ocvwait=float(ConfigSectionMap ("Parameters")['ocvwait']) #datalog in s
vminwait=float(ConfigSectionMap ("Parameters")['vminwait']) #datalog in s
steadyrepeatvmin=float(ConfigSectionMap ("Parameters")['steadyrepeatvmin'])#repeat values n times to determine steady state for vmin
Vmax_Est=0.00
Vmin_Est=0.00
MFCreading=0.00
tempV=0.00
Sensoroutput=0.00
timevec=[0]
sensorvec=[0]
global flag
flag=0.00 #program always start off




class simpleapp_tk(Tkinter.Tk):
    global self
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent=parent
        self.initialize()
    global self  
    def initialize(self): #initialize GUI
        self.grid() #Layout manager
    def initialize(self): #getvalues
        self.grid() #Layout manager

        
        
        #PARAMETER BUTTON
        parameter_button =Tkinter.Button(self,text=u"Biosensing Parameters",
                               command=self.OnParameterClick) #button entry
        parameter_button.grid(column=0,row=0,sticky='W') #button entry location

##        #FILENAME_LABEL
##        self.filenamevariable = Tkinter.StringVar() #variable to call label
##        defaultbg = self.cget('bg')
##        filename_label = Tkinter.Label(self,textvariable=self.filenamevariable,
##                              anchor="w",fg="black",bg=defaultbg) 
##        filename_label.grid(column=0,row=1,sticky='E') #label position
##        self.filenamevariable.set(u"Filename") #default value in display
##        
##        #FILENAME_TEXTENTRY
##        self.filename = Tkinter.StringVar() #variable to call text entry
##        self.entry = Tkinter.Entry(self,textvariable=self.filename) #text entry
##        self.entry.grid(column=1,row=1,sticky='W') #test entry location
##        self.filename.set(u"logfile.txt") #default text prompt
                                                                                   

        #SAVE checkBUTTON
        global var1
        var1 = Tkinter.IntVar()
        save_button =Tkinter.Checkbutton(self,text=u"save",variable=var1,
                               command=self.OnButtonClick) #button entry
        save_button.select()
        save_button.grid(column=2, row=1) #button entry location
        
        #START BUTTON
        start_button =Tkinter.Button(self,text=u"Start",
                               command=self.OnStartClick, bg="green") #button entry
        start_button.grid(column=2,row=2,sticky='EW') #button entry location

        #STOP BUTTON
        stop_button =Tkinter.Button(self,text=u"Stop",
                               command=self.OnStopClick, bg="red") #button entry
        stop_button.grid(column=2,row=3,sticky='EW') #button entry location
        
        #MFC VOLTAGE DISPLAY
        self.mfcdisplayvariable = Tkinter.StringVar() #variable to call label
        global voltageset
        voltageset=self.mfcdisplayvariable
        mfcdisplay_label = Tkinter.Label(self,textvariable=self.mfcdisplayvariable,
                                         anchor="w",fg="black",bg="ivory")
        mfcdisplay_label.grid(column=1,row=2,sticky='NESW') #label position
        self.mfcdisplayvariable.set(str(MFCreading)) #default value in display

        #SENSOR OUTPUT VALUE
        self.sensorvdisplayvariable = Tkinter.StringVar() #variable to call label
        global sensorvset
        sensorvset=self.sensorvdisplayvariable
        sensorvdisplay_label = Tkinter.Label(self,textvariable=self.sensorvdisplayvariable,
                                         anchor="w",fg="black",bg="lavender")
        sensorvdisplay_label.grid(column=1,row=3,sticky='NESW') #label position
        self.sensorvdisplayvariable.set(str(Sensoroutput)) #default value in display

        #MSENSORV_LABEL
        self.sensorvlabelvariable = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        sensorv_label = Tkinter.Label(self,textvariable=self.sensorvlabelvariable,
                              anchor="w",fg="black",bg=defaultbg) 
        sensorv_label.grid(column=0,row=3,sticky='E') #label position
        self.sensorvlabelvariable.set(u"Vmax / Vmin") #default value in display

        #MFCV_LABEL
        self.mfclabelvariable = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        mfc_label = Tkinter.Label(self,textvariable=self.mfclabelvariable,
                              anchor="w",fg="black",bg=defaultbg) 
        mfc_label.grid(column=0,row=2,sticky='E') #label position
        self.mfclabelvariable.set(u"MFC voltage (mV)") #default value in display

        #MVMAX_EST LABEL
        self.vmaxlabelvariable = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        vmax_label = Tkinter.Label(self,textvariable=self.vmaxlabelvariable,
                              anchor="w",fg="black",bg=defaultbg) 
        vmax_label.grid(column=0,row=4,sticky='E') #label position
        self.vmaxlabelvariable.set(u"Current Vmax (mV)") #default value in display

        #VMIN_EST LABEL
        self.vminlabelvariable = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        vmin_label = Tkinter.Label(self,textvariable=self.vminlabelvariable,
                              anchor="w",fg="black",bg=defaultbg)
        #vmin_label.tag_configure("subscript", offset=-4)
        #vmin_label.insert("insert","Vmin","-i-1","subscript","mV")
        #vmin_label.configure(state="disabled")
        vmin_label.grid(column=0,row=5,sticky='E') #label position
        self.vminlabelvariable.set(u"Current Vmin(mV)") #default value in display

        #VMAX_EST DISPLAY
        self.vmaxdisplayvariable = Tkinter.StringVar() #variable to call label
        global vmaxset
        vmaxset=self.vmaxdisplayvariable
        vmaxdisplay_label = Tkinter.Label(self,textvariable=self.vmaxdisplayvariable,
                                         anchor="w",fg="black",bg="lavender")
        vmaxdisplay_label.grid(column=1,row=4,sticky='NESW') #label position
        self.vmaxdisplayvariable.set(str(Vmax_Est)) #default value in display

        #VMIN_EST DISPLAY
        self.vminvdisplayvariable = Tkinter.StringVar() #variable to call label
        global vminvset
        vminvset=self.vminvdisplayvariable
        vminvdisplay_label = Tkinter.Label(self,textvariable=self.vminvdisplayvariable,
                                         anchor="w",fg="black",bg="lavender")
        vminvdisplay_label.grid(column=1,row=5,sticky='NESW') #label position
        self.vminvdisplayvariable.set(str(Vmin_Est)) #default value in display

        #TEMP LABEL
        self.templabelvariable = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        temp_label = Tkinter.Label(self,textvariable=self.templabelvariable,
                              anchor="w",fg="black",bg=defaultbg)
        #vmin_label.tag_configure("subscript", offset=-4)
        #vmin_label.insert("insert","Vmin","-i-1","subscript","mV")
        #vmin_label.configure(state="disabled")
        temp_label.grid(column=0,row=6,sticky='E') #label position
        self.templabelvariable.set(u"Ambient Temp(C)") #default value in display



        #TEMPERATURE DISPLAY
        self.tempvdisplayvariable = Tkinter.StringVar() #variable to call label
        global tempvset
        tempvset=self.tempvdisplayvariable
        tempvdisplay_label = Tkinter.Label(self,textvariable=self.tempvdisplayvariable,
                                         anchor="w",fg="black",bg="lavender")
        tempvdisplay_label.grid(column=1,row=6,sticky='NESW') #label position
        self.tempvdisplayvariable.set(str(tempV)) #default value in display

    
        
        
        #SENSOR_DISPLAY
        self.sensordisplay = Tkinter.StringVar() #variable to call label
        global statusdisplay
        statusdisplay=self.sensordisplay
        sensordisplaylabel = Tkinter.Label(self,textvariable=self.sensordisplay,
                              anchor="center",fg="white",bg="black") #putting a label behind the labels. Labels display text
        sensordisplaylabel.grid(column=0,row=13,columnspan=4,sticky='NESW') #label position
        self.sensordisplay.set(u"MFC-Based Online Biosensor") #default value in display



        #GRAPH
        #self.graphdisplay= Tkinter.StringVar() #variable to call label
        #global graphdisplay
        #graphdisplay=self.graphdisplay
        #graphdisplaylabel = Tkinter.Label(self,textvariable=self.graphdisplay,
                              #anchor="center",fg="white",bg="black") #putting a label behind the labels. Labels display text
        #graphdisplaylabel.grid(column=0,row=7,columnspan=3,sticky='NESW') #label position
        #self.graphdisplay.set(u"Relative condition graph") #default value in display

        global f
        f = Figure(figsize=(3,3), dpi=100, tight_layout=True)

        global a
        a=f.add_subplot(111)
       
        a.set_title('Relative activity')
        a.set_xlabel('time (h)')
        a.set_ylabel('Vmax / Vmin')
        a.set_ylim([0,20])
        #a.plot([],[])
        global canvas
        canvas=FigureCanvasTkAgg (f, self)
        canvas.show()
        canvas.get_tk_widget().grid(column=0,row=9,columnspan=3,sticky='NESW') #graph position

        toolbar_frame= Frame(self)   #New frame to bypass the pack limitation
        toolbar_frame.grid(column=0,row=12,columnspan=4,sticky='NESW')
        toolbar=NavigationToolbar2TkAgg(canvas,toolbar_frame)
        toolbar.update()       


        self.grid_columnconfigure(0,weight=1) #configure column 0 to resize with a weight of 1
        self.resizable(True,False) #a constraints allowing resizeable along horizontally(column)
                                    #(true) and not vertically(rows)--false)
        self.update()
        self.geometry(self.geometry())       #prevents the window from resizing all the time

    global animate
    def animate(i):
        global timevec
        global sensorvec
        
        a.clear()     
        a.set_title('Relative activity')
        a.set_xlabel('time (h)')
        a.set_ylabel('sensor output')
        a.set_ylim([0,ylimit])
        a.plot(timevec,sensorvec)
        
        

    def OnParameterClick(self): #what to do when the button is clicked, proceed to add as a command to the button above
        self.parameter=Tkinter.Toplevel()
        self.parameter.title("Sensor Parameters")

        #TOLERANCE
        self.parameter.tolerance = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        tolerance_label = Tkinter.Label(self.parameter,textvariable=self.parameter.tolerance,
                              anchor="w",fg="black",bg=defaultbg) 
        tolerance_label.grid(column=0,row=0,columnspan=1,sticky='EW') #label position
        self.parameter.tolerance.set(u"Tolerance") #default value in display
        self.parameter.tolerancev = Tkinter.StringVar() #variable to call text entry
        tolerance_value= Tkinter.Entry(self.parameter,textvariable=self.parameter.tolerancev) #text entry
        tolerance_value.grid(column=1,row=0,sticky='NW') #text entry location
        self.parameter.tolerancev.set(str(tolerance)) #default text prompt

        #VMIN
        self.parameter.vmin = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        vmin_label = Tkinter.Label(self.parameter,textvariable=self.parameter.vmin,
                              anchor="w",fg="black",bg=defaultbg) 
        vmin_label.grid(column=0,row=1,columnspan=1,sticky='EW') #label position
        self.parameter.vmin.set(u"Vmin (mV)") #default value in display
        self.parameter.vminv = Tkinter.StringVar() #variable to call text entry
        vmin_value= Tkinter.Entry(self.parameter,textvariable=self.parameter.vminv) #text entry
        vmin_value.grid(column=1,row=1,sticky='NW') #text entry location
        self.parameter.vminv.set(str(Vmin)) #default text prompt
        
        #VFILTER
        self.parameter.vfilter = Tkinter.DoubleVar() #variable to call label
        defaultbg = self.cget('bg')
        vfilter_label = Tkinter.Label(self.parameter,textvariable=self.parameter.vfilter,
                              anchor="w",fg="black",bg=defaultbg) 
        vfilter_label.grid(column=0,row=2,columnspan=1,sticky='EW') #label position
        self.parameter.vfilter.set(u"Vfilter(alpha)") #default value in display
        self.parameter.vfilterv = Tkinter.StringVar() #variable to call text entry
        vfilter_value= Tkinter.Entry(self.parameter,textvariable=self.parameter.vfilterv) #text entry
        vfilter_value.grid(column=1,row=2,sticky='NW') #text entry location
        self.parameter.vfilterv.set(str(alpha1)) #default text prompt

        #GRAPH SPAN
        self.parameter.gspan = Tkinter.DoubleVar() #variable to call label
        defaultbg = self.cget('bg')
        gspan_label = Tkinter.Label(self.parameter,textvariable=self.parameter.gspan,
                              anchor="w",fg="black",bg=defaultbg) 
        gspan_label.grid(column=0,row=3,columnspan=1,sticky='EW') #label position
        self.parameter.gspan.set(u"Graph Span (h)") #default value in display
        self.parameter.gspan = Tkinter.StringVar() #variable to call text entry
        gspan_value= Tkinter.Entry(self.parameter,textvariable=self.parameter.gspan) #text entry
        gspan_value.grid(column=1,row=3,sticky='NW') #text entry location
        self.parameter.gspan.set(str(graphspan)) #default text prompt

        #DELAY
        self.parameter.delay = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        delay_label = Tkinter.Label(self.parameter,textvariable=self.parameter.delay,
                              anchor="w",fg="black",bg=defaultbg) 
        delay_label.grid(column=0,row=4,columnspan=1,sticky='EW') #label position
        self.parameter.delay.set(u"delay(s)") #default value in display
        self.parameter.delayv = Tkinter.StringVar() #variable to call text entry
        delay_value= Tkinter.Entry(self.parameter,textvariable=self.parameter.delayv) #text entry
        delay_value.grid(column=1,row=4,sticky='NW') #text entry location
        self.parameter.delayv.set(str(delay)) #default text prompt

        #YLIMIT
        self.parameter.ylimit = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        ylimit_label = Tkinter.Label(self.parameter,textvariable=self.parameter.ylimit,
                              anchor="w",fg="black",bg=defaultbg) 
        ylimit_label.grid(column=0,row=5,columnspan=1,sticky='EW') #label position
        self.parameter.ylimit.set(u"ylimit") #default value in display
        self.parameter.ylimitv = Tkinter.StringVar() #variable to call text entry
        ylimit_value= Tkinter.Entry(self.parameter,textvariable=self.parameter.ylimitv) #text entry
        ylimit_value.grid(column=1,row=5,sticky='NW') #text entry location
        self.parameter.ylimitv.set(str(ylimit)) #default text prompt

        #ACQSPEEDVMIN
        self.parameter.vminacq = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        vminacq_label = Tkinter.Label(self.parameter,textvariable=self.parameter.vminacq,
                              anchor="w",fg="black",bg=defaultbg) 
        vminacq_label.grid(column=0,row=6,columnspan=1,sticky='EW') #label position
        self.parameter.vminacq.set(u"vminacq (s)") #default value in display
        self.parameter.vminacqv = Tkinter.StringVar() #variable to call text entry
        vminacq_value= Tkinter.Entry(self.parameter,textvariable=self.parameter.vminacqv) #text entry
        vminacq_value.grid(column=1,row=6,sticky='NW') #text entry location
        self.parameter.vminacqv.set(str(vminacq)) #default text prompt

        #ACQSPEEDVMAX
        self.parameter.vmaxacq = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        vmaxacq_label = Tkinter.Label(self.parameter,textvariable=self.parameter.vmaxacq,
                              anchor="w",fg="black",bg=defaultbg) 
        vmaxacq_label.grid(column=0,row=7,columnspan=1,sticky='EW') #label position
        self.parameter.vmaxacq.set(u"vmaxacq (s)") #default value in display
        self.parameter.vmaxacqv = Tkinter.StringVar() #variable to call text entry
        vmaxacq_value= Tkinter.Entry(self.parameter,textvariable=self.parameter.vmaxacqv) #text entry
        vmaxacq_value.grid(column=1,row=7,sticky='NW') #text entry location
        self.parameter.vmaxacqv.set(str(vmaxacq)) #default text prompt

        #PSEUDO STATE REPITITON VMAX
        self.parameter.steadyrepeat = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        steadyrepeat_label = Tkinter.Label(self.parameter,textvariable=self.parameter.steadyrepeat,
                              anchor="w",fg="black",bg=defaultbg) 
        steadyrepeat_label.grid(column=0,row=8,columnspan=1,sticky='EW') #label position
        self.parameter.steadyrepeat.set(u"pseudo state repeat (n)") #default value in display
        self.parameter.steadyrepeatv = Tkinter.StringVar() #variable to call text entry
        steadyrepeat_value= Tkinter.Entry(self.parameter,textvariable=self.parameter.steadyrepeatv) #text entry
        steadyrepeat_value.grid(column=1,row=8,sticky='NW') #text entry location
        self.parameter.steadyrepeatv.set(str(steadyrepeat)) #default text prompt

        #MFC DATA SAVE
        self.parameter.datalog = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        datalog_label = Tkinter.Label(self.parameter,textvariable=self.parameter.datalog,
                              anchor="w",fg="black",bg=defaultbg) 
        datalog_label.grid(column=0,row=9,columnspan=1,sticky='EW') #label position
        self.parameter.datalog.set(u"Data Point Log (s)") #default value in display
        self.parameter.datalogv = Tkinter.StringVar() #variable to call text entry
        datalog_value= Tkinter.Entry(self.parameter,textvariable=self.parameter.datalogv) #text entry
        datalog_value.grid(column=1,row=9,sticky='NW') #text entry location
        self.parameter.datalogv.set(str(datalog)) #default text prompt

        #OCV WAIT
        self.parameter.ocvwait = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        ocvwait_label = Tkinter.Label(self.parameter,textvariable=self.parameter.ocvwait,
                              anchor="w",fg="black",bg=defaultbg) 
        ocvwait_label.grid(column=0,row=10,columnspan=1,sticky='EW') #label position
        self.parameter.ocvwait.set(u"OCV wait (s)") #default value in display
        self.parameter.ocvwaitv = Tkinter.StringVar() #variable to call text entry
        ocvwait_value= Tkinter.Entry(self.parameter,textvariable=self.parameter.ocvwaitv) #text entry
        ocvwait_value.grid(column=1,row=10,sticky='NW') #text entry location
        self.parameter.ocvwaitv.set(str(ocvwait)) #default text prompt


        #VMIN WAIT
        self.parameter.vminwait = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        vminwait_label = Tkinter.Label(self.parameter,textvariable=self.parameter.vminwait,
                              anchor="w",fg="black",bg=defaultbg) 
        vminwait_label.grid(column=0,row=11,columnspan=1,sticky='EW') #label position
        self.parameter.vminwait.set(u"VMIN wait (s)") #default value in display
        self.parameter.vminwaitv = Tkinter.StringVar() #variable to call text entry
        vminwait_value= Tkinter.Entry(self.parameter,textvariable=self.parameter.vminwaitv) #text entry
        vminwait_value.grid(column=1,row=11,sticky='NW') #text entry location
        self.parameter.vminwaitv.set(str(vminwait)) #default text prompt

        #PSEUDO STATE REPITITON VMIN
        self.parameter.steadyrepeatvmin = Tkinter.StringVar() #variable to call label
        defaultbg = self.cget('bg')
        steadyrepeatvmin_label = Tkinter.Label(self.parameter,textvariable=self.parameter.steadyrepeatvmin,
                              anchor="w",fg="black",bg=defaultbg) 
        steadyrepeatvmin_label.grid(column=0,row=12,columnspan=1,sticky='EW') #label position
        self.parameter.steadyrepeatvmin.set(u"pseudo state repeat vmin(n)") #default value in display
        self.parameter.steadyrepeatvminv = Tkinter.StringVar() #variable to call text entry
        steadyrepeatvmin_value= Tkinter.Entry(self.parameter,textvariable=self.parameter.steadyrepeatvminv) #text entry
        steadyrepeatvmin_value.grid(column=1,row=12,sticky='NW') #text entry location
        self.parameter.steadyrepeatvminv.set(str(steadyrepeatvmin)) #default text prompt
        

        

        #SAVE BUTTON
        save_button2 =Tkinter.Button(self.parameter,text=u"save",
                               command=self.OnSaveClick) #button entry
        save_button2.grid(column=1, row=13) #button entry location
        
    #DEFINITIONS OF COMMANDS
        
    def OnSaveClick(self): #this save is in the parameter box
        global tolerance
        global Vmin
        global alpha1
        global graphspan
        global delay
        global ylimit
        global vminacq
        global vmaxacq
        global steadyrepeat
        global steadyrepeatvmin
        global datalog
        global ocvwait
        global vminwait
        self.parameter.tolerancev.set(self.parameter.tolerancev.get())
        tolerance=float(self.parameter.tolerancev.get())
        self.parameter.vminv.set(self.parameter.vminv.get())
        Vmin=float(self.parameter.vminv.get())
        self.parameter.vfilterv.set(self.parameter.vfilterv.get())
        alpha1=float(self.parameter.vfilterv.get())
        self.parameter.destroy()
        graphspan=float(self.parameter.gspan.get())
        self.parameter.destroy()
        delay=float(self.parameter.delayv.get())
        self.parameter.destroy()
        ylimit=float(self.parameter.ylimitv.get())
        self.parameter.destroy()
        vminacq=float(self.parameter.vminacqv.get())
        self.parameter.destroy()
        vmaxacq=float(self.parameter.vmaxacqv.get())
        self.parameter.destroy()
        steadyrepeat=float(self.parameter.steadyrepeatv.get())
        self.parameter.destroy()
        steadyrepeatvmin=float(self.parameter.steadyrepeatvminv.get())
        self.parameter.destroy()
        datalog=float(self.parameter.datalogv.get())
        self.parameter.destroy()
        ocvwait=float(self.parameter.ocvwaitv.get())
        self.parameter.destroy()
        vminwait=float(self.parameter.vminwaitv.get())
        self.parameter.destroy()

        cfgfile=open("/home/pi/Documents/OnlineBiosensor/Configuration/biosensorconfig.ini","w") #overwrite config file to save the most current data
        #Config.add_section('Parameters')
        Config.set('Parameters','tolerance',tolerance)
        Config.set('Parameters','vmin', Vmin)
        Config.set('Parameters','alpha1', alpha1)
        Config.set('Parameters','graphspan', graphspan)
        #Config.set('Parameters','flag', flag)
        Config.set('Parameters','filesaveflag', filesaveflag)
        Config.set('Parameters','restarter', restarter)
        Config.set('Parameters','delay', delay)
        Config.set('Parameters','ylimit', ylimit)
        Config.set('Parameters','vminacq', vminacq)
        Config.set('Parameters','vmaxacq', vmaxacq)
        Config.set('Parameters','steadyrepeat', steadyrepeat)
        Config.set('Parameters','steadyrepeatvmin', steadyrepeatvmin)
        Config.set('Parameters','datalog', datalog)
        Config.set('Parameters','ocvwait', ocvwait)
        Config.set('Parameters','vminwait', vminwait)
        Config.write(cfgfile)
        cfgfile.close()
                                  
   
    def OnStartClick(self): #when start is clicked
        global flag
        flag=1
        restarter=1
        global basetime
        basetime=0
        global start_time
        start_time=time.time()
        global timevec
        timevec=[0]
        global sensorvec
        sensorvec=[0]
        global filesaveflag 
        filesaveflag=var1.get()
##        global filenameprefix
##        filenameprefix=str(self.filename.get())

        if not os.path.exists('/home/pi/Documents/OnlineBiosensor/BiosensingData'):
                            os.makedirs('/home/pi/Documents/OnlineBiosensor/BiosensingData') #create folder for documents if it doesnt exist
        os.chmod("/home/pi/Documents/OnlineBiosensor/BiosensingData", 0777) #make folder write and readable for all
        


        cfgfile=open("/home/pi/Documents/OnlineBiosensor/Configuration/biosensorconfig.ini","w") #overwrite config file to save the most current data
        #Config.add_section('Parameters')
        Config.set('Parameters','tolerance',tolerance)
        Config.set('Parameters','vmin', Vmin)
        Config.set('Parameters','alpha1', alpha1)
        Config.set('Parameters','graphspan', graphspan)
        #Config.set('Parameters','flag', flag)
        Config.set('Parameters','filesaveflag', filesaveflag)
        Config.set('Parameters','restarter', restarter)
        Config.set('Parameters','delay', delay)
        Config.set('Parameters','ylimit', ylimit)
        Config.set('Parameters','vminacq', vminacq)
        Config.set('Parameters','vmaxacq', vmaxacq)
        Config.set('Parameters','steadyrepeat', steadyrepeat)
        Config.set('Parameters','steadyrepeatvmin', steadyrepeatvmin)
        Config.set('Parameters','datalog', datalog)
        Config.set('Parameters','ocvwait', ocvwait)
        Config.set('Parameters','vminwait', vminwait)
        Config.write(cfgfile)
        cfgfile.close()
        
        

    def OnStopClick(self): #when stop is clicked
        global flag
        flag=0
        global restarter
        restarter=0

        cfgfile=open("/home/pi/Documents/OnlineBiosensor/Configuration/biosensorconfig.ini","w") #overwrite config file to save the most current data
        #Config.add_section('Parameters')
        Config.set('Parameters','tolerance',tolerance)
        Config.set('Parameters','vmin', Vmin)
        Config.set('Parameters','alpha1', alpha1)
        Config.set('Parameters','graphspan', graphspan)
        #Config.set('Parameters','flag', flag)
        Config.set('Parameters','filesaveflag', filesaveflag)
        Config.set('Parameters','restarter', restarter)
        Config.set('Parameters','delay', delay)
        Config.set('Parameters','ylimit', ylimit)
        Config.set('Parameters','vminacq', vminacq)
        Config.set('Parameters','vmaxacq', vmaxacq)
        Config.set('Parameters','steadyrepeat', steadyrepeat)
        Config.set('Parameters','steadyrepeatvmin', steadyrepeatvmin)
        Config.set('Parameters','datalog', datalog)
        Config.set('Parameters','ocvwait', ocvwait)
        Config.set('Parameters','vminwait', vminwait)
        Config.write(cfgfile)
        cfgfile.close()
        

    def OnButtonClick(self):
##        global filenameprefix
##        filenameprefix=str(self.filename.get())
        global filesaveflag 
        filesaveflag=var1.get()
            

if __name__ == "__main__": #creation of main. This is where you put your main code
    app = simpleapp_tk(None)
    app.title('MFC Based Online Biosensor') #title of application

    global self
    def __init__(self,parent):
        Tkinter.Tk.__init__(self,parent)
        self.parent=parent
        self.initialize()


    def maincode():  #Biosensing algorithm
        #CONFIGURE LABJACK
        d = u3.U3() #open the first U3 found on the USB
        d.configIO(FIOAnalog = 79) #(79=1001111 binary, so FIO0-FIO3 is set to analog, FI06=analog and the rest to digital...()
        savecounter=0 # define all local variable here or it will repeat after every true.
        profilesaver=10 # this will enable profiles to be saved for 20 minutes in the begining.
        saveprofile=0
        saveprofile2=0
        #profilesaver2=datalog # save data every 20 minutes
        global flag
        global restarter
        global filenameprefix
        global start_time
        start_time=time.time()
        #global timevec
        #timevec=[0]
        #global sensorvec
        #sensorvec=[0]
        global basetime
        basetime=0
        
        
        while True:
            #print flag
##            print Vmin
##            print tolerance
##            print alpha1
            dataacq=1 #data acquisition time during open circuit mode
            state=0


          
            if flag==1:
              
                if filesaveflag==1:
                    savecounter=savecounter+1
##                    #print savecounter
                    if savecounter==1: #helps to save header and filename only once after initialization
                        print "saving & ON"
                        if not os.path.exists('/home/pi/Documents/OnlineBiosensor/BiosensingData'):
                            os.makedirs('/home/pi/Documents/OnlineBiosensor/BiosensingData') #create folder for documents if it doesnt exist
                        os.chdir('/home/pi/Documents/OnlineBiosensor/BiosensingData') #change directory to this new folder and save files here
                        programstarttime=str(datetime.datetime.now()) #get date and time program starts
                        programstart=time.time()
                        profiletimelast=programstart
                        filesuffix=programstarttime[:10]
                        filenameprefixnow='sensoroutputs'
                        #filenameprefixnow=filenameprefixnow[:-4] #get from the gui interface #remove the .txt
                        filename= filenameprefixnow + '.txt' #each file will be used # name will have.txt as type for now
                        filename3='temp&vMFClog' + '.txt' #filename to save MFC profile
                        filename=filename
                        os.chmod("/home/pi/Documents/OnlineBiosensor/BiosensingData", 0777) #make folder write and readable for all
                        save_file= open(filename,"a") #for calling the filename where data has been saved
                        headers=['Date', 'Time', 'Vmax_Est', 'Area', 'OCV_time(s)','Tolerance', 'Vmin', 'alpha1','Vmin_Est','prev_discharge_time','DischargeArea','Ambient_Temperature','Vmax/Vmin','OCVwait','Vminwait','steadystaterepeatocv','steadystaterepeatVmin']
                        headers=' '.join(headers)
                        save_file.write(headers +'\n') #write headers to file
                        save_file.close()
                        filename2=filename
                        save_file2=open(filename3,"a") #for calling the filename where profile has been saved
                        headers2=['Date', 'Time', 'VMFC', 'Temperature']
                        headers2=' '.join(headers2)
                        save_file2.write(headers2 +'\n') #write headers to file
                        save_file2.close()
                        filename4=filename3
##                        print filename
                    else:
                        filename=filename2
##                        print filename
                        
                

                    
  
                    
  
                if state==0:  #MFC is about to be connected to resistor

                    #REINITIALIZE VARIABLES FOR BOTH CHARGE & DISCHARGE CYCLE
                    plateaucounter=0
                    displateaucounter=0
                    voltagelog=[] #initialize voltage log
                    disvoltagelog=[]
                    graphingtime=[] #intialize graphing time
                    timelog=[]
                    distimelog=[]
                    #timevec=timeveca
                    #sensorvec=sensorveca

                    #START DISCHARGE CYCLE
                    d.getFeedback(u3.BitStateWrite(4, 1)) # Set FIO4 to output high therefore connecting resistor & discharging
                    discharge_start=time.time()
                    programtimenow=time.time()
                    discounter=0 #counter for discharge cycle
                    

                    #DELAY CONDITION
                    if 1.0<=Sensoroutput and Sensoroutput<=1.01: #wait for a while if discharge isnt that fast
                            statusdisplay.set(u'BIOSENSOR ON, Resistor Connected, Delay Active, Saving ')
                            time.sleep(delay)
                            
                    #global programstart
                    if (programtimenow-programstart)< profilesaver or savecounter==1: #check if the time for profile saving has elapsed
                        saveprofile=1
                        #profilesaver=profilesaver+profilesaver

                        
                    while state==0: #while MFC is connected to resistor
                        time.sleep(vminacq)

                        tempValue = d.getAIN(6) #get the analog input value from FIO6 which has the temperature sensor
                        tempV=(55.56*tempValue)+255.37-273.5
                        tempV=round(tempV,2)
                        tempvset.set(str(tempV)) #default value in display
                        programtimenow=time.time()
                        
                        ainValue = d.getAIN(1) #get the analog input value from the MFC channel 1, hence AIN(1)
                        ainValue=ainValue*1000 #convert into millivolts
                        

                        if (programtimenow-profiletimelast)>= datalog: #check if the time for profile saving has elapsed
                            saveprofile2=1
                            profiletimelast=time.time()
         
                        
                        if ainValue<=Vmin: #to prevent error
                            ainValue=Vmin
                            Vmin_Est=round(ainValue,2)
                            vminvset.set(str(Vmin_Est)) #display vmin
                            Disarea_curve=trapz(disvoltagelog,distimelog) #integrate and calculate area under dischareg curv
                            discounter=discounter+1
                            discharge_timenow=time.time()
                            discharge_timeelapsed=discharge_timenow-discharge_start
                            MFCreading=round(ainValue,2)
                            voltageset.set(str(MFCreading)) #default value in display

                            discharge_end=time.time()
                            discharge_time=discharge_end-discharge_start

                            state=1
                            d.close() #close labjack
                            break
                            
                        discounter=discounter+1
                        discharge_timenow=time.time()
                        discharge_timeelapsed=discharge_timenow-discharge_start
                        MFCreading=round(ainValue,2)
                        voltageset.set(str(MFCreading)) #default value in display

                        #CHECK IF CONDITION TO CONTINUE SAVING EXISTS
                        if saveprofile==1 or saveprofile2==1: 
                            profiletime=(str(datetime.datetime.now()))[:19]
                            profilestr= (profiletime +' ' + str(MFCreading) +' '+ str(tempV))
                            save_file2= open(filename3,"a") #openfile to save
                            save_file2.write(profilestr +'\n') #write data to file
                            save_file2.close() #close
                            saveprofile2=0

                        #DECIDE WHAT TO DISPLAY ON GUI BASED ON SELECTION    
                        if filesaveflag==1:
                            statusdisplay.set(u'BIOSENSOR ON, Resistor Connected, Saving Enabled')
                        else:
                            statusdisplay.set(u'BIOSENSOR ON, Resistor Connected, Saving Disabled')              

                        #CHECK IF STOP BUTTON HAS BEEN CALLED
                        if flag==0:         #stop button value check
                            break

                        #FILTER VALUES
                        if discounter==1: 
                            ainValue_ftrd=ainValue
                        else:
                            ainValue_ftrd=((alpha1*ainValue)+((1-alpha1)*disvoltagelog[-1]))

                        #TEMPORARILY STORE VALUES   
                        disvoltagelog=disvoltagelog+[ainValue_ftrd] #store discharge voltage in log list initiated earlier
                        distimelog=distimelog+[discharge_timeelapsed]


                        #CHECK PLATEAU CONDITIONS & DO NECESSARY CALCULATIONS

                        if discharge_timeelapsed>vminwait:
                            if len(disvoltagelog)>2:
                                discheck_state=(1-(disvoltagelog[-1]/disvoltagelog[-2]))
                                if (discheck_state >= 0 and discheck_state<=tolerance) or ainValue<Vmin :
                                    displateaucounter=displateaucounter+1
                                else:
                                    displateaucounter=0    
                                #IF PLATEAU CONDITION IS REACHED 3 CONSECUTIVE TIMES
                                if displateaucounter==steadyrepeatvmin: #wait for at specified repeat of the vmin
                                    discharge_end=time.time()
                                    discharge_time=discharge_end-discharge_start
                                    discharge_time=round(discharge_time,2) #round to 2 decimal places
                                    Vmin_Est=disvoltagelog[-1] #estimated Vmin
                                    Vmin_Est=round(Vmin_Est,2)
                                    vminvset.set(str(Vmin_Est)) #display vmin
                                    Disarea_curve=trapz(disvoltagelog,distimelog) #integrate and calculate area under dischareg curve
                                    state=1
                                    d.close() #close labjack
                                    break
                        
                     
                        

                if state==1:    #MFC is now going into open circuit mode
                    d = u3.U3() #reopen the labjack on the USB
                    d.configIO(FIOAnalog = 79) #(15=1111 binary, so FIO0-FIO3 is set to analog and the rest to digital)
                    d.getFeedback(u3.BitStateWrite(4, 0)) #SET FI04 to output low to disconnect resistor
                    OCV_start=time.time()                          
                    counter=0 #reset counter

                    mfcvaluesstore=[] #initiate temp voltage store list
                    while state==1:
                        #time.sleep(dataacq) #wait 1 seconds before every reading in the open circuit phase
                        acquire1=time.time()
                        read=1
                        while read==1:
                            tempValue = d.getAIN(6) #get the analog input value from FIO6 which has the temperature sensor
                            tempV=(55.56*tempValue)+255.37-273.5
                            tempV=round(tempV,2)
                            tempvset.set(str(tempV)) #default value in display
                            ainValue = d.getAIN(1) #get the analog input value from the MFC channel 1, hence AIN(1)
                            mfcvaluesstore=mfcvaluesstore + [ainValue]
                            acquire2=time.time()
                            acquisframe=acquire2-acquire1 #to acquire 5 readings and average
                            if acquisframe>5:
                                acquire1=0
                                acquire2=0
                                read=0
                                break
                        ##                        print ainValue
                        OCV_timenow=time.time()
                        OCVtime_elapsed=OCV_timenow-OCV_start #calculate time elapsed
                        ainValue=np.mean(mfcvaluesstore)
                        mfcvaluesstore=[]
                        ainValue=ainValue*1000 #convert into millivolts
                        MFCreading=round(ainValue,2)
                        voltageset.set(str(MFCreading)) #display value in display
                        programtimenow=time.time()
                        
                        if (programtimenow-profiletimelast)>= datalog: #check if the time for profile saving has elapsed
                            saveprofile2=1
                            profiletimelast=time.time()
                            #profilesaver2=profilesaver2+profilesaver2
                        
                        
                        #saveprofile=1
                        if saveprofile==1 or saveprofile2==1:
                            profiletime=(str(datetime.datetime.now()))[:19]
                            profilestr= (profiletime +' ' + str(MFCreading) +' '+ str(tempV))
                            save_file2= open(filename3,"a") #openfile to save
                            save_file2.write(profilestr +'\n') #write data to file
                            save_file2.close() #close
                            saveprofile2=0
                        if filesaveflag==1:
                            statusdisplay.set(u'BIOSENSOR ON, Open Circuit, Saving Enabled')
                        else:
                            statusdisplay.set(u'BIOSENSOR ON, Open Circuit, Saving Disabled')
                        counter=counter+1 #record it as a step
                        if flag==0: #stop button value check
                            break
                        #apply filter to voltage
                        if counter==1:
                            ainValue_ftrd=ainValue
                        else:
                            ainValue_ftrd=((alpha1*ainValue)+((1-alpha1)*voltagelog[-1]))
                        voltagelog=voltagelog+[ainValue_ftrd] #store voltage in voltage log list initiated earlier
                        timelog=timelog+[OCVtime_elapsed]
                        
##                        print counter
                        #check for plateauing condition after a minimum of specified time for Vmax estimation
                        if OCVtime_elapsed>ocvwait and len(voltagelog)>2: 
                            check_state=((voltagelog[-1]/voltagelog[-2])-1)
                            if check_state<0:
                                check_state=-check_state
                            if check_state<tolerance: # and (voltagelog[-1]-voltagelog[-2])>=0:   #if condition of assumed Vmax attainment has been reached also make sure that negative voltages don't cause switching
                                plateaucounter=plateaucounter+1
                            else:
                                plateaucounter=0
                            if plateaucounter==steadyrepeat: #wait for at least 3 of this plateau conditions to be satisfied simultaneously
                                OCV_end=time.time() #time at this moment of plateau

                                telapsed=OCV_end-start_time #elapsedtime since start
                                tchart=round(((telapsed+basetime)/3600),2) #time in hours since  plotting started
                                
                                global timevec
                                timevec=timevec
                                global sensorvec
                                sensorvec=sensorvec
                                
                                timevec_checker=timevec
                                timevec_checker=timevec_checker+[tchart]
                                check=timevec_checker[-1]-timevec_checker[0]
                                                            
                                
                                OCV_time=OCV_end-OCV_start #calulate time to reach this estimated Vmax
                                OCV_time=round(OCV_time,2) #round to 2 decimal places
                                Vmax_Est=voltagelog[-1] #save this estimated Vmax as the last subject
                                Vmax_Est=round(Vmax_Est,2)
                                vmaxset.set(str(Vmax_Est))

                                Area_curve=trapz(voltagelog,timelog) #integrate and calculate area under curve

                                if Vmin_Est==0:
                                    Vmin_Est=0.1
                                    
                                Sensoroutput=round((Vmax_Est/Vmin_Est),2)

                                
                                sensorvset.set(str(Sensoroutput)) #display value in display

                                if check<=graphspan:
                                    sensorvec=sensorvec+[Sensoroutput]
                                    timevec=timevec+[tchart]

                                else:
                                    aux1=sensorvec
                                    sensorvec=aux1[2:]+[Sensoroutput]
                                    aux2=timevec
                                    timevec=aux2[2:]+[tchart]
                                #print len(sensorvec)
                                #print len(timevec)

                                a=f.add_subplot(111)
                                a.clear()
                                a.plot(timevec,sensorvec, linestyle='--', marker='o')
                                a.set_title('Relative activity')
                                a.set_xlabel('time (h)')
                                a.set_ylabel('Vmax / Vmin')
                                a.set_ylim([0,ylimit])
                                a.plot(timevec,sensorvec)
                                #canvas=FigureCanvasTkAgg (f, self)
                                canvas.show()
                                canvas.get_tk_widget().grid(column=0,row=7,columnspan=3,sticky='NESW')
                                                                                
                                
                                #record all data
                                if filesaveflag==1:
                                    timeofsave=(str(datetime.datetime.now()))[:19]
                                    datastr= (timeofsave +' ' + str(Vmax_Est)+' ' + str(Area_curve)+
                                              ' ' + str(OCV_time)+' ' + str(tolerance)+' '+str(Vmin)+' '+str(alpha1)+' '+str(Vmin_Est)+' '+str(discharge_time)+' '+str(Disarea_curve)+' '+str(tempV)+' '+str(Sensoroutput)+' '+str(ocvwait)+' '+str(vminwait)+' '+str(steadyrepeat)+' '+str(steadyrepeatvmin))
                                    save_file= open(filename,"a") #openfile to save
                                    save_file.write(datastr +'\n') #write data to file
                                    save_file.close() #close
                                saveprofile=0; #reset save profile decider
                                state=0 #turn state to open circuit
                                plateaucounter=0
 
                time.sleep(vmaxacq)
                
            if flag==0:
                d.getFeedback(u3.BitStateWrite(4, 0)) #SET FI04 to output low to disconnect resistor
                print 'OFF'
                while flag==0:
                    #print 'OFF'
                    statusdisplay.set(u'Biosensor-OFF')
                    #print restarter
                    if restarter==1:
                        savecounter=1
                        savecounter=savecounter+1
                        #print savecounter
                        if savecounter==2: #helps to save header and filename only once after reinitialization
                            print "saving & ON"
                            if not os.path.exists('/home/pi/Documents/OnlineBiosensor/BiosensingData'):
                                os.makedirs('/home/pi/Documents/OnlineBiosensor/BiosensingData') #create folder for documents if it doesnt exist
                            os.chdir('/home/pi/Documents/OnlineBiosensor/BiosensingData') #change directory to this new folder and save files here
                            programstarttime=str(datetime.datetime.now()) #get date and time program starts
                            programstart=time.time()
                            filesuffix=programstarttime[:10]
                            filenameprefixnow='sensoroutputs'
                            #filenameprefixnow=filenameprefixnow[:-4] #get from the gui interface #remove the .txt
                            filename= filenameprefixnow + '.txt' #each file will be used # name will have.txt as type for now
                            filename3='temp&vMFClog' + '.txt' #filename to save MFC profile
                            filename=filename
                            os.chmod("/home/pi/Documents/OnlineBiosensor/BiosensingData", 0777) #make folder write and readable for all
                            save_file= open(filename,"a") #for calling the filename where data has been saved
                            headers=['Date', 'Time', 'Vmax_Est', 'Area', 'OCV_time(s)','Tolerance', 'Vmin', 'alpha1','Vmin_Est','prev_discharge_time','DischargeArea','Ambient Temperature','Vmax/Vmin','OCVwait','Vminwait','steadystaterepeatocv','steadystaterepeatVmin']
                            headers=' '.join(headers)
                            save_file.write(headers +'\n') #write headers to file
                            save_file.close()
                            filename2=filename
                            save_file2=open(filename3,"a") #for calling the filename where profile has been saved
                            headers2=['Date', 'Time', 'VMFC']
                            headers2=' '.join(headers2)
                            save_file2.write(headers2 +'\n') #write headers to file
                            save_file2.close()
                            filename4=filename3
                            state=1
                            flag=1
##                          print filename
                    tempValue = d.getAIN(6) #get the analog input value from FIO6 which has the temperature sensor
                    tempV=(55.56*tempValue)+255.37-273.5
                    tempV=round(tempV,2)
                    tempvset.set(str(tempV)) #default value in display        
                    ainValue = d.getAIN(1)
                    ainValue=ainValue*1000 #convert read voltage into millivolts
                    Sensoroutput=0.00
                    sensorvset.set(str(Sensoroutput)) #display value in display
                    MFCreading=round(ainValue,2)
                    voltageset.set(str(MFCreading)) #default value in display
                    time.sleep(1)
                    savecounter=0



    thread=threading.Thread(target=maincode)
    #make measuring thread terminate when the user exits the window
    thread.daemon = True 
    thread.start()

    #global f
    #ani=animation.FuncAnimation(f, animate,interval=1000)
    app.mainloop() #tells the application to loop
    




