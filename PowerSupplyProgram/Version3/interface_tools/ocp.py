import tkinter as tk
import tkinter.ttk as ttk
from mail_handler import MailHandler
from settings import MAX_CURRENT

class OCP(ttk.LabelFrame, MailHandler):
    """
    Overcurrent protection controls
    """
    def __init__(self, parent, portal):
        ttk.LabelFrame.__init__(self, parent, text = 'OCP (Electronic Fuse)')
        MailHandler.__init__(self, portal.mailBox)
        portal.forwarding['OCP state'] = self.setOCPstate
        style = ttk.Style()
        style.configure('option.TRadiobutton', font = ('Helvetica', 15))
        self.ocpState = tk.StringVar()
        ttk.Radiobutton(self, text = 'Enable OCP', command = self.update,
                        variable = self.ocpState,
                        style = 'option.TRadiobutton',
                        value = 'On').grid(row = 0, column = 0, sticky = 'w')
        ttk.Radiobutton(self, text = 'Disable OCP', command = self.update,
                        variable = self.ocpState,
                        style = 'option.TRadiobutton',
                        value = 'Off').grid(row = 1, column = 0, sticky = 'w')
        self.ocpStatus = tk.StringVar()
        ttk.Label(self, textvariable = self.ocpStatus, background = 'white',
                  font = ('Helvetica', 12)).grid(row = 0, column = 1,
                                                 rowspan = 2, sticky = 'nsew')
        self.ocpStatus.set('OCP State\nUnknown')

    def setOCPstate(self, state):
        if state == 32:
            self.ocpStatus.set('OCP State\nActive')
        else:
            self.ocpStatus.set('OCP State\nInactive')

    def update(self):
        if self.ocpState.get() == 'On':
            self.sendMail('Enable OCP')
        else:
            self.sendMail('Disable OCP')
