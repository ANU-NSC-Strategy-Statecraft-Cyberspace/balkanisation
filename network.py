import random
import networkx as nx

class Network:
    def __init__(self):
        self.g = None
        self.centralities = {}

    def update_centralities(self):
        self.centralities = nx.betweenness_centrality(self.g)

    def absolute_balkanisation(self):
        """
        Absolute balkanisation is a measure that does not depend on which nodes happen to be countries.
        Define it as the proportion of nodes not in the largest biconnected component.

        Intuition: these nodes' access to the largest biconnected component (the "main network")
        is fully controlled by some "gatekeeper" node.
        """
        largest = max(nx.biconnected_components(self.g), key=len)
        return 1 - len(largest)/len(self.g)

    def relative_balkanisation(self, countries):
        """
        Relative balkanisation is a measure of the extent to which the country nodes control
        everyone else's access to the network.
        Define it as the proportion of nodes that can only connect to one country without
        passing through some other country.

        Intuition: these nodes' access to the rest of the countries (the "main network")
        is fully controlled by some "gatekeeper" country.
        """
        countries = set(countries)
        candidates = {c for c in nx.articulation_points(self.g) if c in countries}
        for c in candidates:
            c._temp_edges = [node for node in self.g[c] if node not in candidates]
        nett = self.g.copy()
        nett.remove_nodes_from(candidates)
        components = list(nx.connected_component_subgraphs(nett))
        for comp in components:
            for node in comp:
                node._temp_comp = comp
        for c in candidates:
            for node in c._temp_edges:
                node._temp_comp.add_node(c)
                node._temp_comp.add_edge(c, node) # this is unnecessary
        num_balkanised = 0
        for comp in components:
            num_countries = sum(1 for node in comp if node in countries)
            assert num_countries > 0
            if num_countries == 1:
                num_balkanised += len(comp) - 1
        for node in self.g:
            if hasattr(node, '_temp_edges'):
                del node._temp_edges
            elif hasattr(node, '_temp_comp'):
                del node._temp_comp
            else:
                assert False
        return num_balkanised/len(self.g)

    def add_edge(self, a, b):
        self.g.add_edge(a, b)

    def delete_edge(self, a, b):
        self.g.remove_edge(a, b)

    def generate_connection_candidate(self, node, old):
        """
        Suggest a new connection for a node to make after disconnecting from "old".
        If breaking the connection would disconnect the network, the new connection must reconnect it.
        Can return None if there are no valid candidates (in which case the connection to "old" cannot be broken)
        """
        components = nx.number_connected_components(self.g)
        if components > 1:
            return self.preferential_node(exclude=([node, old] + list(nx.node_connected_component(self.g, node))))
        else:
            return self.preferential_node(exclude=([node, old] + list(self.g[node])))

    def preferential_node(self, exclude=[]):
        """ Pick a node at random with probability proportional to its degree """
        total_nodes = sum(len(self.g[node]) for node in self.g if node not in exclude)
        if sum(1 for n in self.g if n not in exclude) == 0:
            return None

        rnd = random.random() * total_nodes

        for node in self.g:
            if node not in exclude:
                rnd -= len(self.g[node])
                if rnd <= 0:
                    return node

        assert False

    def initialise(self, nodes, edges_per_node):
        self.g = nx.generators.barabasi_albert_graph(len(nodes), edges_per_node)
        nx.relabel_nodes(self.g, {i:n for i,n in enumerate(nodes)}, copy=False)

    def calc_path(self, a, b):
        return nx.shortest_path(self.g, a, b)