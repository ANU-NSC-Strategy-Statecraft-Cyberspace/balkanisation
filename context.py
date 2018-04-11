import random
from agents import User, Country
from network import Network

import networkx as nx
from forceatlas2 import forceatlas2_networkx_layout

import matplotlib.pyplot as plt

class Context:
    def __init__(self, param):

        self.network = Network()
        self.param = param
        self.edge_colors = {}
        self.edge_countdowns = {}
        self.node_colors = {}
        self.node_countdowns = {}
        self.balkanisation = []
        self.relative_balkanisation = []

        servers = []

        for i in range(self.param.num_users):
            u = User('U' + str(i))
            u.context = self
            u.network = self.network
            u.prob_block_threat = self.param.user_prob_block_threat
            servers.append(u)

        for i in range(self.param.num_countries):
            c = Country('C' + str(i))
            c.context = self
            c.network = self.network
            c.prob_block_threat = self.param.country_prob_block_threat
            servers.append(c)

        self.network.initialise(servers, self.param.edges_per_node)
        self.pos = self.layout(None, 10)

    def packet_made(self, node, packet):
        if packet.threat:
            for a, b in zip(packet.path, packet.path[1:]):
                self.edge_colors[(a,b)] = [1,0,0]
                self.edge_countdowns[(a,b)] = self.param.skip_frames

            self.node_colors[node] = [1,0,1]
            self.node_countdowns[node] = self.param.skip_frames

    def node_blocked_threat(self, node, packet):
        if packet.threat:
            for a, b in zip([node] + packet.path, packet.path):
                self.edge_colors[(a,b)] = [0,1,0]
                self.edge_countdowns[(a,b)] = self.param.skip_frames

            self.node_colors[packet.receiver] = [0,1,0]
            self.node_countdowns[packet.receiver] = self.param.skip_frames

            self.node_colors[node] = [0,1,1]
            self.node_countdowns[node] = self.param.skip_frames

    def node_received_threat(self, node, packet):
        self.node_colors[node] = [1,0,0]
        self.node_countdowns[node] = self.param.skip_frames

    def run_one_cycle(self, calc_centralities=True, calc_balkanisation=True):
        random.choice(list(self.network.g.nodes)).run_one_cycle()
        if calc_centralities:
            self.network.update_centralities()
        if calc_balkanisation:
            self.balkanisation.append(self.network.balkanisation())
            self.relative_balkanisation.append(self.network.relative_balkanisation([n for n in self.network.g if isinstance(n,Country)]))

    def layout(self, pos, iterations):
        return forceatlas2_networkx_layout(self.network.g, pos=pos, niter=iterations, scalingRatio=0.5)

    def get_colors(self):
        return list(map(lambda x: self.get_node_color(x), self.network.g.nodes()))

    def get_sizes(self):
        return list(map(lambda x: ((self.network.centralities[x]**2)*200 + 10), self.network.g.nodes()))

    def get_edge_colors(self):
        return list(map(lambda x: self.get_edge_color(x), self.network.g.edges()))

    def update(self, i, draw=True, plot=False):
        if i % self.param.skip_frames == 0:
            print(i // self.param.skip_frames)
            self.run_one_cycle(calc_centralities=draw, calc_balkanisation=plot)
        if draw:
            self.pos = self.layout(self.pos, 1)
            nx.draw(self.network.g, pos=self.pos, node_color=self.get_colors(), node_size=self.get_sizes(), edge_color=self.get_edge_colors())

    def plot(self):
        plt.plot(self.balkanisation, label='Absolute')
        plt.plot(self.relative_balkanisation, label='Relative')
        plt.ylim(0,1)
        plt.xlabel('Time')
        plt.ylabel('Balkanisation')
        plt.legend()


    def get_node_color(self, n):
        if n in self.node_colors:
            color = self.node_colors[n]
            self.node_countdowns[n] -= 1
            if self.node_countdowns[n] <= 0:
                del self.node_colors[n]
            return color
        else:
            return [0,0,0] if isinstance(n, User) else [0,0.5,1]

    def get_edge_color(self, e):
        a,b = e
        if (a,b) in self.edge_colors:
            color = self.edge_colors[(a,b)]
            self.edge_countdowns[(a,b)] -= 1
            if self.edge_countdowns[(a,b)] <= 0:
                del self.edge_colors[(a,b)]
            return color
        elif (b,a) in self.edge_colors:
            color = self.edge_colors[(b,a)]
            self.edge_countdowns[(b,a)] -= 1
            if self.edge_countdowns[(b,a)] <= 0:
                del self.edge_colors[(b,a)]
            return color
        else:
            return [0,0,0]
