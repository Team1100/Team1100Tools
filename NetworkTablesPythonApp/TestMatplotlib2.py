import itertools
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

fig, ax = plt.subplots()
xdata, ydata = [], []
ln, = plt.plot([], [], 'ro')

x_data = [-1.0,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0.0,
         0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0 ]

def init():
    return ln,

def update(frame):
    print(frame)
    if frame < len(x_data):
        xdata.append(x_data[frame])
        ydata.append(x_data[frame]*5280)
        ln.set_data(xdata, ydata)
    return ln,

ani = FuncAnimation(fig, update, frames=itertools.count(start=0,step=1),
                    init_func=init, blit=True)
plt.show()
