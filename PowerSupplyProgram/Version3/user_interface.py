import sys, traceback, os.path
from mail_handler import MailHandler
import tkinter as tk
import tkinter.ttk as ttk
from multiprocessing import Pipe
from controller import Controller
from interface_tools import (Voltage, Current, Mode, FileSelector, UserError,
                             Controls, Status, OCP)
from settings import SERIAL_BY_ID_PATH, DEVICE_ID_PATH

class UserInterface(MailHandler):
    """
    User interface runs two event loops, tkinter's main loop and a second loop
    to interact with the controller thread.
    """
    def __init__(self, root):
        mailBox1, mailBox2 = Pipe()
        MailHandler.__init__(self, mailBox1)
        self.controller = Controller(mailBox2)
        self.controller.start()
        self.root = root
        menu = tk.Menu(root)
        menu.add_command(label = 'Find ID', command = self.findID)
        root.config(menu = menu)
        # Controller message handler assignments
        self.forwarding = {'Error':self.showErrorMessage}
        # Voltage display
        Voltage(root, self).grid(row = 0, column = 0, sticky = 'ew')
        # Current display
        Current(root, self).grid(row = 1, column = 0, sticky = 'ew')
        # OCP control
        OCP(root, self).grid(row = 2, column = 0, sticky = 'ew')
        # Mode display
        Mode(root, self).grid(row = 3, column = 0, columnspan = 2,
                              sticky = 'new')
        # Configuration controls
        Controls(root, self).grid(row = 0, column = 1, rowspan = 3,
                                  sticky = 'nsew')
        # Error and status message display
        self.status = Status(root, self)
        self.status.grid(row = 4, column = 0, columnspan = 2, sticky = 'ew')
        # Message handler bindings
        root.bind('<<Update>>', self.update)
        root.bind('<<Exit request>>', self.shutdown)
        root.bind('<<Clear message>>', self.status.clearMessage)
        # Use periodic interrupt to communicate with controller process
        root.after(20, self.initiateUpdate)
        # Intercept window destroy to allow orderly shutdown
        root.protocol('WM_DELETE_WINDOW', self.shutdown)

    def initiateUpdate(self):
        # Check mail queue at regular intervals
        self.root.event_generate('<<Update>>', when = 'tail')
        self.root.after(10, self.initiateUpdate)

    def update(self, event = None):
        # Stimulate controller and check response
        if self.controller.is_alive() is True:
            self.sendMail('Update')
            letter = self.readMail(blocking = False)
            while not letter is None:
                message, attachment = letter
                try:
                    self.forwarding[message](attachment)
                except:
                    errorType, errorValue, errorTraceback = sys.exc_info()
                    print('Error type', errorType)
                    print('Error value', errorValue)
                    print(traceback.print_tb(errorTraceback))
                letter = self.readMail(blocking = False)
        else:
            self.controller.terminate()
            self.root.destroy()

    def findID(self):
        # Find and save power supply USB identification
        if not os.path.exists(SERIAL_BY_ID_PATH):
            UserError('No serial devices connected')
            return
        fileSelector = FileSelector(title = 'Select Serial ID',
                                    operation = 'Open',
                                    defaultPath = SERIAL_BY_ID_PATH,
                                    fileTypes = (('All', '*'),))
        serialIDpath = fileSelector.filePath
        if len(serialIDpath) == 0:
            return
        with open(DEVICE_ID_PATH, 'w+t') as file:
            file.write(os.path.basename(serialIDpath))

    def shutdown(self, event = None):
        self.sendMail('Stop')
        # Give controller some time to cleanup
        self.controller.join(1)
        if self.controller.exitcode is None:
            self.controller.terminate()
        self.root.destroy()

    def showErrorMessage(self, attachment):
        self.status.setMessage(attachment)
