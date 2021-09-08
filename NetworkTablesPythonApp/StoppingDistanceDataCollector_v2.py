import threading
from networktables import NetworkTables
import argparse
from datetime import datetime
import time

date_str = datetime.now().strftime('%Y%m%d%H%M%S')

parser = argparse.ArgumentParser(description = 'Script to log data from robot. ')
parser.add_argument('-o', '--output-file', action = 'store', default = date_str + '_Distance_Data.csv', help = 'output csv file name')
args = parser.parse_args()
print(args)

cond = threading.Condition()
notified = [False]

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
table = NetworkTables.getTable('Shuffleboard/Drive')

# This retrieves a boolean at /SmartDashboard/foo
table.putBoolean('DataCollection', True)
dataCollection = True
commandCurrentState = table.getBoolean('DriveDistanceSim/DriveDistanceSim/running', False)
commandPreviousState = False
commandJustStopped = False

table.putBoolean('DriveDistanceSim/DriveDistanceSim/running', True)

counter = 10

while table.getBoolean('DataCollection', False):
    #dataCollection = table.getBoolean('DataCollection', False)
    if not dataCollection:
        break
    
    commandPreviousState = commandCurrentState
    commandCurrentState = table.getBoolean('DriveDistanceSim/DriveDistanceSim/running', False)
    commandJustStopped = commandPreviousState and not commandCurrentState


    if commandJustStopped:
        time.sleep(3)
        drivingSpeed = table.getNumber('DriveDistance/drivingSpeed', 0)
        sign = 1
        if drivingSpeed < 0:
            sign = -1
        expectedDistance = table.getNumber('DriveDistance/drivingDistance', 0) * sign
        actualDistance = table.getNumber('Data/actualDistance', 0)
        stoppingDistance = abs(actualDistance - expectedDistance)
        print("drivingSpeed = {}, expectedDistance = {}, actualDistance {}, stoppingDistance = {}".format(drivingSpeed, expectedDistance, actualDistance, stoppingDistance))

        with open(args.output_file, 'a') as fh:
            fh.write("{}, {}, {}, {} \n".format(drivingSpeed, expectedDistance, actualDistance, stoppingDistance))

        if counter > 0:
            counter -= 1
            table.putNumber('DriveDistance/drivingSpeed', (drivingSpeed + 1))
            table.putBoolean('DriveDistanceSim/DriveDistanceSim/running', True)

