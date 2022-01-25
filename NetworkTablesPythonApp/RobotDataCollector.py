import threading
from networktables import NetworkTables
import argparse
from datetime import datetime
import time
import matplotlib.pyplot as plt

date_str = datetime.now().strftime('%Y%m%d%H%M%S')

parser = argparse.ArgumentParser(description = 'Script to log data from robot. ')
parser.add_argument('-o', '--output-file', action='store', default=date_str + '_robot_data.csv', help='Name of file to use for writing collected data')
parser.add_argument('-i', '--input-file', action='store', default='robot_nt_names.json', help='List of names to query from NetworkTables and store in the output file')
parser.add_argument('-c', '--data-count', action='store', help='Defines the number of data entries to collect before exiting')
parser.add_argument('-a', '--robot-team', action='store', default=1100, type=int, help='Robot team number')
parser.add_argument('-a', '--robot-ip', action='store', default=None, help='IP Address of the robot to connect to, e.x: 10.11.21.2 or 127.0.0.1')
parser.add_argument('-l', '--use-labels', action='store_true', help='Insert heading labels in the CSV output file')
args = parser.parse_args()
print(args)

cond = threading.Condition()
notified = [False]

def connectionListener(connected, info):
    print(info, '; Connected=%s' % connected)
    with cond:
        notified[0] = True
        cond.notify()

# Decide whether to start using team number or IP address
if args.robot_ip is None:
    NetworkTables.startClientTeam(args.robot_team)
else
    NetworkTables.initialize(server='10.11.21.2')

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

print("Waiting for robot to be enabled")
    
while not robotEnabled:
    time.sleep(1)
    robotEnabled = robotTable.getBoolean('enabled', False)

print("Robot is enabled")

# This retrieves a boolean at /SmartDashboard/foo
table.putBoolean('DataCollection', True)
dataCollection = True
commandCurrentState = table.getBoolean('DriveCompensatedDistance/DriveCompensatedDistance/running', False)
commandPreviousState = False
commandJustStopped = False

table.putBoolean('DriveCompensatedDistance/DriveCompensatedDistance/running', True)

distanceValue = 36
speedValues = [0.1, -0.1, 0.2, -0.2, 0.3, -0.3, 0.4, -0.4, 0.5, -0.5, 0.6, -0.6, 0.7, -0.7, 0.8, -0.8, 0.9, -0.9, 1.0, -1.0]
counter = len(speedValues) - 1 # start at index 1
stoppingDistanceValues = []


table.putNumber('DriveDistance/drivingDistance', distanceValue)
table.putNumber('DriveDistance/drivingSpeed', speedValues[0])

while table.getBoolean('DataCollection', False):
    dataCollection = table.getBoolean('DataCollection', False)
    if not dataCollection:
        break
    
    commandPreviousState = commandCurrentState
    commandCurrentState = table.getBoolean('DriveCompensatedDistance/DriveCompensatedDistance/running', False)
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
        stoppingDistanceValues.append(stoppingDistance)
        print("drivingSpeed = {}, expectedDistance = {}, actualDistance {}, stoppingDistance = {}".format(drivingSpeed, expectedDistance, actualDistance, stoppingDistance))

        with open(args.output_file, 'a') as fh:
            fh.write("{}, {}, {}, {} \n".format(drivingSpeed, expectedDistance, actualDistance, stoppingDistance))

        if counter > 0:           
            table.putNumber('DriveDistance/drivingSpeed', speedValues[len(speedValues) - counter])
            #print('drivingSpeed = {}'.format(speedValues[len(speedValues) - counter]))
            counter -= 1     
            table.putBoolean('DriveCompensatedDistance/DriveCompensatedDistance/running', True)
            

        elif counter == 0:
            print("Done collecting data")
            l = list(zip(speedValues,stoppingDistanceValues))
            l.sort()
            x = [t[0] for t in l]
            y = [t[1] for t in l]

            fig, ax = plt.subplots()

            line1, = ax.plot(x,y,label='robot stopping distance')
            imgFileName = args.output_file[0:-3] + "png"

            ax.legend()
            ax.set_xlabel("Speed in %/100")
            ax.set_ylabel("Stopping Distance in inches")
            ax.set_title("Compensated Stopping Distance vs. Speed for a Distance of {} Inches".format(distanceValue))
            fig.savefig(imgFileName)

            break
            

