import queue

class MailError(Exception):
    pass

class MailHandler():
    """
    Use pipe for communicating between processes
    """
    def __init__(self, mailBox):
        self.mailBox = mailBox
        self.mailBoxes = {}

    def readMail(self, blocking = True, timeout = None):
        # If blocking is true, wait until message is available
        if blocking is True:
            timeout = timeout
        else:
            timeout = 0
        if self.mailBox.poll(timeout):
            try:
                letter = self.mailBox.recv()
            except queue.Empty:
                return None
            return letter

    def sendMail(self, message, attachment = None):
        self.mailBox.send((message, attachment))

