import threading
from networktables import NetworkTables

cond = threading.Condition()
notified = [False]

def connectionListener(connected, info):
    print(info, '; Connected=%s' % connected)
    with cond:
        notified[0] = True
        cond.notify()

NetworkTables.initialize(server='10.0.0.99')
NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

with cond:
    print("Waiting")
    if not notified[0]:
        cond.wait()

# Insert your processing code here
print("Connected!")
table = NetworkTables.getTable('SmartDashboard')

# This retrieves a boolean at /SmartDashboard/foo
motor2 = table.getNumber('Motor2', True)
motor3 = table.getNumber('Motor3', True)
print("motor2 = {}, motor3 = {}".format(motor2, motor3))
