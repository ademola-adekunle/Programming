import tkinter as tk
import tkinter.ttk as ttk
from mail_handler import MailHandler

class Status(ttk.LabelFrame, MailHandler):
    """
    Status message and progress bar display.
    """
    def __init__(self, parent, portal):
        ttk.LabelFrame.__init__(self, parent, text = 'Status')
        MailHandler.__init__(self, portal.mailBox)
        portal.forwarding.update({'Status message':self.setMessage,
                                  'Progress enable':self.enableProgress,
                                  'Progress value':self.setProgressValue,
                                  'Progress disable':self.disableProgress})
        style = ttk.Style()
        style.configure('button.TButton', font = ('Helvetica', 15))
        self.statusMessage = tk.StringVar()
        ttk.Label(self, textvariable = self.statusMessage,
                  font = ('Helvetica', 15)).pack(side = 'left')
        self.statusMessage.set('')
        self.progressValue = tk.DoubleVar()
        self.progressBar = ttk.Progressbar(self, orient = 'horizontal',
                                           mode = 'determinate',
                                           variable = self.progressValue)
        self.clearButton = ttk.Button(self, text = 'Clear',
                                      style = 'button.TButton',
                                      command = self.clearMessage)

    def clearMessage(self, event = None):
        self.statusMessage.set('')
        self.clearButton.pack_forget()

    def setMessage(self, message):
        self.statusMessage.set(message)
        self.clearButton.pack(side = 'right')

    def enableProgress(self, maximum):
        self.progressBar.configure(maximum = maximum)
        self.clearButton.pack_forget()
        self.progressBar.pack(side = 'right')

    def setProgressValue(self, value):
        self.progressValue.set(value)

    def disableProgress(self, attachment):
        self.statusMessage.set('')
        self.progressBar.pack_forget()
