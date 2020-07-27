from multiprocessing import Process
import os.path, time
from mail_handler import MailHandler
from serial_port import SerialPort, SerialError
from settings import (SERIAL_BY_ID_PATH, DEVICE_ID_PATH, BAUD_RATE,
                      RESPONSE_TIME, SETTLING_TIME, VOLTAGE_TOLERANCE,
                      CURRENT_TOLERANCE, VOLTAGE_OFFSET, CURRENT_OFFSET,
                      START_DELAY)

class KoradError(SerialError):
    pass

class Korad(MailHandler):
    """
    Korad KD3005P programmable power supply interface.
    Methods:
    setVoltage(voltage): Set and verify output voltage setting
    setCurrent(current): Set and verify output current setting
    setVoltageReference(voltage, current): Set and verify output voltage and
    current settings and then wait until voltage output is in tolerance or
    timed out.
    setCurrentReference(current, voltage): Set and verify output voltage and
    current settings and then wait until current output is in tolerance or
    timed out.
    setOutputState(state): Set power supply output state to 'ON' or 'OFF'
    readVoltage(): Send output voltage reading to UI and return as data
    readSetVoltage(): Send set voltage reading to UI and return as data
    readCurrent(): Send output current reading to UI and return as data
    readSetCurrent(): Send set current reading to UI and return as data
    readStatus(): Send status reading to UI and return as data
    """
    def __init__(self, controller):
        MailHandler.__init__(self, controller.mailBox)
        self.taskList = [(self.connect, None)]
        self.devicePath = None
        self.serialPort = None
        self.attempts = 0

    def stop(self, attachment = None):
        if not self.serialPort is None:
            try:
                self.serialPort.close()
            except OSError:
                pass
            finally:
                self.serialPort = None
        self.taskList = []

    def run(self):
        if len(self.taskList) == 0:
            return True
        task, parameter = self.taskList[0]
        try:
            task(parameter)
        except SerialError as error:
            self.taskList = [(self.connect, None)]
            raise KoradError(str(error))
        return False

    def setVoltage(self, voltage):
        self.taskList.extend([(self.setupVoltage, voltage)])
        return True

    def setVoltageReference(self, parameters):
        voltage, current = parameters
        low = voltage * VOLTAGE_TOLERANCE - VOLTAGE_OFFSET
        high = voltage * (2 - VOLTAGE_TOLERANCE) + VOLTAGE_OFFSET
        self.settlingTime = time.time() + SETTLING_TIME
        self.taskList.extend([(self.setupVoltage, voltage),
                              (self.setupCurrent, current),
                              (self.read, (b'VOUT1?', 5)),
                              (self.checkVoltage, (low, high))])
        return True

    def readVoltage(self, parameter):
        self.taskList.extend([(self.read, (b'VOUT1?', 5)),
                              (self.sendVoltage, None)])
        return True

    def readSetVoltage(self, parameter):
        self.taskList.extend([(self.read, (b'VSET1?', 5)),
                              (self.sendSetVoltage, None)])
        return True

    def setCurrent(self, current):
        self.taskList.extend([(self.setupCurrent, current)])
        return True

    def setCurrentReference(self, parameters):
        current, voltage = parameters
        low = current * CURRENT_TOLERANCE - CURRENT_OFFSET
        high = current * (2 - CURRENT_TOLERANCE) + CURRENT_OFFSET
        self.settlingTime = time.time() + SETTLING_TIME
        self.taskList.extend([(self.setupVoltage, voltage),
                              (self.setupCurrent, current),
                              (self.read, (b'IOUT1?', 5)),
                              (self.checkCurrent, (low, high))])
        return True

    def readCurrent(self, parameter):
        self.taskList.extend([(self.read, (b'IOUT1?', 5)),
                              (self.sendCurrent, None)])
        return True

    def readSetCurrent(self, parameter):
        self.taskList.extend([(self.read, (b'ISET1?', 5)),
                              (self.sendSetCurrent, None)])
        return True

    def enableOutput(self, state):
        self.taskList.extend([(self.setOutputOn, None)])
        return True

    def disableOutput(self, state):
        self.taskList.extend([(self.setOutputOff, None)])
        return True

    def enableOCP(self, parameter):
        self.taskList.extend([(self.setOCPon, None)])
        return True

    def disableOCP(self, paramter):
        self.taskList.extend([(self.setOCPoff, None)])
        return True

    def readStatus(self, parameter):
        self.taskList.extend([(self.read, (b'STATUS?', 1)),
                              (self.sendStatus, None)])
        return True

    def setupVoltage(self, parameter):
        # Send voltage setting to power supply and verify setting
        if type(parameter) is tuple:
            voltage, attempts = parameter
            attempts += 1
        else:
            voltage = parameter
            attempts = 0
        try:
            self.serialPort.write(b''.join((b'VSET1:',
                                            format(voltage,
                                                   '#05.2f').encode('ASCII'))))
        except ValueError:
            self.taskList = []
            raise KoradError('Invalid voltage value')
        del self.taskList[0]
        self.taskList = [(self.wait, RESPONSE_TIME),
                         (self.read, (b'VSET1?', 5)),
                         (self.checkVoltageSetting,
                          (voltage, attempts))] + self.taskList

    def checkVoltageSetting(self, parameters):
        # Check if voltage setting is successful
        voltage, attempts = parameters
        if attempts > 2:
            self.taskList = []
            raise KoradError('Unable to set voltage')
        if self.readData != format(voltage, '#05.2f').encode('ASCII'):
            self.taskList[0] = (self.setupVoltage, (voltage, attempts))
        else:
            # Success
            del self.taskList[0]

    def checkVoltage(self, parameters):
        # Wait until voltage output is within tolerance or timeout
        if time.time() > self.settlingTime:
            self.taskList = []
            raise KoradError('Voltage source out of tolerance')
        low, high = parameters
        try:
            reading = float(self.readData)
        except ValueError:
            del self.taskList[0]
            self.taskList = [(self.read, (b'VOUT1?', 5)),
                             (self.checkVoltage, (low, high))] + self.taskList
        else:
            if reading < low or reading > high:
                del self.taskList[0]
                self.taskList = [(self.read, (b'VOUT1?', 5)),
                                 (self.checkVoltage,
                                  (low, high))] + self.taskList
            else:
                # Success
                del self.taskList[0]
                self.sendMail('Status message', 'Voltage in tolerance')

    def setupCurrent(self, parameter):
        # Send current setting to power supply and verify setting
        if type(parameter) is tuple:
            current, attempts = parameter
            attempts += 1
        else:
            current = parameter
            attempts = 0
        try:
            self.serialPort.write(b''.join((b'ISET1:',
                                            format(current,
                                                   '#05.3f').encode('ASCII'))))
        except ValueError:
            self.taskList = []
            raise KoradError('Invalid current value')
        del self.taskList[0]
        self.taskList = [(self.wait, RESPONSE_TIME),
                         (self.read, (b'ISET1?', 5)),
                         (self.checkCurrentSetting,
                          (current, attempts))] + self.taskList

    def checkCurrentSetting(self, parameter):
        current, attempts = parameter
        if attempts > 2:
            self.taskList = []
            raise KoradError('Unable to set current')
        else:
            # Returned current setting has extraneous B'\x00' added to end
            if self.readData[0:5] != format(current, '#05.3f').encode('ASCII'):
                self.taskList[0] = (self.setupCurrent, (current, attempts))
            else:
                # Success
                del self.taskList[0]

    def checkCurrent(self, parameters):
        # Wait until current output is within tolerance or timeout
        if time.time() > self.settlingTime:
            self.taskList = []
            raise KoradError('Current source out of tolerance')
        low, high = parameters
        try:
            reading = float(self.readData[0:5])
        except ValueError:
            del self.taskList[0]
            self.taskList = [(self.read, (b'IOUT1?', 5)),
                             (self.checkCurrent, (low, high))] + self.taskList
        else:
            if reading < low or reading > high:
                del self.taskList[0]
                self.taskList = [(self.read, (b'IOUT1?', 5)),
                                 (self.checkCurrent,
                                  (low, high))] + self.taskList
            else:
                # Success
                del self.taskList[0]
                self.sendMail('Status message', 'Current in tolerance')

    def setOutputOn(self, attempts):
        if attempts is None:
            attempts = 0
        else:
            attempts += 1
        self.serialPort.write(b'OUT1')
        del self.taskList[0]
        self.taskList = [(self.wait, RESPONSE_TIME),
                         (self.read, (b'STATUS?', 1)),
                         (self.checkOutputOn, attempts)]

    def checkOutputOn(self, attempts):
        if attempts > 2:
            self.taskList = []
            raise KoradError('Output enable failed')
        try:
            if ord(self.readData) & 64 != 64:
                self.attempts += 1
                self.taskList[0] = (self.setOutputOn, attempts)
            else:
                self.attempts = 0
                del self.taskList[0]
        except (ValueError, TypeError):
            self.attempts += 1
            self.taskList[0] = (self.setOutputOn, attempts)

    def setOutputOff(self, attempts):
        if attempts is None:
            attempts = 0
        else:
            attempts += 1
        self.serialPort.write(b'OUT0')
        del self.taskList[0]
        self.taskList = [(self.wait, RESPONSE_TIME),
                         (self.read, (b'STATUS?', 1)),
                         (self.checkOutputOff, attempts)] + self.taskList

    def checkOutputOff(self, attempts):
        if attempts > 2:
            self.taskList = []
            raise RangeError('Disable output failed')
        try:
            if ord(self.readData) & 64 != 0:
                self.taskList[0] = (self.setOutputOff, attempts)
            else:
                del self.taskList[0]
        except (ValueError, TypeError):
            self.taskList[0] = (self.setOutputOff, attempts)

    def sendVoltage(self, parameter):
        self.sendMail('Voltage', self.readData)
        del self.taskList[0]
        return self.readData

    def sendSetVoltage(self, parameter):
        self.sendMail('Set voltage', self.readData)
        del self.taskList[0]
        return self.readData

    def sendCurrent(self, parameter):
        self.sendMail('Current', self.readData)
        del self.taskList[0]
        return self.readData

    def sendSetCurrent(self, timeout):
        self.sendMail('Set current', self.readData)
        del self.taskList[0]
        return self.readData

    def setOCPoff(self, attempts):
        if attempts is None:
            attempts = 0
        else:
            attempts += 1
        self.serialPort.write(b'OCP0')
        del self.taskList[0]
        self.taskList = [(self.wait, RESPONSE_TIME),
                         (self.read, (b'STATUS?', 1)),
                         (self.checkOCPoff, attempts)] + self.taskList

    def checkOCPoff(self, attempts):
        if attempts > 2:
            self.taskList = []
            raise KoradError('Disable OCP failed')
        try:
            if ord(self.readData) & 32 != 0:
                self.taskList[0] = (self.setOCPoff, attempts)
            else:
                del self.taskList[0]
        except (ValueError, TypeError):
            self.taskList[0] = (self.setOCPoff, attempts)

    def setOCPon(self, attempts):
        if attempts is None:
            attempts = 0
        else:
            attempts += 1
        self.serialPort.write(b'OCP1')
        del self.taskList[0]
        self.taskList = [(self.wait, RESPONSE_TIME),
                         (self.read, (b'STATUS?', 1)),
                         (self.checkOCPon, attempts)] + self.taskList

    def checkOCPon(self, attempts):
        if attempts > 2:
            self.taskList = []
            raise KoradError('Enable OCP failed')
        try:
            if ord(self.readData) & 32 != 32:
                self.taskList[0] = (self.setOCPon, attempts)
            else:
                del self.taskList[0]
        except (ValueError, TypeError):
            self.taskList[0] = (self.setOCPon, attempts)

    def sendStatus(self, parameter):
        # Bit 0 = CV mode, bit 5 = OCP active, bit 6 = output enabled
        status = ord(self.readData)
        if status & 64 == 0:
            self.sendMail('Off')
        elif status & 1 == 1:
            self.sendMail('CV')
        else:
            self.sendMail('CC')
        self.sendMail('OCP state', status & 32)
        del self.taskList[0]
        return self.readData

    def checkPort(self):
        # Verify that power supply is connected
        if self.devicePath is None:
            return False
        return os.path.exists(self.devicePath)
        
    def connect(self, parameter):
        if os.path.exists(DEVICE_ID_PATH) is False:
            raise SerialError('Korad serial ID not found')
        else:
            with open(DEVICE_ID_PATH, 'rt') as file:
                deviceLink = file.readline().strip()
            self.devicePath = os.path.join(SERIAL_BY_ID_PATH, deviceLink)
            if os.path.exists(self.devicePath) is True:
                self.serialPort = SerialPort(deviceLink, BAUD_RATE)
                # Accessing port immediately after connecting will cause hangup
                self.sendMail('Status message', 'Korad not ready...')
                self.sendMail('Progress enable', START_DELAY)
                self.taskList[0] = (self.wait, START_DELAY)
            else:
                self.devicePath = None
                raise SerialError('Power supply is not connected')

    def read(self, parameters):
        # Send read request and then wait for response
        if len(parameters) == 2:
            request, length = parameters
            attempts = 0
        else:
            request, length, attempts = parameters
            attempts += 1
        self.serialPort.write(request)
        self.readData = b''
        self.timeout = time.time() + RESPONSE_TIME
        self.taskList[0] = (self.readResponse, (length, request, attempts))

    def readResponse(self, parameters):
        length, request, attempts = parameters
        if attempts > 2:
            self.taskList = []
            raise KoradError(' '.join(('Read request', request.decode('ASCII'),
                                       'failed')))
        self.readData = b''.join((self.readData, self.serialPort.read()))
        if len(self.readData) >= length:
            # Success
            del self.taskList[0]
            return
        elif time.time() > self.timeout:
            self.taskList[0] = (self.read, (request, length, attempts))

    def wait(self, waitTime):
        if not waitTime is None:
            self.startTime = time.time()
            self.timeout = time.time() + waitTime
            self.taskList[0] = (self.wait, None)
        else:
            self.sendMail('Progress value', time.time() - self.startTime)
            if time.time() > self.timeout or self.checkPort() is False:
                self.sendMail('Progress disable')
                del self.taskList[0]
