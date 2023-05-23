import networkx as nx


class CFGGraph:
    def __init__(self, src_language, src_code, properties, root_node, parser):
        self.src_language = src_language
        self.src_code = src_code
        self.properties = properties
        self.root_node = root_node
        self.parser = parser
        self.index = self.parser.index
        self.all_tokens = self.parser.all_tokens

    def to_networkx(self, CFG_node_list, CFG_edge_list):
        G = nx.MultiDiGraph()
        for node in CFG_node_list:
            label = str(node[1]+1) + "_ " + node[2]
            G.add_node(node[0], label=label, type_label=node[3])
        for edge in CFG_edge_list:
            additional_data = None
            if len(edge) == 4:
                additional_data = edge[3]
            if edge[2].startswith("constructor_call"):
                normal_label = "constructor_call"
            elif edge[2].startswith("method_call"):
                normal_label = "method_call"
            else:
                normal_label = edge[2]
            G.add_edge(
                edge[0],
                edge[1],
                controlflow_type=edge[2],
                edge_type="CFG_edge",
                label=normal_label,
                color="red",
            )
            if additional_data:
                for key,value in additional_data.items():
                    G.edges[edge[0], edge[1], 0][key] = value
        return G
