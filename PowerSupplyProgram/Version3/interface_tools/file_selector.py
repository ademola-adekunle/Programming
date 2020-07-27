from tkinter import filedialog
import os.path, sys

class FileSelector:
    """
    File selection dialog
    """
    def __init__(self, parent = None, title = 'Select File', defaultPath = None,
                 initialfile = None, operation = 'Open',
                 fileTypes = None, defaultExtension = None):
        if fileTypes is None:
            fileTypes = (('Wav', '*.wav'), ('Wave', '*.wave'), ('All','*.*'))
        if defaultPath is None:
            defaultPath = os.path.dirname(sys.path[0])
        if operation == 'Open':
            self.filePath = filedialog.askopenfilename(parent = parent,
                                                       initialdir = defaultPath,
                                                      initialfile = initialfile,
                                                       filetypes = fileTypes,
                                                       title = title,
                                            defaultextension = defaultExtension)
        elif operation == 'Save':
            self.filePath = filedialog.asksaveasfilename(parent = parent,
                                                       initialdir = defaultPath,
                                                       initialfile = initialfile,
                                                         filetypes = fileTypes,
                                                           title = title,
                                            defaultextension = defaultExtension)
