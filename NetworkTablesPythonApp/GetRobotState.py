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

NetworkTables.initialize(server='10.11.21.2') #10.11.21.2 #127.0.0.1
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)


with cond:
    print("Waiting")
    if not notified[0]:
        cond.wait()

# Insert your processing code here
print("Connected!")
table = NetworkTables.getTable('Robot')

# This retrieves a boolean at /SmartDashboard/foo

enabled = table.getBoolean('enabled', False)
print("enabled: {}".format(enabled))
time.sleep(1)






