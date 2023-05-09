import networkx as nx


class ASTGraph:
    def __init__(self, src_language, src_code, properties, root_node, parser):
        self.src_language = src_language
        self.src_code = src_code
        self.properties = properties
        self.root_node = root_node
        self.parser = parser
        self.index = self.parser.index
        self.all_tokens = self.parser.all_tokens
        self.label = self.parser.label
        self.method_map = self.parser.method_map
        self.method_calls = self.parser.method_calls
        self.start_line = self.parser.start_line
        self.graph = self.to_networkx()

    def get_AST_nodes(self, root_node, AST, AST_index):

        if root_node.is_named:
            current_node_id = AST_index[
                (root_node.start_point, root_node.end_point, root_node.type)
            ]
            if current_node_id in self.all_tokens:

                label = self.label[current_node_id]
            else:
                label = root_node.type
            AST.add_node(
                current_node_id,
                node_type=root_node.type,
                label=label,
                shape="box",
                style="rounded, filled",
                fillcolor="#BFE6D3",
                color="white",
            )
            for child in root_node.children:
                if child.is_named:
                    child_id = self.get_AST_nodes(child, AST, AST_index)
                    if child_id != None:
                        AST.add_edge(current_node_id, child_id)
            return current_node_id

    def merge_nodes(self, G, nodes, new_node):
        """
        Merges the selected `nodes` of the graph G into one `new_node`,
        meaning that all the edges that pointed to or from one of these
        `nodes` will point to or from the `new_node`.
        """

        nodes.remove(new_node)

        incoming_edges = G.in_edges(nodes, data=True)
        outgoing_edges = G.out_edges(nodes, data=True)
        for i in incoming_edges:
            G.add_edge(i[0], new_node, **i[2])
        for i in outgoing_edges:
            G.add_edge(new_node, i[1], **i[2])

        for n in nodes:  # remove the merged nodes
            G.remove_node(n)

    def collapse(self, G):
        name_to_index_map = {}
        node_attributes = {}

        for variable in self.all_tokens:
            if variable not in self.method_map:
                name_to_index_map[self.label[variable]] = set()

        for node, properties in G.nodes(data=True):
            name = properties["label"]
            if name in name_to_index_map.keys():
                name_to_index_map[name].add(node)

        for name, indexes in name_to_index_map.items():
            node_list = list(indexes)
            chosen_node = min(node_list)
            node_attributes[chosen_node] = G.nodes(data=True)[chosen_node]
            self.merge_nodes(G, node_list, chosen_node)
        nx.set_node_attributes(G, node_attributes)

    def minimize(self, root_node, blacklisted_nodes):
        if root_node.type in self.properties.get("blacklisted", []):
            blacklisted_nodes.append(
                self.index[(root_node.start_point, root_node.end_point, root_node.type)]
            )

        for child in root_node.children:
            self.minimize(child, blacklisted_nodes)

        return blacklisted_nodes

    def remove_blacklisted_nodes(self, G):
        blacklisted_nodes = self.minimize(self.root_node, [])

        for node in blacklisted_nodes:
            for predecessor in G.predecessors(node):
                for successor in G.successors(node):
                    G.add_edge(predecessor, successor)

            G.remove_node(node)

    def to_networkx(self):
        G = nx.MultiDiGraph()
        self.get_AST_nodes(self.root_node, G, self.index)
        if self.properties.get("collapsed", False) == True:
            self.collapse(G)
        if self.properties.get("minimized", False) == True:
            self.remove_blacklisted_nodes(G)

        nx.set_edge_attributes(G, "AST_edge", "edge_type")
        nx.set_edge_attributes(G, "indigo", "color")
        nx.set_edge_attributes(G, "vee", "shape")
        return G
