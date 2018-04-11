import random
import numpy as np
from queue import Queue
import networkx as nx

def flip_coin(prob_of_heads):
    return random.random() <= prob_of_heads

class Packet:
    def __init__(self):
        self.receiver = None    # The intended receiver
        self.path = None        # The current calculated path to the receiver
        self.threat = False     # Whether the packet is a threat


class Server:
    def __repr__(self):
        return self.name

    def __init__(self, name):
        self.name = name
        self.context = None
        self.network = None

        self.prob_block_threat = 0.0

    def process_packet(self, packet, source):
        if packet.receiver == self:
            if packet.threat:
                if self.threat_detected(packet):
                    self.context.node_blocked_threat(self, packet)
                else:
                    self.log_threat(source, packet)
        else:
            if packet.threat and self.threat_detected(packet):
                self.context.node_blocked_threat(self, packet)
            else:
                packet.path.pop(0).process_packet(packet, self)

    def run_one_cycle(self):
        packet = Packet()

        packet.threat = True

        packet.receiver = self
        while packet.receiver == self:
            packet.receiver = random.choice(list(self.network.g.nodes))

        packet.path = self.network.calc_path(self, packet.receiver)

        self.context.packet_made(self, packet)

        # Send packet on to the next server
        packet.path.pop(0)
        packet.path.pop(0).process_packet(packet, self)

    def log_threat(self, server, packet):
        pass

    def threat_detected(self, packet):
        """ Returns true if the server thinks the packet is a threat. """
        assert packet.threat
        return flip_coin(self.prob_block_threat)

class User(Server):
    def log_threat(self, server, packet):
        self.context.node_received_threat(self, packet)

        # temporarily break connection
        self.network.delete_edge(self, server)
        candidate = self.network.generate_connection_candidate(self, server)
        if candidate is not None and self.candidate_is_better(candidate, server):
            # make new connection
            self.network.add_edge(self, candidate)
        else:
            # restore old connection
            self.network.add_edge(self, server)


    def candidate_is_better(self, candidate, server):
        """ Whether candidate would be safer to connect to than server """
        if candidate == server:
            return False

        serv_threat = threat_exposure(self.network.g, self, server)
        cand_threat = threat_exposure(self.network.g, self, candidate)
        return cand_threat < serv_threat

class Country(Server):
    pass

def threat_exposure(g, start, second):
    """
    Compute the level of threat exposure, defined as the probability that a threat packet
    from a random node travelling along a randomly chosen shortest-path will reach 'start'
    without being blocked, given the network g with the additional edge 'start-second'.

    The computation proceeds with a BFS through the network, with the twist that we keep track of
    all the shortest paths to a node rather than just the shortest path we happened to find first.
    """
    # For each node, keep track of the length of the shortest path/s leading to it, and a
    # list of the threat exposure from all successor nodes (neighbours for whom at least one shortest path to 'start' leads through this node)
    data = {n: (np.inf, None) for n in g}
    data[start] = (0, None)
    queue = Queue()

    for n in g[start]:
        assert n is not second
        queue.put(n)
        data[n] = (1, [1])
    queue.put(second)
    data[second] = (1, [1])

    total_threat = 0

    while not queue.empty():
        node = queue.get()
        distance, threats = data[node]
        threat = np.mean(threats) * (1 - node.prob_block_threat)
        total_threat += threat
        for neighbour in g[node]:
            neighb_distance, neighb_threats = data[neighbour]
            if neighb_distance < distance + 1:
                # Not a shortest path
                continue
            elif neighb_distance > distance + 1:
                # Found our first shortest path
                assert neighb_distance == np.inf
                queue.put(neighbour)
                data[neighbour] = (distance + 1, [threat])
            elif neighb_distance == distance + 1:
                # Found another shortest path
                neighb_threats.append(threat)
            else:
                assert False

    return total_threat

