import tkinter as tk
import tkinter.ttk as ttk
from mail_handler import MailHandler
from .user_error import UserError
from settings import MAX_VOLTAGE, MAX_CURRENT

class Controls(ttk.LabelFrame, MailHandler):
    """
    Power supply controls.
    """
    def __init__(self, parent, portal):
        ttk.LabelFrame.__init__(self, parent, text = 'Output Configuration')
        MailHandler.__init__(self, portal.mailBox)
        style = ttk.Style()
        style.configure('buttonOn.TButton', font = ('Helvetica', 15),
                        foreground = 'Green')
        style.configure('buttonOff.TButton', font = ('Helvetica', 15),
                        foreground = 'Red')
        style.configure('option.TRadiobutton', font = ('Helvetica', 15))
        # Configuration options
        self.configuration = tk.StringVar()
        ttk.Radiobutton(self, text = 'Voltage', command = self.update,
                        variable = self.configuration,
                        style = 'option.TRadiobutton',
                        value = 'Voltage').grid(row = 0, column = 0,
                                                columnspan = 2,
                                                sticky = 'w')
        ttk.Radiobutton(self, text = 'Current', command = self.update,
                        variable = self.configuration,
                        style = 'option.TRadiobutton',
                        value = 'Current').grid(row = 1, column = 0,
                                                columnspan = 2,
                                                sticky = 'w')
        ttk.Radiobutton(self, text = 'Voltage Reference',
                        command = self.update,
                        variable = self.configuration,
                        style = 'option.TRadiobutton',
                        value = 'Voltage reference').grid(row = 2, column = 0,
                                                          columnspan = 2,
                                                          sticky = 'w')
        ttk.Radiobutton(self, text = 'Current Reference',
                        command = self.update,
                        variable = self.configuration,
                        style = 'option.TRadiobutton',
                        value = 'Current reference').grid(row = 3, column = 0,
                                                          columnspan = 2,
                                                          sticky = 'w')
        self.configuration.set('Voltage')
        # Voltage entry
        ttk.Label(self, text = 'Voltage',
                  font = ('Helvetica', 15)).grid(row = 4, column = 0)
        self.voltage = tk.StringVar()
        self.voltageEntry = ttk.Entry(self, textvariable = self.voltage,
                                      width = 6, font = ('Helvetica', 15))
        self.voltageEntry.grid(row = 4, column = 1)
        self.voltage.set('00.00')
        self.voltageEntry.bind('<Return>', self.sendConfiguration)
        # Current entry
        ttk.Label(self, text = 'Current:',
                  font = ('Helvetica', 15)).grid(row = 5, column = 0)
        self.current = tk.StringVar()
        self.currentEntry = ttk.Entry(self, textvariable = self.current,
                                      width = 6, font = ('Helvetica', 15))
        self.currentEntry.grid(row = 5, column = 1)
        self.current.set('0.000')
        self.currentEntry.bind('<Return>', self.sendConfiguration)
        self.currentEntry.configure(state = 'disabled')
        # Configuration activate button
        self.send = ttk.Button(self, text = 'Send Configuration',
                               style = 'button.TButton',
                               command = self.sendConfiguration)
        self.send.grid(row = 6, column = 0, columnspan = 2, sticky = 'ew')
        # Disable output button
        ttk.Button(self, text = 'Disable output', style = 'buttonOff.TButton',
                   command = self.disableOutput).grid(row = 7, column = 0,
                                                      columnspan = 2,
                                                      sticky = 'ew')
        # Enable output button
        ttk.Button(self, text = 'Enable output', style = 'buttonOn.TButton',
                   command = self.enableOutput).grid(row = 8, column = 0,
                                                     columnspan = 2,
                                                     sticky = 'ew')

    def disableOutput(self):
        self.sendMail('Disable output')

    def enableOutput(self):
        self.sendMail('Enable output')

    def update(self):
        selection = self.configuration.get()
        if selection == 'Voltage':
            self.voltageEntry.configure(state = 'normal')
            self.currentEntry.configure(state = 'disabled')
            self.voltage.set('00.00')
        elif selection == 'Current':
            self.voltageEntry.configure(state = 'disabled')
            self.currentEntry.configure(state = 'normal')
            self.current.set('0.000')
        elif selection == 'Voltage reference':
            self.voltageEntry.configure(state = 'normal')
            self.currentEntry.configure(state = 'normal')
            self.voltage.set('00.00')
            self.current.set(format(MAX_CURRENT, '#05.3f'))
        elif selection == 'Current reference':
            self.voltageEntry.configure(state = 'normal')
            self.currentEntry.configure(state = 'normal')
            self.current.set('0.000')
            self.voltage.set(format(MAX_VOLTAGE, '#05.2f'))

    def getVoltage(self):
        try:
            voltage = float(self.voltage.get())
        except ValueError:
            UserError('Invalid voltage entry')
            return
        if voltage < 0 or voltage > MAX_VOLTAGE:
            UserError('Voltage out of range')
            return
        return voltage

    def getCurrent(self):
        try:
            current = float(self.current.get())
        except ValueError:
            UserError('Invalid current entry')
            return
        if current < 0 or current > MAX_CURRENT:
            UserError('Current out of range')
            return
        return current

    def sendConfiguration(self, event = None):
        selection = self.configuration.get()
        if selection == 'Voltage':
            voltage = self.getVoltage()
            if not voltage is None:
                self.sendMail('Set voltage', voltage)
                self.event_generate('<<Clear message>>')
        elif selection == 'Current':
            current = self.getCurrent()
            if not current is None:
                self.sendMail('Set current', current)
                self.event_generate('<<Clear message>>')
        else:
            voltage = self.getVoltage()
            if voltage is None:
                return
            current = self.getCurrent()
            if current is None:
                return
        if selection == 'Voltage reference':
            self.sendMail('Set voltage reference', (voltage, current))
            self.event_generate('<<Clear message>>')
        elif selection == 'Current reference':
            self.sendMail('Set current reference', (current, voltage))
            self.event_generate('<<Clear message>>')
