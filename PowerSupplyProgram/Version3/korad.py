#!/usr/bin/env python3

import tkinter as tk
import tkinter.ttk as ttk
from user_interface import UserInterface

def main():
    # Setup user interface
    root = tk.Tk()
    root.title('Korad KD3005P')
    root.resizable(width = False, height = False)
    UserInterface(root)
    root.mainloop()

if __name__ == '__main__':
    main()
