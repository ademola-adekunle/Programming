import sys, os

SERIAL_BY_ID_PATH = os.path.join(os.sep, 'dev', 'serial', 'by-id')
DEVICE_FILE_PATH = os.path.join(os.sep, 'dev')
DEVICE_ID_PATH = os.path.join(sys.path[0], 'Device ID.txt')
START_DELAY = 30 # Wait time after connection is established
BAUD_RATE = '9600'
MAX_VOLTAGE = 30
MAX_CURRENT = 5
RESPONSE_TIME = 0.075 # Wait time before reading result of setting command
SETTLING_TIME = 5 # Maximum wait time for voltage or current to be in tolerance
VOLTAGE_TOLERANCE = 0.9995
CURRENT_TOLERANCE = 0.995
VOLTAGE_OFFSET = 0.005
CURRENT_OFFSET = 0.01
