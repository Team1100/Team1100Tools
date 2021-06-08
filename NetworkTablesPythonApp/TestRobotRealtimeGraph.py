import threading
from networktables import NetworkTables

import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# initialize graphing variables
fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [])

# initialize network table variables
cond = threading.Condition()
notified = [False]

# open file
from pathlib import Path
home = str(Path.home())
from datetime import datetime
date_str = datetime.now().strftime('%Y%m%d%H%M%S')
file = "{}/Documents/{}_frc_data.csv".format(home,date_str)
fh = open(file,mode='w')

def connectionListener(connected, info):
    print(info, '; Connected=%s' % connected)
    with cond:
        notified[0] = True
        cond.notify()

NetworkTables.initialize(server='127.0.0.1')
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

with cond:
    print("Waiting")
    if not notified[0]:
        cond.wait()

# Insert your processing code here
print("Connected!")
table = NetworkTables.getTable('SmartDashboard')

# graphing functions
def init():
    ax.set_xlim(-1,1)
    ax.set_ylim(-2048,2048)
    return ln,

def update(frame):
    motorInput = table.getNumber('Motor2Input', True)
    motorOutput = table.getNumber('Motor2FakeOutput', True)
    xdata.append(motorInput)
    ydata.append(motorOutput)
    ln.set_data(xdata, ydata)
    timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    fh.write("{}, {:0.3f}, {:0.3f}\n".format(timestamp, motorInput, motorOutput))
    return ln,


# Start graphing
ani = FuncAnimation(fig, update, frames=itertools.count(start=0,step=1),
                    init_func=init, blit=True, interval=10)
plt.show()

fh.close()
