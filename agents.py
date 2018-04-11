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
        self.alpha = None
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

        packet.threat = flip_coin(self.alpha)

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
        """Returns true if the ``server`` thinks the ``packet`` is a threat."""
        assert packet.threat
        return flip_coin(self.prob_block_threat)

class User(Server):
    def log_threat(self, server, packet):
        self.context.node_received_threat(self, packet)
        self.network.delete_edge(self, server)
        candidate = self.network.generate_connection_candidate(self, server)
        if candidate is not None and self.candidate_is_better(candidate, server):
            self.network.add_edge(self, candidate)
        else:
            self.network.add_edge(self, server)


    def candidate_is_better(self, candidate, server):
        """Looks for a better server parent."""
        """
        if server.prob_block_threat == 1.0 and candidate.prob_block_threat < 1.0:
            return False
        elif candidate.prob_block_threat == 1.0 and server.prob_block_threat < 1.0:
            return True
        elif candidate.prob_block_threat == 0.0 and server.prob_block_threat == 0.0:
            return flip_coin(0.5)
        else:
            return flip_coin(candidate.prob_block_threat / (candidate.prob_block_threat + server.prob_block_threat))
        """
        if candidate == server:
            return False

        serv_threat = super_bfs(self.network.g, self, server)
        cand_threat = super_bfs(self.network.g, self, candidate)
        return cand_threat < serv_threat

class Country(Server):
    pass

def super_bfs(g, start, second):
    state = {n: (np.inf, None) for n in g}
    state[start] = (0, 0)
    queue = Queue()

    for n in g[start]:
        queue.put(n)
        state[n] = (1, [1])
    queue.put(second)
    state[second] = (1, [1])

    total_weight = 0

    while not queue.empty():
        s = queue.get()
        d, w = state[s]
        w = np.mean(w) * (1 - s.prob_block_threat)
        total_weight += w
        for n in g[s]:
            dn, dw = state[n]
            if dn < d + 1:
                continue
            elif dn > d + 1:
                assert dn == np.inf
                queue.put(n)
                state[n] = (d + 1, [w])
            elif dn == d + 1:
                dw.append(w)
            else:
                assert False

    return total_weight

