import tkinter as tk
import tkinter.ttk as ttk
from settings import MAX_VOLTAGE
from .user_error import UserError

class Voltage(ttk.LabelFrame,):
    """
    Voltage control and display
    """
    def __init__(self, parent, portal):
        ttk.LabelFrame.__init__(self, parent, text = 'Voltage')
        # Controller message assignment
        portal.forwarding.update({'Voltage':self.outputVoltage,
                                  'Set voltage':self.setVoltage})
        # Display
        self.voltageDisplay = tk.StringVar()
        ttk.Label(self, textvariable = self.voltageDisplay, width = 6,
                  background = 'white', font = ('Helvetica', 40, 'bold italic'),
                  anchor = 'center').grid(row = 0, column = 0, sticky = 'ew')
        self.voltageDisplay.set('--.--')
        # Voltage setting
        self.voltageSetting = tk.StringVar()
        ttk.Label(self, textvariable = self.voltageSetting, width = 10,
                  background = 'white', font = ('Helvetica', 20, 'bold italic'),
                  anchor = 'center').grid(row = 1, column = 0, sticky = 'ew')
        self.voltageSetting.set('Set: --.--')

    def outputVoltage(self, voltage):
        self.voltageDisplay.set(voltage.decode('ASCII'))

    def setVoltage(self, voltage):
        self.voltageSetting.set(''.join(('Set: ', voltage.decode('ASCII'))))
