from multiprocessing import Process
from mail_handler import MailHandler
import time
from korad_tools import Korad, KoradError

class Controller(Process, MailHandler):
    """
    Process controller used to interact between UI and Korad.
    """
    def __init__(self, mailBox):
        MailHandler.__init__(self, mailBox)
        Process.__init__(self, target = self.mainLoop)

    def mainLoop(self):
        self.bindings = {'Update':self.update,
                         'Set voltage':self.setVoltage,
                         'Set current':self.setCurrent,
                         'Set voltage reference':self.setVoltageReference,
                         'Set current reference':self.setCurrentReference,
                         'Disable output':self.disableOutput,
                         'Enable output':self.enableOutput,
                         'Enable OCP':self.enableOCP,
                         'Disable OCP':self.disableOCP}
        self.korad = Korad(self)
        self.taskList = [(self.waitKorad, None)]
        # State machine
        self.running = True
        while self.running is True:
            try:
                letter = self.readMail(blocking = True)
                if not letter is None:
                    message, attachment = letter
                    if message == 'Stop':
                        self.stop()
                        break
                    self.bindings[message](attachment)
                if len(self.taskList) == 0:
                    self.loadIdleTasks()
                task, parameters = self.taskList[0]
                if task(parameters) is True:
                    del self.taskList[0]
            except KoradError as error:
                self.sendMail('Status message', str(error))
        self.sendMail('Stopped')

    def waitKorad(self, parameter):
        return self.korad.run()

    def setVoltage(self, voltage):
        self.taskList.extend([(self.korad.setVoltage, voltage),
                              (self.waitKorad, None)])

    def setVoltageReference(self, parameters):
        voltage, current = parameters
        self.taskList.extend([(self.korad.setVoltageReference, (voltage,
                                                                current)),
                              (self.waitKorad, None)])

    def setCurrent(self, current):
        self.taskList.extend([(self.korad.setCurrent, current),
                              (self.waitKorad, None)])

    def setCurrentReference(self, parameters):
        current, voltage = parameters
        self.taskList.extend([(self.korad.setCurrentReference, (current,
                                                                voltage)),
                              (self.waitKorad, None)])

    def disableOutput(self, attachment):
        self.taskList.extend([(self.korad.disableOutput, None),
                              (self.waitKorad, None)])

    def enableOutput(self, attachment):
        self.taskList.extend([(self.korad.enableOutput, None),
                              (self.waitKorad, None)])

    def enableOCP(self, attachment):
        self.taskList.extend([(self.korad.enableOCP, None),
                              (self.waitKorad, None)])

    def disableOCP(self, attachment):
        self.taskList.extend([(self.korad.disableOCP, None),
                              (self.waitKorad, None)])

    def stop(self, attachment = None):
        self.korad.stop()

    def update(self, attachment):
        pass

    def loadIdleTasks(self):
        self.taskList.extend([(self.korad.readVoltage, None),
                            (self.waitKorad, None),
                            (self.korad.readSetVoltage, None),
                            (self.waitKorad, None),
                            (self.korad.readCurrent, None),
                            (self.waitKorad, None),
                            (self.korad.readSetCurrent, None),
                            (self.waitKorad, None),
                            (self.korad.readStatus, None),
                            (self.waitKorad, None)])
