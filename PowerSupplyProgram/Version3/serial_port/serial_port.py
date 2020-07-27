import os, termios, time, fcntl, struct
from .baud_rates import BAUD_RATES
from settings import SERIAL_BY_ID_PATH, DEVICE_FILE_PATH

class SerialError(Exception):
    pass

class SerialPort():
    """
    Serial port read, write and modem line control.
    """
    def __init__(self, deviceLink, baudRate = 9600):
        self.devicePathLink = os.path.join(SERIAL_BY_ID_PATH, deviceLink)
        self.baudRate = baudRate
        self.port = None
        # Modem control lines, ioctl expects 32 bit integer parameter.
        self.cStructure = struct.Struct('I')
        self.dtrOut = self.cStructure.pack(termios.TIOCM_DTR)
        self.ctsIn = self.cStructure.pack(termios.TIOCM_CTS)
        self.rtsOut = self.cStructure.pack(termios.TIOCM_RTS)
        self.dsrIn = self.cStructure.pack(termios.TIOCM_DSR)
        self.dcdIn = self.cStructure.pack(termios.TIOCM_CAR)
        self.riIn = self.cStructure.pack(termios.TIOCM_RI)
        # Integer structure required for ioctl return variable
        self.integerZero = self.cStructure.pack(0)

    def read(self):
        # Return all data in serial buffer
        try:
            self.checkPort()
            return os.read(self.port, 500)
        except (TypeError, OSError) as error:
            raise SerialError(''.join(('Read error: ', str(error))))

    def write(self, data):
        try:
            self.checkPort()
            os.write(self.port, data)
            return
        except (TypeError, OSError) as error:
            raise SerialError(''.join(('Write error: ', str(error))))

    def close(self):
        # Close port
        if not self.port is None:
            try:
                os.close(self.port)
            except OSError:
                pass
            finally:
                self.port = None

    def setDTRstate(self, state):
        try:
            self.checkPort()
            if state is True:
                command = termios.TIOCMBIS
            else:
                command = termios.TIOCMBIC
            fcntl.ioctl(self.port, command, self.dtrOut)
        except OSError as error:
            raise SerialError(''.join(('Set DTR line error: ', str(error))))

    def setRTSstate(self, state):
        try:
            self.checkPort()
            if state is True:
                command = termios.TIOCMBIS
            else:
                command = termios.TIOCMBIC
            fcntl.ioctl(self.port, command, self.rtsOut)
        except OSError as error:
            raise SerialError(''.join(('Set RTS line error: ', str(error))))

    def readControlLines(self):
        try:
            self.checkPort()
            state = self.cStructure.unpack(fcntl.ioctl(self.port,
                                                       termios.TIOCMGET,
                                                       self.integerZero))[0]
            return({'DTR':state & termios.TIOCM_DTR == termios.TIOCM_DTR,
                    'CTS':state & termios.TIOCM_CTS == termios.TIOCM_CTS,
                    'RTS':state & termios.TIOCM_RTS == termios.TIOCM_RTS,
                    'DSR':state & termios.TIOCM_DSR == termios.TIOCM_DSR,
                    'DCD':state & termios.TIOCM_CAR == termios.TIOCM_CAR,
                    'RI':state & termios.TIOCM_RI == termios.TIOCM_RI})
        except OSError as error:
           raise SerialError(''.join(('Read control lines error: ',
                                      str(error))))

    def checkPort(self):
        if os.path.exists(self.devicePathLink) is False:
            self.close()
            raise SerialError('Serial device not connected')
        if self.port is None:
            try:
                virtualPort = os.path.basename(os.readlink(self.devicePathLink))
                self.port = os.open(os.path.join(DEVICE_FILE_PATH, virtualPort),
                                    os.O_RDWR|os.O_NOCTTY|os.O_NONBLOCK)
                self.configurePort()
            except OSError as error:
                raise SerialError(str(error))

    def configurePort(self):
        # Clear all flags. Baud rate setting may set some bits in cflag.
        oflag = lflag = cflag = 0
        # Set baudRate
        ispeed = BAUD_RATES[self.baudRate]
        ospeed = BAUD_RATES[self.baudRate]
        # Get revised cflag and set additional bits as required
        cflag = termios.tcgetattr(self.port)[2]
        # Enable receiver, 8 bit character, ignore modem control lines
        cflag = cflag | termios.CREAD | termios.CS8 | termios.CLOCAL
        # Ignore break, carriage return, parity and framing errors
        iflag = termios.IGNBRK | termios.IGNCR | termios.IGNPAR
        cc = termios.tcgetattr(self.port)[6]
        # Set timeout to 0 and minimum number of characters to 0
        cc[termios.VTIME] = 0
        cc[termios.VMIN] = 0
        # Final write of modified flags and settings
        flags = [iflag, oflag, cflag, lflag, ispeed, ospeed, cc]
        termios.tcsetattr(self.port, termios.TCSANOW, flags)

    def setBaudRate(self, baudRate):
        try:
            self.checkPort()
            self.baudRate = baudRate
            self.configurePort()
        except OSError as error:
            raise SerialError(str(error))
