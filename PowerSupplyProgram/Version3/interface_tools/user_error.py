import tkinter as tk
import tkinter.ttk as ttk

class UserError(tk.Toplevel):
    """
    User interface error display
    """
    def __init__(self, errorMessage):
        tk.Toplevel.__init__(self)
        self.title('Monitor Error')
        if isinstance(errorMessage, str):
            ttk.Label(self, background = 'Yellow', width = -20,
                      text = errorMessage).pack(side = 'top')
        elif isinstance(errorMessage, tuple):
            for row in range(0, len(errorMessage)):
                ttk.Label(self, background = 'Yellow', width = -20,
                          text = errorMessage[row]).grid(row = row, column = 0)
        self.bind('<FocusOut>', self.terminate)
        # Intercept window destroy to allow orderly shutdown
        self.protocol('WM_DELETE_WINDOW', self.terminate)
        self.grab_set()

    def terminate(self, event = None):
        self.grab_release()
        self.destroy()

