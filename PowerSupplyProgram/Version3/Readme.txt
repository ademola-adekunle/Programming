Installation: Extract in an easily accessible folder such as the user's home folder. This will create a 'Korad KD3005P'
directory and subdirectories.
Uninstallation: Delete the 'Korad KD3005P' directory.
Run program command: python3 'path-to-Korad KD3005P directory/Korad KD3005P/korad.py'
Note that user must be a member of the 'dialout' group.
When first connected, the Korad will be unresponsive to serial commands for up to thirty seconds. Attempting to
communicate will cause the power supply to become unresponsive. To accomodate this behaviour, no communication is
attempted for thirty seconds after initial connection.
This appears to be unique to the Korad supply as other serial devices such as Arduinos don't have this behaviour.
After main dialog is shown, click on 'Find ID' on menu bar to get serial ID for power supply. The ID will be stored
in a configuration file (Serial ID.txt)and only needs to set once. The ID is unique to the power supply since it
contains the power supply serial number. Subsequent uses of the GUI will automatically connect to the power supply.
Only standard Python libraries and Tkinter are used. Serial communication is done using the standard OS and Termios
libraries.
Source: READM