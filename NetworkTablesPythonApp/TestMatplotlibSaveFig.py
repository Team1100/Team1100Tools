import matplotlib.pyplot as plt

# Steps:
# 1 Collect the info to graph as x coord, y coord
# 2 Sort the data based on X value of the coord (speed)
# 3 Graph it from -1 to 1
# 4 Save the figure

def exampleSetup(save_location):
    xi = [0.1, -0.1, 0.2, -0.2, 0.3, -0.3, 0.4, -0.4, 0.5, -0.5, 0.6, -0.6, 0.7, -0.7, 0.8, -0.8, 0.9, -0.9, 1.0, -1.0]
    yi = [0.5379257202148438, 0.19322967529296875, 0.020885467529296875, 0.15876388549804688, 0.2966423034667969,
         0.5034561157226562, 0.2966423034667969, 0.7792129516601562, 0.6758041381835938, 0.9860305786132812,
         0.055355072021484375, 0.19322967529296875, 0.9170913696289062, 1.53753662109375, 1.53753662109375,
         2.4337425231933594, 0.5379257202148438, 2.192455291748047, 1.882232666015625, 1.3307228088378906]

    l = list(zip(xi,yi))
    l.sort()
    x = [t[0] for t in l]
    y = [t[1] for t in l]

    fig, ax = plt.subplots()

    # Using set_dashes to modify dashing of an existing line
    line1, = ax.plot(x,y,label='data set 1')

    ax.legend()
    fig.savefig(save_location)

save_loc = "fig.png"
exampleSetup(save_loc)
