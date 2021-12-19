import threading
from networktables import NetworkTables
import argparse
from datetime import datetime
import time
import matplotlib.pyplot as plt

date_str = datetime.now().strftime('%Y%m%d%H%M%S')

parser = argparse.ArgumentParser(description = 'Script to log data from robot. ')
parser.add_argument('-o', '--output-file', action = 'store', default = date_str + '_Accelerometer_Values.csv', help = 'output csv file name')
args = parser.parse_args()
print(args)

cond = threading.Condition()
notified = [False]

def connectionListener(connected, info):
    print(info, '; Connected=%s' % connected)
    with cond:
        notified[0] = True
        cond.notify()

NetworkTables.initialize(server='10.11.21.2') #127.0.0.1
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

with cond:
    print("Waiting")
    if not notified[0]:
        cond.wait()

# Insert your processing code here
print("Connected!")
table = NetworkTables.getTable('Shuffleboard/Drive')
robotTable = NetworkTables.getTable('Robot')
robotEnabled = robotTable.getBoolean('enabled', False)

counter = 1000

while counter > 0:
   

        instantAcceleration = table.getNumber('Accelerometer/instantAccel', 0)
        currentTime = table.getNumber('Accelerometer/currentTime', 0)
        print("currentTime = {}, instantAcceleration = {}".format(currentTime, instantAcceleration))
        counter -= 1
        with open(args.output_file, 'a') as fh:
            fh.write("{}, {}\n".format(currentTime, instantAcceleration ))
                

        
            

