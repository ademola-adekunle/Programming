import tkinter as tk
import tkinter.ttk as ttk

class Mode(tk.LabelFrame):
    """
    Display current power supply operating mode
    """
    def __init__(self, parent, portal):
        tk.LabelFrame.__init__(self, parent, text = 'Mode')
        portal.forwarding.update({'Off':self.outputOff,
                                  'CV':self.constantVoltage,
                                  'CC':self.constantCurrent})
        self.mode = tk.StringVar()
        ttk.Label(self, textvariable = self.mode, justify = 'center',
                  anchor = 'center',
                  font = ('Helvetica', 15)).grid(row = 1, column = 0,
                                                 sticky = 'ew')
        self.mode.set('---')

    def outputOff(self, attachment):
        self.mode.set('Output disabled')

    def constantVoltage(self, attachment):
        self.mode.set('Constant voltage')

    def constantCurrent(self, attachment):
        self.mode.set('Constant current')
