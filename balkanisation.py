from context import Context, Parameters

import numpy as np
import random

import matplotlib.pyplot as plt
import matplotlib.animation as animation

np.random.seed(0)
random.seed(0)


#######################################
# Program Start
#######################################

# Create a context
param = Parameters()
param.skip_frames = 2
param.edges_per_node = 2

context = Context(param)

loops = 10000
show = False
save = False
plot = True
make_animation = show or save

fig, ax = plt.subplots()

def update(i):
    ax.clear()
    context.update(i, draw=make_animation, plot=plot)

if make_animation:
    graph_ani = animation.FuncAnimation(fig, update, loops * param.skip_frames, init_func=lambda: None, interval=5, blit=False, repeat=False)
else:
    for i in range(loops * param.skip_frames):
        update(i)

if show:
    plt.show()
if save:
    graph_ani.save('{}.mp4'.format('saved'), fps=10)
plt.close()

if plot:
    context.plot()
    plt.show()
    plt.close()
