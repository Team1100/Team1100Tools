import time
import numpy as np
import matplotlib.pyplot as plt

def exampleSetup():
    x = np.linspace(0,10,500)
    y = np.sin(x)

    fig, ax = plt.subplots()

    # Using set_dashes to modify dashing of an existing line
    line1, = ax.plot(x,y,label='line1')
    line2, = ax.plot(x,y - 0.2,label='line2')

    ax.legend()
    plt.show()


fig, ax = plt.subplots()

x = [-1]
y = [-5820]

incr = [-1.0,-0.9,-0.8,-0.7,-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0.0,
         0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0 ]

for i in incr:
    x.append(i)
    y.append(5280*i)
    # Using set_dashes to modify dashing of an existing line
    line1, = ax.plot(x,y,label='line1')

    ax.legend()
    plt.show()
    time.sleep(1)
    print(i)
