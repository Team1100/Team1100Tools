import threading
from networktables import NetworkTables
import argparse
import time


parser = argparse.ArgumentParser(description = 'Script to log data from robot. ')
args = parser.parse_args()
print(args)

cond = threading.Condition()
notified = [False]

def connectionListener(connected, info):
    print(info, '; Connected=%s' % connected)
    with cond:
        notified[0] = True
        cond.notify()

NetworkTables.initialize(server='10.11.21.2')
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)


with cond:
    print("Waiting")
    if not notified[0]:
        cond.wait()

# Insert your processing code here
print("Connected!")
table = NetworkTables.getTable('Shuffleboard/Drive')

# This retrieves a boolean at /SmartDashboard/foo

table.putBoolean('DataCollection', False)

time.sleep(1)






