from context import Context

import numpy as np
import random

import matplotlib.pyplot as plt
import matplotlib.animation as animation

np.random.seed(0)
random.seed(0)

class Parameters:
    def __init__(self):
        # Simulation settings
        self.user_prob_block_threat = 0.0    # Probability that an ordinary user will block a threat
        self.country_prob_block_threat = 1.0 # Probability that a country will block a threat

        self.edges_per_node = 1 # Number of edges per node: 1 is a tree, 2 is a scale-free network. Any higher is too dense to be interesting.

        self.num_users = 100
        self.num_countries = 10

        # Display settings
        self.skip_frames = 2 # Frames of animation to run between packet sends (higher numbers makes for smoother (but slower) video)
        self.steps = 10000   # How many packet sends to do in total
        self.show = True     # Whether to render a matplotlib animation on-screen
        self.save = False    # Whether to save the matplotlib animation as a video
        self.fps = 200       # Animation frames-per-second
        self.save_file = 'balkanisation.mp4'
        self.plot = True     # Whether to plot the degree of balkanisation over time after the simulation concludes



param = Parameters()

context = Context(param)

make_animation = param.show or param.save

fig, ax = plt.subplots()

def update(i):
    ax.clear()
    context.update(i, draw=make_animation, plot=param.plot)

if make_animation:
    graph_ani = animation.FuncAnimation(fig, update, param.steps * param.skip_frames, init_func=lambda: None, interval=1000//param.fps, blit=False, repeat=False)
else:
    for i in range(param.steps * param.skip_frames):
        update(i)

if param.show:
    plt.show()
if param.save:
    graph_ani.save(param.save_file, fps=param.fps)
plt.close()

if param.plot:
    context.plot()
    plt.show()
    plt.close()
