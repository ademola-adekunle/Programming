import tkinter as tk
import tkinter.ttk as ttk
from settings import MAX_CURRENT

class Current(ttk.LabelFrame):
    """
    Voltage control and display
    """
    def __init__(self, parent, portal):
        ttk.LabelFrame.__init__(self, parent, text = 'Current')
        # Controller message assignment
        portal.forwarding.update({'Current':self.outputCurrent,
                                  'Set current':self.setCurrent})
        # Display
        self.currentDisplay = tk.StringVar()
        ttk.Label(self, textvariable = self.currentDisplay, width = 6,
                  background = 'white', font = ('Helvetica', 40, 'bold italic'),
                  anchor = 'center').grid(row = 0, column = 0, sticky = 'nsew')
        self.currentDisplay.set('-.---')
        # Current setting
        self.currentSetting = tk.StringVar()
        ttk.Label(self, textvariable = self.currentSetting, width = 11,
                  background = 'white', font = ('Helvetica', 20, 'bold italic'),
                  anchor = 'center').grid(row = 1, column = 0, sticky = 'nsew')
        self.currentSetting.set('Set: -.---')

    def outputCurrent(self, current):
        self.currentDisplay.set(current.decode('ASCII'))

    def setCurrent(self, current):
        self.currentSetting.set(''.join(('Set: ', current.decode('ASCII'))))
