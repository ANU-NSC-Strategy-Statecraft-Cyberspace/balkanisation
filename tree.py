import random
import networkx as nx

class Tree:
    def __init__(self):
        self.g = None
        self.centralities = {}

    def update_centralities(self):
        self.centralities = nx.betweenness_centrality(self.g)

    def balkanisation(self):
        largest = max(nx.biconnected_components(self.g), key=len)
        return 1 - len(largest)/len(self.g)

    def relative_balkanisation(self, countries):
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
        Breaks the connection between two nodes. Then, one of the nodes
        makes a new connection elsewhere.
        """
        components = nx.number_connected_components(self.g)
        if components > 1:
            return self.preferential_node(exclude=([node, old] + list(nx.node_connected_component(self.g, node))))
        else:
            return self.preferential_node(exclude=([node, old] + list(self.g[node])))

    def preferential_node(self, exclude=[]):
        total_nodes = sum(len(self.g[node]) for node in self.g if node not in exclude)
        if sum(1 for n in self.g if n not in exclude) == 0:
            return None

        rnd = random.random() * total_nodes

        for node in self.g:
            if node not in exclude:
                rnd -= len(self.g[node])
                if rnd <= 0:
                    return node

        raise Exception ("did not pick a node!")

    def initialise(self, nodes, edges_per_node):
        self.g = nx.generators.barabasi_albert_graph(len(nodes), edges_per_node)
        nx.relabel_nodes(self.g, {i:n for i,n in enumerate(nodes)}, copy=False)

    def calc_path(self, a, b):
        return nx.shortest_path(self.g, a, b)