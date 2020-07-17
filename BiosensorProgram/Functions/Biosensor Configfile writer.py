import ConfigParser
from ConfigParser import SafeConfigParser
config = ConfigParser.RawConfigParser()
parser = SafeConfigParser()

parser.add_section('Parameters')

tolerance = 0.9
alpha1 = 0.9
vmin = 10.0
graphspan = 10.0
filesaveflag = 1
restarter = 1
delay = 60.0
ylimit = 700.0
vminacq = 1.0
vmaxacq = 5.0
steadyrepeat = 3.0
datalog = 300.0
ocvwait = 900.0
vminwait = 10.0
steadyrepeatvmin = 3.0
pumpratemlpermin = 50.0
targetpumpratemlperday = 250.0
para_interval = 7
y2limit = 700.0
y3limit = 700.0
y5limit = 100
y6limit = 200
pumprate = 2.0
targetpumprate = 250


parser.set('Parameters','tolerance',str(tolerance))
parser.set('Parameters','vmin', str(vmin))
parser.set('Parameters','alpha1', str(alpha1))
parser.set('Parameters','graphspan', str(graphspan))
parser.set('Parameters','filesaveflag', str(filesaveflag))
parser.set('Parameters','restarter', str(restarter))
parser.set('Parameters','delay', str(delay))
parser.set('Parameters','y2limit', str(y2limit))
parser.set('Parameters','y3limit', str(y3limit))
parser.set('Parameters','y5limit', str(y5limit))
parser.set('Parameters','y6limit', str(y6limit))
parser.set('Parameters','vminacq', str(vminacq))
parser.set('Parameters','vmaxacq', str(vmaxacq))
parser.set('Parameters','steadyrepeat', str(steadyrepeat))
parser.set('Parameters','steadyrepeatvmin', str(steadyrepeatvmin))
parser.set('Parameters','datalog', str(datalog))
parser.set('Parameters','ocvwait', str(ocvwait))
parser.set('Parameters','vminwait', str(vminwait))
parser.set('Parameters','pumpratemlpermin', str(pumprate))
parser.set('Parameters','targetpumpratemlperday', str(targetpumprate))
with open (r'C:\Users\adekunlea\Documents\OnlineBiosensor\Configuration\biosensorconfig.ini', 'w') as configfile: #Windows format
   parser.write(configfile)
configfile.close()
